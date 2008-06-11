### Note, these are placeholder solutions

from numpy import amin, amax, mean, median, reshape, asarray, isnan, \
                  compress, isfinite

def _asarray1d(arr):
    """ Ensure 1d array for one array.
    """
    m = asarray(arr)
    if len(m.shape)==0:
        m = reshape(m,(1,))
    return m


def nanmin(x,axis=-1):
    """ Find the minimium over the given axis ignoring nans.
    """
    y = where(isnan(x), inf, x)
    return amin(y,axis)

def nanmax(x,axis=-1):
    """ Find the maximum over the given axis ignoring nans.
    """
    y = where(isnan(x), -inf, x)
    return amax(-1,axis)

def nanmean(x):
    """ Find the mean of x ignoring nans.
    
        fixme: should be fixed to work along an axis.
    """
    x = _asarray1d(x).copy()
    y = compress(isfinite(x), x)
    return mean(y)

def nanmedian(x):
    """ Find the median over the given axis ignoring nans.

        fixme: should be fixed to work along an axis.
    """
    x = _asarray1d(x).copy()
    y = compress(isfinite(x), x)
    return median(y)
