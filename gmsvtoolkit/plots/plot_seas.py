#!/usr/bin/env python3
"""
BSD 3-Clause License

Copyright (c) 2025, University of Southern California
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

This module plots FAS
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import numpy as np
import matplotlib as mpl
mpl.use('AGG')
import glob
import pylab
import argparse

# Import GMSVToolkit modules
from plots import plot_config
from core.station_list import StationList
from utils import file_utilities

def plot_seas(freqs_seas,eas_smoothed_data,
              seas_plot, station, units=None,
              plot_title=None):
    """
    Create a SEAS plot
    """
    # Set plot dims
    pylab.gcf().set_size_inches(11, 8.5)
    pylab.gcf().clf()

    # Adjust title y-position
    if plot_title is None:
        plot_title = "Station : %s" % (station)
    t = pylab.title(plot_title, size=12)

    # Adjust units
    if units == "g":
        y_label = "Fourier Amplitude (g)"
        plot_scale = [0.01, 100, 0.000000001, 0.0001]
    else:
        y_label = "Fourier Amplitude (cm/s/s)"
        plot_scale = [0.01, 100, 0.001, 1000]

    pylab.plot(freqs_seas, eas_smoothed_data, 'k',
               lw=1.25, label="Smoothed EAS")
    pylab.legend(loc='upper right')
    pylab.xscale('log')
    pylab.yscale('log')
    pylab.ylabel(y_label)
    pylab.xlabel('Frequency (Hz)')
    pylab.axis(plot_scale)
    pylab.grid(True)
    pylab.grid(which='major', linestyle='-', color='lightgray')
    pylab.grid(which='minor', linewidth=0.5, color='gray')

    # Save plot
    pylab.savefig(seas_plot, format="png",
                  transparent=False, dpi=plot_config.dpi)
    pylab.close()

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    parser = argparse.ArgumentParser(description="Plot SEAS")
    parser.add_argument("--input-dir", dest="input_dir",
                        help="input directory")
    parser.add_argument("--output-dir", dest="output_dir",
                        help="output directory")
    parser.add_argument("-o", "--output", "--output-file",
                        dest="output_file",
                        help="output plot file")
    parser.add_argument("--batch-file", "-b", dest="batch_file", 
                        help="file with list of timeseries to process")
    parser.add_argument("--station-id", "-id", dest="station_id",
                        help="station id")
    parser.add_argument("--station-list", "-s", dest="station_list",
                        help="station list for batch processing")
    parser.add_argument("--plot-title", "--title", dest="plot_title",
                        help="plot title")
    parser.add_argument("--input-seas-file", dest="input_seas_file",
                        help="input seas file")
    parser.add_argument("--comp-label", dest="comp_label",
                        help="comparison label used for the output file prefix")
    parser.add_argument("--units", dest="units",
                        help="units, g or cm/s/s (default)")
    args = parser.parse_args()

    return args

def run():
    """
    Run SEAS plotting code
    """

    # Parse command-line options
    args = parse_arguments()

    # Look at paths
    input_dir = ""
    output_dir = ""
    plot_title = None
    comp_label = None
    units = "cm/s/s"
    if args.output_dir:
        output_dir = args.output_dir
    if args.input_dir:
        input_dir = args.input_dir
    if args.plot_title:
        plot_title = args.plot_title
    if args.comp_label:
        comp_label = args.comp_label
    if args.units:
        units = args.units.lower()
    if units != "g" and units != "cm/s/s":
        print("[ERROR]: Units must be either g or cm/s/s!")
        sys.exit(1)
        
    if args.station_id:
        # Single comparison mode
        if args.input_seas_file:
            input_seas_file = os.path.join(input_dir, args.input_seas_file)
        else:
            print("[ERROR]: Must specify input_seas_file!")
            sys.exit(1)
        if args.output_file:
            output_file = args.output_file
        else:
            if args.comp_label:
                output_file = "%s.%s.seas.png" % (comp_label,
                                             args.station_id)
            else:
                output_file = "%s.seas.png" % (args.station_id)
        output_file = os.path.join(output_dir, output_file)
        run_single_station(args.station_id, output_file,
                           input_seas_file=input_seas_file,
                           plot_title=plot_title,
                           units=units)
    elif args.batch_file:
        # Batch file mode
        batch_file = os.path.abspath(args.batch_file)
        run_batch_mode(batch_file, input_dir,
                       output_dir, comp_label,
                       units)
    elif args.station_list:
        # Run through the station list
        station_list = os.path.abspath(args.station_list)
        run_station_list_mode(station_list, input_dir,
                              output_dir, comp_label,
                              units)
    else:
        print("[ERROR]: Must include station_id, batch_file, or station_list!")
        sys.exit(1)

def run_single_station(station, output_file,
                       input_seas_file=None,
                       plot_title=None,
                       units=None):

    print("[PLOTSEAS]: Generating SEAS plot for station %s" % (station))

    # Find input file(s) to load
    if input_seas_file is not None:
        (freqs_seas,
         s_eas) = file_utilities.read_seas_file(input_seas_file)
    else:
        print("[ERROR]: Must specify input_seas_file!")
        sys.exit(1)

    # Create comparison plot
    plot_seas(freqs_seas, s_eas,
              output_file, station, units=units,
              plot_title=plot_title)

def run_batch_mode(batch_file, input_dir,
                   output_dir, comp_label=None,
                   units=None):
    """
    Generated SEAS plots for stations in a batch file
    """
    # Open batch file
    input_list = open(batch_file, 'r')
    for line in input_list:
        line = line.strip()
        if not line:
            continue

        station_name = line

        run_directory_mode(station_name, input_dir,
                           output_dir, comp_label,
                           units)

    input_list.close()

def run_station_list_mode(station_file, input_dir,
                          output_dir, comp_label=None,
                          units=None):
    """
    Generates SEAS plots for stations in a station list
    """
    stations = StationList(station_file)
    station_list = stations.get_station_list()

    # Loop through stations
    for station in station_list:
        station_name = station.scode

        run_directory_mode(station_name, input_dir,
                           output_dir, comp_label,
                           units)

def run_directory_mode(station_name, input_dir,
                       output_dir, comp_label=None,
                       units=None):
    """
    Used by both station_mode and batch_mode, finds files matching
    the station name and generates comparison plot
    """
    # Find input file
    input_seas_file = None

    # First try combined file
    if comp_label is None:
        comp_label = ""
    input_list = glob.glob("%s%s%s*%s*" %
                           (input_dir, os.sep, comp_label, station_name))
    if len(input_list) == 1:
        # Found combined file, use it!
        input_seas_file = input_list[0]
    else:
        # Look for seas file
        input_list = glob.glob("%s%s%s*%s*seas*" %
                               (input_dir, os.sep, comp_label, station_name))
        if len(input_list) == 1:
            # Found seas file, use it!
            input_seas_file = input_list[0]
        else:
            # SEAS file not found, abort!
            print("[ERROR]: Can't find input file for station %s" %
                  (station_name))
            sys.exit(1)

    # Set up output file
    if comp_label:
        output_file = "%s.%s.seas.png" % (comp_label,
                                         station_name)
    else:
        output_file = "%s.seas.png" % (station_name)
    output_file = os.path.join(output_dir, output_file)

    run_single_station(station_name, output_file,
                       input_seas_file=input_seas_file,
                       units=units)

if __name__ == '__main__':
    run()
