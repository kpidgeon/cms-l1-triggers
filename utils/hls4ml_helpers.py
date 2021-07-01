
### Copied and modified from
### https://github.com/fastmachinelearning/hls4ml/

from __future__ import print_function
import os
import re
import xml.etree.ElementTree as ET
from hls4ml.converters import convert_from_keras_model
from hls4ml.report.vivado_report import _parse_build_script, _find_solutions
import yaml
from qkeras.utils import _add_supported_quantized_objects
from tensorflow.keras.models import load_model

def parse_yaml_config_no_model(config_file):
  """
  Parse the hls4ml YAML config file without loading in the stored model,
  as for qkeras models the custom objects aren't recognised.
  
  Parameters:
    path: str
        Config file path e.g. '/path/to/model/hls4ml_prj/hls4ml_config.yml'
        
  Returns:
    config: dict
        The parsed YAML config.
  """
  
  def construct_keras_model(loader, node):
    return
  
  yaml.add_constructor(u'!keras_model', construct_keras_model, Loader=yaml.SafeLoader)
  
  print('Loading configuration from', config_file)
  with open(config_file, 'r') as file:
    parsed_config = yaml.load(file, Loader=yaml.SafeLoader)
  
  return parsed_config


def load_qkeras_hls_model(path):
  """
  Load a qkeras model from a hls4ml project.
  
  Parameters:
    path: str
        Model path e.g. '/path/to/model/hls4ml_prj/'
        
  Returns:
    hls_model: HLSModel
        The reconstructed HLSModel object that is based on a QKeras model.
  """
  
  co = {}
  _add_supported_quantized_objects(co)
  # load qkeras model
  qkeras_model = load_model(os.path.join(path, 'keras_model.h5'), custom_objects=co)
  
  # parse the hls4ml config file without loading the model from 'keras_model.h5'
  cfg = parse_yaml_config_no_model(os.path.join(path, 'hls4ml_config.yml'))
  
  hls_model = convert_from_keras_model(qkeras_model,
                                                         hls_config=cfg['HLSConfig'],
                                                        output_dir=cfg['OutputDir'],
                                                        fpga_part=cfg['XilinxPart'],
                                                        clock_period=cfg['ClockPeriod'],
                                                        io_type=cfg['IOType'],
                                                        project_name=cfg['ProjectName'])
  
  return hls_model


def load_qkeras_model(path):
  co = {}
  _add_supported_quantized_objects(co)
  # load qkeras model
  qkeras_model = load_model(os.path.join(path, 'keras_model.h5'), custom_objects=co)
  
  return qkeras_model


def parse_vivado_impl_report(hls_dir):
	if not os.path.exists(hls_dir):
		print('Path {} does not exist. Exiting.'.format(hls_dir))
		return
	
	prj_dir = None
	top_func_name = None
	
	if os.path.isfile(hls_dir + '/build_prj.tcl'):
		prj_dir, top_func_name = _parse_build_script(hls_dir + '/build_prj.tcl')
					
	if prj_dir is None or top_func_name is None:
		print('Unable to read project data. Exiting.')
		return
		
	sln_dir = hls_dir + '/' + prj_dir
	if not os.path.exists(sln_dir):
		print('Project {} does not exist. Rerun "hls4ml build -p {}".'.format(prj_dir, hls_dir))
		return
		
	solutions = _find_solutions(sln_dir)
	if len(solutions) > 1:
		print('WARNING: Found {} solution(s) in {}. Using the first solution.'.format(len(solutions), sln_dir))
			
	report = {}
			
	sim_file = hls_dir + '/tb_data/csim_results.log'
	if os.path.isfile(sim_file):
		csim_results = []
		with open(sim_file, 'r') as f:
			for line in f.readlines():
				csim_results.append([float(r) for r in line.split()])
				report['CSimResults'] = csim_results
	
	sim_file = hls_dir + '/tb_data/rtl_cosim_results.log'
	if os.path.isfile(sim_file):
		cosim_results = []
		with open(sim_file, 'r') as f:
			for line in f.readlines():
				cosim_results.append([float(r) for r in line.split()])
				report['CosimResults'] = cosim_results
	
	impl_file = sln_dir + '/' + solutions[0] + '/impl/report/vhdl/{}_export.xml'.format(top_func_name)
	if os.path.isfile(impl_file):
		root = ET.parse(impl_file).getroot()
		
		# timing
		perf_node = root.find('./TimingReport')
		report['TargetClockPeriod'] = perf_node.find('./TargetClockPeriod').text
		report['AchievedClockPeriod'] = perf_node.find('./AchievedClockPeriod').text
		# Area
		area_node = root.find('./AreaReport')
		for child in area_node.find('./Resources'):
			report[child.tag] = child.text
			for child in area_node.find('./AvailableResources'):
				report['Available' + child.tag] = child.text
		else:
			print('Export report not found.')
			
	return report