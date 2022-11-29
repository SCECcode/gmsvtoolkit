#!/usr/bin/env python3
"""
BSD 3-Clause License

Copyright (c) 2022, Southern California Earthquake Center
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The program contains several input/output utility
functions used by other modules.
"""
from __future__ import division, print_function, absolute_import

# Import Python modules
import os
import sys
import numpy as np

def peer_get_num_lines(input_file):
    """
    Return number of lines from a file
    """
    num_lines = 0
    
    try:
        ifile = open(input_file)
        for line in ifile:
            num_lines = num_lines + 1
        ifile.close()
    except OSError as e:
        print("[ERROR]: error reading file: %s" % (e.filename))
        sys.exit(1)

    return num_lines

def bbp_get_num_samples(input_file):
    """
    Read the number of samples from a BBP file
    """
    num_samples = 0

    try:
        ifile = open(input_file)
        for line in ifile:
            line = line.strip()
            if not line:
                continue
            # Skip comments
            if line.startswith("#") or line.startswith("%"):
                continue
            num_samples = num_samples + 1
        ifile.close()
    except OSError as e:
        print("[ERROR]: error reading bbp file: %s" % (e.filename))
        sys.exit(1)

    return num_samples

def bbp_get_dt(input_file):
    """
    Read timeseries file and return dt
    """
    val1 = None
    val2 = None
    file_dt = None

    # Figure out dt first, we need it later
    ifile = open(input_file)
    for line in ifile:
        # Skip comments
        if line.startswith("#") or line.startswith("%"):
            continue
        pieces = line.split()
        pieces = [float(piece) for piece in pieces]
        if val1 is None:
            val1 = pieces[0]
            continue
        if val2 is None:
            val2 = pieces[0]
            break
    ifile.close()

    # Quit if cannot figure out dt
    if val1 is None or val2 is None:
        print("[ERROR]: Cannot determine dt from file! Exiting...")
        sys.exit(1)

    # Return dt
    return val2 - val1
# end get_dt

def read_file_bbp2(filename):
    """
    This function reads a bbp file and returns the timeseries in the
    format time, h1, h2, up tuple
    """
    time = []
    h1_comp = []
    h2_comp = []
    ud_comp = []

    try:
        input_file = open(filename, 'r')
        for line in input_file:
            line = line.strip()
            if line.startswith('#') or line.startswith('%'):
                # Skip comments
                continue
            # Trim in-line comments
            if line.find('#') > 0:
                line = line[:line.find('#')]
            if line.find('%') > 0:
                line = line[:line.find('%')]
            # Make them float
            pieces = line.split()
            pieces = [float(piece) for piece in pieces]
            time.append(pieces[0])
            h1_comp.append(pieces[1])
            h2_comp.append(pieces[2])
            ud_comp.append(pieces[3])
        input_file.close()
    except OSError as e:
        print("[ERROR]: error reading bbp file: %s" % (e.filename))
        sys.exit(1)

    # Convert to NumPy Arrays
    time = np.array(time)
    h1_comp = np.array(h1_comp)
    h2_comp = np.array(h2_comp)
    ud_comp = np.array(ud_comp)

    # All done!
    return time, h1_comp, h2_comp, ud_comp
# end of read_file_bbp2

def read_rdxx(input_rdxx_file):
    """
    Reads RotDXX input file

    Inputs:
        input_rdxx_file - filename for the input file
    Outputs:
        periods - array containing periods
        comp1 - array with first component from the file
        comp2 - array with second component from the file
        comp3 - array with third component from the file
    """
    periods = []
    comp1 = []
    comp2 = []
    comp3 = []
    input_file = open(input_rdxx_file, 'r')
    for line in input_file:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        items = line.split()
        items = [float(item) for item in items]
        periods.append(items[0])
        comp1.append(items[1])
        comp2.append(items[2])
        comp3.append(items[3])
    input_file.close()

    return np.array(periods), np.array(comp1), np.array(comp2), np.array(comp3)
