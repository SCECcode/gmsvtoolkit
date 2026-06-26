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

This module plots the FAS comparison for two smc8 files.
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

def plot_fas_comparison(station, outfile, label1, label2,
                        input_fas_file1=None, input_seas_file1=None,
                        input_fas_file2=None, input_seas_file2=None,
                        lfreq=None, hfreq=None, plot_title=None,
                        units=None):
    """
    Plots the FAS comparison between simulated and observed seismograms
    """
    # Set up ticks to match matplotlib 1.x style
    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['ytick.direction'] = 'in'
    mpl.rcParams['lines.linewidth'] = 1.0
    mpl.rcParams['lines.dashed_pattern'] = [6, 6]
    mpl.rcParams['lines.dashdot_pattern'] = [3, 5, 1, 5]
    mpl.rcParams['lines.dotted_pattern'] = [1, 3]
    mpl.rcParams['lines.scale_dashes'] = False

    # Read data
    if (input_fas_file1 is not None and input_seas_file1 is not None and
          input_fas_file2 is not None and input_seas_file2 is not None):
        (input1_freqs, input1_fas_h1,
         input1_fas_h2,
         input1_eas) = file_utilities.read_eas_file(input_fas_file1)
        (freqs_seas1,
         input1_s_eas) = file_utilities.read_seas_file(input_seas_file1)
        (input2_freqs, input2_fas_h1,
         input2_fas_h2,
         input2_eas) = file_utilities.read_eas_file(input_fas_file2)
        (freqs_seas2,
         input2_s_eas) = file_utilities.read_seas_file(input_seas_file2)
        input1_fas_h1 = np.abs(input1_fas_h1)
        input1_fas_h2 = np.abs(input1_fas_h2)
        input2_fas_h1 = np.abs(input2_fas_h1)
        input2_fas_h2 = np.abs(input2_fas_h2)
    else:
        print("[ERROR]: Must specify "
              "input_eas_file[1-2] and input_seas_file[1-2]!")
        sys.exit(1)

    # Start plot
    pylab.clf()

    # Figure out limits for x and y axis
    min_x = min([min(input1_freqs),
                 min(input2_freqs),
                 min(freqs_seas1),
                 min(freqs_seas2)])
    max_x = max([max(input1_freqs),
                 max(input2_freqs),
                 max(freqs_seas1),
                 max(freqs_seas2)])
    min_horiz_y = min([min(input1_fas_h1), min(input2_fas_h1),
                       min(input1_fas_h2), min(input2_fas_h2)]) / 1.1
    max_horiz_y = 1.1 * max([max(input1_fas_h1), max(input2_fas_h1),
                             max(input1_fas_h2), max(input2_fas_h2)])
    min_vert_y = min([min(input1_fas_h1), min(input2_fas_h1),
                      min(input1_fas_h2), min(input2_fas_h2)]) / 1.1
    max_vert_y = 1.1 * max([max(input1_fas_h1), max(input2_fas_h1),
                            max(input1_fas_h2), max(input2_fas_h2)])

    if plot_title is None:
        plot_title = "FAS for station %s" % (station)
    pylab.suptitle(plot_title, size=14)

    pylab.subplots_adjust(top=0.85)
    pylab.subplots_adjust(bottom=0.15)
    pylab.subplots_adjust(left=0.075)
    pylab.subplots_adjust(right=0.975)
    pylab.subplots_adjust(hspace=0.3)
    pylab.subplots_adjust(wspace=0.3)

    # Adjust units
    if units == "g":
        y_label = "Fourier Amplitude (g)"
        scale_y_min = 0.000001
        scale_y_max = 1
    else:
        y_label = "Fourier Amplitude (cm/s/s)"
        scale_y_min = 0.001
        scale_y_max = 1000
    plot_scale = [0.01, 100, scale_y_min, scale_y_max]

    # First plot
    ax1 = pylab.subplot(131)
    ax1.set_title('FAS H1', fontsize='small')
    pylab.plot(input2_freqs, input2_fas_h1, label=str(label2),
               linewidth=0.5, color='k')
    pylab.plot(input1_freqs, input1_fas_h1, label=str(label1),
               linewidth=0.5, color='r')
    pylab.xscale('log')
    pylab.yscale('log')
    pylab.xlabel('Frequency (Hz)')
    pylab.ylabel(y_label)
    pylab.axis(plot_scale)
    pylab.grid(True)
    pylab.grid(which='major', linestyle='-', color='lightgray')
    #pylab.grid(b=True, which='minor', linewidth=0.5, color='gray')
    if lfreq is not None:
        pylab.vlines(lfreq, scale_y_min, scale_y_max,
                     color='violet', linestyles='--')
    if hfreq is not None:
        pylab.vlines(hfreq, scale_y_min, scale_y_max,
                     color='r', linestyles='--')
    pylab.legend(prop=mpl.font_manager.FontProperties(size=8))

    # Second plot
    ax2 = pylab.subplot(132)
    ax2.set_title('FAS H2', fontsize='small')
    pylab.plot(input2_freqs, input2_fas_h2, label=str(label2),
               linewidth=0.5, color='k')
    pylab.plot(input1_freqs, input1_fas_h2, label=str(label1),
               linewidth=0.5, color='r')
    pylab.xscale('log')
    pylab.yscale('log')
    pylab.xlabel('Frequency (Hz)')
    pylab.ylabel(y_label)
    pylab.axis(plot_scale)
    pylab.grid(True)
    pylab.grid(which='major', linestyle='-', color='lightgray')
    if lfreq is not None:
        pylab.vlines(lfreq, scale_y_min, scale_y_max,
                     color='violet', linestyles='--')
    if hfreq is not None:
        pylab.vlines(hfreq, scale_y_min, scale_y_max,
                     color='r', linestyles='--')
    pylab.legend(prop=mpl.font_manager.FontProperties(size=8))

    # Third plot
    ax3 = pylab.subplot(133)
    ax3.set_title('Smoothed EAS', fontsize='small')
    pylab.plot(freqs_seas2, input2_s_eas, label=str(label2),
               linewidth=0.5, color='k')
    pylab.plot(freqs_seas1, input1_s_eas, label=str(label1),
               linewidth=0.5, color='r')
    pylab.xscale('log')
    pylab.yscale('log')
    pylab.xlabel('Frequency (Hz)')
    pylab.ylabel(y_label)
    pylab.axis(plot_scale)
    pylab.grid(True)
    pylab.grid(which='major', linestyle='-', color='lightgray')
    if lfreq is not None:
        pylab.vlines(lfreq, scale_y_min, scale_y_max,
                     color='violet', linestyles='--')
    if hfreq is not None:
        pylab.vlines(hfreq, scale_y_min, scale_y_max,
                     color='r', linestyles='--')
    pylab.legend(prop=mpl.font_manager.FontProperties(size=8))

    pylab.gcf().set_size_inches(10, 4)
    pylab.savefig(outfile, format="png", dpi=plot_config.dpi)
    pylab.close()

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    parser = argparse.ArgumentParser(description="Plot FAS "
                                     " comparison of two files.")
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
                        help="station id for comparison")
    parser.add_argument("--station-list", "-s", dest="station_list",
                        help="station list for batch processing")
    parser.add_argument("--plot-title", "--title", dest="plot_title",
                        help="plot title")
    parser.add_argument("--low-freq", "--lf", dest="lfreq",
                        help="adds vertical line at this low frequency corner")
    parser.add_argument("--high-freq", "--hf", dest="hfreq",
                        help="adds vertical line at this high frequency corner")
    parser.add_argument("--input-fas-file1", dest="input_fas_file1",
                        help="input fas file 1")
    parser.add_argument("--input-seas-file1", dest="input_seas_file1",
                        help="input seas file 1")
    parser.add_argument("--input-fas-file2", dest="input_fas_file2",
                        help="input fas file 2")
    parser.add_argument("--input-seas-file2", dest="input_seas_file2",
                        help="input seas file 2")
    parser.add_argument("--labels", "-l", dest="labels",
                        help="comma-separated comparison labels")
    parser.add_argument("--comp-label", dest="comp_label",
                        help="comparison label used for the output file prefix")
    parser.add_argument("--units", dest="units",
                        help="units, g or cm/s/s (default)")
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
    units = "cm/s/s"
    input_dirs = args.input_dirs
    if args.output_dir:
        output_dir = args.output_dir
    if args.input_dir:
        input_dir = args.input_dir
    if args.plot_title:
        plot_title = args.plot_title
    if args.comp_label:
        comp_label = args.comp_label
    labels = args.labels
    if labels is not None:
        labels = [label.strip() for label in labels.split(",")]
    if args.units:
        units = args.units.lower()
    if units != "g" and units != "cm/s/s":
        print("[ERROR]: Units must be either g or cm/s/s!")
        sys.exit(1)

    if args.station_id:
        # Single station comparison mode, we need two sets of files,
        # each set includes a file with FAS/EAS and a second file
        # with the SEAS data

        # Look for set of input files (1)
        if args.input_fas_file1 and args.input_seas_file1:
            input_fas_file1 = os.path.join(input_dir,
                                           args.input_fas_file1)
            input_seas_file1 = os.path.join(input_dir,
                                            args.input_seas_file1)
        else:
            print("[ERROR]: Must specify "
                  "input_fas_file1 and input_seas_file1!")
            sys.exit(1)

        # Look for set of input files (2)
        if args.input_fas_file2 and args.input_seas_file2:
            input_fas_file2 = os.path.join(input_dir,
                                           args.input_fas_file2)
            input_seas_file2 = os.path.join(input_dir,
                                            args.input_seas_file2)
        else:
            print("[ERROR]: Must specify "
                  "input_fas_file2 and input_seas_file2!")
            sys.exit(1)
        # Look for labels
        if len(labels) != 2:
            print("[ERROR]: Must include two labels for the comparison plot!")
            sys.exit(1)
        if args.output_file:
            output_file = args.output_file
        else:
            if args.comp_label:
                output_file = "%s.%s.fas.comparison.png" % (comp_label,
                                                            args.station_id)
            else:
                output_file = "%s.fas.comparison.png" % (args.station_id)
        output_file = os.path.join(output_dir, output_file)
        lfreq = None
        hfreq = None
        if args.lfreq:
            lfreq = args.lfreq
        if args.hfreq:
            hfreq = args.hfreq
        plot_station_comparison(args.station_id, output_file,
                                labels[0], labels[1],
                                input_fas_file1=input_fas_file1,
                                input_seas_file1=input_seas_file1,
                                input_fas_file2=input_fas_file2,
                                input_seas_file2=input_seas_file2,
                                lfreq=lfreq, hfreq=hfreq,
                                plot_title=plot_title,
                                units=units)
    else:
        if len(input_dirs) < 1:
            print("[ERROR]: Please specify at least one input directory!")
            sys.exit(1)
        if labels is None:
            print("[ERROR]: Please specify as many labels as input directories!")
            sys,exit(1)
        if len(labels) != len(input_dirs):
            print("[ERROR]: Please specify as many labels as input directories!")
            sys,exit(1)
        if args.batch_file:
            # Batch file mode
            batch_file = os.path.abspath(args.batch_file)
            plot_batch_mode(batch_file, input_dirs, labels,
                            output_dir, comp_label,
                            units)
        elif args.station_list:
            # Run through the station list
            station_list = os.path.abspath(args.station_list)
            plot_station_list_mode(station_list, input_dirs, labels,
                                   output_dir, comp_label,
                                   units)
        else:
            print("[ERROR]: Must specify station_id, batch_file, or station_list!")
            sys.exit(1)

