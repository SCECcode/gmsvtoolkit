#!/usr/bin/env python3
"""
BSD 3-Clause License

Copyright (c) 2026, University of Southern California
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

This module is used to calculate FAS
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import glob
import time
import atexit
import shutil
import numpy as np
import argparse
import tempfile

# Imports needed from the GMSVToolkit
from core import exceptions
from utils import os_utilities
from utils import file_utilities
from core.station_list import StationList

# Import FAS functions
from metrics import fas_eas

B_PARAM = 188.5
W_PARAM = 1.0/(10.0**(3.0/B_PARAM))
CM2G = 980.664999

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

def find_acc_file(input_dir, station_name, label):
    """
    Looks into input_dir for a acceleration seismogram for station station_name
    """
    # Find input file
    input_list = glob.glob("%s%s*%s.%s*.bbp" %
                           (input_dir, os.sep, label, station_name))
    if not len(input_list):
        # Try to match filename without the label
        input_list = glob.glob("%s%s%s.bbp" %
                               (input_dir, os.sep, station_name))
        if not len(input_list):
            print("[ERROR]: Can't find input file for station %s" % (station_name))
            sys.exit(1)
    if len(input_list) > 1:
        # Found more than one file, check if we can find a single file that includes .acc.bbp
        input_list = [filename for filename in input_list if ".acc.bbp" in filename]
        if len(input_list) > 1:
            print("[ERROR]: Found multiple input files for station %s" % (station_name))
            sys.exit(1)

    input_file = os.path.basename(input_list[0])

    return input_file

def compute_fas(acc1, acc2, dt):
    """
    Computes FAS/EAS/SEAS for the provided horizontal components
    """
    b = B_PARAM
    w = W_PARAM

    # Compute fas, eas, and smoothed eas (seas)
    [fas_freq, fas_1, fas_2, eas,
     seas_freq, seas] = fas_eas.get_smooth_eas(acc1, acc2, dt, b, w)

    return fas_freq, fas_1, fas_2, eas, seas_freq, seas

def compute_station_fas(a_tmpdir, a_outdir_fas, acc_file,
                        station_name, output_prefix,
                        input_unit="cm/s/s", output_unit="cm/s/s",
                        output_mode="both", logfile=None):
    """
    Computes FAS for a station
    """
    # Read dt from input file
    dt = file_utilities.read_bbp_dt(acc_file)
    # Read two horizontal components from input file
    [_, acc1, acc2, _] = file_utilities.read_bbp_file(acc_file)

    # Convert units if needed
    if input_unit == "cm/s/s" and output_unit == "g":
        # Convert units from cm/s/s to g
        acc1 = acc1 / CM2G
        acc2 = acc2 / CM2G
    if input_unit == "g" and output_unit == "cm/s/s":
        acc1 = acc1 * CM2G
        acc2 = acc2 * CM2G

    [fas_freq, fas_1, fas_2, eas,
     seas_freq, seas] = compute_fas(acc1, acc2, dt)
    
    # Write file with FAS/EAS first
    if output_mode == "both" or output_mode == "fas":
        output_basename = "%s.eas.fs.col" % (output_prefix)
        output_filename = os.path.join(a_outdir_fas, output_basename)
        output_file = open(output_filename, 'w')
        output_file.write("# Freq(Hz)      FAS H1 (%s)      FAS H2 (%s)      EAS (%s)\n" %
                          (output_unit, output_unit, output_unit))
        for f0, f1, f2, e0 in zip(fas_freq, fas_1, fas_2, eas):
            output_file.write("%2.7E\t%2.7E\t%2.7E\t%2.7E\n" %
                              (f0, f1, f2, e0))
        output_file.close()

    # Now, we write the file with the SEAS
    if output_mode == "both" or output_mode == "seas":
        output_basename = "%s.seas.fs.col" % (output_prefix)
        output_filename = os.path.join(a_outdir_fas, output_basename)
        output_file = open(output_filename, 'w')
        output_file.write("# Freq(Hz)      Smoothed EAS (%s) b=%3.4f\n" %
                          (output_unit, B_PARAM))
        for f0, s0 in zip(seas_freq, seas):
            output_file.write("%2.7E\t%2.7E\n" %
                              (f0, s0))
        output_file.close()

class FAS(object):
    """
    Implement FAS analisys for the Broadband Platform
    """
    def __init__(self):
        """
        Initializes class variables
        """
        pass

    def parse_arguments(self):
        """
        This function takes care of parsing the command-line arguments and
        asking the user for any missing parameters that we need
        """
        parser = argparse.ArgumentParser(description="Compute FAS "
                                         " for a set of seismograms.")
        parser.add_argument("--station-list", "-s", dest="station_list", required=True,
                            help="station list for batch processing")
        parser.add_argument("--output-dir", dest="output_dir",
                            help="output directory")
        parser.add_argument("--logfile", dest="logfile",
                            help="file to store processing log messages")
        parser.add_argument("--labels", "-l", dest="labels", required=True,
                            help="comma-separated comparison labels")
        parser.add_argument("--input-unit", dest="input_unit", default="cm/s/s",
                            help="input units: (g or cm/s/s)")
        parser.add_argument("--output-unit", dest="output_unit", default="cm/s/s",
                            help="output units: (g or cm/s/s)")
        parser.add_argument("--fas-only", dest="fas_only", action="store_true",
                            help="outputs only the FAS/EAS file, default is both FAS/EAS and SEAS files")
        parser.add_argument("--seas-only", dest="seas_only", action="store_true",
                            help="outputs only the SEAS file, default is both FAS/EAS and SEAS files")
        parser.add_argument('input_dirs', nargs='*')
        
        args = parser.parse_args()
        return args

    def run(self):
        """
        Run FAS analysis codes
        """
        # Parse command-line options
        args = self.parse_arguments()

        output_dir = ""
        logfile = None
        if args.output_dir is not None:
            output_dir = args.output_dir
        output_dir = os.path.abspath(output_dir)
        if args.logfile is not None:
            logfile = os.path.abspath(args.logfile)
        station_file = os.path.abspath(args.station_list)

        # Find what users want to output
        if args.fas_only and args.seas_only:
            print("[ERROR]: Specify only one of --fas-only and --seas-only")
            sys.exit(-1)
        output_mode = "both"
        if args.fas_only:
            output_mode = "fas"
        if args.seas_only:
            output_mode = "seas"

        # Figure out units
        input_unit = args.input_unit.lower()
        output_unit = args.output_unit.lower()
        if input_unit != "g" and input_unit != "cm/s/s":
            print("[ERROR]: Input unit must be 'g' or 'cm/s/s'")
            sys.exit(-1)
        if output_unit != "g" and output_unit != "cm/s/s":
            print("[ERROR]: Output unit must be 'g' or 'cm/s/s'")
            sys.exit(-1)
        
        # Sort input directories/labels
        input_dirs = args.input_dirs
        labels = args.labels
        if len(input_dirs) < 1:
            print("[ERROR]: Please specify at least one input directory!")
            sys.exit(1)
        labels = [label.strip() for label in labels.split(",")]
        if len(labels) != len(input_dirs):
            print("[ERROR]: Please specify as many labels as input directories!")
            sys,exit(1)

        self.run_fas_seas(station_file, input_dirs, labels,
                          output_dir, input_unit=input_unit,
                          output_unit=output_unit,
                          output_mode=output_mode,
                          logfile=logfile, temp_dir=None)

    def run_fas_seas(self, station_file, input_dirs, labels,
                     output_dir, input_unit="cm/s/s",
                     output_unit="cm/s/s", output_mode="both",
                     logfile=None, temp_dir=None):
        """
        Run FAS/SEAS analysis codes
        """
        sta_base = os.path.basename(os.path.splitext(station_file)[0])

        if temp_dir is None:
            # Create temp directory if needed
            temp_dir = tempfile.mkdtemp()
            # And clean up later
            atexit.register(cleanup, temp_dir)

        # Make paths absolute paths
        temp_dir = os.path.abspath(temp_dir)
        output_dir = os.path.abspath(output_dir)
        input_dirs = [os.path.abspath(input_dir) for input_dir in input_dirs]

        if logfile is None:
            # Create our own log file
            logfile = os.path.join(temp_dir,
                                   "%s.fas.log" % ("-".join(labels)))
        #
        # Make sure the tmp and out directories exist
        #
        os_utilities.mkdirs([temp_dir, output_dir], print_cmd=False)

        slo = StationList(station_file)
        site_list = slo.get_station_list()

        for input_dir, label in zip(input_dirs, labels):
            # Process each input directory
            print("==> Processing %s" % (label))
            for station in site_list:
                # Process each station
                station_name = station.scode
                print("===> Processing station: %s..." % (station_name),
                      end="", flush=True)
                acc_file = find_acc_file(input_dir, station_name, label)
                input_acc_file = os.path.join(input_dir, acc_file)
                output_prefix = "%s.%s" % (label, station_name)
                
                # Compute seismogram's FAS
                t1 = time.time()
                compute_station_fas(temp_dir, output_dir, input_acc_file,
                                    station_name, output_prefix=output_prefix,
                                    input_unit=input_unit, output_unit=output_unit,
                                    output_mode=output_mode, logfile=logfile)
                t2 = time.time()
                print("%10.2f s" % (t2 - t1))
                
        # All done
        print("=> Processing done!")

if __name__ == '__main__':
    ME = FAS()
    ME.run()
    sys.exit(0)
