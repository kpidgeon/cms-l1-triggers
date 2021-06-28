import matplotlib.pyplot as plt
from sklearn.metrics import auc as _auc
import pandas as pd

def plot_roc(ax, fpr, tpr, xlabel=None, ylabel=None, 
             legend=False, auc=True, **kwargs):

    lbl = ''
    if 'label' in kwargs:
      lbl += kwargs['label'] + ' '
      del kwargs['label']
        
    if auc:
      lbl += f'AUC={_auc(fpr, tpr):.2f}'
      
    ax.plot(fpr, tpr, label=lbl, **kwargs)
    
    if xlabel is None:
        ax.set_xlabel('False positive rate')
    else:
        ax.set_xlabel(xlabel)
    
    
    if ylabel is None:
        ax.set_ylabel('True positive rate')
    else:
        ax.set_ylabel(ylabel)
    
    if legend:
        ax.legend()




def plot_eff_rate(ax, effs, rates, effs_errs=None, rates_errs=None, 
                  xlabel=None, ylabel=None, legend=False, **kwargs):
  
  plot = 'plot'
  if effs_errs is not None or rates_errs is not None:
    plot = 'errorbar'
    
  if effs_errs is None:
    effs_errs = np.zeros(effs.shape)
      
  if rates_errs is None:
    rates_errs = np.zeros(rates.shape)
        
        
  if plot == 'plot':
    ax.plot(rates, effs, **kwargs)
  elif plot == 'errorbar':
    ax.errorbar(x=rates, y=effs, xerr=rates_errs, yerr=effs_errs, 
                **kwargs)
            
            
  ax.set_ylim((0, 1.))
            
  if xlabel is None:
    ax.set_xlabel('Trigger rate (kHz)')
  else:
    ax.set_xlabel(xlabel)
              
  if ylabel is None:
    ax.set_ylabel('Signal efficiency')
  else:
    ax.set_ylabel(ylabel)
              
  if legend:
    ax.legend()
    
    
    
def plot_resources(ax, build_result, relative=True, use_percentage=True):
      
  res = ['BRAM_18K', 'DSP48E', 'FF', 'LUT']
    
  abs_usage = [float(build_result[r]) for r in res if r in res]
  rel_usage = [abs_usage[i] / float(build_result['Available' + r])
              for i, r in enumerate(res) if r in res]
    
  data = pd.DataFrame(data={'resource': [r for r in res],
                            'usage': abs_usage,
                            'rel_usage': rel_usage})
    
  if ax is not None:
    if relative:
      if use_percentage:
        ax.bar(res, data['rel_usage']*100.)
      else:
        ax.bar(res, data['rel_usage'])
    else:
      ax.bar(res, abs_usage)
        
  return data
    
    
    