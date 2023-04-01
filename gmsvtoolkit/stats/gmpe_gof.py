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

Broadband Platform script to generate GMPE comparison plot
against ground observations for stations in the station list.
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import glob
import math
import argparse

# Import GMSV Toolkit modules
from core import gmsvtoolkit_config
from core.station_list import StationList
from core import exceptions
from utils import os_utilities
from utils.src_utilities import parse_src_file
from models import gmpe_config

# Import Pynga and its utilities
from models.pynga import utils as putils

def read_gmpe(input_file):
    """
    Reads the GMPE input_file and returns the periods along with the data
    """
    # Start empty
    gmpe_data = []
    gmpe_models = None

    gmpefile = open(input_file, 'r')
    for line in gmpefile:
        line = line.strip()
        if line.startswith('#period'):
            # This line contains the models we want to use
            gmpe_models = line.split(None, 1)[1]
            gmpe_models = gmpe_models.split()
        if line.startswith('#'):
            # Skip other comments
            continue
        values = line.split()
        values = [float(value) for value in values]
        # Extract period and rotd50 value
        period = values[0]
        medians = values[1:]
        gmpe_data.append((period, medians))
    gmpefile.close()

    # Make sure we parsed the line with the model names
    if gmpe_models is None:
        raise exceptions.ProcessingError("Cannot find GMPE models in %s" %
                                         (input_file))

    # Return the station median data
    return gmpe_data, gmpe_models

def read_rotd50(input_file):
    """
    Reads the RotD50 input_file and returns the periods with rotd50 data
    """
    # Start empty
    periods = []
    rd50 = []

    rd50file = open(input_file, 'r')
    for line in rd50file:
        line = line.strip()
        if line.startswith('#'):
            # Skip comments
            continue
        values = line.split()
        if len(values) != 4:
            # We are looking for 4 items, skip this line
            continue
        # Convert to floats
        values = [float(value) for value in values]
        # Extract period and rotd50 value
        periods.append(values[0])
        rd50.append(values[3])
    rd50file.close()

    return (periods, rd50)