def plot_station_comparison(station, output_file,
                            label1, label2,
                            input_fas_file1=None,
                            input_seas_file1=None,
                            input_fas_file2=None,
                            input_seas_file2=None,
                            lfreq=None, hfreq=None,
                            plot_title=None,
                            units=None):

    print("[PLOTFASCOMPARISON]: Generating FAS comparison plot for station %s" % (station))
    # Create comparison plot
    plot_fas_comparison(station, output_file,
                        label1, label2,
                        input_fas_file1=input_fas_file1,
                        input_seas_file1=input_seas_file1,
                        input_fas_file2=input_fas_file2,
                        input_seas_file2=input_seas_file2,
                        lfreq=lfreq, hfreq=hfreq,
                        plot_title=plot_title,
                        units=units)

def plot_batch_mode(batch_file, input_dirs, labels,
                    output_dir, comp_label=None,
                    units=None):
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
        lfreq = None
        hfreq = None

        plot_directory_mode(station_name, lfreq,
                            hfreq, input_dirs, labels,
                            output_dir, comp_label,
                            units)

    input_list.close()

def plot_station_list_mode(station_file, input_dirs, labels,
                           output_dir, comp_label=None,
                           units=None):
    """
    Generates FAS comparison plots for stations in a station list
    """
    stations = StationList(station_file)
    station_list = stations.get_station_list()

    # Loop through stations
    for station in station_list:
        station_name = station.scode
        lfreq = station.low_freq_corner
        hfreq = station.high_freq_corner

        plot_directory_mode(station_name, lfreq,
                            hfreq, input_dirs, labels,
                            output_dir, comp_label,
                            units)

