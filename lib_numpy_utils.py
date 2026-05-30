#!/usr/bin/env python

# Functions and objects for navigating NIFTI-format features, when
# using Python's NumPy module. 
# 
# auth: PA Taylor (SSCC, NIMH, NIH, USA)
#       RC Reynolds (SSCC, NIMH, NIH, USA)
# ============================================================================

import numpy   as     np

from . import lib_simple_utils as lsu
from . import lib_nifti_defs   as lnd

# ============================================================================
# mapping rules from NumPy Python types to NIFTI data types.

# The mapping rules are made to address the following situation:
# having a NumPy array of a given dtype, and wanting to know what the
# correspondindg NIFTI type (and bitpix) should be.  As a further
# subtlety, one might have to choose a NIFTI type that has some
# 'lossyness'; additionally, one might be forced to change the dtype
# of the array itself, to match with a chooseable or chosen NIFTI
# type.  Each mapping dictionary includes this rich set of information
# in its values.
#
# There are multiple dictionaries here, because there are (at least) a
# few major ways that one might want to choose to map all possible
# NumPy datatypes to NIFTI types. Some of these are due to constraints
# within the available set of nifti types (and/or the plethora of
# NumPy types). Some of these are due to practical software
# considerations.  
# 
# Some of the mappings might lead to lossy-ness, which we denote here,
# as well.  Some of these are unavoidable, and some are very unlikely.
#
# The structure of the dictionaries here is the same.
#    key   : NumPy datatype (and this list could grow over time)
#    value : list of 3 elements:
#            [0] known NIFTI keyword within type and bitpix fields, to
#                which the 'key' dtype will be mapped
#            [1] name of NumPy dtype to which the 'key' dtype will be 
#                mapped;  this might be different than the 'key' one by 
#                necessity or choice/convenience
#            [2] a string denoting whether the given dtype->type mapping
#                will be:
#                'same'   : no change in type (inherently lossless...)
#                'noloss' : preserve all values,
#                'lossy'  : will necessarily lose values, if the full
#                           input domain is used
#                'sysdep' : the input dtype has system-dependent properties,
#                           and therefore may or may not be lossy, if the
#                           full input domain is used                    

# keywords for selecting respective mapping rules (AKA dictionary)
LIST_allowed_np_dtype_maps = [
    'general',
    'reduced',
    'afni_rules',
]
STR_allowed_np_dtype_maps = ', '.join(LIST_allowed_np_dtype_maps)

# how each known NumPy numerical datatype maps to NIFTI codes;
#  the 'theoretical' general list for many software
DICT_np_dtype_to_nifti1_type_general = {
    np.bool        : ["NIFTI_TYPE_UINT8", np.uint8, 
                      'noloss'],
    np.bool_       : ["NIFTI_TYPE_UINT8", np.uint8, 
                      'noloss'],                          # alias for np.bool
    np.uint8       : ["NIFTI_TYPE_UINT8", np.uint8, 
                      'same'],
    np.uint16      : ["NIFTI_TYPE_UINT16", np.uint16, 
                      'same'],
    np.uint32      : ["NIFTI_TYPE_UINT32", np.uint32, 
                      'same'],
    np.uintc       : ["NIFTI_TYPE_UINT32", np.uint32, 
                      'same'],                            # alias for np.uint32
    np.uint64      : ["NIFTI_TYPE_UINT64", np.uint64, 
                      'same'],    
    np.uint        : ["NIFTI_TYPE_UINT64",np.uint64, 
                      'same'],                            # alias for np.uint64
    np.int8        : ["NIFTI_TYPE_INT8",  np.int8, 
                      'same'],
    np.int16       : ["NIFTI_TYPE_INT16", np.int16, 
                      'same'],
    np.int32       : ["NIFTI_TYPE_INT32", np.int32, 
                      'same'],
    np.intc        : ["NIFTI_TYPE_INT32", np.int32, 
                      'same'],                            # alias for np.int32
    np.int64       : ["NIFTI_TYPE_INT64", np.int64, 
                      'same'],    
    np.int_        : ["NIFTI_TYPE_INT64", np.int64, 
                      'same'],                            # alias for np.int64
    np.long        : ["NIFTI_TYPE_INT64", np.int64, 
                      'same'],                            # alias for np.int64
    np.longlong    : ["NIFTI_TYPE_INT64", np.int64, 
                      'sysdep'],                          # tricky, sys-dep
    np.float16     : ["NIFTI_TYPE_FLOAT32", np.float32, 
                      'noloss'],                          # NB: upgrade!
    np.float32     : ["NIFTI_TYPE_FLOAT32", np.float32, 
                      'same'],
    np.float64     : ["NIFTI_TYPE_FLOAT64", np.float64, 
                      'same'],
    np.double      : ["NIFTI_TYPE_FLOAT64", np.float64, 
                      'same'],                           # alias for np.float64
    np.longdouble  : ["NIFTI_TYPE_FLOAT64", np.float64, 
                      'sysdep'],                          # tricky, sys-dep
    np.complex64   : ["NIFTI_TYPE_COMPLEX64", np.complex64, 
                      'same'],
    np.complex128  : ["NIFTI_TYPE_COMPLEX128", np.complex128, 
                      'noloss'],
    np.clongdouble : ["NIFTI_TYPE_COMPLEX128", np.complex128, 
                      'sysdep'],                             # tricky, sys-dep
}

