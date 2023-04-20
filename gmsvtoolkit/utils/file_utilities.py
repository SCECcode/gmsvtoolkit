#!/usr/bin/env python3
"""
BSD 3-Clause License

Copyright (c) 2023, Southern California Earthquake Center
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

# GMSVToolkit files
from core import exceptions

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

def count_header_lines(a_bbpfile):
    """
    Function counts and returns the number of header lines in a BBP file
    """
    header_lines = 0

    my_file = open(a_bbpfile, 'r')
    for line in my_file:
        line = line.strip()
        # Check for empty lines, we count them too
        if not line:
            header_lines = header_lines + 1
            continue
        # Check for comments
        if line.startswith('%') or line.startswith('#'):
            header_lines = header_lines + 1
            continue
        # Reached non header line
        break
    my_file.close()

    return header_lines

def read_bbp_samples(bbp_file):
    """
    Reads BBP file and returns the number of samples in the timeseries
    """
    number_of_samples = 0

    try:
        input_file = open(bbp_file)
        for line in input_file:
            line = line.strip()
            if not line:
                continue
            # Skip comments
            if line.startswith("#") or line.startswith("%"):
                continue
            number_of_samples = number_of_samples + 1
        input_file.close()
    except OSError as e:
        print("[ERROR]: reading bbp file: %s" % (e.filename))
        sys.exit(1)

    return number_of_samples

def read_bbp_dt(bbp_file):
    """
    Reads BBP file and returns dt
    """
    val1 = None
    val2 = None
    file_dt = None

    # Figure out dt first, we need it later
    input_file = open(bbp_file)
    for line in input_file:
        line = line.strip()
        if not line:
            continue
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
    input_file.close()

    # Quit if cannot figure out dt
    if val1 is None or val2 is None:
        print("[ERROR]: Cannot determine dt from file! Exiting...")
        sys.exit(1)

    # Return dt
    return val2 - val1
# end get_dt

def read_bbp_file(filename):
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

def add_extra_points(input_bbp_file, output_bbp_file, num_points):
    """
    Add num_points data points at the end of the input_bbp_File,
    writing the result to output_bbp_file
    """
    bbp_dt = None
    bbp_t1 = None
    bbp_t2 = None
    input_file = open(input_bbp_file, 'r')
    output_file = open(output_bbp_file, 'w')

    for line in input_file:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("%"):
            output_file.write("%s\n" % (line))
            continue
        pieces = line.split()
        cur_dt = float(pieces[0])
        if bbp_dt is None:
            if bbp_t1 is None:
                bbp_t1 = cur_dt
            elif bbp_t2 is None:
                bbp_t2 = cur_dt
                bbp_dt = bbp_t2 - bbp_t1
        # Still write the line to output file
        output_file.write("%s\n" % (line))

    # Close input file
    input_file.close()

    if bbp_dt is None:
        raise exceptions.ParameterError("Cannot find DT in %s!" %
                                        (input_bbp_file))
    for _ in range(0, num_points):
        cur_dt = cur_dt + bbp_dt
        output_file.write("%5.7f   %5.9e   %5.9e    %5.9e\n" %
                          (cur_dt, 0.0, 0.0, 0.0))

    output_file.close()

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

def read_fas_file(fas_file):
    """
    Reads FAS file and returns freq and fas arrays
    """
    freqs = []
    fas = []

    # Read input file
    input_file = open(fas_file, 'r')
    # Skip headers
    for line in input_file:
        line = line.strip()
        # skip blank lines
        if not line:
            continue
        if line.startswith("freq"):
            break
    for line in input_file:
        line = line.strip()
        # skip blank lines
        if not line:
            continue
        pieces = line.split()
        pieces = [float(piece) for piece in pieces]
        freqs.append(pieces[0])
        fas.append(pieces[1])
    # All done!
    input_file.close()

    return freqs, fas

def read_fas_eas_file(fas_input_file):
    """
    Reads the fas_input_file, returning
    freq, fas_h1, fas_h2, eas, seas
    """
    freqs = []
    fas_h1 = []
    fas_h2 = []
    eas = []
    seas = []

    input_file = open(fas_input_file, 'r')
    for line in input_file:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("%"):
            continue
        pieces = line.split()
        if len(pieces) != 5:
            continue
        pieces = [float(piece) for piece in pieces]
        freqs.append(pieces[0])
        fas_h1.append(pieces[1])
        fas_h2.append(pieces[2])
        eas.append(pieces[3])
        seas.append(pieces[4])
    input_file.close()

    return freqs, fas_h1, fas_h2, eas, seas
