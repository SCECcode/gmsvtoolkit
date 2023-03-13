#!/usr/bin/env python
"""
BSD 3-Clause License

Copyright (c) 2022, University of Southern California
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

This module contains functions to generate RotD50 PSA comparison plots
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import glob
import matplotlib as mpl
mpl.use('AGG')
import pylab
import argparse

# Import plot config file
from plots import plot_config
from core.station_list import StationList
from utils.file_utilities import read_rdxx

def create_rdxx_plot(station_id, input_files, labels, output_file,
                     lfreq=None, hfreq=None, mode="rotd50",
                     quiet=False):
    """
    This function generates the a plot with three subplots showing
    psa5 and rotdxx comparisons for the input files
    """
    if not quiet:
        print("[PLOTRDXX]: Plotting comparison for station %s..." % (station_id))

    # Select plot titles
    if mode.lower() == "rotd50":
        plot_titles = ["Hor 1", "Hor 2", "RotD50"]
    elif mode.lower() == "rotd100":
        plot_titles = ["Hor 1", "Hor 2", "RotD100"]
    else:
        print("[ERROR]: mode must be set to rotd50 or rotd100!")
        sys.exit(1)

    # Select line styles to use
    all_styles = ['C0', 'C2', 'k', 'r', 'b', 'm', 'g', 'c', 'y',
                  'brown', 'gold', 'blueviolet', 'grey', 'pink']
    if len(input_files) > len(all_styles):
        print("[ERROR]: Too many files to plot!")
        sys.exit(-1)
    styles = all_styles[0:len(input_files)]

    # Convert min/max frequencies to periods
    if lfreq is None:
        pmax = None
    else:
        pmax = 1.0 / float(lfreq)

    if hfreq is None:
        pmin = None
    else:
        pmin = 1.0 / float(hfreq)

    # Read input files
    rdxxs = [read_rdxx(input_file) for input_file in input_files]

    # Check nummber of periods, separate PSA by component
    periods = rdxxs[0][0]
    min_y = min(rdxxs[0][1])
    max_y = max(rdxxs[0][1])
    psa_h1 = []
    psa_h2 = []
    psa_rdxx = []
    for rdxx in rdxxs:
        psa_h1.append(rdxx[1])
        psa_h2.append(rdxx[2])
        psa_rdxx.append(rdxx[3])
        min_y = min(min_y, min(rdxx[1]))
        min_y = min(min_y, min(rdxx[2]))
        min_y = min(min_y, min(rdxx[3]))
        max_y = max(max_y, max(rdxx[1]))
        max_y = max(max_y, max(rdxx[2]))
        max_y = max(max_y, max(rdxx[3]))
        if len(rdxx[0]) != len(periods):
            print("[PLOTRDXX]: All inputs must have the same number of periods!")
            sys.exit(1)

    # Figure out plot limits
    min_x = min(periods)
    max_x = max(periods)
    min_horiz_y = min_y / 1.2
    max_horiz_y = 1.1 * max_y

    # Set up ticks to match matplotlib 1.x style
    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['ytick.direction'] = 'in'
    mpl.rcParams['lines.linewidth'] = 1.0
    mpl.rcParams['lines.dashed_pattern'] = [6, 6]
    mpl.rcParams['lines.dashdot_pattern'] = [3, 5, 1, 5]
    mpl.rcParams['lines.dotted_pattern'] = [1, 3]
    mpl.rcParams['lines.scale_dashes'] = False

    # Start plot
    pylab.clf()
    pylab.suptitle('PSA for station %s, %s' %
                   (station_id, " vs ".join(labels)), size=14)

    pylab.subplots_adjust(top=0.85)
    pylab.subplots_adjust(bottom=0.15)
    pylab.subplots_adjust(left=0.075)
    pylab.subplots_adjust(right=0.975)
    pylab.subplots_adjust(hspace=0.3)
    pylab.subplots_adjust(wspace=0.3)

    # First plot
    ax1 = pylab.subplot(131)
    for psa, label, style in zip(psa_h1, labels, styles):
        pylab.plot(periods, psa, style, label=label, lw=0.5)
    pylab.xlim(min_x, max_x)
    pylab.xscale('log')
    pylab.ylim(min_horiz_y, max_horiz_y)
    pylab.ylabel("PSA (g)")
    ax1.set_title('%s' % (plot_titles[0]), fontsize='small')
    pylab.xlabel('Period (s)')
    # Add vertical lines
    if pmin is not None:
        pylab.vlines(pmin, min_horiz_y, max_horiz_y,
                     color='violet', linestyles='--')
    if pmax is not None:
        pylab.vlines(pmax, min_horiz_y, max_horiz_y, color='r', linestyles='--')
    pylab.legend(prop=mpl.font_manager.FontProperties(size=8))

    # Second plot
    ax2 = pylab.subplot(132)
    for psa, label, style in zip(psa_h2, labels, styles):
        pylab.plot(periods, psa, style, label=label, lw=0.5)
    pylab.xlim(min_x, max_x)
    pylab.xscale('log')
    pylab.ylim(min_horiz_y, max_horiz_y)
    pylab.ylabel("PSA (g)")
    ax2.set_title('%s' % (plot_titles[1]), fontsize='small')
    pylab.xlabel('Period (s)')
    # Add vertical lines
    if pmin is not None:
        pylab.vlines(pmin, min_horiz_y, max_horiz_y,
                     color='violet', linestyles='--')
    if pmax is not None:
        pylab.vlines(pmax, min_horiz_y, max_horiz_y, color='r', linestyles='--')
    pylab.legend(prop=mpl.font_manager.FontProperties(size=8))

    # Third plot
    ax3 = pylab.subplot(133)
    for psa, label, style in zip(psa_rdxx, labels, styles):
        pylab.plot(periods, psa, style, label=label, lw=0.5)
    pylab.xlim(min_x, max_x)
    pylab.xscale('log')
    pylab.ylim(min_horiz_y, max_horiz_y)
    pylab.ylabel("PSA (g)")
    ax3.set_title('%s' % (plot_titles[2]), fontsize='small')
    pylab.xlabel('Period (s)')
    # Add vertical lines
    if pmin is not None:
        pylab.vlines(pmin, min_horiz_y, max_horiz_y,
                     color='violet', linestyles='--')
    if pmax is not None:
        pylab.vlines(pmax, min_horiz_y, max_horiz_y, color='r', linestyles='--')
    pylab.legend(prop=mpl.font_manager.FontProperties(size=8))

    # All done, save plot
    pylab.gcf().set_size_inches(10, 4)
    
    if output_file.lower().endswith(".png"):
        fmt = 'png'
    elif output_file.lower().endswith(".pdf"):
        fmt = 'pdf'
    else:
        print("[ERROR]: Unknown format!")
        sys.exit(1)

    pylab.savefig(output_file, format=fmt,
                  transparent=False,
                  dpi=plot_config.dpi)
    pylab.close()

class PlotRotDXX(object):

    def __init__(self, mode=None):
        self.mode = mode
        self.comp_label = None

    def parse_arguments(self):
        """
        This function takes care of parsing the command-line arguments and
        asking the user for any missing parameters that we need
        """
        parser = argparse.ArgumentParser(description="Plot RotD50/RotD100 "
                                         " comparison of two or more files.")
        parser.add_argument("--input-dir", dest="input_dir",
                            help="input directory")
        parser.add_argument("--output-dir", dest="output_dir",
                            help="output directory")
        parser.add_argument("-o", "--output", "--output-file",
                            dest="output_file",
                            help="output rd100 file")
        parser.add_argument("--batch-file", "-b", dest="batch_file", 
                            help="file with list of timeseries to process")
        parser.add_argument("--station-id", "-id", dest="station_id",
                            help="station id for comparison")
        parser.add_argument("--station-list", "-s", dest="station_list",
                            help="station list for batch processing")
        parser.add_argument("--labels", "-l", dest="labels",
                            help="comma-separated comparison labels")
        parser.add_argument("--comp-label", dest="comp_label",
                            help="comparison label used for the output file prefix")
        parser.add_argument("--rotd100", dest="rotd100", action="store_true",
                            help="select RotD100 comparison")
        parser.add_argument("--rotd50", dest="rotd50", action="store_true",
                            help="select RotD50 comparison (default)")
        parser.add_argument("--low-freq", "--lf", dest="lfreq",
                            help="adds vertical line at this low frequency corner")
        parser.add_argument("--high-freq", "--hf", dest="hfreq",
                            help="adds vertical line at this high frequency corner")
        parser.add_argument('input_files', nargs='*')
        args = parser.parse_args()

        return args
        
    def run(self):
        """
        Run PlotRotDXX module
        """
        # Parse command-line options
        args = self.parse_arguments()

        # Make sure we have something to do
        if len(args.input_files) == 0:
            print("[ERROR]: Must specify at least one input file/directory!")
            sys.exit(1)

        # Set mode
        self.mode = "rotd50"
        if args.rotd100 and args.rotd50:
            print("[ERROR]: Please specify --rotd50 or --rotd100, not both!")
            sys.exit(1)
        if args.rotd100:
            self.mode = "rotd100"

        # Look at paths
        output_dir = ""
        if args.output_dir:
            output_dir = args.output_dir
        input_files = args.input_files
        labels = args.labels
        if labels is not None:
            labels = [label.strip() for label in labels.split(",")]
            if len(labels) != len(input_files):
                print("[ERROR] Please specify as many labels as input files!")
                sys,exit(1)
            
        if args.station_id:
            # Single comparison mode
            if args.output_file:
                output_file = args.output_file
            else:
                if args.comp_label:
                    output_file = "%s_%s_%s.png" % (args.comp_label,
                                                    args.station_id,
                                                    self.mode)
                else:
                    output_file = "%s_%s.png" % (args.station_id,
                                                 self.mode)
            output_file = os.path.join(output_dir, output_file)
            lfreq = None
            hfreq = None
            if args.lfreq:
                lfreq = args.lfreq
            if args.hfreq:
                hfreq = args.hfreq
            self.run_single_station(input_files, labels, output_file,
                                    args.station_id, lfreq=lfreq, hfreq=hfreq)
        elif args.batch_file:
            # Batch file mode
            self.run_batch_mode(args.batch_file, input_files, labels,
                                output_dir, args.comp_label)
        elif args.station_list:
            # Run through the station list
            self.run_station_mode(args.station_list, input_files, labels,
                                  output_dir, args.comp_label)
        else:
            print("[ERROR]: Must include station_id, batch_file, or station_list!")
            sys.exit(1)

    def run_single_station(self, input_files, labels, output_file,
                           station, lfreq=None, hfreq=None):
        """
        Generates RotDXX comparison plots for a single station
        """
        print("[PLOTRDXX]: Generating RotDXX comparison plot for station %s" % (station))
        create_rdxx_plot(station, input_files, labels, output_file,
                         lfreq=lfreq, hfreq=hfreq, mode=self.mode,
                         quiet=True)

    def run_batch_mode(self, batch_file, input_dirs, labels,
                       output_dir, comp_label):
        """
        Generated RotDXX comparison plots for stations in a batch file
        """
        if self.mode == "rotd50":
            extension = "rd50"
        elif self.mode == "rotd100":
            extension = "rd100"
        else:
            print("[ERROR]: mode %s is invalid, must be rotd50 or rotd100!" % (self.mode))
            sys.exit(1)

        # Open batch file
        input_list = open(batch_file, 'r')
        for line in input_list:
            line = line.strip()
            if not line:
                continue

            station_name = line
            lfreq = None
            hfreq = None
            
            self.run_directory_mode(station_name, extension, lfreq,
                                    hfreq, input_dirs, labels,
                                    output_dir, comp_label)

        input_list.close()

    def run_station_mode(self, station_file, input_dirs, labels,
                         output_dir, comp_label):
        """
        Generates RotDXX comparison plots for stations in a station list
        """
        if self.mode == "rotd50":
            extension = "rd50"
        elif self.mode == "rotd100":
            extension = "rd100"
        else:
            print("[ERROR]: mode %s is invalid, must be rotd50 or rotd100!" % (self.mode))
            sys.exit(1)

        stations = StationList(station_file)
        station_list = stations.get_station_list()

        # Loop through stations
        for station in station_list:
            station_name = station.scode
            lfreq = station.low_freq_corner
            hfreq = station.high_freq_corner

            self.run_directory_mode(station_name, extension, lfreq,
                                    hfreq, input_dirs, labels,
                                    output_dir, comp_label)

    def run_directory_mode(self, station_name, extension, lfreq, hfreq,
                           input_dirs, labels, output_dir, comp_label):
        """
        Used by both station_mode and batch_mode, finds files matching
        the station name and generates comparison plot
        """
        # Make list of all input files
        input_files = []
        for input_dir in input_dirs:
            input_list = glob.glob("%s%s*%s*.%s" %
                                   (input_dir, os.sep, station_name, extension))
            if len(input_list) != 1:
                print("[ERROR]: Can't find input file for station %s" % (station_name))
                sys.exit(1)

            input_files.append(input_list[0])
            
        # Set up output file
        if comp_label:
            output_file = "%s_%s_%s.png" % (comp_label,
                                            station_name,
                                            self.mode)
        else:
            output_file = "%s_%s.png" % (station_name,
                                         self.mode)
        output_file = os.path.join(output_dir, output_file)

        self.run_single_station(input_files, labels, output_file,
                                station_name, lfreq=lfreq, hfreq=hfreq)
            
if __name__ == '__main__':
    print("Running module: %s" % (os.path.basename(sys.argv[0])))
    ME = PlotRotDXX()
    ME.run()
    