# how each known NumPy numerical datatype maps to NIFTI codes;
# the 'in practice' reduced list for many software
DICT_np_dtype_to_nifti1_type_reduced = {
    np.bool        : ["NIFTI_TYPE_UINT8", np.uint8, 
                      'noloss'],
    np.bool_       : ["NIFTI_TYPE_UINT8", np.uint8, 
                      'noloss'],                          # alias for np.bool
    np.uint8       : ["NIFTI_TYPE_UINT8", np.uint8, 
                      'same'],
    np.uint16      : ["NIFTI_TYPE_UINT16", np.uint16, 
                      'same'],
    np.uint32      : ["NIFTI_TYPE_UINT32", np.uint32, 
                      'same'],
    np.uintc       : ["NIFTI_TYPE_UINT32", np.uint32, 
                      'same'],                            # alias for np.uint32
    np.uint64      : ["NIFTI_TYPE_UINT32", np.uint32, 
                      'lossy'],
    np.uint        : ["NIFTI_TYPE_UINT32", np.uint32, 
                      'lossy'],                           # alias for np.uint64
    np.int8        : ["NIFTI_TYPE_INT8",  np.int8, 
                      'same'],
    np.int16       : ["NIFTI_TYPE_INT16", np.int16, 
                      'same'],
    np.int32       : ["NIFTI_TYPE_INT32", np.int32, 
                      'same'],
    np.intc        : ["NIFTI_TYPE_INT32", np.int32, 
                      'same'],                            # alias for np.int32
    np.int64       : ["NIFTI_TYPE_INT32", np.int32, 
                      'lossy'],
    np.int_        : ["NIFTI_TYPE_INT32", np.int32, 
                      'lossy'],                           # alias for np.int64
    np.long        : ["NIFTI_TYPE_INT32", np.int32, 
                      'lossy'],                           # alias for np.int64
    np.longlong    : ["NIFTI_TYPE_INT32", np.int32, 
                      'lossy'],                           # tricky, sys-dep
    np.float16     : ["NIFTI_TYPE_FLOAT32", np.float32,
                      'noloss'],                          # NB: upgrade!
    np.float32     : ["NIFTI_TYPE_FLOAT32", np.float32, 
                      'same'],
    np.float64     : ["NIFTI_TYPE_FLOAT32", np.float32, 
                      'lossy'],
    np.double      : ["NIFTI_TYPE_FLOAT32", np.float32, 
                      'lossy'],                          # alias for np.float64
    np.longdouble  : ["NIFTI_TYPE_FLOAT32", np.float32, 
                      'lossy'],                           # tricky, sys-dep
    np.complex64   : ["NIFTI_TYPE_COMPLEX64", np.complex64, 
                      'same'],
    np.complex128  : ["NIFTI_TYPE_COMPLEX64", np.complex64, 
                      'lossy'],
    np.clongdouble : ["NIFTI_TYPE_COMPLEX64", np.complex64, 
                      'lossy'],                             # tricky, sys-dep
}

# how each known NumPy numerical datatype maps to NIFTI codes;
# the 'in practice' list for AFNI
DICT_np_dtype_to_nifti1_type_afni_rules = {
    # MRI_byte
    np.bool        : ["NIFTI_TYPE_UINT8", np.uint8, 
                      'noloss'],
    np.bool_       : ["NIFTI_TYPE_UINT8", np.uint8, 
                      'noloss'],                          # alias for np.bool
    np.uint8       : ["NIFTI_TYPE_UINT8", np.uint8, 
                      'same'],
    # MRI_short
    np.int8        : ["NIFTI_TYPE_INT16", np.int16, 
                      'noloss'],
    np.int16       : ["NIFTI_TYPE_INT16", np.int16, 
                      'same'],
    # MRI_float
    np.uint16      : ["NIFTI_TYPE_UINT16", np.float32, 
                      'noloss'],
    np.uint32      : ["NIFTI_TYPE_UINT32", np.float32, 
                      'lossy'],
    np.uintc       : ["NIFTI_TYPE_UINT32", np.float32, 
                      'lossy'],                           # alias for np.uint32
    np.uint64      : ["NIFTI_TYPE_UINT32", np.float32, 
                      'lossy'],
    np.uint        : ["NIFTI_TYPE_UINT32",np.float32, 
                      'lossy'],                           # alias for np.int64
    np.int32       : ["NIFTI_TYPE_INT32", np.float32, 
                      'lossy'],
    np.intc        : ["NIFTI_TYPE_INT32", np.float32, 
                      'lossy'],                           # alias for np.int32
    np.int64       : ["NIFTI_TYPE_INT32", np.float32,
                      'lossy'],
    np.int_        : ["NIFTI_TYPE_INT32", np.float32,
                      'lossy'],                           # alias for np.int64
    np.long        : ["NIFTI_TYPE_INT32", np.float32,
                      'lossy'],                           # alias for np.int64
    np.longlong    : ["NIFTI_TYPE_INT32", np.float32,
                      'lossy'],                           # tricky, sys-dep
    np.float16     : ["NIFTI_TYPE_FLOAT32", np.float32,
                      'noloss'],                          # NB: upgrade!
    np.float32     : ["NIFTI_TYPE_FLOAT32", np.float32,
                      'same'],
    np.float64     : ["NIFTI_TYPE_FLOAT32", np.float32,
                      'lossy'],
    np.double      : ["NIFTI_TYPE_FLOAT32", np.float32,
                      'lossy'],                          # alias for np.float64
    np.longdouble  : ["NIFTI_TYPE_FLOAT32", np.float32,
                      'lossy'],                           # tricky, sys-dep
    # MRI_complex
    np.complex64   : ["NIFTI_TYPE_COMPLEX64", np.complex64,
                      'same'],
    np.complex128  : ["NIFTI_TYPE_COMPLEX64", np.complex64,
                      'lossy'],
    np.clongdouble : ["NIFTI_TYPE_COMPLEX64", np.complex64,
                      'lossy'],                            # tricky, sys-dep
    # MRI_rgb  --- TBD
    # MRI_rgba --- not possible
}


