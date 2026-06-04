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
# NumPy dtypes to NIFTI dtypes. Some of these are due to constraints
# within the available set of nifti types (and/or the plethora of
# NumPy types). Some of these are due to practical software
# considerations.  
# 
# Some of the mappings might lead to lossy-ness, which we denote here,
# as well.  Some of these are unavoidable, and some are very unlikely.
#
# The structure of the dictionaries here is the same.
#    key   : NumPy dtype (and this list could grow over time)
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

# special keywords output during mapping process, to describe the
# relative dtype-in and dtype-to-be-out
LIST_allowed_map_desc = [
    'lossy',
    'noloss',
    'same',
    'sysdep',
]
STR_allowed_map_desc = ', '.join(LIST_allowed_map_desc)

# how each known NumPy numerical dtype maps to NIFTI codes;
# the 'theoretical' general list for many software
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

# how each known NumPy numerical dtype maps to NIFTI codes;
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

# how each known NumPy numerical dtype maps to NIFTI codes;
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

# the keys are the special keywords for selecting respective mapping
# rules (AKA dictionary), given by the value
DICT_allowed_np_dtype_map_rules = {
    'general'    : DICT_np_dtype_to_nifti1_type_general,
    'reduced'    : DICT_np_dtype_to_nifti1_type_reduced,
    'afni_rules' : DICT_np_dtype_to_nifti1_type_afni_rules,
}
LIST_allowed_np_dtype_map_rules = list(DICT_allowed_np_dtype_map_rules.keys())
STR_allowed_np_dtype_map_rules  = ', '.join(LIST_allowed_np_dtype_map_rules)

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


def translate_numpy_dtype_to_nifti(din, map_rules='reduced', verb=1):
    """The input din is a numpy dtype, likely obtained as the
attribute describing the elements of some numpy array (e.g.,
NPARRAY.dtype.type).  This function determines which NIFTI type and
bitpix values it will correspond to.

Because life is complicated, some choices have to be made about
mapping some potential NumPy dtypes to the more restricted set of
NIFTI types. There are 3 sets of mapping rules, which are basically
just dictionaries for every known (or found) NumPy dtype.  The user
must choose one mapping style, via the map_rules kwarg.  The options
for kwarg values are: 
     general, reduced, afni_rules

This function will output the NumPy dtype that the should be used for
the output np.array.  Sometimes this is the same as the input,
sometimes it is different but lossless, and sometimes lossy (or
system-dependent potentially lossy).  So, there is a keyword output to
describe the specific mapping:
     lossy, noloss, sysdep, same

Parameters
----------
din : (np.ndarray).dtype
    a NumPy array's dtype
map_rules : str
    a keyword argument to specify the set of mapping rules to be used
    (see LIST_allowed_np_dtype_map_rules for opts)
verb : int
    amount of verbosity to use in general processing

Returns
-------
is_fail : int
    0 for success, nonzero for failure
nifti_key : str
    the text string that is the key for type and bitpix dictionaries
    in the NIFTI definition
nifti_datatype : int
    code for the NIFTI header field: datatype
nifti_bitpix : int
    code for the NIFTI header field: bitpix
dout : (np.ndarray).dtype
    the recommended NumPy dtype for outputtting, to match nifti_datatype 
    and nifti_bitpix
map_desc : str
    a special keyword for describing the mapping from din -> dout;
    see LIST_allowed_map_desc

    """

    # init null values
    nifti_key      = ''
    nifti_datatype = 0
    nifti_bitpix   = 0
    dout           = None
    map_desc       = None

    BAD_RETURN = (-1, nifti_key, nifti_datatype, nifti_bitpix, dout, map_desc)

    # verify map_rules is allowed
    is_fail, D = select_map_rules(map_rules, verb=verb)
    if is_fail :
        return BAD_RETURN

    # verify key is allowed
    D_keys = list(D.keys())
    if din not in D_keys :
        msg = "NumPy input dtype '{}' not known. ".format(din)
        msg+= "Should be one of these:\n"
        msg+= ','.join(D_keys)
        lsu.EP1(msg)
        return BAD_RETURN

    # the values from the mapping dict for this input dtype
    nifti_key, dout, map_desc = D[din]

    # ... and we map the nifti_key code to the actual field values (ints)
    nifti_datatype = lnd.DICT_nifti_datatype[nifti_key]
    nifti_bitpix   = lnd.DICT_nifti_bitpix[nifti_key]

    return 0, nifti_key, nifti_datatype, nifti_bitpix, dout, map_desc

def select_map_rules(map_rules, verb=1):
    """Verify that the input map_rules str is a valid
choice. Then output the chosen dictionary.

Parameters
----------
map_rules : str
    a keyword argument (see LIST_allowed_np_dtype_maps for opts)
verb : int
    amount of verbosity to use in general processing

Returns
-------
is_fail : int
    0 for success, nonzero for failure
D : dict
    the dictionary describing/defining the chosen map_rules

"""

    D = {}
    BAD_RETURN = ( -2, D)

    # check keyword arg
    if map_rules not in LIST_allowed_np_dtype_map_rules :
        msg = "Chosen map_rules '{}' ".format(map_rules)
        msg+= "not in known list: {}".format(STR_allowed_np_dtype_map_rules)
        lsu.EP1(msg)
        return BAD_RETURN

    D = DICT_allowed_np_dtype_map_rules[map_rules]

    return 0, D


# ===========================================================================

if __name__ == "__main__" :

    print("++ No examples yet")
