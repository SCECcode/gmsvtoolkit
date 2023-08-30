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

This module plots the FAS comparison for two smc8 files.
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

def plot_fas_comparison(station, input_file1, input_file2, label1, label2,
                        outfile, lfreq=None, hfreq=None, plot_title=None):
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
    (input1_freqs, input1_fas_h1,
     input1_fas_h2, input1_eas,
     input1_s_eas) = file_utilities.read_fas_eas_file(input_file1)
    (input2_freqs, input2_fas_h1,
     input2_fas_h2, input2_eas,
     input2_s_eas) = file_utilities.read_fas_eas_file(input_file2)

    # Start plot
    pylab.clf()

    # Figure out limits for x and y axis
    min_x = min([min((input1_freqs)), min(input2_freqs)])
    max_x = max([max((input1_freqs)), max(input2_freqs)])
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
    pylab.ylabel("Fourier Amplitude")
    pylab.axis([0.01, 100, 0.001, 1000])
    pylab.grid(True)
    pylab.grid(which='major', linestyle='-', color='lightgray')
    #pylab.grid(b=True, which='minor', linewidth=0.5, color='gray')
    if lfreq is not None:
        pylab.vlines(lfreq, 0.001, 1000,
                     color='violet', linestyles='--')
    if hfreq is not None:
        pylab.vlines(hfreq, 0.001, 1000,
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
    pylab.ylabel("Fourier Amplitude")
    pylab.axis([0.01, 100, 0.001, 1000])
    pylab.grid(True)
    pylab.grid(which='major', linestyle='-', color='lightgray')
    if lfreq is not None:
        pylab.vlines(lfreq, 0.001, 1000,
                     color='violet', linestyles='--')
    if hfreq is not None:
        pylab.vlines(hfreq, 0.001, 1000,
                     color='r', linestyles='--')
    pylab.legend(prop=mpl.font_manager.FontProperties(size=8))

    # Third plot
    ax3 = pylab.subplot(133)
    ax3.set_title('Smoothed EAS', fontsize='small')
    pylab.plot(input2_freqs, input2_s_eas, label=str(label2),
               linewidth=0.5, color='k')
    pylab.plot(input1_freqs, input1_s_eas, label=str(label1),
               linewidth=0.5, color='r')
    pylab.xscale('log')
    pylab.yscale('log')
    pylab.xlabel('Frequency (Hz)')
    pylab.ylabel("Fourier Amplitude")
    pylab.axis([0.01, 100, 0.001, 1000])
    pylab.grid(True)
    pylab.grid(which='major', linestyle='-', color='lightgray')
    if lfreq is not None:
        pylab.vlines(lfreq, 0.001, 1000,
                     color='violet', linestyles='--')
    if hfreq is not None:
        pylab.vlines(hfreq, 0.001, 1000,
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
    parser.add_argument("--input-file1", dest="input_file1",
                        help="input file 1")
    parser.add_argument("--input-file2", dest="input_file2",
                        help="input file 2")
    parser.add_argument("--labels", "-l", dest="labels",
                        help="comma-separated comparison labels")
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
    labels = args.labels
    if labels is not None:
        labels = [label.strip() for label in labels.split(",")]

    if args.station_id:
        # Single comparison mode
        if not args.input_file1 or not args.input_file2:
            print("[ERROR]: Must include both input_file1 and input_file2!")
            sys.exit(1)
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
        input_file1 = os.path.join(input_dir, args.input_file1)
        input_file2 = os.path.join(input_dir, args.input_file2)
        run_single_station(input_file1, input_file2,
                           labels[0], labels[1],
                           output_file, args.station_id,
                           lfreq=lfreq, hfreq=hfreq,
                           plot_title=plot_title)
    elif args.batch_file:
        # Batch file mode
        batch_file = os.path.abspath(args.batch_file)
        run_batch_mode(batch_file, args.input_dirs, labels,
                       output_dir, comp_label)
    elif args.station_list:
        # Run through the station list
        station_list = os.path.abspath(args.station_list)
        run_station_mode(station_list, input_dirs, labels,
                         output_dir, comp_label)
    else:
        print("[ERROR]: Must include station_id, batch_file, or station_list!")
        sys.exit(1)

def run_single_station(input_file1, input_file2,
                       label1, label2,
                       output_file, station,
                       lfreq=None, hfreq=None,
                       plot_title=None):
    
    print("[PLOTFASCOMPARISON]: Generating FAS comparison plot for station %s" % (station))
    # Create comparison plot
    plot_fas_comparison(station, input_file1, input_file2,
                        label1, label2, output_file,
                        lfreq=lfreq, hfreq=hfreq,
                        plot_title=plot_title)

def run_batch_mode(batch_file, input_dirs, labels,
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
        lfreq = None
        hfreq = None
            
        run_directory_mode(station_name, lfreq,
                           hfreq, input_dirs, labels,
                           output_dir, comp_label)

    input_list.close()

def run_station_mode(station_file, input_dirs, labels,
                     output_dir, comp_label=None):
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

        run_directory_mode(station_name, lfreq,
                           hfreq, input_dirs, labels,
                           output_dir, comp_label)

def run_directory_mode(station_name, lfreq, hfreq,
                       input_dirs, labels, output_dir,
                       comp_label=None):
    """
    Used by both station_mode and batch_mode, finds files matching
    the station name and generates comparison plot
    """
    # Make list of all input files
    input_files = []
    for input_dir, label in zip(input_dirs, labels):
        input_list = glob.glob("%s%s*%s.smc8.smooth.fs.col" %
                               (input_dir, os.sep, station_name))
        if len(input_list) != 1:
            # Try using the label to pick only one file
            input_list = glob.glob("%s%s%s*%s.smc8.smooth.fs.col" %
                                   (input_dir, os.sep, label, station_name))
            if len(input_list) != 1:
                print("[ERROR]: Can't find input file for station %s" % (station_name))
                sys.exit(1)

        input_files.append(input_list[0])
            
    # Set up output file
    if comp_label:
        output_file = "%s.%s.fas.comparison.png" % (comp_label,
                                                    station_name)
    else:
        output_file = "%s.fas.comparison.png" % (station_name)
    output_file = os.path.join(output_dir, output_file)

    run_single_station(input_files[0], input_files[1],
                       labels[0], labels[1],
                       output_file, station_name,
                       lfreq=lfreq, hfreq=hfreq)

if __name__ == '__main__':
    run()
