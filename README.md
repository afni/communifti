# The CommuNifti Library

Libraries of functions for interacting with NIFTI format datasets (Cox
et al., 2004) from various formats and packages in the neuroimaging
community.

----------

## AFNI-NIFTI

One major grouping of functions here maps the header attributes in
AFNI (Cox, 1996) BRIK/HEAD format datasets to be mapped over to NIFTI
header fields.  These functions do not require the AFNI software
package to be installed in order to run. That is, these functions
mirror what the AFNI C code would do, but purely in native Python.

There are also libraries of test functions that _do_ use AFNI, to be
able to compare results with the expected answer. These are primarily
to be used just for development, rather than applications.

Libraries of mapping functions (no AFNI install needed):  
  lib_afni_read_head.py  : read AFNI HEAD file attributes 
  lib_afni_head2nifti.py : map AFNI HEAD file attributes to NIFTI fields

Libraries of testing functions (AFNI install needed):  
  lib_afni_read_head_test.py  : reading of AFNI HEAD file attributes
  lib_afni_head2nifti_test.py : test attribute-field mapping

----------

## Reading and writing NIFTI

Another grouping of functions consider reading and writing NIFTI, in
the context of processing occurring in between those operations.  At
present, these functions make use of Nibabel (Brett et al.,
2024). They also add an important layer of header-field propagation
and checking for consistency/updates in the final output volumes.

Libraries of reading/writing functions (Nibabel install needed):  
  lib_nibabel_read_nifti.py   : read NIFTI into Nibabel object
  lib_nibabel_write_nifti.py  : write NIFTI dset to disk from Nibabel object

-----------

## Supplemental code

The above functionality also depends on having NumPy installed, to a
large extent, to manage data arrays.  We have tried to make the
functionality all work for both Numpy v1.* and 2.*.  Additional NIFTI
header information from the main C code libraries is also
included.  Finally, there are some convenience tools for working

Libraries of supplemental functions/objects
  lib_nifti_defs.py   : information about NIFTI headers
  lib_numpy_utils.py  : convenient tools for navigating array and data types
  lib_simple_utils.py : convenient functions for printing and more

-----------

## References

Brett M, Markiewicz CJ, Hanke M, et al. (2024). nipy/nibabel: 5.3.1
(5.3.1). Zenodo. https://doi.org/10.5281/zenodo.13936989

Cox RW (1996). AFNI: software for analysis and visualization of
functional magnetic resonance neuroimages. Comput Biomed
Res. 29(3):162-73. doi: 10.1006/cbmr.1996.0014. PMID: 8812068.

Cox RW, Ashburner J, Breman H, et al. (2004). A (sort of) new image
data format standard: NiFTI-1. Presented at the 10th Annual Meeting of
the Organization for Human Brain Mapping.
