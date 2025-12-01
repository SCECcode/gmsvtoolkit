#!/usr/bin/env python3
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
from core import gmsvtoolkit_config

# Import FAS functions
from metrics import fas_smc
from metrics import fas_seas

COMPS = ['000', '090', 'ver']

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

def compute_fas(a_tmpdir, a_outdir_fas, acc_file,
                station_name, output_prefix, logfile=None):
    """
    Computes FAS for a station
    """
    install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
    asc2smc_control_file = "asc2smc.ctl"
    smc2fs2_control_file = "smc2fs2.ctl"
    header_lines = file_utilities.count_header_lines(os.path.join(a_tmpdir,
                                                                  acc_file))
    if logfile is None:
        logfile = os.path.join(a_tmpdir, "%s.fas.log" % (station_name))
    # Work on both NS and EW components
    for comp, data_column in zip(["NS", "EW"], [2, 3]):
        # First we convert from BBP to SMC format
        fas_smc.create_boore_asc2smc(os.path.join(a_tmpdir,
                                                  asc2smc_control_file),
                                     acc_file, data_column, header_lines,
                                     ".smc8.%s" % (comp))
        cmd = ("%s << END >> %s 2>&1\n" %
               (os.path.join(install.USGS_BIN_DIR, "asc2smc"),
                logfile) +
               "%s\n" % (asc2smc_control_file) +
               "END\n")
        os_utilities.runprog(cmd, False, abort_on_error=True)
        # Then, we run the smc2fs2 FAS tool
        smc_file = "%s.smc8.%s" % (acc_file, comp)
        fas_smc.create_boore_smc2fs2(os.path.join(a_tmpdir,
                                                  smc2fs2_control_file),
                                     smc_file, ".no_smooth.fs.col")
        cmd = ("%s >> %s 2>&1\n" %
               (os.path.join(install.USGS_BIN_DIR, "smc2fs2"),
                logfile))
        os_utilities.runprog(cmd, False, abort_on_error=True)

    # Calculate EAS and smoothed EAS
    ns_file = os.path.join(a_tmpdir,
                           "%s.smc8.NS.no_smooth.fs.col" % (acc_file))
    ew_file = os.path.join(a_tmpdir,
                           "%s.smc8.EW.no_smooth.fs.col" % (acc_file))
    output_file = os.path.join(a_outdir_fas,
                               "%s.smc8.smooth.fs.col" %
                               (output_prefix))
    (freqs, ns_fas,
     ew_fas, eas, smoothed_eas) = fas_seas.calculate_smoothed_eas(ns_file,
                                                                  ew_file,
                                                                  output_file)

