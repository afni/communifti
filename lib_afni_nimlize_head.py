#!/usr/bin/env python

# ============================================================================
# 
# A library file for helping to convert AFNI-format *.HEAD files info
# that has already been read in, to a NIML-format XML structure, which
# can be used to populate a NIFTI extension.
#
# auth: PA Taylor (SSCC, NIMH, NIH, USA)
#
# ============================================================================

import os, sys, copy

# ============================================================================
# list of AFNI HEAD attributes that are removed when creating NIFTI
# dset NIML extension

# List of dataset attributes NOT to save in a NIfTI-1.1 file (see
# thd_nifti_write.c -> static char *badlist[])
LIST_afni_attr_remove_nifti_ext = [
    'IDCODE_STRING',
    'DATASET_RANK',
    'DATASET_DIMENSIONS',
    'TYPESTRING',
    'SCENE_DATA',
    'ORIENT_SPECIFIC',
    'ORIGIN',
    'DELTA',
    'TAXIS_NUMS',
    'TAXIS_FLOATS',
    'TAXIS_OFFSETS',
    'BYTEORDER_STRING',
    'BRICK_TYPES',
    'BRICK_FLOAT_FACS',
    'STAT_AUX',
    'LABEL_1',
    'LABEL_2',
    'DATASET_NAME',
]

# ============================================================================

def nimlize_afni_adict(Adict, Ndict, use_removelist=True, verb=1):
    """

Parameters
----------
Adict : dict
    dictionary of AFNI header attributes; each value is a list
Ndict : dict
    dictionary of NIFTI header attributes
use_remove_list : bool
    follow the AFNI C code and remove some AFNI attr from the NIFTI 
    NIML ext here
verb : int
    verbosity level for messages whilst working

Returns
-------
is_fail : int
    0 on success, nonzero on failure
nimldict : dict
    dictionary of NIML-format header attributes

"""

    BAD_RETURN = ( -1, {} )

    # ----- preliminary extraction/processing

    # get XML self_idcode from IDCODE attribute
    if 'IDCODE_STRING' in Adict:
        self_idcode = Adict['IDCODE_STRING'][0]
    else:
        self_idcode = ''

    # get NIfTI_nums string from NIFTI field info
    is_fail, str_nifti_nums = make_nifti_nums(Ndict, verb=verb)
    if is_fail:
        return BAD_RETURN

    nimldict = {
        'name'        : 'AFNI_attributes',
        'self_idcode' : self_idcode,
        'NIfTI_nums'  : str_nifti_nums,
        'elements'    : [],
    }

    # ----- fill nimldict['elements'] with all (utilized) AFNI attributes

    for aname, avals in Adict.items():


        # skip over some AFNI HEAD attributes, like main C code does
        if use_removelist and aname in LIST_afni_attr_remove_nifti_ext :
            continue

        # process the attribute -> NIML dictionary element
        is_fail, dict_elem = \
            make_AFNI_atr_element(aname, avals, verb=verb)
        if is_fail :
            return BAD_RETURN

        # ... and attach the NIML element to the main nimldict
        nimldict['elements'].append(dict_elem)


    return 0, nimldict

# ---------------------

def make_nifti_nums(Ndict, verb=1):
    """Supplementary function to create a nifti_nums string from the
'dim' field in a NIFTI dset header (provided via input Ndict
dictionary of NIFTI info).

The nifti_nums string contains: dim[1:6], and datatype.

Parameters
----------
Ndict : dict
    dictionary of NIFTI header attributes
verb : int
    verbosity level for messages whilst working

Returns
-------
is_fail : int
    0 on success, nonzero on failure
str_nifti_nums : str
    string of the nifti_nums info

    """

    BAD_RETURN = (-1, '')

    # check for necessary keys

    if 'dim' not in Ndict.keys() :
        print("** ERROR: Failure to create nifti_nums str;")
        print("   No 'dim' key in input Ndict")
        return BAD_RETURN

    if 'datatype' not in Ndict.keys() :
        print("** ERROR: Failure to create nifti_nums str;")
        print("   No 'datatype' key in input Ndict")
        return BAD_RETURN

    try: 
        # Do the work to estimate the nifti_nums string

        dim = Ndict['dim']

        nx = dim[1]
        ny = dim[2]
        nz = dim[3]
        nt = dim[4]
        nu = dim[5]

        datatype = Ndict['datatype'][0]

        str_nifti_nums = '{},{},{},{},{},{}'.format(
            nx, ny, nz, nt, nu, datatype
        )

        return 0, str_nifti_nums

    except:
        print("** ERROR: failed to make nifti_nums from")
        print("   Ndict[dim]      : {}".format(Ndict['dim']))
        print("   Ndict[datatype] : {}".format(Ndict['datatype']))
        
        return BAD_RETURN

# ----------------

