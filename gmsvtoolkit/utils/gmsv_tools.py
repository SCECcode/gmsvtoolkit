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

GMSVToolkit seismogram processing tools
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import glob
import atexit
import shutil
import argparse
import tempfile

# Import GMSVToolkit modules
from core import gmsvtoolkit_config
from core.station_list import StationList
from utils import os_utilities

VALID_FORMATS = ["acc", "vel", "dis"]
COMPS = [".000", ".090", ".ver"]
INSTALL = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    parser = argparse.ArgumentParser(description="GMSVToolkit Seismogram "
                                     "processing tools.")
    parser.add_argument("--input-dir", dest="input_dir",
                        help="input directory")
    parser.add_argument("--output-dir", dest="output_dir",
                        help="output directory")
    parser.add_argument("-i", "--input", "--input-file",
                        dest="input_file",
                        help="input BBP file")
    parser.add_argument("-o", "--output", "--output-file",
                        dest="output_file",
                        help="output BBP file")
    parser.add_argument("--batch-file", "-b", dest="batch_file", 
                        help="file with list of timeseries to process")
    parser.add_argument("--station-list", "-s", dest="station_list",
                        help="station list for batch processing")
    parser.add_argument("--input-format", dest="input_format", required=True,
                        help="convert from input format: acc, vel, dis")
    parser.add_argument("--output-format", dest="output_format", required=True,
                        help="convert to output format: acc, vel, dis")
    parser.add_argument("--input-suffix", "--suffix", dest="input_suffix",
                        help="suffix used for input files")
    args = parser.parse_args()

    return args

def split_file(bbp_in, work_dir, prefix="gmsv_tools_tmp"):
    """
    Splits bbp_in into 3 1-component files
    """
    nsfile = os.path.join(work_dir, (prefix + COMPS[0]))
    ewfile = os.path.join(work_dir, (prefix + COMPS[1]))
    udfile = os.path.join(work_dir, (prefix + COMPS[2]))

    cmd = ("%s " % (os.path.join(INSTALL.GP_BIN_DIR, "wcc2bbp")) +
           "nsfile=%s ewfile=%s udfile=%s " %
           (nsfile, ewfile, udfile) +
           "wcc2bbp=0 < %s >> /dev/null 2>&1" %
           (bbp_in))
    os_utilities.runprog(cmd, print_cmd=False, abort_on_error=True)

def join_files(bbp_out, units, work_dir, prefix_proc="gmsv_tools_tmp_proc"):
    """
    Joins the 3 single-component bbp files into bbp_out
    """
    nsfile = os.path.join(work_dir, (prefix_proc + COMPS[0]))
    ewfile = os.path.join(work_dir, (prefix_proc + COMPS[1]))
    udfile = os.path.join(work_dir, (prefix_proc + COMPS[2]))

    cmd = ("%s " % (os.path.join(INSTALL.GP_BIN_DIR, "wcc2bbp")) +
           "nsfile=%s ewfile=%s udfile=%s " %
           (nsfile, ewfile, udfile) +
           "units=%s " % (units) +
           "wcc2bbp=1 > %s 2>> /dev/null" %
           (bbp_out))
    os_utilities.runprog(cmd, print_cmd=False, abort_on_error=True)

def read_bbp_units(filename):
    """
    Get the units from the file's header
    Returns either "m" or "cm"
    """
    units = None

    try:
        input_file = open(filename, 'r')
        for line in input_file:
            if line.find("time(sec)") > 0:
                units = line.split()[2]
                break
        input_file.close()
    except IOError:
        print("[ERROR]: Cannot open file %s, exiting...." % (filename))
        sys.exit(-1)

    # Make sure we got something
    if units is None:
        print("[ERROR]: Cannot find units in bbp file!")
        sys.exit(-1)

    # Parse and figure what what we got
    units_start = units.find("(")
    units_end = units.find(")")
    if units_start < 0 or units_end < 0:
        print("[ERROR]: Cannot parse units in bbp file!")
        sys.exit(-1)

    units = units[units_start+1:units_end]

    # Check if we got what we needed
    if units == "cm" or units == "cm/s" or units == "cm/s/s":
        return units

    # Invalid units in this file
    print("[ERROR]: Cannot parse units in bbp file!")
    sys.exit(-1)
# end of read_bbp_units