# ============================================================================

def try_convert_list_float_int_str_arr(x, exit_on_error=False, 
                                       listify_all=True, verb=1):
    """For input NumPy arr x, see how it can convert in the following
descending order: if ndim>0, list; else, float, int, str.  If none of
those work, return None. If listify_all=True, then all outputs will be
of type list; that is, if a non-collection-type value VAL would be
output, then [VAL] will be returned.

If an error on input occurs, this program will by default return a
value of None, plus the type of the item input (its supposed to be a
np.ndarray, folks!). But users can change this behavior with the
exit_on_error kwarg.

This function was created primarily to navigate dealing with nibabel
header field values.  Those are sometimes ndim=0 arrays.

Parameters
----------
x : np.ndarray
    a NumPy array to consider converting to various types (described above)
exit_on_error: bool
    toggle whether to exit totally on input error, or to just whine
    vociferously
verb : int
    amount of verbosity to use in general processing

Returns
-------
y : list or float or int or str
    one of a descending list of types to try converting to, with str being
    the last
ytype : str
    the simple-string-format type of the item returned

    """

    # NB: in this function we use the .item() method a few times,
    # because nibabel has made ndim=0 arrays, and that is a good way
    # to get the value out and also convert it automatically to a
    # reasonable/generic type.

    import numpy as np

    if not(isinstance(x, np.ndarray)) :
        xtype = lsu.simple_type(x)
        msg   = "Input must be of type 'str', not '{}'".format(xtype)
        if exit_on_error :
            ab.EP(msg)
        else:
            ab.WP(msg)
            return None, xtype

    # check first if x can be converted to a list
    try:
        y = list(x)
        ytype = lsu.simple_type(y)

        # ... and convert elements to either float or int:
        z = [ele.item() for ele in y]

        return z, ytype
    except:
        pass

    y = x.item()

    if listify_all :
        y = [y]

    # just the type as a simple str
    ytype = lsu.simple_type(y)

    return y, ytype


def def translate_numpy_dtype_to_nifti(din, verb=1):
    """The input din is a numpy dtype, likely obtained as the
attribute describing the elements of some numpy array (e.g.,
NPARRAY.dtype).  This function determines which NIFTI type and bitpix
values it will correspond to.

This function also outputs a new type that the array should be
converted to, for the purpose of writing, if necessary.  (Otherwise,
the value returned for that information is: None)

Parameters
----------
din : (np.ndarray).dtype
    a NumPy array's dtype
verb : int
    amount of verbosity to use in general processing

Returns
-------
is_fail : int
    0 for success, nonzero for failure
nifti_type : int
    code for the NIFTI header field: type
nifti_bitpix : int
    code for the NIFTI header field: bitpix
dout : (np.ndarray).dtype
    a NumPy array's dtype
newtype : int
    0 for din==dout, else nonzero

    """

    # init null values
    nifti_type   = ''
    nifti_bitpix = ''
    newtype      = None

    BAD_RETURN = (-1, nifti_type, nifti_bitpix, newtype)


    if din in DICT_np_dtype_to_nifti_type_strict.keys():
        type_key = DICT_np_dtype_to_nifti_type_strict[din]
    else:
        # **** TEMPORARY: probably have more conditions here
        lsu.EP1("Unknown dtype: {}".format(din))
        return BAD_RETURN
                
    if din != dout :
        if verb :
            msg = "converting dtype {} -> {}".format(d, type_key)
            lsu.WP(msg)

    nifti_type   = lnd.DICT_nifti_type[dnifti]
    nifti_bitpix = lnd.DICT_nifti_bitpix[dnifti]



    return 0, nifti_type, nifti_bitpix, newtype

# ===========================================================================

if __name__ == "__main__" :
