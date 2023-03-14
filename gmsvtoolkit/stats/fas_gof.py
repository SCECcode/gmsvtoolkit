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

Generates FAS GoF plot
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import glob
import numpy as np
import atexit
import shutil
import argparse
import tempfile

# Import GMSVToolkit modules
from core import gmsvtoolkit_config
from core.station_list import StationList
from utils.src_utilities import parse_src_file
from utils.file_utilities import read_bbp_dt
from utils import os_utilities
from stats import resid2uncer

# Import Pynga and its utilities
from models.pynga import utils as putils

# Some constants used in the code
COMPS_FAS = ["fash1", "fash2", "seas"]
MIN_CDST = 0
MAX_CDST = 25

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

def find_smc_file(input_dir, station_name, prefix):
    """
    Looks into input_dir for a smc8 fas file for station station_name
    """
    # Find input file
    input_list = glob.glob("%s%s*%s.%s.smc8.smooth.fs.col" %
                           (input_dir, os.sep, prefix, station_name))
    if not len(input_list):
        print("[ERROR]: Can't find input file for station %s" % (station_name))
        sys.exit(1)
    if len(input_list) > 1:
        # Found more than one file
        print("[ERROR]: Multiple smc8 files found for station %s: " % (station_name))
        print(input_list)
        print("[ERROR]: Please try using --sim-prefix/--obs-prefix options to match a single file!")
        sys.exit(1)

    input_file = os.path.basename(input_list[0])

    return input_file

def rewrite_fas_eas_file(fas_input_file, fas_output_file):
    """
    Reads the fas_input_file, and writes its
    content back without the eas column so that
    it can be used by the GoF tools
    """
    input_file = open(fas_input_file, 'r')
    output_file = open(fas_output_file, 'w')
    output_file.write("# Freq(Hz)\t FAS H1 (cm/s)\t FAS H2 (cm/s)\t "
                   "Smoothed EAS (cm/s)\n")
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
        output_file.write("%2.7E\t%2.7E\t%2.7E\t%2.7E\n" %
                          (pieces[0], pieces[1], pieces[2], pieces[4]))

    input_file.close()
    output_file.close()

