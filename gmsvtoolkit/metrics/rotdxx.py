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

Program to compute RotDXX
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
from utils import os_utilities
from core import gmsvtoolkit_config
from utils.peer_formatter import bbp2peer, peer2bbp
from core.station_list import StationList

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

def do_rotdxx(workdir, peer_input_e_file, peer_input_n_file,
              output_rotd100_file, logfile):
    """
    This function runs the rotd100 command inside workdir, using
    the inputs and outputs specified
    """
    install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()

    # Make sure we don't have absolute path names
    peer_input_e_file = os.path.basename(peer_input_e_file)
    peer_input_n_file = os.path.basename(peer_input_n_file)
    output_rotd100_file = os.path.basename(output_rotd100_file)

    # Save cwd, change back to it at the end
    old_cwd = os.getcwd()
    os.chdir(workdir)

    # Make sure we remove the output files first or Fortran will
    # complain if they already exist
    try:
        os.unlink(output_rotd100_file)
    except OSError:
        pass

    # Write config file for rotd100 program
    rd100_config_filename = "rotd100_inp.cfg"
    rd100_conf = open(rd100_config_filename, 'w')
    # This flag indicates inputs acceleration
    rd100_conf.write("2 interp flag\n")
    # This flag indicate we are processing two input files
    rd100_conf.write("1 Npairs\n")
    # Number of headers in the file
    rd100_conf.write("6 Nhead\n")
    rd100_conf.write("%s\n" % peer_input_e_file)
    rd100_conf.write("%s\n" % peer_input_n_file)
    rd100_conf.write("%s\n" % output_rotd100_file)
    # Close file
    rd100_conf.close()

    progstring = ("%s >> %s 2>&1" %
                  (os.path.join(install.UCB_BIN_DIR,
                                "rotd100"), logfile))
    os_utilities.runprog(progstring, abort_on_error=True, print_cmd=False)

    # Delete RotD100 control file
    os.unlink(rd100_config_filename)

    # Restore working directory
    os.chdir(old_cwd)

def do_split_rotdxx(in_rotdxx_file, out_rotdxx_file, mode):
    """
    Create a RotD50 or RotD100 file out of the RotDXX
    mode selects the output: rotd50 or rotd100
    """
    if mode.lower() != "rotd50" and mode.lower() != "rotd100":
        print("[ERROR]: mode must be set to 'rotd50' or 'rotd100'!")
        sys.exit(1)
    
    # Open input and output files
    in_file = open(in_rotdxx_file, 'r')
    out_file = open(out_rotdxx_file, 'w')

    # Rewrite first line with correct header
    if mode.lower() == "rotd50":
        out_file.write("#  Psa5_N Psa5_E RotD50\n")
    else:
        out_file.write("#  Psa5_N Psa5_E RotD100\n")
    # Skip first line
    line = in_file.readline()
    
    for line in in_file:
        line = line.strip()
        # Skip comments
        if line.startswith('#'):
            out_file.write("%s\n" % (line))
            continue
        pieces = line.split()
        if mode.lower() == "rotd50":
            pieces = pieces[0:4]
        else:
            pieces = pieces[0:5]
            del pieces[3]
        out_file.write("  %s\n" % (" ".join(pieces)))

    # Close everything
    in_file.close()
    out_file.close()

