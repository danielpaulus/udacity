# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 17:07:03 2016

@author: daniel
"""

import numpy as np



#these arrays will be used to define the state space
#by creating the cartesian product which will result in a total of 512 combinations
next_waypoint=['wp_left', 'wp_right', 'wp_forward','wp_none']
traffic_light=['green','red']
oncoming=['on_forward','on_left','on_right','on_none']
left=['lf_forward','lf_left','lf_right','lf_none']
right=['rg_forward','rg_left','rg_right','rg_none']


#helper method
def form_state_space():
    result= cartesian((next_waypoint,traffic_light,oncoming,left,right))
    print "Created state space with {} entries.".format(len(result))
    return result


#taken from: http://stackoverflow.com/questions/1208118/using-numpy-to-build-an-array-of-all-combinations-of-two-arrays
def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out