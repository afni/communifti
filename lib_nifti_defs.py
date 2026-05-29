#!/usr/bin/env python

# ============================================================================
# 
# A library of basic data objects for NIFTI-1 standard datasets (Cox
# et al., 2004). 
#
# For reference, the NIFTI header fields are listed, defined and
# described here:
# https://github.com/NIFTI-Imaging/nifti_clib/blob/master/nifti2/nifti1.h
#
# auth: PA Taylor (SSCC, NIMH, NIH, USA)
#
# ============================================================================

import sys, copy

# ============================================================================
# nifti1 header: dictionaries

# this section includes subsets of values with relevant properties to
# be aware of (officially unused keys, etc.)

# dict of all NIFTI-1 header fields
dict_nifti1 = {
    'sizeof_hdr'      : None,     # int
    'data_type'       : None,     # char [10]
    'db_name'         : None,     # char [18]
    'extents'         : None,     # int
    'session_error'   : None,     # short
    'regular'         : None,     # char
    'dim_info'        : None,     # char 
    'dim'             : None,     # short [8]
    'intent_p1'       : None,     # float
    'intent_p2'       : None,     # float
    'intent_p3'       : None,     # float
    'intent_code'     : None,     # short
    'datatype'        : None,     # short
    'bitpix'          : None,     # short
    'slice_start'     : None,     # short
    'pixdim'          : None,     # float [8]
    'vox_offset'      : None,     # float
    'scl_slope'       : None,     # float
    'scl_inter'       : None,     # float
    'slice_end'       : None,     # short
    'slice_code'      : None,     # char
    'xyzt_units'      : None,     # char
    'cal_max'         : None,     # float
    'cal_min'         : None,     # float
    'slice_duration'  : None,     # float
    'toffset'         : None,     # float
    'glmax'           : None,     # int
    'glmin'           : None,     # int
    'descrip'         : None,     # char [80]
    'aux_file'        : None,     # char [24]
    'qform_code'      : None,     # short
    'sform_code'      : None,     # short
    'quatern_b'       : None,     # float
    'quatern_c'       : None,     # float
    'quatern_d'       : None,     # float
    'qoffset_x'       : None,     # float
    'qoffset_y'       : None,     # float
    'qoffset_z'       : None,     # float
    'srow_x'          : None,     # float [4]
    'srow_y'          : None,     # float [4]
    'srow_z'          : None,     # float [4]
    'intent_name'     : None,     # char [16]
    'magic'           : None,     # char [4]
}

# dict of unused fields in nifti1 (and their default/constant values)
dict_nifti1_unused = {
    'data_type'       : b'',      # char [10]
    'db_name'         : b'',      # char [18]
    'extents'         : 0,        # int
    'session_error'   : 0,        # short
    'regular'         : b'r',     # char
    'glmax'           : 0,        # int
    'glmin'           : 0,        # int
}

# ============================================================================

# which keys in the nifti1 header dict should come from the data
# array, when applying/copying the header to a new set?
list_nifti1_recalc_from_data = [
    'datatype',                   # short
    'bitpix',                     # short
]

# ============================================================================
# global nifti types structure list (per type, ordered oldest to newest)

# See afni/src/nifti/niftilib/nifti1_io.c
# -> static const nifti_type_ele nifti_type_list

