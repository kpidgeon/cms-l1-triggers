import numpy as np



def confusion_matrix_components(true, pred):
    
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




def _confusion_matrix(true, pred, thresholds):
    
    tn, fp, fn, tp = [], [], [], []
    for t in thresholds:
        
        _tn, _fp, _fn, _tp = confusion_matrix_components(true, pred)
        
        tn.append(_tn)
        fp.append(_fp)
        fn.append(_fn)
        tp.append(_tp)
        
    return np.array(tn), np.array(fp), np.array(fn), np.array(tp)



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
    
    if true.shape != pred.shape:
        raise ValueError('true and pred should be 1D arrays of the same length.')
        

    rates = fpr*bg_rate
    rates_errs = np.zeros(rates.shape)
    
    effs = tpr
    effs_errs = np.zeros(effs.shape)
    
    if errors == 'binomial':
        tn, fp, fn, tp = _confusion_matrix(true, pred, thresholds)
        
        # calculate binomial errors
        effs_errs = np.sqrt((effs * (1-effs)) / (tp+fn))
        rates_errs = np.sqrt((fpr * (1-fpr)) / (fp+tn))*bg_rate
        

    # rate in Hz
    return rates, rates_errs, effs, effs_errs



def optimal_eff_rate(effs, rates, effs_errs=None, rates_errs=None):
    
    if effs.shape != rates.shape:
        raise ValueError(f"Shapes {effs.shape} and {rates.shape} are not aligned.")
    
    _rs = set()
    _es = []
    
    # store indices of optimal efficiencies
    # for indexing pre-computed errors
    _idx = []
    
    for idx, i in enumerate(effs):
        if not rates[idx] in _rs:
            _rs.add(rates[idx])
            _es.append(i)
            _idx.append(idx)
        elif i > _es[-1]:
            _es[-1] = i
            _idx[-1] = idx
        
    
    effs_errs = np.take(effs_errs, _idx)
    rates_errs = np.take(rates_errs, _idx)
    
    return sorted(list(_es)), sorted(list(_rs)), effs_errs, rates_errs