def make_AFNI_atr_element(aname, avals, verb=1):
    """Create a dictionary representation of one AFNI_atr NIML element.

This follows the attribute conversion performed by AFNI's
THD_nimlize_dsetatr() in thd_nimlatr.c.

Parameters
----------
aname : str
    AFNI attribute name.
avals : list
    Attribute values from an Adict.  The values should all be
    Python int, float or str objects.
verb : int
    Verbosity level for messages whilst working.

Returns
-------
is_fail : int
    0 on success, nonzero on failure.
dict_elem : dict
    Dictionary representation of one NIML AFNI_atr element.

"""

    BAD_RETURN = (-1, {})

    # ----- basic checks

    if not isinstance(aname, str) or not len(aname):
        print("** ERROR: AFNI attribute name must be a nonempty string")
        return BAD_RETURN

    try:
        nvals = len(avals)
    except:
        print("** ERROR: AFNI attribute values must be list-like:", aname)
        return BAD_RETURN

    if not nvals:
        print("** ERROR: AFNI attribute has no values:", aname)
        return BAD_RETURN

    # NB: there are 3 types the AFNI attribute can be: float, int or
    # str, and each one gets dealt in its own way.

    # ----- integer attribute

    # NB: bool is a subclass of int in Python, but is not appropriate here.
    if isinstance(avals[0], int) and not isinstance(avals[0], bool):

        for val in avals:
            if not isinstance(val, int) or isinstance(val, bool):
                print("** ERROR: mixed/non-int values in attribute:", aname)
                return BAD_RETURN

        dict_elem = {
            'name'     : 'AFNI_atr',
            'atr_name' : aname,
            'ni_type'  : 'int',
            'ni_dimen' : nvals,
            'values'   : list(avals),
        }

    # ----- float attribute

    elif isinstance(avals[0], float):

        for val in avals:
            if not isinstance(val, float):
                print("** ERROR: mixed/non-float values in attribute:", aname)
                return BAD_RETURN

        dict_elem = {
            'name'     : 'AFNI_atr',
            'atr_name' : aname,
            'ni_type'  : 'float',
            'ni_dimen' : nvals,
            'values'   : list(avals),
        }

    # ----- string attribute

    elif isinstance(avals[0], str):

        for val in avals:
            if not isinstance(val, str):
                print("** ERROR: mixed/non-str values in attribute:", aname)
                return BAD_RETURN

        # Reconstruct the packed ATR_string character array. In most
        # cases, individual strings are separated by NUL characters
        # and which has a final NUL terminator. However, BRICK_STATSYM
        # is a special case additionally split at ';'. All of that is
        # managed within this function
        is_fail, astr = repack_string_attribute(aname, avals, verb=verb)
        if is_fail :
            return BAD_RETURN

        # AFNI's THD_nimlize_dsetatr() breaks ATR_string contents into
        # pieces of at most SZMAX=1000 characters before applying
        # THD_zblock().  ZBLOCK is '~', replacing embedded NULs.
        SZMAX = 1000

        sar = []
        ibot = 0
        nch  = len(astr)

        while ibot < nch:
            itop = min(ibot + SZMAX, nch)

            ss = astr[ibot:itop]
            ss = ss.replace('\0', '~')

            sar.append(ss)
            ibot = itop

        # AFNI removes the final ZBLOCK corresponding to the terminating
        # NUL, except for the special one-character/null-only case.
        if len(sar[-1]) > 1 and sar[-1].endswith('~'):
            sar[-1] = sar[-1][:-1]

        dict_elem = {
            'name'     : 'AFNI_atr',
            'atr_name' : aname,
            'ni_type'  : 'String',
            'ni_dimen' : len(sar),
            'values'   : sar,
        }

    # ----- unknown type

    else:
        print("** ERROR: unrecognized AFNI attribute value type:")
        print("   attr : {}".format(aname))
        print("   type : {}".format(type(avals[0])))
        return BAD_RETURN

    if verb > 2:
        print("++ Created NIML AFNI_atr element: {}".format(aname))
        print("   ni_type  : {}".format(dict_elem['ni_type']))
        print("   ni_dimen : {}".format(dict_elem['ni_dimen']))

    return 0, dict_elem

# ----------------------

def repack_string_attribute(name, avals, verb=1):
    """Reconstruct the AFNI internal string value from an Adict string list.

By default, each str element of alist is joined with '\0'. Note that
BRICK_STATSYM is treated specially, to rejoin the list elements with:
';'.


Parameters
----------
name : str
    name of the AFNI attribute
avals : list (of str)
    the contents of the AFNI attribute (list of str)
verb : int
    verbosity level

Returns
-------
is_fail : int
    0 on success, nonzero on failure
astr : str
    single string from concatenating all 

    """

    BAD_RETURN = (-1, '')

    try:
        for val in avals:
            if not isinstance(val, str):
                print("** ERROR: non-string value in string attribute:", name)
                return BAD_RETURN
    except:
        print("** ERROR: string attribute values must be list-like:", name)
        return BAD_RETURN

    # BRICK_STATSYM consists of semicolon-separated stat-symbol strings
    if name == 'BRICK_STATSYM':
        astr = ';'.join(avals)

    # special AFNI null-string representation
    elif len(avals) == 1 and avals[0] == '(null)':
        astr = ''

    # general ATR_string: individual strings are NUL-separated
    else:
        astr = '\0'.join(avals)

    # each ATR_string has final NUL terminator
    astr += '\0'

    return 0, astr

# ============================================================================

if __name__ == "__main__" : 

    print("++ No examples yet.")
    sys.exit(0)