# this is a dictionary of key=name and value=type
DICT_nifti_type = {
    "DT_UNKNOWN"              :    0,
    "DT_NONE"                 :    0,
    "DT_BINARY"               :    1,
    "DT_UNSIGNED_CHAR"        :    2,
    "DT_UINT8"                :    2,
    "NIFTI_TYPE_UINT8"        :    2,
    "DT_SIGNED_SHORT"         :    4,
    "DT_INT16"                :    4,
    "NIFTI_TYPE_INT16"        :    4,
    "DT_SIGNED_INT"           :    8,
    "DT_INT32"                :    8,
    "NIFTI_TYPE_INT32"        :    8,
    "DT_FLOAT"                :   16,
    "DT_FLOAT32"              :   16,
    "NIFTI_TYPE_FLOAT32"      :   16,
    "DT_COMPLEX"              :   32,
    "DT_COMPLEX64"            :   32,
    "NIFTI_TYPE_COMPLEX64"    :   32,
    "DT_DOUBLE"               :   64,
    "DT_FLOAT64"              :   64,
    "NIFTI_TYPE_FLOAT64"      :   64,
    "DT_RGB"                  :  128,
    "DT_RGB24"                :  128,
    "NIFTI_TYPE_RGB24"        :  128,
    "DT_ALL"                  :  255,
    "DT_INT8"                 :  256,
    "NIFTI_TYPE_INT8"         :  256,
    "DT_UINT16"               :  512,
    "NIFTI_TYPE_UINT16"       :  512,
    "DT_UINT32"               :  768,
    "NIFTI_TYPE_UINT32"       :  768,
    "DT_INT64"                : 1024,
    "NIFTI_TYPE_INT64"        : 1024,
    "DT_UINT64"               : 1280,
    "NIFTI_TYPE_UINT64"       : 1280,
    "DT_FLOAT128"             : 1536,
    "NIFTI_TYPE_FLOAT128"     : 1536,
    "DT_COMPLEX128"           : 1792,
    "NIFTI_TYPE_COMPLEX128"   : 1792,
    "DT_COMPLEX256"           : 2048,
    "NIFTI_TYPE_COMPLEX256"   : 2048,
    "DT_RGBA32"               : 2304,
    "NIFTI_TYPE_RGBA32"       : 2304,
}

# bits per pixel ("bitpix"), AKA bits per voxel
DICT_nifti_bitpix = {
    "DT_UNKNOWN"              :    0*8,
    "DT_NONE"                 :    0*8,
    "DT_BINARY"               :    0*8,
    "DT_UNSIGNED_CHAR"        :    1*8,
    "DT_UINT8"                :    1*8,
    "NIFTI_TYPE_UINT8"        :    1*8,
    "DT_SIGNED_SHORT"         :    2*8,
    "DT_INT16"                :    2*8,
    "NIFTI_TYPE_INT16"        :    2*8,
    "DT_SIGNED_INT"           :    4*8,
    "DT_INT32"                :    4*8,
    "NIFTI_TYPE_INT32"        :    4*8,
    "DT_FLOAT"                :    4*8,
    "DT_FLOAT32"              :    4*8,
    "NIFTI_TYPE_FLOAT32"      :    4*8,
    "DT_COMPLEX"              :    8*8,
    "DT_COMPLEX64"            :    8*8,
    "NIFTI_TYPE_COMPLEX64"    :    8*8,
    "DT_DOUBLE"               :    8*8,
    "DT_FLOAT64"              :    8*8,
    "NIFTI_TYPE_FLOAT64"      :    8*8,
    "DT_RGB"                  :    3*8,
    "DT_RGB24"                :    3*8,
    "NIFTI_TYPE_RGB24"        :    3*8,
    "DT_ALL"                  :    0*8,
    "DT_INT8"                 :    1*8,
    "NIFTI_TYPE_INT8"         :    1*8,
    "DT_UINT16"               :    2*8,
    "NIFTI_TYPE_UINT16"       :    2*8,
    "DT_UINT32"               :    4*8,
    "NIFTI_TYPE_UINT32"       :    4*8,
    "DT_INT64"                :    8*8,
    "NIFTI_TYPE_INT64"        :    8*8,
    "DT_UINT64"               :    8*8,
    "NIFTI_TYPE_UINT64"       :    8*8,
    "DT_FLOAT128"             :   16*8,
    "NIFTI_TYPE_FLOAT128"     :   16*8,
    "DT_COMPLEX128"           :   16*8,
    "NIFTI_TYPE_COMPLEX128"   :   16*8,
    "DT_COMPLEX256"           :   32*8,
    "NIFTI_TYPE_COMPLEX256"   :   32*8,
    "DT_RGBA32"               :    4*8,
    "NIFTI_TYPE_RGBA32"       :    4*8,
}

# ============================================================================

if __name__ == "__main__" :

    # example use cases
    print("++ None yet")