def plot_directory_mode(station_name, lfreq, hfreq,
                        input_dirs, labels, output_dir,
                        comp_label=None, units=None):
    """
    Used by both station_mode and batch_mode, finds files matching
    the station name and generates comparison plot
    """
    if comp_label is None:
        comp_label = ""

    # Make list of all input files
    input_fas_files = []
    input_seas_files = []

    for input_dir, label in zip(input_dirs, labels):
        input_list = glob.glob("%s%s*%s.eas.fs.col" %
                               (input_dir, os.sep, station_name))
        if len(input_list) == 1:
            # Found fas file!
            input_fas_files.append(input_list[0])
        else:
            # Add label to see if we can get one match
            input_list = glob.glob("%s%s%s*%s.eas.fs.col" %
                                   (input_dir, os.sep, label,
                                    station_name))
            if len(input_list) == 1:
                # Found fas file!
                input_fas_files.append(input_list[0])
            else:
                # EAS file not found, abort!
                print("[ERROR]: Can't find fas/eas input file for station %s" %
                      (station_name))
                sys.exit(1)
        # Now look for seas file
        input_list = glob.glob("%s%s*%s.seas.fs.col" %
                               (input_dir, os.sep, station_name))
        if len(input_list) == 1:
            # Found seas file, use it!
            input_seas_files.append(input_list[0])
        else:
            # Add label to see if we can get a single match
            input_list = glob.glob("%s%s%s*%s.seas.fs.col" %
                                   (input_dir, os.sep, label,
                                    station_name))
            if len(input_list) == 1:
                # Found seas file, use it!
                input_seas_files.append(input_list[0])
            else:
                # SEAS file not found, abort!
                print("[ERROR]: Can't find seas input file for station %s" %
                      (station_name))
                sys.exit(1)

    # Set up output file
    if comp_label:
        output_file = "%s.%s.fas.comparison.png" % (comp_label,
                                                    station_name)
    else:
        output_file = "%s.fas.comparison.png" % (station_name)
    output_file = os.path.join(output_dir, output_file)

    input_fas_file1 = input_fas_files[0]
    input_seas_file1 = input_seas_files[0]
    input_fas_file2 = input_fas_files[1]
    input_seas_file2 = input_seas_files[1]
    
    plot_station_comparison(station_name, output_file,
                            labels[0], labels[1],
                            input_fas_file1=input_fas_file1,
                            input_seas_file1=input_seas_file1,
                            input_fas_file2=input_fas_file2,
                            input_seas_file2=input_seas_file2,
                            lfreq=lfreq, hfreq=hfreq,
                            units=units)

if __name__ == '__main__':
    run()
