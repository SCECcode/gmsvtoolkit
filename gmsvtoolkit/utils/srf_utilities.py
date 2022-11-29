#!/usr/bin/env python
"""
BSD 3-Clause License

Copyright (c) 2022, University of Southern California
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

Utilities used to work with SRF files
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import uuid
import shutil
import tempfile

# Import GMSVToolkit files
from core import exceptions
from utils import os_utilities
from core import gmsvtoolkit_config

def get_magnitude(velfile, srffile, suffix="tmp"):
    """
    Scans the srffile and returns the magnitude of the event
    """
    magfile = os.path.join(tempfile.gettempdir(),
                           "%s_%s" %
                           (str(uuid.uuid4()), suffix))
    install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
    cmd = ("%s velfile=%s < %s 2> %s" %
           (os.path.join(install.GP_BIN_DIR, "srf2moment"),
            velfile, srffile, magfile))
    os_utilities.runprog(cmd, False)
    srf2moment_fp = open(magfile, 'r')
    srf2moment_data = srf2moment_fp.readlines()
    srf2moment_fp.close()
    #magnitude on last line
    mag_line = srf2moment_data[len(srf2moment_data) - 4]
    pieces = mag_line.split()
    magnitude = float(pieces[5].split(")")[0])
    cmd = "rm %s" % (magfile)
    os_utilities.runprog(cmd, False)
    return magnitude

def get_hypocenter(srffile, suffix="tmp"):
    """
    Looks up the hypocenter of an event in a srffile
    """
    hypfile = os.path.join(tempfile.gettempdir(),
                           "%s_%s" %
                           (str(uuid.uuid4()), suffix))
    install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
    cmd = ("%s < %s > %s" %
           (os.path.join(install.GP_BIN_DIR, "srf_gethypo"),
            srffile, hypfile))
    os_utilities.runprog(cmd)
    srf_hypo_fp = open(hypfile, 'r')
    srf_hypo_data = srf_hypo_fp.readline()
    srf_hypo_fp.close()
    srf_hypo = srf_hypo_data.split()
    hypo = []
    for i in range(0, 3):
        hypo.append(float(srf_hypo[i]))
    cmd = "rm %s" % (hypfile)
    os_utilities.runprog(cmd)
    return hypo

def get_srf_num_segments(srf_file):
    """
    Returns number of segments in a SRF file
    """
    srf_segments = None

    srf = open(srf_file, 'r')
    for line in srf:
        if line.startswith("PLANE"):
            # Found the plane line, read number of segments
            srf_segments = int(line.split()[1])
            break
    srf.close()

    if srf_segments is None:
        print("[ERROR]: Could not read number of segments from "
              "SRF file: %s" % (src_file))
        sys.exit(1)

    # Return number of segments
    return srf_segments

def get_srf_params(srf_file, segment=0):
    """
    Reads fault_len, width, dlen, dwid, and azimuth from the srf_file
    Segment allows users to specify segment of interest (0-based)
    """
    srf_params1 = None
    srf_params2 = None
    srf = open(srf_file, 'r')
    for line in srf:
        if line.startswith("PLANE"):
            # Found the plane line, read number of segments
            srf_segments = int(line.split()[1])
            if srf_segments < segment + 1:
                print("[ERROR]: Requested parameters from segment %d, "
                      "       SRF file only has %d segment(s)!" %
                      (segment + 1, srf_segments))
                sys.exit(1)
            for _ in range(segment):
                # Skip lines to get to the segment we want
                _ = next(srf)
                _ = next(srf)
            # The next line should have what we need
            srf_params1 = next(srf)
            srf_params2 = next(srf)
            break
    srf.close()
    if srf_params1 is None or srf_params2 is None:
        print("[ERROR]: Cannot determine parameters from SRF file %s" %
              (srf_file))
        sys.exit(1)
    srf_params1 = srf_params1.strip()
    srf_params1 = srf_params1.split()
    srf_params2 = srf_params2.strip()
    srf_params2 = srf_params2.split()
    # Make sure we have the correct number of pieces
    if len(srf_params1) != 6 or len(srf_params2) != 5:
        print("[ERROR]: Cannot parse params from SRF file %s" %
              (srf_file))
        sys.exit(1)

    # Pick the parameters that we need
    params = {}
    params["lon"] = float(srf_params1[0])
    params["lat"] = float(srf_params1[1])
    params["dim_len"] = int(srf_params1[2])
    params["dim_wid"] = int(srf_params1[3])
    params["fault_len"] = float(srf_params1[4])
    params["fault_width"] = float(srf_params1[5])
    params["azimuth"] = int(float(srf_params2[0]))

    return params

def get_srf_info(srf_file):
    """
    This function reads a SRF file and returns version,
    number of segments, and a list with the nstk values
    for each segment
    """
    version = None
    num_segments = None
    nstk = []

    # Read SRF file
    input_file = open(srf_file, 'r')
    for line in input_file:
        line = line.strip()
        # Skip blank lines
        if not line:
            continue
        version = int(float(line))
        break

    # Read number of segments
    for line in input_file:
        line = line.strip()
        # Skip blank lines
        if not line:
            continue
        pieces = line.split()
        if len(pieces) == 2:
            # Get number of planes
            if pieces[0].lower() == "plane":
                num_segments = int(float(pieces[1]))
                break

    if num_segments is None or version is None:
        exceptions.ParameterError("Cannot parse SRF file!")

    # Read nstk for each segment
    for line in input_file:
        line = line.strip()
        # Skip blank lines
        if not line:
            continue
        pieces = line.split()
        if len(pieces) != 6:
            continue
        nstk.append(int(float(pieces[2])))
        # Check if we got nstk for each segment
        if len(nstk) == num_segments:
            break

    input_file.close()
    if len(nstk) != num_segments:
        exceptions.ParameterError("Cannot read nstk from SRF file!")

    return version, num_segments, nstk

def read_srf_trace(srf_file, num_segment, nstk):
    """
    This function reads an SRF file and returns the
    top layer trace for the segment specified
    """
    install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()

    srf2xyz_bin = os.path.join(install.GP_BIN_DIR, "srf2xyz")
    tmpdir = tempfile.mkdtemp(prefix="bbp-")
    f_seg = os.path.join(tmpdir, "srf_points_seg-%d.txt" % (num_segment))

    # Run srf2xyz
    cmd = ("%s lonlatdep=1 nseg=%d < %s > %s" %
           (srf2xyz_bin, num_segment, srf_file, f_seg))
    os_utilities.runprog(cmd)

    # Parse result and extract points
    points = []

    input_file = open(f_seg, 'r')
    for line in input_file:
        line = line.strip()
        if not line:
            continue
        pieces = line.split()
        pieces = [float(piece) for piece in pieces]
        points.append((pieces[0], pieces[1]))
        if len(points) == nstk:
            break
    input_file.close()

    # Delete temp files
    shutil.rmtree(tmpdir)

    return points

