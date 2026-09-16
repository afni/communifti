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
### Notes:
# + The default value for vox_offset in a .nii file is 352, but adding
#   one or more extensions will change this.
# + The NIfTI-1.1 header struct is 348 bytes long.  See this discussion
#   about adding extension(s), and using ecode and esize:
#   http://nifti.nimh.nih.gov/nifti-1/documentation/faq#Q21

ALL_nifti1_keys = list(dict_nifti1.keys())

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

ALL_nifti1_unused_keys = list(dict_nifti1_unused.keys())

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

# this is a dictionary of key=name and value=datatype (or =code)
DICT_nifti_datatype = {
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

ALL_nifti_datatype_keys = list(DICT_nifti_datatype.keys())

# bits per pixel ("bitpix"), AKA bits per voxel (datatype code shown, too);
# see nifti1.h for the datatype code and bitpix values
DICT_nifti_bitpix = {         # bit/vox      code
    "DT_UNKNOWN"              :    0,     #    0 
    "DT_NONE"                 :    0,     #    0 
    "DT_BINARY"               :    1,     #    1 (would be problematic: no /8)
    "DT_UNSIGNED_CHAR"        :    1*8,   #    2 
    "DT_UINT8"                :    1*8,   #    2 
    "NIFTI_TYPE_UINT8"        :    1*8,   #    2 
    "DT_SIGNED_SHORT"         :    2*8,   #    4 
    "DT_INT16"                :    2*8,   #    4 
    "NIFTI_TYPE_INT16"        :    2*8,   #    4 
    "DT_SIGNED_INT"           :    4*8,   #    8 
    "DT_INT32"                :    4*8,   #    8 
    "NIFTI_TYPE_INT32"        :    4*8,   #    8 
    "DT_FLOAT"                :    4*8,   #   16 
    "DT_FLOAT32"              :    4*8,   #   16 
    "NIFTI_TYPE_FLOAT32"      :    4*8,   #   16 
    "DT_COMPLEX"              :    8*8,   #   32 
    "DT_COMPLEX64"            :    8*8,   #   32 
    "NIFTI_TYPE_COMPLEX64"    :    8*8,   #   32 
    "DT_DOUBLE"               :    8*8,   #   64 
    "DT_FLOAT64"              :    8*8,   #   64 
    "NIFTI_TYPE_FLOAT64"      :    8*8,   #   64 
    "DT_RGB"                  :    3*8,   #  128 
    "DT_RGB24"                :    3*8,   #  128 
    "NIFTI_TYPE_RGB24"        :    3*8,   #  128 
    "DT_ALL"                  :    0  ,   #  255 
    "DT_INT8"                 :    1*8,   #  256 
    "NIFTI_TYPE_INT8"         :    1*8,   #  256 
    "DT_UINT16"               :    2*8,   #  512 
    "NIFTI_TYPE_UINT16"       :    2*8,   #  512 
    "DT_UINT32"               :    4*8,   #  768 
    "NIFTI_TYPE_UINT32"       :    4*8,   #  768 
    "DT_INT64"                :    8*8,   # 1024 
    "NIFTI_TYPE_INT64"        :    8*8,   # 1024 
    "DT_UINT64"               :    8*8,   # 1280 
    "NIFTI_TYPE_UINT64"       :    8*8,   # 1280 
    "DT_FLOAT128"             :   16*8,   # 1536 
    "NIFTI_TYPE_FLOAT128"     :   16*8,   # 1536 
    "DT_COMPLEX128"           :   16*8,   # 1792 
    "NIFTI_TYPE_COMPLEX128"   :   16*8,   # 1792 
    "DT_COMPLEX256"           :   32*8,   # 2048 
    "NIFTI_TYPE_COMPLEX256"   :   32*8,   # 2048 
    "DT_RGBA32"               :    4*8,   # 2304 
    "NIFTI_TYPE_RGBA32"       :    4*8,   # 2304 
}

ALL_nifti_bitpix_keys = list(DICT_nifti_bitpix.keys())

# ============================================================================
# NIFTI slice codes (see niftilib/nifti1.h)

# nifti1 slice order codes, describing the acquisition order of the slices
NIFTI_SLICE_UNKNOWN  = 0
NIFTI_SLICE_SEQ_INC  = 1
NIFTI_SLICE_SEQ_DEC  = 2
NIFTI_SLICE_ALT_INC  = 3
NIFTI_SLICE_ALT_DEC  = 4
NIFTI_SLICE_ALT_INC2 = 5
NIFTI_SLICE_ALT_DEC2 = 6


# ============================================================================
# NIFTI extension codes, which are defined here:
# https://github.com/NIFTI-Imaging/nifti_clib/blob/master/niftilib/nifti1_io.h
# and see http://nifti.nimh.nih.gov/nifti-1/documentation/faq#Q21

# NIfTI-1.1 extension codes
DICT_nifti_ecode = {
    "NIFTI_ECODE_IGNORE"                :  0,  # formerly UNKNOWN
    "NIFTI_ECODE_DICOM"                 :  2,  # raw DICOM attributes  
    "NIFTI_ECODE_AFNI"                  :  4,  # AFNI
    "NIFTI_ECODE_COMMENT"               :  6,  # plain ASCII text only
    "NIFTI_ECODE_XCEDE"                 :  8,  # Xcede
    "NIFTI_ECODE_JIMDIMINFO"            : 10,  # 
    "NIFTI_ECODE_WORKFLOW_FWDS"         : 12,  # workflow-based approaches
    "NIFTI_ECODE_FREESURFER"            : 14,  # FreeSurfer
    "NIFTI_ECODE_PYPICKLE"              : 16,  # embedded Python objs, pynifti
    "NIFTI_ECODE_MIND_IDENT"            : 18,  # LONI MiND code
    "NIFTI_ECODE_B_VALUE"               : 20,  # LONI MiND code
    "NIFTI_ECODE_SPHERICAL_DIRECTION"   : 22,  # LONI MiND code
    "NIFTI_ECODE_DT_COMPONENT"          : 24,  # LONI MiND code
    "NIFTI_ECODE_SHC_DEGREEORDER"       : 26,  # LONI MiND code
    "NIFTI_ECODE_VOXBO"                 : 28,  # Voxbo
    "NIFTI_ECODE_CARET"                 : 30,  # Caret/Wustl
    "NIFTI_ECODE_CIFTI"                 : 32,  # CIFTI-2
    "NIFTI_ECODE_VARIABLE_FRAME_TIMING" : 34, 
    "NIFTI_ECODE_EVAL"                  : 38,  # Munster U. Hospital 
    "NIFTI_ECODE_MATLAB"                : 40,  # MATLAB extension 
    "NIFTI_ECODE_QUANTIPHYSE"           : 42,  # Quantiphyse extension 
    "NIFTI_ECODE_MRS"                   : 44,  # MRS extension 
}

### Notes about ecodes from the NIFTI C code:
# + "NIFTI_MAX_ECODE" : 44,  # ****** maximum extension code ******
# + 36 is currently unassigned, waiting on NIFTI_ECODE_AGILENT_PROCPAR 

# ============================================================================

if __name__ == "__main__" :

    # example use cases
    print("++ None yet")












































