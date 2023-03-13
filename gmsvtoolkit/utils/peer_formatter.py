#!/usr/bin/env python
"""
BSD 3-Clause License

Copyright (c) 2023, University of Southern California
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
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

Utilities converting PEER seismograms into bbp format, and bbp
into PEER format.  Designed specifically for use on SCEC
validation study that needs to convert 6 header line PEER-format
acceleration time series into bbp format and bbp format to a 6
header line PEER format.

Created on Aug 17, 2012
@author: maechlin
"""
from __future__ import division, print_function

# Number of header lines in PEER files
PEER_HEADER_LINES = 6

# Import Python modules
import sys

# Import GMSVToolkit modules
from core import constants
from core import exceptions
from utils.file_utilities import read_bbp_dt, read_bbp_samples, peer_get_num_lines

def peer2bbp(in_peer_n_file, in_peer_e_file, in_peer_z_file, out_bbp_file):
    """
    This function converts the 3 input peer files (N/E/Z) to a
    3-component bbp file
    """
    # Check if input files match
    num_lines_n = peer_get_num_lines(in_peer_n_file)
    num_lines_e = peer_get_num_lines(in_peer_e_file)
    num_lines_z = peer_get_num_lines(in_peer_z_file)

    if num_lines_n == num_lines_e  == num_lines_z:
        # Good, this is what we want!
        pass
    else:
        raise exceptions.ProcessingError("Input files don't have "
                                         "same number of lines!")

    # Write bbp file header
    bbp_file = open(out_bbp_file, "w")
    bbp_file.write("#    time(sec)      N-S(cm/s/s)      E-W(cm/s/s)      U-D(cm/s/s)\n")

    # Open input files
    with open(in_peer_n_file, 'r') as peer_fn_n, open(in_peer_e_file, 'r') as peer_fn_e, open(in_peer_z_file, 'r') as peer_fn_z:
        # First read header
        for line_n, line_e, line_z in zip(peer_fn_n, peer_fn_e, peer_fn_z):
            line_n = line_n.strip()
            line_e = line_e.strip()
            line_z = line_z.strip()
            
            if not line_n:
                continue

            pieces_n = line_n.split()
            pieces_e = line_e.split()
            pieces_z = line_z.split()

            if pieces_n[0].lower() == "acceleration":
                break

        # Next line should have dt and number of points in the file
        line_n = peer_fn_n.readline()
        line_e = peer_fn_e.readline()
        line_z = peer_fn_z.readline()

        line_n = line_n.strip()
        pieces_n = line_n.split()
        
        pts = float(pieces_n[0])
        dt = float(pieces_n[1])
        cur_dt = 0.0

        # Now read the data
        for line_n, line_e, line_z in zip(peer_fn_n, peer_fn_e, peer_fn_z):
            line_n = line_n.strip()
            line_e = line_e.strip()
            line_z = line_z.strip()
            
            if not line_n:
                continue

            pieces_n = [float(piece) * constants.G2CMSS for piece in line_n.split()]
            pieces_e = [float(piece) * constants.G2CMSS for piece in line_e.split()]
            pieces_z = [float(piece) * constants.G2CMSS for piece in line_z.split()]

            for piece_n, piece_e, piece_z in zip(pieces_n, pieces_e, pieces_z):
                bbp_file.write("%7e   % 8e   % 8e   % 8e\n" % (cur_dt, piece_n,
                                                               piece_e, piece_z))
                cur_dt = cur_dt + dt
        
    # Close output the file
    bbp_file.close()

def bbp2peer(in_bbp_file, out_peer_n_file, out_peer_e_file, out_peer_z_file):
    """
    Convert bbp file into three peer files for use by RotD50/100 and
    other programs that input PEER format seismograms
    """
    npts = read_bbp_samples(in_bbp_file)
    dt = read_bbp_dt(in_bbp_file)
    num_header_lines = 0
    header_lines = []

    # Open file
    bbp_file = open(in_bbp_file, "r")

    # Loop through header
    while(True):
        pos = bbp_file.tell()
        line = bbp_file.readline()
        if not line:
            # Test for EOF
            break
        line = line.strip()
        if not line:
            # Skip blank lines
            continue
        if line.startswith("#") or line.startswith("%"):
            # Keep track of comments
            num_header_line = num_header_lines + 1
            header_lines.append("%s\n" % (line))
            continue
        # line contains first data point
        break

    # Go back to previous line so we read the first data point again
    bbp_file.seek(pos)

    # Adjust header lines, so we always have enough
    while len(header_lines) <= (PEER_HEADER_LINES - 2):
        header_lines.append("\n")

    # Prepare to write 6 colume format
    n_file = open(out_peer_n_file, "w")
    e_file = open(out_peer_e_file, "w")
    z_file = open(out_peer_z_file, "w")

    for line in header_lines[0:(PEER_HEADER_LINES - 2)]:
        n_file.write(line)
        e_file.write(line)
        z_file.write(line)

    n_file.write("Acceleration in g\n")
    n_file.write("  %d   %1.6f   NPTS, DT\n" % (npts, dt))
    e_file.write("Acceleration in g\n")
    e_file.write("  %d   %1.6f   NPTS, DT\n" % (npts, dt))
    z_file.write("Acceleration in g\n")
    z_file.write("  %d   %1.6f   NPTS, DT\n" % (npts, dt))

    cur_item = 0
    for line in bbp_file:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("%"):
            continue
        pieces = [float(piece) for piece in line.split()]
        n_val = (float(pieces[1]) / constants.G2CMSS)
        e_val = (float(pieces[2]) / constants.G2CMSS)
        z_val = (float(pieces[3]) / constants.G2CMSS)

        # Write data
        n_file.write("% 12.7E " % (n_val))
        e_file.write("% 12.7E " % (e_val))
        z_file.write("% 12.7E " % (z_val))

        if (cur_item % 5) == 4:
            n_file.write("\n")
            e_file.write("\n")
            z_file.write("\n")

        cur_item = cur_item + 1

    # Done reading input file
    bbp_file.close()
    
    # Add newline at the end of last line to avoid issue when rotd50.f
    # reads the file (only when compiled with gfortran 4.3.3 on HPCC)
    n_file.write("\n")
    e_file.write("\n")
    z_file.write("\n")

    # Close all files
    n_file.close()
    e_file.close()
    z_file.close()
