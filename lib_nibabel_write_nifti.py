#!/usr/bin/env python

import os
import numpy   as     np
import nibabel as     nib

from . import lib_simple_utils as lsu
from . import lib_numpy_utils  as lnu

# ***have to decide about torch tensors, too, as input data arrays??

# assorted I/O and other tools for going back and forth from
# volumetric datasets, via nibabel

# ============================================================================

class BabelNiftiWrite:
    """This object is for reuniting, verifying and updating a
nibabel-format NIFTI header with an numerical array, with the goal of
writing out a valid NIFTI dataset to disk.

The assumption is that the data array was read in along with the
header, and that the grid itself has not been changed. That is, the
dataset was not reoriented nor were the number of dimensions along any
axis changed.  These properties will be checked for consistency with
the header info.

It *is* permitted for the datum type or the number of values per voxel
to have changed.  These pieces of information will be compared between
the data and the header, and if there is disagreement, the header will
be updated to become consistent with the data block.

Parameters
----------
data : array
    data array, 3D or 4D
nib_hdr : Nifti1Header
    nibabel-formatted NIFTI header obj, presumably matching the spatial
    grid on which the data array sits
prefix : str
    name for output dset to be written
do_log : bool
    True to do logging of any shell commands, False to not do so
verb: int
    level of verbosity to use while processing (probably not very widely
    used here)

Returns
-------
bnw : BabelNiftiWrite
    an object that takes a data array and a nibabel-format header and writes 
    a NIFTI dset to disk

    """

    def __init__( self, data, nib_hdr, prefix,
                  do_overwrite=False,
                  do_log=False, verb=1 ):

        # general variables
        self.verb            = verb
        self.do_log          = do_log

        # main data variables
        self.data_in        = data             # 3D or 4D np.ndarray of data
        self.nib_hdr_in     = nib_hdr          # nibabel format hdr (read in)
        self.prefix         = prefix           # output name for dset

        self.do_overwrite   = do_overwrite     # flag to allow overwriting

        # derived attributes
        self.Ndict_in       = {}               # simple dict of nifti fields
        self.nib_hdr_out    = None             # nibabel format hdr (to write)
        self.data_out       = None             # np.ndarray to write out


        # ------ take action

        tmp = self.basic_setup()
        if tmp : return

        tmp = self.copy_hdr()
        if tmp : return

        tmp = self.check_consistency_all()
        if tmp : return

        tmp = self.synchronize_hdr_all()
        if tmp : return

        


    # ------ methods

    def basic_setup(self):
        """Check basic properties of the inputs, as well as feasibility for
    running"""

        BAD_RETURN = -1
        
        # output dset must be nifti
        if not(self.prefix.endswith('.nii')) and \
           not(self.prefix.endswith('.nii.gz')) :
            self.prefix+= '.nii.gz'

        # overwriting or not
        if os.path.isfile(self.prefix) :
            if not(self.do_overwrite) :
                msg = "Exiting, since the output file "
                msg+= "exists already and overwrite was not used:\n"
                msg+= self.prefix
                lsu.EP1(msg)
                return BAD_RETURN
            else:
                msg = "Will overwrite existing file:\n"
                msg+= prefix
                lsu.WP(msg)

        # check shape
        ndim = len(self.data_dim)
        if ndim not in [3, 4] :
            msg = "Array does not have 3 or 4 dims, instead it has "
            msg+= "{} of them: {}".format(ndim, ', '.join(self.data_dim))
            lsu.EP1(msg)
            return BAD_RETURN

    def copy_hdr(self):
        """Do two tasks here about copying the header. First,
        initialize the output nibabel-format header (just a copy of
        the input one). Second, make a simpler dict format of the
        input one."""

        BAD_RETURN = -2

        # task 1
        self.nib_hdr_out = copy.deepcopy(self.nib_hdr_in)

        # task 2
        is_fail, self.Ndict_in = make_dict_of_nibabel_hdr(self.nib_hdr_in, 
                                                          verb=self.verb)

        if is_fail :
            lsu.EP1("Failed to make dict of hdr fields from input hdr")
            return BAD_RETURN

        return 0

    def check_consistency_all(self):
        """Verify that necessary properties are consistent between the
        data and the hdr.  In this check, we will _exit_ if something
        does not match."""

        if verb :
            lsu.IP("Check consistency of some data and header properties")

        BAD_RETURN = -3

        is_fail = self.check_consistency_dim(self)
        if is_fail :
            return BAD_RETURN

        # others to add?

        return 0

    def check_consistency_dim(self):
        """Check consistency of one dset property: nifti field 'dim'.
        Do spatial dimensions of the data and those recorded in the
        hdr match?"""

        BAD_RETURN = -3

        # get data dims (should have 3 or 4 dims)
        ndim_data = len(self.data_dim)
        if ndim_data < 3 or ndim_data > 4 :
            msg = "number of dims in data is not in range [3, 4], "
            msg+= "but: {}".format(ndim_data)
            ab.EP1(msg)
            return BAD_RETURN

        # get hdr dims (should have 3, 4 or 5 dims)
        hdr_dim = self.Ndict['dim']
        ndim_hdr = hdr_dim[0]
        if ndim_hdr < 3 or ndim_hdr > 5 :
            msg = "number of dims in hdr is not in range [3, 5], "
            msg+= "but: {}".format(ndim_hdr)
            ab.EP1(msg)
            return BAD_RETURN

        # ... and compare just spatial dims
        for ii in range(3) :
            if self.data_dim[ii] != hdr_dim[1+ii] :
                msg = "Mismatch in spatial dims of "
                msg+= "data: {},\n".format(self.data_dim[:3])
                msg+= "and in the header: {}".format(hdr_dim[1:4])
                ab.EP1(msg)
                return BAD_RETURN

        return 0

    def synchronize_hdr_all(self):
        """Some properties of the data_in array might be different
        than the originally loaded dset (like the dtype or the number
        of vols). Here we check all ones that are OK to be different,
        and we would also now adjust the header."""

        if verb :
            lsu.IP("Synchronize some data and header properties")

        BAD_RETURN = -3

        is_fail = self.syncrhonize_hdr_type(self)
        if is_fail :
            return BAD_RETURN

        # others to add?

        return 0


    def synchronize_hdr_type(self):
        """ **** """

        BAD_RETURN = -3

        # get dtype of data_in arr
        dtype = self.data_in.dtype

        # *****

        return 0
        
    # ---------

    @property
    def data_dim(self):

        """The spatial dimensions of the data array."""
        return np.shape(self.data_in)

# ----------------------------------------------------------------------------

def make_dict_of_nibabel_hdr(nib_hdr, verb=1):
    """For a given nibabel-formatted NIFTI header, called nib_hdr,
read in all header fields (i.e., attributes) to make a
dictionary. 

Parameters
----------
nib_hdr : Nifti1Header
    nibabel-formatted NIFTI header obj
verb : int
    verbosity level for messages whilst working

Returns
-------
is_fail : int
    0 on success, nonzero on failure
Ndict : dict
    dictionary of NIFTI header fields; each value is a list

    """

    BAD_RETURN = (-1, 0)


    # initialize default
    Ndict = {}

    for key in ALL_nifti1_keys :
        val = nib_hdr.get(key)
        # this next step occurs bc some values are ndim=0 arrays
        val_list, val_type = lnu.try_convert_list_float_int_str_arr(val)
        Ndict[key] = val_list

        if verb > 1 :
            print("   {:<20s}  : {}".format(key, val_list))

    return 0, Ndict


# ============================================================================

if __name__ == "__main__" :

    print("++ No examples yet")
