def resize(hist: np.ndarray, bin_x: int, bin_y: int) -> np.ndarray:
    """
    Resize a 2D histogram i.e. change the bin resolution for a histogram of
    counts or similar, where interpolation using something like cv2.resize
    doesn't make sense.
    

    Parameters
    ----------
    hist: np.ndarray
        2D histogram
    
    bin_x: int
        The new number of bins along the x (zeroth) dimension.
        Must satisfy hist.shape[0] % bin_x == 0.
        
    bin_y: int
        The new number of bins along the y (first) dimension.
        Must satisfy hist.shape[1] % bin_y == 0.
    
    Returns
    -------
    out: np.ndarray
        Resized histogram of size (bin_x, bin_y).
    """
    
    if hist.shape[0] % bin_x != 0 or hist.shape[1] % bin_y != 0:
        raise ValueError("Can't resize histogram without interpolation.")
    
    
    return hist.reshape(bin_x, hist.shape[0]//bin_x, bin_y, hist.shape[1]//bin_y).sum(axis=1).sum(axis=2)