class GMPEGoF(object):
    """
    This class implements the methods used to generate a comparison
    between GMPE data and a set of rotd50 results.
    """

    def __init__(self, comp_label=None,
                 run_prefix=None,
                 gmpe_group_name=None):
        """
        Initialize basic parameters
        """
        self.comp_label = comp_label
        self.run_prefix = run_prefix
        self.gmpe_group_name = gmpe_group_name
        self.src_keys = None
        self.gmpe_groups = [item for item in gmpe_config.GMPES]

    def calculate_residuals(self, station, gmpe_model, gmpe_data,
                            comp_periods, comp_data, resid_file,
                            print_headers):
        """
        This function calculates the residuals for the gmpe data
        versus the comp_data, and outputs the results to the resid_file
        """
        # Get gmpe periods
        gmpe_periods = [points[0] for points in gmpe_data]
        # Find common set
        period_set = sorted(list(set(gmpe_periods).intersection(comp_periods)))
        # Create new index arrays for the comparison set and gmpes
        gmpe_items = []
        comp_items = []
        for period in period_set:
            gmpe_items.append(gmpe_periods.index(period))
            comp_items.append(comp_periods.index(period))
        # Get gmpe data array
        gmpe_group = gmpe_config.GMPES[self.gmpe_group_name]
        index = gmpe_group["models"].index(gmpe_model)
        res1 = [points[1][index] for points in gmpe_data]

        # Update gmpe_data, and comp_data arrays
        gmpe_points = []
        comp_points = []
        for item1, item2 in zip(gmpe_items, comp_items):
            gmpe_points.append(res1[item1])
            comp_points.append(comp_data[item2])

        # Calculate residuals
        for idx in range(0, len(comp_points)):
            if gmpe_points[idx] != 0.0:
                gmpe_points[idx] = math.log(comp_points[idx]/gmpe_points[idx])
            else:
                gmpe_points[idx] = -99

        # Now, output to file
        if print_headers:
            outf = open(resid_file, 'w')
            outf.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %
                       ("EQ", "Mag", "stat", "lon", "lat", "stat_seq_no",
                        "Vs30", "close_dist", "Xcos", "Ycos", "T_min",
                        "T_max", "comp"))
            for period in period_set:
                outf.write("\t%.5e" % (period))
            outf.write("\n")
        else:
            outf = open(resid_file, 'a')

        # Calculate Rrup
        origin = (self.src_keys['lon_top_center'],
                  self.src_keys['lat_top_center'])
        dims = (self.src_keys['fault_length'], self.src_keys['dlen'],
                self.src_keys['fault_width'], self.src_keys['dwid'],
                self.src_keys['depth_to_top'])
        mech = (self.src_keys['strike'], self.src_keys['dip'],
                self.src_keys['rake'])

        site_geom = [float(station.lon), float(station.lat), 0.0]
        (fault_trace1, up_seis_depth,
         low_seis_depth, ave_dip,
         dummy1, dummy2) = putils.FaultTraceGen(origin, dims, mech)
        _, rrup, _ = putils.DistanceToSimpleFaultSurface(site_geom,
                                                         fault_trace1,
                                                         up_seis_depth,
                                                         low_seis_depth,
                                                         ave_dip)

        outf.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %
                   (self.comp_label, str(self.src_keys['magnitude']),
                    station.scode, station.lon, station.lat, "-999",
                    station.vs30, rrup, "-999", "-999"))

        if station.high_freq_corner > 0:
            outf.write("\t%.3f" %
                       (1.0 / station.high_freq_corner))
        else:
            outf.write("\t-99999.999")
        if station.low_freq_corner > 0:
            outf.write("\t%.3f" %
                       (1.0 / station.low_freq_corner))
        else:
            outf.write("\t-99999.999")
        outf.write("\t%s" % (gmpe_model.lower()))
        for value in gmpe_points:
            outf.write("\t%.5e" % (value))
        outf.write("\n")
        outf.close()

        return period_set

    def parse_arguments(self):
        """
        This function takes care of parsing the command-line arguments and
        asking the user for any missing parameters that we need
        """
        parser = argparse.ArgumentParser(description="Generates PSA comparison "
                                         " files needed to create GMPE GoF.")
        parser.add_argument("--gmpe-dir", dest="gmpe_dir", required=True,
                            help="input directory with GMPE data")
        parser.add_argument("--comp-dir", dest="comp_dir", required=True,
                            help="input directory with comparison files")
        parser.add_argument("--output-dir", dest="output_dir",
                            help="output directory")
        parser.add_argument("--src-file", "--src", dest="src_file", required=True,
                            help="source description file (SRC file)")
        parser.add_argument("--station-list", "-s", dest="station_list", required=True,
                            help="station list")
        parser.add_argument("--comp-label", dest="comp_label", required=True,
                            help="comparison label used for the output file prefix")
        parser.add_argument("--run-prefix", dest="run_prefix",
                            help="prefix to be added to the comparison files")
        parser.add_argument("--gmpe-group", dest="gmpe_group", required=True,
                            help="GMPE group %s" % (self.gmpe_groups))
        args = parser.parse_args()

        return args
    
    def run(self):
        """
        Calculate residuals between GMPE results and a second data set
        """
        # Parse command-line options
        args = self.parse_arguments()

        src_file = os.path.abspath(args.src_file)
        station_list = os.path.abspath(args.station_list)
        self.comp_label = args.comp_label
        self.gmpe_group_name = args.gmpe_group
        
        if not args.output_dir:
            output_dir = ""
        else:
            output_dir = args.output_dir
        if not args.run_prefix:
            self.run_prefix = None
        else:
            self.run_prefix = args.run_prefix
            
        gmpe_dir = os.path.abspath(args.gmpe_dir)
        comp_dir = os.path.abspath(args.comp_dir)

        # Run GMPE GoF module
        self.run_gmpe_gof(station_list, src_file,
                          gmpe_dir, comp_dir, output_dir)
        
    def run_gmpe_gof(self, station_file, src_file,
                     gmpe_dir, comp_dir, output_dir):
        """
        Calculates the residuals for the GMPE GoF
        """
        install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()

        # Parse input files
        self.src_keys = parse_src_file(src_file)
        stations = StationList(station_file)
        site_list = stations.get_station_list()
        print_headers = True

        # Go through each station, and print comparison headers for
        # the first station we process
        gmpe_models = []
        for station in site_list:
            station_name = station.scode

            # Find input files for this station
            gmpe_files = glob.glob("%s%s*%s*.ri50" %
                                   (gmpe_dir, os.sep,
                                   station_name))
            if len(gmpe_files) != 1:
                print("[ERROR]: Can't find GMPE file for station %s" % (station_name))
                sys.exit(1)
            gmpe_file = gmpe_files[0]

            comp_files = glob.glob("%s%s*%s*.rd50" %
                                   (comp_dir, os.sep,
                                   station_name))
            if len(comp_files) != 1:
                print("[ERROR]: Can't find comparison file for station %s" % (station_name))
                sys.exit(1)
            comp_file = comp_files[0]
            
            gmpe_data, gmpe_models[:] = read_gmpe(gmpe_file)
            comp_periods, comp_data = read_rotd50(comp_file)

            # Loop through the NGA methods
            for gmpe_model in gmpe_models:
                if self.run_prefix is not None:
                    resid_file = os.path.join(output_dir, "%s-%s.resid.txt" %
                                              (gmpe_model.lower(),
                                               str(self.run_prefix)))
                else:
                    resid_file = os.path.join(output_dir, "%s.resid.txt" %
                                              (gmpe_model.lower()))
                period_set = self.calculate_residuals(station, gmpe_model,
                                                      gmpe_data, comp_periods,
                                                      comp_data, resid_file,
                                                      print_headers)
            print_headers = False

        for gmpe_model in gmpe_models:
            # Now call the resid2uncer_varN program to summarize the
            # residuals and create the files needed for the GOF plot
            if self.run_prefix is not None:
                resid_file = os.path.join(output_dir, "%s-%s.resid.txt" %
                                          (gmpe_model.lower(),
                                           str(self.run_prefix)))
                fileroot = os.path.join(output_dir, "%s-GMPE-%s_r%d-all-rd50-%s" %
                                        (self.comp_label, str(self.run_prefix),
                                         0, gmpe_model.lower()))
            else:
                resid_file = os.path.join(output_dir, "%s.resid.txt" %
                                          (gmpe_model.lower()))
                fileroot = os.path.join(output_dir, "%s-GMPE_r%d-all-rd50-%s" %
                                        (self.comp_label, 0, gmpe_model.lower()))
            
            os_utilities.check_path_lengths([resid_file, fileroot],
                                            os_utilities.GP_MAX_FILENAME)
            cmd = ("%s " % os.path.join(install.GP_BIN_DIR,
                                        "resid2uncer_varN") +
                   "residfile=%s fileroot=%s " % (resid_file, fileroot) +
                   "comp=%s nstat=%d nper=%d " % (gmpe_model.lower(),
                                                  len(site_list),
                                                  len(period_set)) +
                   "min_cdst=%d >> /dev/null 2>&1" % (0))
            os_utilities.runprog(cmd, abort_on_error=True, print_cmd=False)

if __name__ == "__main__":
    print("Running module: %s" % (os.path.basename(sys.argv[0])))
    ME = GMPEGoF()
    ME.run()
