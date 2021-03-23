 
### Copied and modified from
### https://github.com/fastmachinelearning/hls4ml/
### blob/3d80b3302a7c58c6aa270eff105127da9f7c3509/hls4ml/report/vivado_report.py#L99 ###

from __future__ import print_function
import os
import re
import xml.etree.ElementTree as ET
from hls4ml.report.vivado_report import _parse_build_script, _find_solutions

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