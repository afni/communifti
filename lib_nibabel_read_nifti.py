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

# -------------------------------------------------------------------------

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
map_rules : str
    keyword (see lib_numpy_utils.DICT_allowed_np_dtype_map_rules) for
    the set of rules to apply when figuring out what dtype the data
    array should have, along with its corresponding NIFTI datatype/pixdim.
do_rm_exts : bool
    should the extensions be removed from header? (probably...)
do_overwrite : bool
    should the dataset be written out if a dset already exists there?
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
                  map_rules="reduced",
                  do_rm_exts=True, do_overwrite=False,
                  do_log=False, verb=1 ):

        # general variables
        self.verb            = verb
        self.do_log          = do_log

        # main data variables
        self.data_in        = data             # 3D or 4D np.ndarray of data
        self.nib_hdr_in     = nib_hdr          # nibabel format hdr (read in)
        self.prefix         = prefix           # output name for dset

        self.map_rules      = map_rules        # keyword from list in lnu
        self.do_rm_exts     = do_rm_exts       # remove extensions 

        self.do_overwrite   = do_overwrite     # flag to allow overwriting

        # derived attributes
        self.Ndict_in       = {}               # simple dict of nifti fields
        self.Ndict_out      = {}               # simple dict of nifti fields
        self.nib_hdr_out    = None             # nibabel format hdr (to write)
        self.data_out       = None             # np.ndarray, if converted
        self.nifti_key      = ''
        self.nifti_type     = 0
        self.nifti_bitpix   = 0 
        self.map_desc       = ''


        # ------ take action

        tmp = self.basic_setup()
        if tmp : return

        tmp = self.copy_hdr()
        if tmp : return

        tmp = self.check_consistency_all()
        if tmp : return

        tmp = self.set_data_dtype_hdr_datatype()
        if tmp : return

        tmp = self.set_hdr_nv()
        if tmp : return

        # ***** add in removing extensions by default ****

        tmp = self.write_dset()
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

        # check shape/dims of data array
        ndim = len(self.data_dim)
        if ndim not in [3, 4] :
            msg = "Array does not have 3 or 4 dims, instead it has "
            msg+= "{} of them: {}".format(ndim, ', '.join(self.data_dim))
            lsu.EP1(msg)
            return BAD_RETURN

        # check shape of hdr dim array
        hdr_dim = self.nib_hdr_in['dim']
        ndim_hdr = hdr_dim[0]
        if ndim_hdr not in [3, 4, 5] :
            msg = "The hdr does not have 3, 4 or 5 dims, instead it has "
            msg+= "{} of them: {}".format(ndim_hdr, hdr_dim)
            lsu.EP1(msg)
            return BAD_RETURN

        # verify map_rules keyword is allowed
        if self.map_rules not in lnu.LIST_allowed_np_dtype_map_rules :
            ttt = lnu.STR_allowed_np_dtype_map_rules
            msg = "Chosen map_rules '{}' ".format(self.map_rules)
            msg+= "not in known list: {}".format(ttt)
            lsu.EP1(msg)
            return BAD_RETURN

        return 0

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

        self.Ndict_out = copy.deepcopy(self.Ndict_in)

        return 0

    def check_consistency_all(self):
        """Verify that necessary properties are consistent between the
        data and the hdr.  In this check, we will _exit_ if something
        does not match."""

        if self.verb :
            lsu.IP("Check consistency of some data and header properties")

        BAD_RETURN = -3

        is_fail = self.check_consistency_dim()
        if is_fail :
            return BAD_RETURN

        # others to add?

        return 0

    def check_consistency_dim(self):
        """Check consistency of one dset property: nifti field 'dim'.
        Do spatial dimensions of the data and those recorded in the
        hdr match? NB: the size/shape of data and nib_hdr dims was checked
        during setup, so numbers of dims should be OK."""

        BAD_RETURN = -3

        # get data dims (should have 3 or 4 dims)
        ndim_data = len(self.data_dim)

        # get hdr dim (was checked on input for size)
        hdr_dim = self.Ndict_in['dim']
        ndim_hdr = hdr_dim[0]

        # ... and compare just spatial dims
        for ii in range(3) :
            if self.data_dim[ii] != hdr_dim[1+ii] :
                msg = "Mismatch in spatial dims of "
                msg+= "data: {},\n".format(self.data_dim[:3])
                msg+= "and in the header: {}".format(hdr_dim[1:4])
                lsu.EP1(msg)
                return BAD_RETURN

        return 0

    '''
    def synchronize_hdr_all(self):
        """Some properties of the data_in array might be different
        than the originally loaded dset (like the dtype or the number
        of vols). Here we check all ones that are OK to be different,
        and we would also now adjust the header."""

        if self.verb :
            lsu.IP("Synchronize some data and header properties")

        BAD_RETURN = -3

        is_fail = self.syncrhonize_hdr_type(self)
        if is_fail :
            return BAD_RETURN

        # others to add?

        return 0
    '''

    def set_data_dtype_hdr_datatype(self):
        """Start from the input data array's current dtype, and see what
        if it needs to be converted, and what NIFTI datatype would be most
        appropriate in any case.  Also warn about potential lossyness"""

        BAD_RETURN = -4

        # get dtype of data_in arr
        din = self.data_in.dtype.type

        is_fail, nifti_key, nifti_datatype, nifti_bitpix, dout, map_desc = \
            lnu.translate_numpy_dtype_to_nifti(din, 
                                               map_rules=self.map_rules, 
                                               verb=self.verb)
        if is_fail :
            return BAD_RETURN

        # save NIFTI-related info
        self.nifti_key      = nifti_key
        self.nifti_datatype = nifti_datatype
        self.nifti_pitbix   = nifti_bitpix
        self.map_desc       = map_desc

        # ----- data arr update (if needed)

        # if we have a new datatype to use, make new output arr
        # (otherwise, don't bother; save mem)
        if map_desc != 'same' :
            self.data_out = self.data_in.astype(dout)

        # ----- hdr update/sync

        # both the output header
        self.nib_hdr_out['datatype'] = self.nifti_datatype
        self.nib_hdr_out['bitpix']   = self.nifti_bitpix

        # ... and the dict copy of it
        self.Ndict_out['datatype'] = self.nifti_datatype
        self.Ndict_out['bitpix']   = self.nifti_bitpix

        return 0

    def set_hdr_nv(self):
        """Start from the input data array's shape, and get the number
        of volumes.  Then check if the header number of volume
        information needs to be updated."""

        BAD_RETURN = -5

        # get dtype of data_in arr
        data_nv = self.data_nv

        # get ndim from hdr, and figure out what it has for nv
        hdr_dim0 = self.Ndict_in['dim'][0]
        if hdr_dim0 == 3 :
            hdr_nv = 1
        else:
            hdr_nv = self.Ndict_in['dim'][hdr_dim0]

        if data_nv != hdr_nv :
            # only go through cases we need to edit/update hdr

            if hdr_dim0 == 3 :
                # hdr was for 3D data, and now we have more vols, so make 4D
                update_dim0 = 4             # diff
                update_idx  = 4             # diff
                update_nv   = data_nv       # diff
            elif hdr_dim0 > 3 and data_nv == 3 :
                # hdr was for >3D data, and now we have fewer vols
                update_dim0 = 3             # diff
                update_idx  = hdr_dim0      # diff
                update_nv   = 1             # diff
            elif hdr_dim0 > 3 and data_nv > 3 :
                # hdr was for >3D data, and now we have a different >3D
                update_dim0 = hdr_dim0      # same 
                update_idx  = hdr_dim0      # same 
                update_nv   = data_nv       # diff
            else:
                msg = "Should not reach here (set_hdr_nv):\n"
                msg+= "data dims : {}\n".format(self.data_dim)
                msg+= "hdr dims  : {}\n".format(self.Ndict_in['dim'])
                lsu.EP1(msg)

            # ----- hdr update/sync

            # both the output header
            self.nib_hdr_out['dim'][0] = update_dim0
            self.nib_hdr_out['dim'][update_idx] = update_nv

            # ... and the dict copy of it
            self.Ndict_out['dim'][0] = update_dim0
            self.Ndict_out['dim'][update_idx] = update_nv

        return 0

    def write_dset(self):
        """Write out the NIFTI volume."""

        BAD_RETURN = -6

        # NB: this is not a copy, just a renaming (in case we had to
        # reformat array, which we might not have done)
        if self.data_out is not None :
            dset = self.data_out
        else:
            dset = self.data_in

        # need affine as separate arg by position, so just get from hdr
        oaff = self.nib_hdr_out.get_best_affine()

        # remove extensions
        if self.do_rm_exts :
            self.nib_hdr_out.extensions.clear()


        ovol = nib.Nifti1Image(dset, oaff, header=self.nib_hdr_out)

        nib.save(ovol, self.prefix)

        return 0

    # ---------

    @property
    def data_dim(self):
        """The spatial (and maybe temporal) dimensions of the data array."""
        return np.shape(self.data_in)

    @property
    def data_nv(self):
        """The number of volumes (nv) in the data array."""
        S  = self.data_dim
        ns = len(S)
        if ns == 3 :
            return 1
        elif ns == 4 :
            return S[3]
        else:
            # should never happen, bc this was checked earlier
            msg = "Expected 3 or 4 dims in data arr, not {}: ".format(ns)
            msg = "{}".format(' '.join([str(val) for val in S]))
            lsu.EP1(msg)
            return -1

# ----------------------------------------------------------------------------


# ============================================================================

if __name__ == "__main__" :

    print("++ No examples yet")
