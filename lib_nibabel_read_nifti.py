#!/usr/bin/env python

import os, copy

import numpy   as np
import nibabel as nib

from . import lib_simple_utils as lsu

# read in NIFTI volumes via nibabel, and convert to desired pieces

# ============================================================================

def read_nifti_to_nibabel(fname, set_dtype=None, verb=1):
    """For a given NIFTI dset fname, provide a data array and header
separately.  This function uses nibabel and NumPy.

The user can choose to set an explicit dtype for the data array
elements using the dtype kwarg, (e.g., : set_dtype=np.float32).

Parameters
----------
fname : str
    name of NIFTI dset/file
set_dtype : dtype
    user-chosen dtype for the data array elements using the dtype
verb : int
    verbosity level for messages whilst working

Returns
-------
is_fail : int
    0 on success, nonzero on failure
data : np.ndarray
    the data array part of the NIFTI dset
nib_hdr : Nifti1Header
    nibabel-formatted NIFTI header obj

    """

    BAD_RETURN = (-1, None, None)

    # check existence of dset
    if not(os.path.isfile(fname)) :
        msg = "Input NIFTI fname {} does not exist.".format(fname)
        lsu.EP1(msg)
        return BAD_RETURN

    # read dset
    try:
        A = nib.load(fname)
    except:
        msg = "Failed to read NIFTI dset: {}.".format(fname)
        lsu.EP1(msg)
        return BAD_RETURN

    # ----- data part

    data = np.asanyarray(A.dataobj)
    
    # ... and maybe convert it to a chosen type, via the user
    if set_dtype is not None:
        try:
            if verb :
                ttt = lsu.simple_type(data.dtype.type)
                uuu = lsu.simple_type(set_dtype)
                msg = "Converting dset {} ".format(fname)
                msg+= "array of dtype '{}' ".format(ttt)
                msg+= "to be user choice: {}".format(uuu)
            data = data.astype(set_dtype)
        except:
            msg = "Failed to set data array to dtype: {}".format(set_dtype)
            lsu.EP1(msg)
            return BAD_RETURN

    # ----- header part

    try: 
        nib_hdr = A.header.copy()
    except:
        msg = "Failed get nibabel header for NIFTI dset: {}".format(fname)
        lsu.EP1(msg)
        return BAD_RETURN

    return 0, data, nib_hdr

def read_nifti_to_nibabel_simple(fname, verb=1):
    """For a given NIFTI dset fname simply check+read in the file as a
Nifti1Image, not as a separated array+hdr pair---see
read_nifti_to_nibabel() for that.  This function uses nibabel.

Parameters
----------
fname : str
    name of NIFTI dset/file
verb : int
    verbosity level for messages whilst working

Returns
-------
is_fail : int
    0 on success, nonzero on failure
A : nib.Nifti1Image
    the nibabel-formatted Nifti1Image dset

    """

    BAD_RETURN = (-1, None)

    # check existence of dset
    if not(os.path.isfile(fname)) :
        msg = "Input NIFTI fname {} does not exist.".format(fname)
        lsu.EP1(msg)
        return BAD_RETURN

    # read dset
    try:
        A = nib.load(fname)
    except:
        msg = "Failed to read NIFTI dset: {}.".format(fname)
        lsu.EP1(msg)
        return BAD_RETURN

    return 0, A

# ----------------------------------------------------------------------------


# ============================================================================

if __name__ == "__main__" :

    print("++ No examples yet")