class RotDXX(object):
    """
    Module for computing RotD100/50 provided by UCB
    """

    def __init__(self):
        """
        Initializes class variables
        """
        self.vertical = None
        self.mode = None

    def parse_arguments(self):
        """
        This function takes care of parsing the command-line arguments and
        asking the user for any missing parameters that we need
        """
        parser = argparse.ArgumentParser(description="Compute RotDXX "
                                         " for one or more seismograms.")
        parser.add_argument("--input-dir", dest="input_dir",
                            help="input directory")
        parser.add_argument("--output-dir", dest="output_dir",
                            help="output directory")
        parser.add_argument("-i", "--input", "--input-file",
                            dest="input_file",
                            help="input acceleration BBP file")
        parser.add_argument("-o", "--output", "--output-file",
                            dest="output_file",
                            help="output rd100 file")
        parser.add_argument("--batch-file", "-b", dest="batch_file", 
                            help="file with list of timeseries to process")
        parser.add_argument("--station-list", "-s", dest="station_list",
                            help="station list for batch processing")
        parser.add_argument("--vertical", "-v", dest="vertical", action="store_true",
                            help="process vertical component instead of horizontals")
        parser.add_argument("--rotd100", dest="rotd100", action="store_true",
                            help="enable RotD100 output")
        parser.add_argument("--rotd50", dest="rotd50", action="store_true",
                            help="enable RotD50 output (default)")
        args = parser.parse_args()

        return args

    def run(self):
        """
        Run RotDXX module
        """
        # Parse command-line options
        args = self.parse_arguments()

        # Set mode
        self.mode = "rotd50"
        if args.rotd100 and args.rotd50:
            self.mode = "both"
        elif args.rotd100:
            self.mode = "rotd100"

        # Set input and output directories
        if args.input_dir is None:
            input_dir = "."
        else:
            input_dir = args.input_dir
        if args.output_dir is None:
            output_dir = "."
        else:
            output_dir = args.output_dir

        input_file = None
        batch_file = None
        station_file = None
        self.vertical = args.vertical
        if args.input_file is not None:
            input_file = args.input_file
        elif args.batch_file is not None:
            batch_file = args.batch_file
        elif args.station_list is not None:
            station_file = args.station_list
        else:
            print("[ERROR]: Must specify either input file, batch file, or station file!")
            sys.exit(1)

        # Run in batch mode
        if input_file is None:
            if batch_file is not None:
                self.run_batch_mode(batch_file, input_dir, output_dir)
            else:
                self.run_station_mode(station_file, input_dir, output_dir)
        else:
            if args.output_file is not None:
                output_base = os.path.splitext(args.output_file)[0]
            else:
                output_base = os.path.splitext(input_file)[0]

            # Run RotD100
            self.run_single_file(input_file, output_base,
                                 input_dir, output_dir)

    def run_single_file(self, input_file, output_base,
                        input_dir, output_dir, temp_dir=None):
        """
        Calculate RotDXX for a single acceleration seismogram
        """
        if temp_dir is None:
            # Create temp directory if needed
            temp_dir = tempfile.mkdtemp()
            # And clean up later
            atexit.register(cleanup, temp_dir)
        
        print("[ROTDXX]: Processing %s" % (input_file))
        peer_n_file = "temp-peer_n.peer"
        peer_e_file = "temp-peer_e.peer"
        peer_z_file = "temp-peer_z.peer"
        output_temp_file = "temp.rdxx"
        logfile = "temp-rotdxx-log.txt"
        bbp2peer(os.path.join(input_dir, input_file),
                 os.path.join(temp_dir, peer_n_file),
                 os.path.join(temp_dir, peer_e_file),
                 os.path.join(temp_dir, peer_z_file))
        output_temp_file = os.path.join(temp_dir,
                                        output_temp_file)
        if self.vertical:
            # Calculate RotDXX for vertical component
            do_rotdxx(temp_dir, peer_z_file, peer_z_file,
                      output_temp_file, logfile)
        else:
            # Calculate RotDXX for horizontal components
            do_rotdxx(temp_dir, peer_e_file, peer_n_file,
                      output_temp_file, logfile)
        if self.mode == "rotd50" or self.mode == "both":
            output_file = "%s.rd50" % (output_base)
            do_split_rotdxx(os.path.join(temp_dir, output_temp_file),
                            os.path.join(output_dir, output_file),
                            "rotd50")
        if self.mode == "rotd100" or self.mode == "both":
            output_file = "%s.rd100" % (output_base)
            do_split_rotdxx(os.path.join(temp_dir, output_temp_file),
                            os.path.join(output_dir, output_file),
                            "rotd100")

    def run_batch_mode(self, batch_file, input_dir,
                       output_dir, temp_dir=None):
        """
        Calculates RotDXX for a list of acceleration seismograms
        """
        if temp_dir is None:
            # Create temp directory if needed
            temp_dir = tempfile.mkdtemp()
            # And clean up later
            atexit.register(cleanup, temp_dir)

        input_list = open(batch_file, 'r')
        for line in input_list:
            line = line.strip()
            if not line:
                continue

            input_file = line
            output_base = os.path.splitext(input_file)[0]

            # Run RotDXX
            self.run_single_file(input_file, output_base,
                                 input_dir, output_dir, temp_dir)

        input_list.close()

    def run_station_mode(self, station_file, input_dir,
                         output_dir, temp_dir=None):
        """
        Calculates RotDXX for stations in a station list
        """
        if temp_dir is None:
            # Create temp directory if needed
            temp_dir = tempfile.mkdtemp()
            # And clean up later
            atexit.register(cleanup, temp_dir)

            stations = StationList(station_file)
            station_list = stations.get_station_list()

            # Loop through stations
            for station in station_list:
                station_name = station.scode

                # Find input file
                input_list = glob.glob("%s%s*%s*.acc.bbp" %
                                       (input_dir, os.sep, station_name))
                if len(input_list) != 1:
                    print("[ERROR]: Can't find input file for station %s" % (station_name))
                    sys.exit(1)

                input_file = os.path.basename(input_list[0])
                output_base = input_file[0:input_file.find(".acc.bbp")]

                # Run RotDXX
                self.run_single_file(input_file, output_base,
                                     input_dir, output_dir, temp_dir)

if __name__ == '__main__':
    print("Running module: %s" % (os.path.basename(sys.argv[0])))
    ME = RotDXX()
    ME.run()
