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

This module plots FAS
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import matplotlib as mpl
mpl.use('AGG')
import glob
import pylab
import argparse

# Import GMSVToolkit modules
from plots import plot_config
from core.station_list import StationList
from utils import file_utilities

def plot_fas(freqs, h1_data, h2_data, eas_smoothed_data,
             fas_plot, station, plot_title=None):
    """
    Create a plot of both FAS components
    """
    # Set plot dims
    pylab.gcf().set_size_inches(11, 8.5)
    pylab.gcf().clf()

    # Adjust title y-position
    if plot_title is None:
        plot_title = "Station : %s" % (station)
    t = pylab.title(plot_title, size=12)

    pylab.plot(freqs, h1_data, 'b', lw=0.75, label="H1")
    pylab.plot(freqs, h2_data, 'r', lw=0.75, label="H2")
    pylab.plot(freqs, eas_smoothed_data, 'k', lw=1.25, label="Smoothed EAS")
    pylab.legend(loc='upper right')
    pylab.xscale('log')
    pylab.yscale('log')
    pylab.ylabel('Fourier Amplitude (cm/s)')
    pylab.xlabel('Frequency (Hz)')
    pylab.axis([0.01, 100, 0.001, 1000])
    pylab.grid(True)
    pylab.grid(b=True, which='major', linestyle='-', color='lightgray')
    pylab.grid(b=True, which='minor', linewidth=0.5, color='gray')

    # Save plot
    pylab.savefig(fas_plot, format="png",
                  transparent=False, dpi=plot_config.dpi)
    pylab.close()

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    parser = argparse.ArgumentParser(description="Plot FAS")
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
    parser.add_argument("--input-file", dest="input_file",
                        help="input file")
    parser.add_argument("--comp-label", dest="comp_label",
                        help="comparison label used for the output file prefix")
    parser.add_argument('input_dirs', nargs='*')
    args = parser.parse_args()

    return args

def run():
    """
    Run FAS comparison plotting code
    """

    # Parse command-line options
    args = parse_arguments()

    # Look at paths
    input_dir = ""
    output_dir = ""
    plot_title = None
    comp_label = None
    input_dirs = args.input_dirs
    if args.output_dir:
        output_dir = args.output_dir
    if args.input_dir:
        input_dir = args.input_dir
    if args.plot_title:
        plot_title = args.plot_title
    if args.comp_label:
        comp_label = args.comp_label

    if args.station_id:
        # Single comparison mode
        if not args.input_file:
            print("[ERROR]: Must specify input_file!")
            sys.exit(1)
        if args.output_file:
            output_file = args.output_file
        else:
            if args.comp_label:
                output_file = "%s.%s.fas.png" % (comp_label,
                                             args.station_id)
            else:
                output_file = "%s.fas.png" % (args.station_id)
        output_file = os.path.join(output_dir, output_file)
        input_file = os.path.join(input_dir, args.input_file)
        run_single_station(input_file, output_file,
                           args.station_id, plot_title=plot_title)
    elif args.batch_file:
        # Batch file mode
        batch_file = os.path.abspath(args.batch_file)
        run_batch_mode(batch_file, input_dir,
                       output_dir, comp_label)
    elif args.station_list:
        # Run through the station list
        station_list = os.path.abspath(args.station_list)
        run_station_mode(station_list, input_dir,
                         output_dir, comp_label)
    else:
        print("[ERROR]: Must include station_id, batch_file, or station_list!")
        sys.exit(1)

def run_single_station(input_file, output_file,
                       station, plot_title=None):

    print("[PLOTFAS]: Generating FAS plot for station %s" % (station))
    # Read data
    (freqs, fas_h1,
     fas_h2, eas, s_eas) = file_utilities.read_fas_eas_file(input_file)

    # Create comparison plot
    plot_fas(freqs, fas_h1, fas_h2, s_eas,
             output_file, station, plot_title=plot_title)

def run_batch_mode(batch_file, input_dir,
                   output_dir, comp_label=None):
    """
    Generated FAS comparison plots for stations in a batch file
    """
    # Open batch file
    input_list = open(batch_file, 'r')
    for line in input_list:
        line = line.strip()
        if not line:
            continue

        station_name = line

        run_directory_mode(station_name, input_dir,
                           output_dir, comp_label)

    input_list.close()

def run_station_mode(station_file, input_dir,
                     output_dir, comp_label=None):
    """
    Generates FAS plots for stations in a station list
    """
    stations = StationList(station_file)
    station_list = stations.get_station_list()

    # Loop through stations
    for station in station_list:
        station_name = station.scode

        run_directory_mode(station_name, input_dir,
                           output_dir, comp_label)

def run_directory_mode(station_name, input_dir,
                       output_dir, comp_label=None):
    """
    Used by both station_mode and batch_mode, finds files matching
    the station name and generates comparison plot
    """
    # Fine input file
    input_list = glob.glob("%s%s*%s.smc8.smooth.fs.col" %
                           (input_dir, os.sep, station_name))
    if len(input_list) != 1:
        print("[ERROR]: Can't find input file for station %s" % (station_name))
        sys.exit(1)
    input_file = input_list[0]

    # Set up output file
    if comp_label:
        output_file = "%s.%s.fas.png" % (comp_label,
                                         station_name)
    else:
        output_file = "%s.fas.png" % (station_name)
    output_file = os.path.join(output_dir, output_file)

    run_single_station(input_file, output_file,
                       station_name)

if __name__ == '__main__':
    run()
