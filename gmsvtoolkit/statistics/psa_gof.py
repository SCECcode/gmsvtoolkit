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

This module contains functions to generate PSA GoF data files
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import glob
import argparse

# Import GMSV Toolkit functions
from core import gmsvtoolkit_config
from core.station_list import StationList
from utils.file_utilities import read_rdxx
from utils.src_utilities import parse_src_file
from utils import os_utilities

# Import Pynga and its utilities
from models.pynga import utils as putils

class PSAGoF(object):

    def __init__(self, mode=None, min_cdst=0, max_cutoff=None):
        self.mode = mode
        self.src_keys = None
        self.min_cdst = min_cdst
        self.max_cutoff = max_cutoff
        self.comp_label = None

    def parse_arguments(self):
        """
        This function takes care of parsing the command-line arguments and
        asking the user for any missing parameters that we need
        """
        parser = argparse.ArgumentParser(description="Generates PSA comparison "
                                         " files needed to create PSA GoF.")
        parser.add_argument("--sims-dir", dest="sims_dir",
                            help="input directory with simulation data")
        parser.add_argument("--obs-dir", dest="obs_dir",
                            help="input directory with observed data")
        parser.add_argument("--output-dir", dest="output_dir",
                            help="output directory")
        parser.add_argument("-o", "--output", "--output-file",
                            dest="output_file",
                            help="output rd100 file")
        parser.add_argument("--src-file", "--src", dest="src_file",
                            help="source description file (SRC file)")
        parser.add_argument("--station-list", "-s", dest="station_list",
                            help="station list")
        parser.add_argument("--labels", "-l", dest="labels",
                            help="comma-separated comparison labels")
        parser.add_argument("--comp-label", dest="comp_label",
                            help="comparison label used for the output file prefix")
        parser.add_argument("--rotd100", dest="rotd100", action="store_true",
                            help="select RotD100 comparison")
        parser.add_argument("--rotd50", dest="rotd50", action="store_true",
                            help="select RotD50 comparison (default)")
        parser.add_argument("--max-cutoff", dest="max_cutoff", type=float, default=1000.0,
                            help="select max cutoff distance (km) for the comparison")
        args = parser.parse_args()

        return args
        
    def run(self):
        """
        Parse parameters and then run PSAGoF module
        """
        # Parse command-line options
        args = self.parse_arguments()

        # Check input parameters
        if not args.src_file:
            print("[ERROR]: Please specify source description file!")
            sys.exit(1)
        if not args.station_list:
            print("[ERROR]: Please specify station list!")
            sys.exit(1)
        if not args.sims_dir:
            print("[ERROR]: Please specify simulation folder!")
            sys.exit(1)
        if not args.obs_dir:
            print("[ERROR]: Please specify observation folder!")
            sys.exit(1)
        if not args.output_dir:
            output_dir = ""
        else:
            output_dir = args.output_dir
        if not args.comp_label:
            print("[ERROR]: Please specify comp-label prefix!")
            sys,exit(1)
        self.comp_label = args.comp_label

        # Allow user to replace default max_cutoff value
        self.max_cutoff = args.max_cutoff

        if args.rotd100 and args.rotd50:
            print("[ERROR]: Please specify --rotd50 or --rotd100, not both!")
            sys.exit(1)

        # Set mode
        self.mode = "rotd50"
        if args.rotd100:
            self.mode = "rotd100"

        # Run PSA GoF module
        self.run_psa_gof(args.station_list, args.src_file,
                         args.obs_dir, args.sims_dir, output_dir)

    def run_psa_gof(self, a_station_list, a_src_file,
                    obs_dir, sims_dir, output_dir):
        """
        Parse parameters and then run PSAGoF module
        """
        install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()

        # Pick mode
        extension = "rd50"
        comps = ["psa5n", "psa5e", "rotd50"]
        if self.mode == "rotd100":
            extension = "rd100"
            comps = ["rotd50", "rotd100", "ratio"]

        # Parse input files
        station_base = os.path.basename(os.path.splitext(a_station_list)[0])
        self.src_keys = parse_src_file(a_src_file)
        stations = StationList(a_station_list)
        station_list = stations.get_station_list()
        print_header = 1

        # Select output file
        outfile = os.path.join(output_dir, "%s.%s-resid.txt" %
                               (self.comp_label, extension))
        if os.path.exists(outfile):
            os.remove(outfile)

        # Loop through stations
        for station in station_list:
            station_name = station.scode
            station_lon = float(station.lon)
            station_lat = float(station.lat)

            # Calculate Rrup
            origin = (self.src_keys['lon_top_center'],
                      self.src_keys['lat_top_center'])
            dims = (self.src_keys['fault_length'], self.src_keys['dlen'],
                    self.src_keys['fault_width'], self.src_keys['dwid'],
                    self.src_keys['depth_to_top'])
            mech = (self.src_keys['strike'], self.src_keys['dip'],
                    self.src_keys['rake'])

            site_geom = [station_lon, station_lat, 0.0]
            (fault_trace1, up_seis_depth,
             low_seis_depth, ave_dip,
             dummy1, dummy2) = putils.FaultTraceGen(origin, dims, mech)
            _, rrup, _ = putils.DistanceToSimpleFaultSurface(site_geom,
                                                             fault_trace1,
                                                             up_seis_depth,
                                                             low_seis_depth,
                                                             ave_dip)

            # Find input files for observed and simulated data
            obs_files = glob.glob("%s%s*%s*.%s" %
                                   (obs_dir, os.sep,
                                    station_name, extension))
            if len(obs_files) != 1:
                print("[ERROR]: Can't find observation file for station %s" % (station_name))
                sys.exit(1)
            obs_file = obs_files[0]

            sim_files = glob.glob("%s%s*%s*.%s" %
                                   (sims_dir, os.sep,
                                    station_name, extension))
            if len(sim_files) != 1:
                print("[ERROR]: Can't find simulation file for station %s" % (station_name))
                sys.exit(1)
            sim_file = sim_files[0]

            os_utilities.check_path_lengths([obs_file, sim_file, outfile],
                                            os_utilities.GP_MAX_FILENAME)

            # Calculate residuals
            cmd = ("%s bbp_format=1 " %
                   (os.path.join(install.GP_BIN_DIR, "gen_resid_tbl_3comp")) +
                   "datafile1=%s simfile1=%s " % (obs_file, sim_file) +
                   "comp1=%s comp2=%s comp3=%s " % (comps[0], comps[1], comps[2]) +
                   "eqname=%s mag=%s stat=%s lon=%.4f lat=%.4f " %
                   (self.comp_label.split("-")[0], self.src_keys['magnitude'],
                    station_name, station_lon, station_lat) +
                   "vs30=%d cd=%.2f " % (int(station.vs30), rrup) +
                   "flo=%f fhi=%f " % (float(station.low_freq_corner),
                                       float(station.high_freq_corner)) +
                   "print_header=%d >> %s 2>> /dev/null" %
                   (print_header, outfile))
            os_utilities.runprog(cmd, abort_on_error=True, print_cmd=False)

            # Only print header the first time
            if print_header == 1:
                print_header = 0

        # Now summarize the results
        for comp in comps:
            # Build paths and check lengths
            fileroot = os.path.join(output_dir, "%s_r%d-%d-%s-%s" %
                                    (self.comp_label, self.min_cdst,
                                     self.max_cutoff, extension, comp))
            os_utilities.check_path_lengths([outfile, fileroot],
                                            os_utilities.GP_MAX_FILENAME)

            cmd = ("%s " % (os.path.join(install.GP_BIN_DIR, "resid2uncer_varN")) +
                   "residfile=%s fileroot=%s " % (outfile, fileroot) +
                   "comp=%s nstat=%d nper=63 " % (comp, len(station_list)) +
                   "min_cdst=%d max_cdst=%d >> /dev/null 2>&1" %
                   (self.min_cdst, self.max_cutoff))
            os_utilities.runprog(cmd, abort_on_error=True, print_cmd=False)

if __name__ == '__main__':
    print("Running module: %s" % (os.path.basename(sys.argv[0])))
    ME = PSAGoF()
    ME.run()
