#!/usr/bin/env python

import sys

# ----------------------------------------------------------------------------
# Convenient and simple functions to stylize printing of messages.
# APRINT() is the main workhorse; BP(), IP(), EP() and WP() are just
# short/convenient wrappers

def BP(S, indent=True):
    '''Warning print string S'''
    APRINT(S, ptype='BLANK', indent=indent)

def IP(S, indent=True):
    '''Info print string S'''
    APRINT(S, ptype='INFO', indent=indent)

def WP(S, indent=True):
    '''Warning print string S'''
    APRINT(S, ptype='WARNING', indent=indent)

def EP(S, indent=True, end_exit=True):
    '''Error print string S

    By default, exit after printing

    '''
    APRINT(S, ptype='ERROR', indent=indent)

    if end_exit :
       sys.exit(1)

def EP1(S, indent=True):
    '''Error print string S, and return 1.

    Basically, compact form of EP(...)
    '''
    APRINT(S, ptype='ERROR', indent=indent)

    return 1

def APRINT(S, ptype=None, indent=True, flush=True):
    '''Print Error/Warn/Info for string S

    This function is not meant to be used directly, in general; use
    {W|E|I}P(), instead.
    '''

    if ptype == 'WARNING' :
       ptype_str = "+* WARNING:"
    elif ptype == 'ERROR' :
       ptype_str = "** ERROR:"
    elif ptype == 'INFO' :
       ptype_str = "++"
    elif ptype == 'BLANK' :
       ptype_str = "  "
    else:
       print("**** Unrecognized print type '{}'. So, error about\n"
             "     a warning, error or info message!\n".format(ptype))
       sys.exit(1)

    if indent :
       S = S.replace( "\n", "\n   ")

    out = "{} ".format(ptype_str)
    out+= S

    if ptype == 'ERROR' :
       out+= "\n"
    
    print(out, flush=flush)

# ----------------------------------------------------------------------------

def simple_type(x):
    """When printing the type(...) of something, the format is annoyingly:
    <class 'TYPE'>.  This returns the simple string 'TYPE', unless
    something weird happens, in which case it will just return the
    standard-but-likely-annoying format.

Parameters
----------
x : any object type
    some object whose type you want to have as a simple str

Returns
-------
xtype : str
    simple string of the type of x

    """

    a = type(x)
    # get extended type info as str
    b = "{}".format(a)
    # remove: <class ', and: '>
    if len(b) > 10 :
        c = b[8:-2]
        return c
    else:
        return b


# ============================================================================

if __name__ == "__main__" :

    print("++ No examples yet")
