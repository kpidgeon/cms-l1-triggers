import numpy as np
from sklearn.metrics import confusion_matrix


def _confusion_matrix(true, pred):
    
    tn, fp, fn, tp = 0, 0, 0, 0
    
    for i in range(len(true)):
        
        if true[i] == pred[i]:
            if true[i]:
                tp += 1
            else:
                tn += 1
        else:
            if true[i]:
                fn += 1
            else:
                fp += 1
    
    return tn, fp, fn, tp


def custom_roc(pred, true, discrim_thresholds=None):
  
  if discrim_thresholds is None:
    discrim_thresholds = [2.] + [i for i in np.arange(0, 1., .001)]
  
  tn, fp, fn, tp = np.array(
    [[_confusion_matrix(true, 
                        list(map(lambda x: x>t, pred)))] for t in discrim_thresholds]).T
    
  fpr = fp / (fp + tn)
  tpr = tp / (tp + fn)
  
  return fpr, tpr, discrim_thresholds
  
  


def eff_rate(fpr, tpr, thresholds, bg_rate, true=None, pred=None, errors=None):
    """
    Transform a ROC curve into an efficiency vs. trigger rate curve.
    
    Efficiency is just the True Positive Rate (TPR), and the trigger rate
    is approximately R = FPR * bg_rate, assuming a negligible signal
    cross-section.
    
    
    Parameters
    ----------
    fpr, tpr, thresholds: np.array
        These are the return values of sklearn.roc_curve, but they could come
        from another source.
        
    bg_rate: float
        This the frequency of background events with which to normalise the FPR.
        For pileup at the LHC, this is 40MHz, the bunch-crossing rate.
        
    true, pred: np.array (default: None)
        The true labels and predicted labels.
        
    errors: str (default: None)
        The type of errors to calculate. Must be one of {'binomial'}.
        
    
    Returns
    -------
    rates, rates_errs: np.array
        The trigger rates and corresponding errors (errors are zero if type
        unspecified).
    
    effs, effs_errs: np.array
        The signal efficiencies (a.k.a sensitivity) and corresponding errors
        (errors are zero if type unspecified).    
    """
        

    rates = fpr*bg_rate
    rates_errs = np.zeros(rates.shape)
    
    effs = tpr
    effs_errs = np.zeros(effs.shape)
    
    if errors == 'binomial':
      
      if true is None or pred is None:
        raise ValueError('true and pred must be provided for error calculation.')
      
      if true.shape[0] != pred.shape[0]:
        raise ValueError('true and pred should be 1D arrays of the same length.')
      
      print('Calculating errors')
      # could have used sklearn.confusion_matrix here
      tn, fp, fn, tp = np.array(
	[[_confusion_matrix(true, 
		     list(map(lambda x: x>t, pred)))] for t in thresholds]).T
	
      # calculate binomial errors
      effs_errs = np.sqrt((effs * (1-effs)) / (tp+fn))
      rates_errs = np.sqrt((fpr * (1-fpr)) / (fp+tn))*bg_rate
      

    # get rate in kHz by default
    rates = np.divide(rates, 1000)
    rates_errs = np.divide(rates_errs, 1000)

    return rates, rates_errs, effs, effs_errs



def optimal_eff_rate(effs, rates, effs_errs=None, rates_errs=None):
    
    if effs.shape != rates.shape:
        raise ValueError(f"Shapes {effs.shape} and {rates.shape} are not aligned.")


    uniq_rates = set()
    opt_effs = []
    
    # store indices of optimal efficiencies
    # for indexing pre-computed errors
    idx = []
    
    for _idx, i in enumerate(effs):
        if not rates[_idx] in uniq_rates:
            uniq_rates.add(rates[_idx])
            opt_effs.append(i)
            idx.append(_idx)
        elif i > opt_effs[-1]:
            opt_effs[-1] = i
            idx[-1] = _idx
        
    if effs_errs is not None:
      effs_errs = np.take(effs_errs, idx)
    else:
      effs_errs = np.zeros(opt_effs.shape)
	
    
    if rates_errs is not None:
      rates_errs = np.take(rates_errs, idx)
    else:
      rates_errs = np.zeros(uniq_rates.shape)    


    return (np.array(opt_effs), np.array(sorted(list(uniq_rates))),
            effs_errs, rates_errs)