def integrate(bbp_in, bbp_out, temp_dir):
    """
    Generates bbp_out by integrating bbp_in
    """
    units_in = read_bbp_units(bbp_in)
    if units_in == "cm":
        print("[ERROR]: Already have a displacement file!")
        sys.exit(-1)
    if units_in == "cm/s/s":
        units_out = "cm/s"
    elif units_in == "cm/s":
        units_out = "cm"
    else:
        print("[ERROR]: Unknown unit in the input file!")
        sys.exit(-1)

    # Split file to get each component separate
    prefix = "gmsv_tools_tmp"
    prefix_proc = "gmsv_tools_tmp_proc"
    split_file(bbp_in, temp_dir, prefix=prefix)

    # Process each component
    for component in COMPS:
        filein = os.path.join(temp_dir, (prefix + component))
        fileout = os.path.join(temp_dir, (prefix_proc + component))
        cmd = ("%s integ=1 filein=%s fileout=%s" %
               (os.path.join(INSTALL.GP_BIN_DIR, "integ_diff"),
                filein, fileout))
        os_utilities.runprog(cmd, print_cmd=False, abort_on_error=True)

    # Put 3-component BBP file back together
    join_files(bbp_out, units_out, temp_dir, prefix_proc)

def diff(bbp_in, bbp_out, temp_dir):
    """
    Generates bbp_out by derivating bbp_in
    """
    units_in = read_bbp_units(bbp_in)
    if units_in == "cm/s/s":
        print("[ERROR]: Already have an acceleration file!")
        sys.exit(-1)
    if units_in == "cm":
        units_out = "cm/s"
    elif units_in == "cm/s":
        units_out = "cm/s/s"
    else:
        print("[ERROR]: Unknown unit in the input file!")
        sys.exit(-1)

    # Split file to get each component separate
    prefix = "gmsv_tools_tmp"
    prefix_proc = "gmsv_tools_tmp_proc"
    split_file(bbp_in, temp_dir, prefix=prefix)

    # Process each component
    for component in COMPS:
        filein = os.path.join(temp_dir, (prefix + component))
        fileout = os.path.join(temp_dir, (prefix_proc + component))
        cmd = ("%s diff=1 filein=%s fileout=%s" %
               (os.path.join(INSTALL.GP_BIN_DIR, "integ_diff"),
                filein, fileout))
        os_utilities.runprog(cmd, print_cmd=False, abort_on_error=True)

    # Put 3-component BBP file back together
    join_files(bbp_out, units_out, temp_dir, prefix_proc)

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def run():
    """
    GMSVToolkit Tools
    """
    args = parse_arguments()

    # Check paths
    input_dir = ""
    output_dir = ""
    if args.input_dir:
        input_dir = args.input_dir
    if args.output_dir:
        output_dir = args.output_dir
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    if args.input_file:
        convert_file(args.input_file, args.input_format,
                     args.output_format, output_file=args.output_file,
                     input_dir=input_dir, output_dir=output_dir)
    elif args.station_list:
        convert_station_file(args.station_list,
                             args.input_format, args.output_format,
                             input_dir, output_dir,
                             input_suffix=args.input_suffix)
    elif args.batch_file:
        convert_batch_file(args.batch_file,
                           args.input_format, args.output_format,
                           input_dir, output_dir,
                           input_suffix=args.input_suffix)
    else:
        print("[ERROR]: Must specify input_file, station_list or batch_file!")
        sys.exit(-1)

def select_action(input_format, output_format):
    """
    Select action based on the input and output formats
    """
    input_format = input_format.lower()
    output_format = output_format.lower()
    if input_format not in VALID_FORMATS:
        print("[ERROR]: input format must be one of %s" % (VALID_FORMATS))
        sys.exit(-1)
    if output_format not in VALID_FORMATS:
        print("[ERROR]: output format must be one of %s" % (VALID_FORMATS))
        sys.exit(-1)
    input_index = VALID_FORMATS.index(input_format)
    output_index = VALID_FORMATS.index(output_format)
    if input_index > output_index:
        action_type = "diff"
    else:
        action_type = "int"
    action_count = abs(input_index - output_index)

    return action_type, action_count

def convert_station_file(station_file,
                         input_format, output_format,
                         input_dir, output_dir,
                         input_suffix=None,
                         temp_dir=None):
    """
    Process a station list and convert each file as
    indicated by action_type and action_count
    """
    action_type, action_count = select_action(input_format, output_format)

    stations = StationList(station_file)
    station_list = stations.get_station_list()

    # Loop through stations
    for station in station_list:
        station_name = station.scode

        run_directory_mode(station_name,
                           input_format, output_format,
                           input_dir, output_dir,
                           action_type, action_count,
                           input_suffix=input_suffix,
                           temp_dir=temp_dir)