def resample_bbp_file(input_bbp_file, output_bbp_file,
                      site, old_dt, new_dt, a_tmpdir,
                      prefix="temp", logfile=None):
    """
    Resamples input_bbp_file to new_dt, writing the result to
    output_bbp_file
    """
    install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
    if logfile is None:
        logfile = os.path.join(a_tmpdir, "%s.fas.log" % (site))
    # Make sure we have a string
    prefix = str(prefix)

    print("--> Resampling   %.4f --> %.4f - %s... " %
          (old_dt, new_dt, os.path.basename(input_bbp_file)))
    # Create path names and check if their sizes are within bounds
    nsfile = os.path.join(a_tmpdir,
                          "%s.%s-fas.acc.000" % (prefix, site))
    ewfile = os.path.join(a_tmpdir,
                          "%s.%s-fas.acc.090" % (prefix, site))
    udfile = os.path.join(a_tmpdir,
                          "%s.%s-fas.acc.ver" % (prefix, site))
    bbpfile = input_bbp_file

    os_utilities.check_path_lengths([nsfile, ewfile, udfile],
                                    os_utilities.GP_MAX_FILENAME)

    progstring = ("%s " %
                  (os.path.join(install.GP_BIN_DIR, "wcc2bbp")) +
                  "nsfile=%s ewfile=%s udfile=%s " %
                  (nsfile, ewfile, udfile) +
                  "wcc2bbp=0 < %s >> %s 2>&1" %
                  (bbpfile, logfile))
    os_utilities.runprog(progstring, abort_on_error=True,
                         print_cmd=False)

    for component in COMPS:
        # Set up paths for each component file
        infile = os.path.join(a_tmpdir,
                              "%s.%s-fas.acc.%s" %
                              (prefix, site, component))

        outfile = os.path.join(a_tmpdir, "%s.%s-fas-resamp.%s" %
                               (prefix, site, component))
        os_utilities.check_path_lengths([infile, outfile],
                                        os_utilities.GP_MAX_FILENAME)

        progstring = ("%s newdt=%f " %
                      (os.path.join(install.GP_BIN_DIR,
                                    "wcc_resamp_arbdt"), new_dt) +
                      "infile=%s outfile=%s >> %s 2>&1" %
                      (infile, outfile, logfile))
        os_utilities.runprog(progstring, abort_on_error=True,
                             print_cmd=False)

    # Put the acc file back together
    nsfile = os.path.join(a_tmpdir, "%s.%s-fas-resamp.000" %
                          (prefix, site))
    ewfile = os.path.join(a_tmpdir, "%s.%s-fas-resamp.090" %
                          (prefix, site))
    udfile = os.path.join(a_tmpdir, "%s.%s-fas-resamp.ver" %
                          (prefix, site))
    bbpfile = output_bbp_file
    cmd = ("%s " % (os.path.join(install.GP_BIN_DIR, "wcc2bbp")) +
           "nsfile=%s ewfile=%s udfile=%s " %
           (nsfile, ewfile, udfile) +
           "units=cm/s/s wcc2bbp=1 > %s 2>> %s" %
           (bbpfile, logfile))
    os_utilities.runprog(cmd, abort_on_error=True, print_cmd=False)

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
        parser.add_argument('input_folders', nargs='*')
        
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
        
        # Sort input folders/labels
        input_folders = args.input_folders
        labels = args.labels
        if len(input_folders) < 1:
            print("[ERROR]: Please specify at least one input folder!")
            sys.exit(1)
        labels = [label.strip() for label in labels.split(",")]
        if len(labels) != len(input_folders):
            print("[ERROR] Please specify as many labels as input folders!")
            sys,exit(1)

        if len(input_folders) == 1:
            input_dir = input_folders[0]
            label = labels[0]
            self.run_scenario(station_file, input_dir, label,
                              output_dir, logfile=logfile,
                              temp_dir=None)
        else:
            self.run_validation(station_file, input_folders, labels,
                                output_dir, logfile=logfile, temp_dir=None)
            
    def run_scenario(self, station_file, input_dir, label,
                     output_dir, logfile=None, temp_dir=None):
        """
        Run FAS analysis codes for scenario simulations
        """
        install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
        sta_base = os.path.basename(os.path.splitext(station_file)[0])

        if temp_dir is None:
            # Create temp directory if needed
            temp_dir = tempfile.mkdtemp()
            # And clean up later
            atexit.register(cleanup, temp_dir)

        # Make all paths absolute
        temp_dir = os.path.abspath(temp_dir)
        input_dir = os.path.abspath(input_dir)
        output_dir = os.path.abspath(output_dir)
        
        if logfile is None:
            # Create our own log file
            logfile = os.path.join(temp_dir,
                                   "%s.%s.fas.log" %
                                   (label, sta_base))
        #
        # Make sure the tmp and out directories exist
        #
        os_utilities.mkdirs([input_dir, temp_dir, output_dir], print_cmd=False)

        slo = StationList(station_file)
        site_list = slo.get_station_list()

        # Save current directory
        old_cwd = os.getcwd()
        os.chdir(temp_dir)

        # Initial values
        new_dt = 10000000.0
        new_samples = 0

        # Pre-processing, find lowest dt among all input timeseries
        for site in site_list:
            acc_file = find_acc_file(input_dir, site.scode, label)

            # Read DT from simulated file
            input_syn_acc_file = os.path.join(input_dir, acc_file)
            syn_dt = file_utilities.read_bbp_dt(input_syn_acc_file)
            new_dt = min(new_dt, syn_dt)

        print("==> Target DT set to %.4f" % (new_dt))

        syn_rs_array = []

        print("==> Pre-processing step 1: matching dt...")
        for site in site_list:
            acc_file = find_acc_file(input_dir, site.scode, label)

            shutil.copy2(os.path.join(input_dir, acc_file),
                         os.path.join(temp_dir, acc_file))

            # Read DT from input file
            input_syn_acc_file = os.path.join(temp_dir, acc_file)
            syn_dt = file_utilities.read_bbp_dt(input_syn_acc_file)

            if syn_dt == new_dt:
                input_rs_syn_acc_file = input_syn_acc_file
            else:
                input_rs_syn_acc_file = os.path.join(temp_dir,
                                                     "rs-%s" %
                                                     (acc_file))
                resample_bbp_file(input_syn_acc_file,
                                  input_rs_syn_acc_file,
                                  site.scode,
                                  syn_dt, new_dt,
                                  temp_dir,
                                  logfile=logfile)

            # Keep list of files to be used later
            syn_rs_array.append(input_rs_syn_acc_file)

        print("==> Pre-processing step 2: matching samples...")
        for (site,
             input_rs_syn_acc_file) in zip(site_list,
                                           syn_rs_array):
            # Read samples
            syn_samples = file_utilities.read_bbp_samples(input_rs_syn_acc_file)
            new_samples = max(new_samples, syn_samples)

        print("==> Target samples set to %d" % (new_samples))

        for (site,
            input_rs_syn_acc_file) in zip(site_list,
                                           syn_rs_array):

            acc_file = find_acc_file(input_dir, site.scode, label)

            print("==> Processing station: %s" % (site.scode))

            # Make sure file has new_samples data points
            syn_samples = file_utilities.read_bbp_samples(input_rs_syn_acc_file)

            if syn_samples == new_samples:
                input_final_syn_acc_file = input_rs_syn_acc_file
            else:
                input_final_syn_acc_file = os.path.join(temp_dir,
                                                        "pad-%s" %
                                                        (acc_file))
                extra_points = new_samples - syn_samples
                print("=====> Adding %d extra points to %s" %
                      (extra_points, os.path.basename(input_rs_syn_acc_file)))
                file_utilities.add_extra_points(input_rs_syn_acc_file,
                                                input_final_syn_acc_file,
                                                extra_points)

            # Compute FAS for calculated seismogram
            output_prefix = "%s.%s" % (label, site.scode)
            print("=====> computing FAS for seismogram... ", end="", flush=True)
            t1 = time.time()
            compute_fas(temp_dir, output_dir,
                        os.path.basename(input_final_syn_acc_file),
                        site.scode, output_prefix,
                        logfile=logfile)
            t2 = time.time()
            print("%10.2f s" % (t2 - t1))

        # All done, restore working directory
        os.chdir(old_cwd)

    def run_validation(self, station_file, input_folders, labels,
                       output_dir, logfile=None, temp_dir=None):
        """
        Run FAS analysis codes for validation simulations
        """
        install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
        sta_base = os.path.basename(os.path.splitext(station_file)[0])

        if temp_dir is None:
            # Create temp directory if needed
            temp_dir = tempfile.mkdtemp()
            # And clean up later
            #atexit.register(cleanup, temp_dir)

        # Make paths absolute paths
        temp_dir = os.path.abspath(temp_dir)
        output_dir = os.path.abspath(output_dir)
        input_folders = [os.path.abspath(input_folder) for input_folder in input_folders]

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

        # Save current directory
        old_cwd = os.getcwd()
        os.chdir(temp_dir)

        # Initial values
        new_dt = 10000000.0
        new_samples = 0

        # Pre-processing, find lowest dt among all input timeseries
        for site in site_list:
            for input_folder, label in zip(input_folders, labels):
                acc_file = find_acc_file(input_folder, site.scode, label)
                input_acc_file = os.path.join(input_folder, acc_file)
                # Read dt and keep minimum value
                file_dt = file_utilities.read_bbp_dt(input_acc_file)
                new_dt = min(new_dt, file_dt)
                
        print("==> Target DT set to %.4f" % (new_dt))

        all_rs_array = [[] for _ in input_folders]

        print("==> Pre-processing step 1: matching dt...")
        for site in site_list:
            for input_folder, label, rs_array in zip(input_folders,
                                                     labels,
                                                     all_rs_array):
                acc_file = find_acc_file(input_folder, site.scode, label)
 
                shutil.copy2(os.path.join(input_folder, acc_file),
                             os.path.join(temp_dir, acc_file))

                input_acc_file = os.path.join(input_folder, acc_file)

                # Read dt
                file_dt = file_utilities.read_bbp_dt(input_acc_file)
                # Keep track of largest dt for this station
                if file_dt == new_dt:
                    input_rs_acc_file = input_acc_file
                else:
                    # Resample if needed
                    input_rs_acc_file = os.path.join(temp_dir,
                                                     "rs-%s" %
                                                     (acc_file))
                    resample_bbp_file(input_acc_file,
                                  input_rs_acc_file,
                                  site.scode,
                                  file_dt, new_dt,
                                  temp_dir,
                                  logfile=logfile)
                rs_array.append(input_rs_acc_file)

        print("==> Pre-processing step 2: matching samples...")
        for rs_array in all_rs_array:
            for site, input_rs_acc_file in zip(site_list, rs_array):
                # Read samples
                station_samples = file_utilities.read_bbp_samples(input_rs_acc_file)
                new_samples = max(new_samples, station_samples)

        print("==> Target samples set to %d" % (new_samples))

        for rs_array, input_folder, label in zip(all_rs_array,
                                                 input_folders,
                                                 labels):
            for site, input_rs_acc_file in zip (site_list, rs_array):
                acc_file = find_acc_file(input_folder, site.scode, label)

                print("==> Processing %s - station: %s" % (label, site.scode))

                # Make sure both files have equal number of data points
                acc_samples = file_utilities.read_bbp_samples(input_rs_acc_file)

                if acc_samples == new_samples:
                    input_final_acc_file = input_rs_acc_file
                else:
                    input_final_acc_file = os.path.join(temp_dir,
                                                        "pad-%s" %
                                                        (acc_file))
                    extra_points = new_samples - acc_samples
                    print("=====> Adding %d extra points to %s" %
                          (extra_points, os.path.basename(input_rs_acc_file)))
                    file_utilities.add_extra_points(input_rs_acc_file,
                                                    input_final_acc_file,
                                                    extra_points)

                # Compute seismogram's FAS
                output_prefix = "%s.%s" % (label, site.scode)
                print("=====> Computing FAS for seismogram... ", end="", flush=True)
                t1 = time.time()
                compute_fas(temp_dir, output_dir,
                            os.path.basename(input_final_acc_file),
                            site.scode, output_prefix=output_prefix,
                            logfile=logfile)
                t2 = time.time()
                print("%10.2f s" % (t2 - t1))
                
        print("processing done!")

        # All done, restore working directory
        os.chdir(old_cwd)

if __name__ == '__main__':
    ME = FAS()
    ME.run()
    sys.exit(0)
