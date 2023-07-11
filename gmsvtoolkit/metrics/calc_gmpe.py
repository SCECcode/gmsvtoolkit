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

Broadband Platform script to generate GMPE data for stations in the
station list.
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import argparse

# Import GMSVToolkit modules
from models import gmpe_config
from core.station_list import StationList
from utils.src_utilities import parse_src_file

# Import Pynga and its utilities
from models.pynga import utils as putils

class CalculateGMPE(object):
    """
    This class implements the methods used to generate the GMPE data
    for a list of stations.
    """

    def __init__(self):
        """
        Initialize class variables
        """
        self.src_keys = None
        self.gmpe_groups = [item for item in gmpe_config.GMPES]

    def calculate_gmpe(self, gmpe_group_name, station, output_file):
        """
        This function calculates the gmpe for a station and writes the
        output in the output_file
        """
        gmpe_group = gmpe_config.GMPES[gmpe_group_name]
        src_keys = self.src_keys
        origin = (src_keys['lon_top_center'], src_keys['lat_top_center'])
        dims = (src_keys['fault_length'], src_keys['dlen'],
                src_keys['fault_width'], src_keys['dwid'],
                src_keys['depth_to_top'])
        mech = (src_keys['strike'], src_keys['dip'], src_keys['rake'])

        # Station location
        site_geom = [float(station.lon), float(station.lat), 0.0]
        (fault_trace1, upper_seis_depth,
         lower_seis_depth, ave_dip,
         dummy1, dummy2) = putils.FaultTraceGen(origin, dims, mech)
        rjb, rrup, rx = putils.DistanceToSimpleFaultSurface(site_geom,
                                                            fault_trace1,
                                                            upper_seis_depth,
                                                            lower_seis_depth,
                                                            ave_dip)

        # Pick Vs30 from station list
        vs30 = station.vs30

        z10 = None # Let PyNGA calculate it
        z25 = None # Let PyNGA calculate it

        # Compute PSA for this station
        station_median = []
        for period in gmpe_group["periods"]:
            period_medians = []
            for nga_model in gmpe_group["models"]:
                median = gmpe_config.calculate_gmpe(gmpe_group_name,
                                                    nga_model,
                                                    src_keys['magnitude'],
                                                    rjb, vs30,
                                                    period,
                                                    rake=src_keys['rake'],
                                                    dip=src_keys['dip'],
                                                    W=src_keys['fault_width'],
                                                    Ztor=src_keys['depth_to_top'],
                                                    Rrup=rrup, Rx=rx,
                                                    Z10=z10, Z25=z25)
                period_medians.append(median)
            station_median.append((period, period_medians))

        # Create label
        file_label = ""
        for nga_model in gmpe_group["models"]:
            file_label = "%s %s" % (file_label, nga_model)
        # Output data to file
        outfile = open(output_file, 'w')
        outfile.write("#station: %s\n" % (station.scode))
        outfile.write("#period%s\n" % (file_label))
        for item in station_median:
            period = item[0]
            vals = item[1]
            out_str = "%.4f" % (period)
            for method in vals:
                out_str = out_str + "\t%.6f" % (method)
            outfile.write("%s\n" % (out_str))
        outfile.close()

        # Return list
        return station_median

    def parse_arguments(self):
        """
        This function takes care of parsing the command-line arguments and
        asking the user for any missing parameters that we need
        """
        parser = argparse.ArgumentParser(description="Calculate GMPEs for "
                                         " a set of stations.")
        parser.add_argument("--output-dir", dest="output_dir",
                            help="output directory")
        parser.add_argument("--gmpe-group", dest="gmpe_group", required=True,
                            help="GMPE group %s" % (self.gmpe_groups))
        parser.add_argument("-o", "--output", "--output-file",
                            dest="output_file",
                            help="output rd100 file")
        parser.add_argument("--station-list", "-s", dest="station_list", required=True,
                            help="station list for batch processing")
        parser.add_argument("--src-file", "--src", dest="src_file", required=True,
                            help="source description file (SRC file)")
        args = parser.parse_args()

        return args

    def run(self):
        """
        Calculate GMPEs for a list of stations
        """
        # Parse command-line options
        args = self.parse_arguments()

        station_file = os.path.abspath(args.station_list)
        src_file = os.path.abspath(args.src_file)
        gmpe_group = args.gmpe_group.lower()
        if gmpe_group not in self.gmpe_groups:
            print("[ERROR]: gmpe-group must be %s" % (self.gmpe_groups))
            sys.exit(1)

        # Set output directory
        if args.output_dir is None:
            output_dir = "."
        else:
            output_dir = args.output_dir

        self.run_station_mode(station_file, src_file,
                              gmpe_group, output_dir)

    def run_station_mode(self, station_file, src_file,
                         gmpe_group, output_dir):
        """
        Calculates GMPEs for a list of stations
        """
        # Parse source file
        self.src_keys = parse_src_file(src_file)

        # Now parse station list
        stations = StationList(station_file)
        station_list = stations.get_station_list()

        # Loop through stations
        for station in station_list:
            station_name = station.scode

            print("==> Calculating GMPE for station: %s" % (station_name))
            output_file = os.path.join(output_dir, "%s-gmpe.ri50" % (station_name))
            self.calculate_gmpe(gmpe_group, station, output_file)
            
if __name__ == '__main__':
    print("Running module: %s" % (os.path.basename(sys.argv[0])))
    ME = CalculateGMPE()
    ME.run()
