#!/usr/bin/env python

# ============================================================================
# 
# A library file for helping to convert text to be properly formatted for a
# NIFTI extension.
#
# auth: PA Taylor (SSCC, NIMH, NIH, USA)
#
# ============================================================================

import sys
import struct

# ============================================================================
# general preparation of text content to be valid NIFTI extension

# For AFNI content, we would want to make sure add_nul is True, and
# call it like:
#
#   is_fail, ext_content, esize = \
#       pack_nifti_extension_content(
#           niml_text,
#           add_nul=True,
#           verb=verb
#       )

def pack_nifti_extension_content(content, add_nul=False,
                                 encoding='utf-8', verb=1):
    """Pack content according to NIFTI extension size/alignment rules.

If content is a str, it is encoded using the specified encoding.
The content is then padded so that the total extension size (esize),
including the 8-byte esize/ecode header, is a multiple of 16 bytes.

This function also outputs the requisite esize value (total extension
size) for the packed content.

For AFNI extensions, one should use: add_nul=True .

Parameters
----------
content : str or bytes
    Extension content.
add_nul : bool
    Append a terminating NUL byte before padding.
encoding : str
    Encoding to use if content is a str.
verb : int
    Verbosity level.

Returns
-------
is_fail : int
    0 on success, nonzero on failure.
ext_content : bytes
    Content including any requested NUL terminator and zero padding.
esize : int
    Total extension size, including the 8-byte esize/ecode header.

    """

    BAD_RETURN = (-1, b'', 0)

    if isinstance(content, str):
        try:
            content = content.encode(encoding)
        except:
            print("** ERROR: failed to encode extension content")
            return BAD_RETURN

    elif isinstance(content, bytes):
        content = bytes(content)

    else:
        print("** ERROR: extension content must be str or bytes")
        return BAD_RETURN

    if add_nul:
        content += b'\0'

    # esize includes 4 bytes for esize + 4 bytes for ecode
    esize = len(content) + 8

    # NIFTI extensions are padded so esize is a multiple of 16
    esize = ((esize + 15) // 16) * 16

    # pad content to exactly esize - 8 bytes
    npad = esize - 8 - len(content)
    ext_content = content + b'\0' * npad

    if verb > 2:
        print("++ Packed NIFTI extension content:")
        print("   esize         : {}".format(esize))
        print("   content bytes : {}".format(len(ext_content)))
        print("   padding bytes : {}".format(npad))

    return 0, ext_content, esize


# ============================================================================

if __name__ == "__main__" : 

    print("++ No examples yet.")
    sys.exit(0)