class FASGoF(object):
    """
    This class generates GOF plots for the FAS data
    """

    def __init__(self, comp_label=None, max_cutoff=MAX_CDST):
        """
        Initialize class instance variables
        """
        self.comp_label = comp_label
        self.max_cutoff = max_cutoff

    def summarize_fas(self, site_list, a_outdir):
        """
        Summarizes all FAS data and creates the FAS GOF plot
        """
        fas_residfile = os.path.join(a_outdir, "%s.fas-resid.txt" %
                                     (self.comp_label))
        for comp in COMPS_FAS:
            # Build paths and check lengths
            fileroot = os.path.join(a_outdir, "%s_r%d-%d-fas-%s" %
                                    (self.comp_label, MIN_CDST,
                                     self.max_cutoff, comp))
            os_utilities.check_path_lengths([fas_residfile, fileroot],
                                            os_utilities.GP_MAX_FILENAME)
            resid2uncer.resid2uncer_py(fas_residfile, fileroot, comp,
                                        len(site_list), MIN_CDST,
                                        self.max_cutoff)

    def parse_arguments(self):
        """
        This function takes care of parsing the command-line arguments and
        asking the user for any missing parameters that we need
        """
        parser = argparse.ArgumentParser(description="Generates FAS comparison "
                                         " files needed to create FAS GoF.")
        parser.add_argument("--sim-dir", dest="sim_dir",
                            help="input directory with FAS .smc8 files")
        parser.add_argument("--obs-dir", dest="obs_dir",
                            help="input directory with FAS .smc8 files")
        parser.add_argument("--output-dir", dest="output_dir",
                            help="output directory")
        parser.add_argument("--src-file", "--src", dest="src_file",
                            help="source description file (SRC file)")
        parser.add_argument("--station-list", "-s", dest="station_list",
                            help="station list")
        parser.add_argument("--comp-label", dest="comp_label",
                            help="comparison label used for the output file prefix")
        parser.add_argument("--max-cutoff", dest="max_cutoff", type=float, default=1000.0,
                            help="select max cutoff distance (km) for the comparison")
        parser.add_argument("--acc-dir", dest="acc_dir",
                            help="input directory with acc seismograms")
        parser.add_argument("--acc-prefix", dest="acc_prefix", default="",
                            help="prefix for acc seismograms (default is no prefix)")
        parser.add_argument("--acc-suffix", dest="acc_suffix", default=".acc.bbp",
                            help="suffix for acc seismograms (default .acc.bbp)")
        parser.add_argument("--obs-prefix", dest="obs_prefix", default="",
                            help="prefix for observation smc8 FAS files")
        parser.add_argument("--sim-prefix", dest="sim_prefix", default="",
                            help="prefix for simulation smc8 FAS files")
        args = parser.parse_args()

        return args

    def run(self):
        """
        Parse parameters and then run FASGoF module
        """
        # Parse command-line options
        args = self.parse_arguments()

        # Check input parameters
        if not args.src_file:
            print("[ERROR]: Please specify source description file!")
            sys.exit(1)
        src_file = os.path.abspath(args.src_file)
        if not args.station_list:
            print("[ERROR]: Please specify station list!")
            sys.exit(1)
        station_list = os.path.abspath(args.station_list)
        if not args.sim_dir:
            print("[ERROR]: Please specify simulation folder!")
            sys.exit(1)
        if not args.obs_dir:
            print("[ERROR]: Please specify observation folder!")
            sys.exit(1)
        output_dir = ""
        if args.output_dir:
            output_dir = args.output_dir
        output_dir = os.path.abspath(output_dir)
        acc_dir = None
        if args.acc_dir:
            acc_dir = args.acc_dir
        if not args.comp_label:
            print("[ERROR]: Please specify comp-label prefix!")
            sys,exit(1)
        self.comp_label = args.comp_label

        # Allow user to replace default max_cutoff value
        self.max_cutoff = args.max_cutoff

        # Run FAS GoF
        self.run_fas_gof(station_list, src_file,
                         args.obs_dir, args.sim_dir, output_dir,
                         acc_dir=acc_dir, acc_prefix=args.acc_prefix,
                         acc_suffix=args.acc_suffix,
                         sim_prefix=args.sim_prefix,
                         obs_prefix=args.obs_prefix)

    def run_fas_gof(self, a_station_list, a_src_file,
                    obs_dir, sims_dir, output_dir,
                    acc_dir=None, acc_prefix="",
                    acc_suffix=".acc.bbp",
                    sim_prefix="", obs_prefix=""):
        """
        Generates data files used to plot FAS GoF
        """
        # Initialize basic variables
        install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()

        # Create temp folder
        temp_dir = tempfile.mkdtemp()
        # And clean up later
        atexit.register(cleanup, temp_dir)
        
        # Parse input files
        sta_base = os.path.basename(os.path.splitext(a_station_list)[0])
        src_keys = parse_src_file(a_src_file)
        stations = StationList(a_station_list)
        station_list = stations.get_station_list()
        print_header_fas = 1

        # Select output file
        fas_resid_output = os.path.join(output_dir, "%s.fas-resid.txt" %
                                        (self.comp_label))
        if os.path.exists(fas_resid_output):
            os.remove(fas_resid_output)

        # Loop through stations
        for station in station_list:
            station_name = station.scode
            station_lon = float(station.lon)
            station_lat = float(station.lat)

            # Calculate Rrup
            origin = (src_keys['lon_top_center'],
                      src_keys['lat_top_center'])
            dims = (src_keys['fault_length'], src_keys['dlen'],
                    src_keys['fault_width'], src_keys['dwid'],
                    src_keys['depth_to_top'])
            mech = (src_keys['strike'], src_keys['dip'],
                    src_keys['rake'])

            site_geom = [float(station.lon), float(station.lat), 0.0]
            (fault_trace1, up_seis_depth,
             low_seis_depth, ave_dip,
             dummy1, dummy2) = putils.FaultTraceGen(origin, dims, mech)
            _, rrup, _ = putils.DistanceToSimpleFaultSurface(site_geom,
                                                             fault_trace1,
                                                             up_seis_depth,
                                                             low_seis_depth,
                                                             ave_dip)

            if acc_dir:
                # Pick up DT from simulated file
                acc_file = "%s%s%s" % (acc_prefix, station_name, acc_suffix)
                input_acc_file = os.path.join(acc_dir, acc_file)
                syn_dt = read_bbp_dt(input_acc_file)
                max_syn_freq = 1.0 / (syn_dt * 2)
                if max_syn_freq < station.high_freq_corner:
                    print("station %s: freq: %f, syn_dt: %f" %
                          (station_name, station.high_freq_corner, max_syn_freq))
            else:
                # Just use frequency from station list
                max_syn_freq = station.high_freq_corner    

            # Create path names and check if their sizes are within bounds
            sim_file_in = find_smc_file(sims_dir, station_name, sim_prefix)
            sim_file_in = os.path.join(sims_dir, sim_file_in)
            obs_file_in = find_smc_file(obs_dir, station_name, obs_prefix)
            obs_file_in = os.path.join(obs_dir, obs_file_in)
            # Temp files
            sim_file_tmp = os.path.join(temp_dir, "tmp.fas.sim.txt")
            obs_file_tmp = os.path.join(temp_dir, "tmp.fas.obs.txt")
            rewrite_fas_eas_file(sim_file_in, sim_file_tmp)
            rewrite_fas_eas_file(obs_file_in, obs_file_tmp)
            outfile = os.path.join(output_dir, "%s.fas-resid.txt" %
                                   (self.comp_label))
            os_utilities.check_path_lengths([obs_file_tmp, sim_file_tmp, outfile],
                                            os_utilities.GP_MAX_FILENAME)

            gen_resid_bin = os.path.join(install.GP_BIN_DIR,
                                         "gen_resid_tbl_3comp")
            cmd = ("%s bbp_format=1 " % (gen_resid_bin) +
                   "datafile1=%s simfile1=%s " % (obs_file_tmp,
                                                  sim_file_tmp) +
                   "comp1=fash1 comp2=fash2 comp3=seas " +
                   "eqname=%s mag=%s stat=%s lon=%.4f lat=%.4f " %
                   (self.comp_label, src_keys['magnitude'],
                    station_name, station_lon, station_lat) +
                   "vs30=%d cd=%.2f " % (int(station.vs30), rrup) +
                   "flo=%f fhi=%f " % (1.0 / min(float(station.high_freq_corner),
                                                 max_syn_freq),
                                       1.0 / float(station.low_freq_corner)) +
                   "print_header=%d >> %s 2>> /dev/null" %
                   (print_header_fas, outfile))
            os_utilities.runprog(cmd, abort_on_error=True, print_cmd=False)

            # Only need to print header the first time
            if print_header_fas == 1:
                print_header_fas = 0

        # Finished per station processing, now summarize and plot the data
        if os.path.exists(fas_resid_output):
            self.summarize_fas(station_list, output_dir)

if __name__ == "__main__":
    print("Running module: %s" % (os.path.basename(sys.argv[0])))
    ME = FASGoF()
    ME.run()