def convert_batch_file(batch_file,
                       input_format, output_format,
                       input_dir, output_dir,
                       input_suffix=None,
                       temp_dir=None):
    """
    Process a batch file and convert each file as
    indicated by action_type and action_count
    """
    action_type, action_count = select_action(input_format, output_format)
    
    # Open batch file
    input_list = open(batch_file, 'r')
    for line in input_list:
        line = line.strip()
        if not line:
            continue

        station_name = line

        run_directory_mode(station_name,
                           input_format, output_format,
                           input_dir, output_dir,
                           action_type, action_count,
                           input_suffix=input_suffix,
                           temp_dir=temp_dir)

    input_list.close()

def run_directory_mode(station_name,
                       input_format, output_format,
                       input_dir, output_dir,
                       action_type, action_count,
                       input_suffix=None,
                       temp_dir=None):
    """
    Create input and output filenames for station_name and
    then call convert_single_file
    """
    if temp_dir is None:
        # Create temp directory if needed
        temp_dir = tempfile.mkdtemp()
        # And clean up later
        atexit.register(cleanup, temp_dir)

    # Find input file
    if input_suffix is None:
        extension = ".%s.bbp" % (input_format)
    else:
        extension = input_suffix
    input_list = glob.glob("%s%s*%s*%s" %
                           (input_dir, os.sep, station_name, extension))
    if len(input_list) != 1:
        print("[ERROR]: Can't find input file for station %s" % (station_name))
        sys.exit(1)
    input_file = input_list[0]

    # Build output_file name
    base_file = os.path.basename(input_file)
    if input_suffix is None:
        base_tokens = base_file.split('.')[0:-2]
    else:
        suffix_index = base_file.rfind(input_suffix)
        base_tokens = [base_file[0:suffix_index]]
    if not base_tokens:
        print("[ERROR]: Invalid BBP filename: %s" % (input_file))
        sys.exit(1)
    base_tokens = list(base_tokens)
    base_tokens.append(output_format)
    base_tokens.append('bbp')
    output_file = os.path.join(output_dir, '.'.join(base_tokens))
    
    convert_single_file(input_file, output_file,
                        action_type, action_count,
                        temp_dir)

def convert_single_file(input_file, output_file,
                        action_type, action_count,
                        temp_dir=None):
    """
    Convert a single file by differentiation or integration,
    can be used more than once to go from displacement to
    acceleration (or vice versa) directly
    """
    if temp_dir is None:
        # Create temp directory if needed
        temp_dir = tempfile.mkdtemp()
        # And clean up later
        atexit.register(cleanup, temp_dir)

    if action_count == 0:
        # Nothing to do, just copy file to destination
        print("[GMSV_TOOLS]: Copying %s --> %s" %
              (os.path.basename(input_file),
               os.path.basename(output_file)))
        shutil.copy(input_file, output_file)
        return

    print("[GMSV_TOOLS]: Converting %s --> %s" %
          (os.path.basename(input_file),
           os.path.basename(output_file)))

    # Itereate action_count times
    tmp_input = input_file
    for count in range(0, action_count):
        if count == action_count - 1:
            # Last time!
            tmp_output = output_file
        else:
            tmp_output = os.path.join(temp_dir, "temp_file.bbp")
        # Run action
        if action_type == "int":
            integrate(tmp_input, tmp_output, temp_dir)
        elif action_type == "diff":
            diff(tmp_input, tmp_output, temp_dir)
        tmp_input = tmp_output        

def convert_file(input_file, input_format, output_format,
                 output_file=None, input_dir="",
                 output_dir="", temp_dir=None):
    """
    Converts a single file from input format
    to output format
    """
    # Set up input and output files
    input_file = os.path.join(input_dir, input_file)
    if output_file is None:
        base_file = os.path.basename(input_file)
        base_tokens = base_file.split('.')[0:-2]
        if not base_tokens:
            print("[ERROR]: Invalid BBP filename: %s" % (input_file))
            sys.exit(1)
        base_tokens = list(base_tokens)
        base_tokens.append(output_format)
        base_tokens.append('bbp')
        output_file = os.path.join(output_dir, '.'.join(base_tokens))
    else:
        output_file = os.path.join(output_dir, output_file)

    action_type, action_count = select_action(input_format, output_format)

    convert_single_file(input_file, output_file,
                        action_type, action_count,
                        temp_dir=temp_dir)

if __name__ == '__main__':
    run()
