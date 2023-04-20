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

This module contains functions to generate seismogram comparison plots
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import glob
import numpy as np
import matplotlib as mpl
mpl.use('AGG')
import matplotlib.pyplot as plt
import argparse

# Import plot config file
from plots import plot_config
from core.station_list import StationList
from utils.file_utilities import read_bbp_file, read_bbp_dt, read_bbp_samples

def plot_overlay_timeseries(input_files, labels,
                            mode, num_components,
                            output_file, xmin, xmax,
                            orientations=None,
                            plot_title=None):
    """
    Plotting a comparison of multiple timeseries, supports
    a maximum of 12 timeseries

    Inputs:
        input_files - array of files to use as input
        labels      - array of labels to use for the legend
                      (in same order as input_files array)
        output_file - filename to use for the output plot
        args.xmin   - min x for timeseries plot (s)
        args.xmax   - max x for timeseries plot (s)
        plot_title  - title of the plot, default no title
    Outputs:
        Plot generated as output_file
    """
    all_styles = ['k', 'r', 'b', 'm', 'g', 'c', 'y', 'brown',
                  'gold', 'blueviolet', 'grey', 'pink']

    # Check num_components
    if num_components != 2 and num_components != 3:
        print("[ERROR]: num_components must be 2 or 3!")
        sys.exit(-1)

    # Orientation for each component
    if orientations is None:
        orientations = [0.0, 90.0, 'up']

    # Check number of input timeseries
    if len(input_files) > len(all_styles):
        print("[ERROR]: Too many timeseries to plot (%d), maximum number is %d!" %
              (len(input_files), len(all_styles)))
        sys.exit(-1)

    # Read input files
    all_data = []

    # Loop through all files
    for input_file in input_files:
        # Get filenames for displacement, velocity and acceleration bbp files
        work_dir = os.path.dirname(input_file)
        base_file = os.path.basename(input_file)

        base_tokens = base_file.split('.')[0:-2]
        if not base_tokens:
            print("[ERROR]: Invalid BBP filename: %s" % (input_file))
            sys.exit(1)
        dis_tokens = list(base_tokens)
        vel_tokens = list(base_tokens)
        acc_tokens = list(base_tokens)

        dis_tokens.append('dis')
        vel_tokens.append('vel')
        acc_tokens.append('acc')

        dis_tokens.append('bbp')
        vel_tokens.append('bbp')
        acc_tokens.append('bbp')

        dis_file = os.path.join(work_dir, '.'.join(dis_tokens))
        vel_file = os.path.join(work_dir, '.'.join(vel_tokens))
        acc_file = os.path.join(work_dir, '.'.join(acc_tokens))

        # Now initialize data structures and read needed files
        data = {}
        data['acc'] = None
        data['vel'] = None
        data['dis'] = None
        data['acc_file'] = os.path.basename(acc_file)
        data['vel_file'] = os.path.basename(vel_file)
        data['dis_file'] = os.path.basename(dis_file)
        dt = None
        samples = None
        
        if 'acc' in mode:
            data['acc'] = read_bbp_file(acc_file)
            dt = read_bbp_dt(acc_file)
            samples = read_bbp_samples(acc_file)
        if 'vel' in mode:
            data['vel'] = read_bbp_file(vel_file)
            if dt is None:
                dt = read_bbp_dt(vel_file)
                samples = read_bbp_samples(vel_file)
        if 'dis' in mode:
            data['dis'] = read_bbp_file(dis_file)
            if dt is None:
                dt = read_bbp_dt(dis_file)
                samples = read_bbp_samples(dis_file)
        data['dt'] = dt
        data['samples'] = samples
        all_data.append(data)
        
    # Limits on x axis
    delta_ts = [timeseries['dt'] for timeseries in all_data]
    xtmin = xmin
    xtmax = xmax
    if xtmin is None:
        xtmin = 0.0

    min_is = [int(xtmin/delta_t) for delta_t in delta_ts]
    if xtmax is not None:
        max_is = [int(xtmax/delta_t) for delta_t in delta_ts]
    else:
        max_is = [timeseries['samples'] for timeseries in all_data]
        xtmax = max([timeseries['samples'] *
                     timeseries['dt'] for timeseries in all_data])

    # Labels
    if labels is None:
        labels_acc = [data['acc_file'] for data in all_data]
        labels_vel = [data['vel_file'] for data in all_data]
        labels_dis = [data['dis_file'] for data in all_data]
    else:
        if len(labels) != len(all_data):
            print("[ERROR]: Must provide as many labels as data files!")
            sys.exit(-1)
        labels_acc = labels
        labels_vel = labels
        labels_dis = labels

    # Create plot
    num_rows = num_components
    num_columns = len(mode)
    f, axarr = plt.subplots(nrows=num_rows,
                            ncols=num_columns,
                            figsize=(14, 9))

    # Change array shape since NumPy doesn't make a distinction
    # between column and vector arrays
    if len(axarr.shape) == 1:
        axarr.shape = (axarr.shape[0], 1)
    
    # For each component: h1, h2, vertical
    for i in range(0, num_components):

        samples = [data['samples'] for data in all_data]

        # Get orientation
        orientation = orientations[i]
        if type(orientation) is not str:
            orientation = str(int(orientation))

        # Set up plot titles
        title_acc = "Acceleration : %s" % (orientation)
        title_vel = "Velocity : %s" % (orientation)
        title_dis = "Displacement : %s" % (orientation)

        # cutting signal by bounds
        if 'dis' in mode:
            displs = [data['dis'][i+1] for data in all_data]
            c_displs = [dis[min_i:max_i] for dis, min_i, max_i in zip(displs,
                                                                      min_is,
                                                                      max_is)]
        if 'vel' in mode:
            vels = [data['vel'][i+1] for data in all_data]
            c_vels = [vel[min_i:max_i] for vel, min_i, max_i in zip(vels,
                                                                    min_is,
                                                                    max_is)]
        if 'acc' in mode:
            accs = [data['acc'][i+1] for data in all_data]
            c_accs = [acc[min_i:max_i] for acc, min_i, max_i in zip(accs,
                                                                    min_is,
                                                                    max_is)]
        times = [np.arange(xtmin,
                           min(xtmax, (delta_t * sample)),
                           delta_t) for delta_t, sample in zip(delta_ts,
                                                               samples)]

        index = 0
        if 'acc' in mode:
            axarr[i][index].set_title(title_acc)
            axarr[i][index].grid(True)
            styles = all_styles[0:len(times)]
            for timeseries, c_acc, style in zip(times, c_accs, styles):
                axarr[i][index].plot(timeseries, c_acc, style)
            # Add labels to first plot
            if i == 0:
                axarr[i][index].legend(labels_acc, prop={'size':6})
            axarr[i][index].set_xlim([xtmin, xtmax])
            index = index + 1

        if 'vel' in mode:
            axarr[i][index].set_title(title_vel)
            axarr[i][index].grid(True)
            styles = all_styles[0:len(times)]
            for timeseries, c_vel, style in zip(times, c_vels, styles):
                axarr[i][index].plot(timeseries, c_vel, style)
            # Add labels to first plot
            if i == 0:
                axarr[i][index].legend(labels_vel, prop={'size':6})
            axarr[i][index].set_xlim([xtmin, xtmax])
            index = index + 1
        
        if 'dis' in mode:
            axarr[i][index].set_title(title_dis)
            axarr[i][index].grid(True)
            styles = all_styles[0:len(times)]
            for timeseries, c_dis, style in zip(times, c_displs, styles):
                axarr[i][index].plot(timeseries, c_dis, style)
            # Add labels to first plot
            if i == 0:
                axarr[i][index].legend(labels_dis, prop={'size':6})
            axarr[i][index].set_xlim([xtmin, xtmax])

    # Make nice plots with tight_layout
    f.tight_layout()

    # Add overall title if provided
    if plot_title is not None:
        st = plt.suptitle(plot_title, fontsize=16)
        # shift subplots down:
        #st.set_y(0.95)
        f.subplots_adjust(top=0.92)

    # All done, save plot
    if output_file.lower().endswith(".png"):
        fmt = 'png'
    elif output_file.lower().endswith(".pdf"):
        fmt = 'pdf'
    else:
        print("[ERROR]: Unknown format!")
        sys.exit(-1)

    plt.savefig(output_file, format=fmt,
                transparent=False,
                dpi=plot_config.dpi)
    plt.close()

class PlotSeismograms(object):

    def __init__(self, mode=["acc", "vel", "dis"], n_comp=None):
        self.mode = mode[:]
        self.n_comp = n_comp
        self.comp_label = None

    def parse_arguments(self):
        """
        This function takes care of parsing the command-line arguments and
        asking the user for any missing parameters that we need
        """
        parser = argparse.ArgumentParser(description="Plot seismogram "
                                         " comparison of two or more timeseries.")
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
        parser.add_argument("--labels", "-l", dest="labels",
                            help="comma-separated comparison labels")
        parser.add_argument("--comp-label", dest="comp_label",
                            help="comparison label used for the output file prefix")
        parser.add_argument("-2", "--two", "--two-component", dest="two_comp", action="store_true",
                            help="select two component comparison (default 3-component)")
        parser.add_argument("--acc", "--acceleration", dest="plot_acc", action="store_true",
                            help="plot acceleration comparison")
        parser.add_argument("--vel", "--velocity", dest="plot_vel", action="store_true",
                            help="plot velocity comparison")
        parser.add_argument("--dis", "--displacement", dest="plot_dis", action="store_true",
                            help="plot displacement comparison")
        parser.add_argument("--all", dest="plot_all", action="store_true",
                            help="plot acceleration/velocity/displacement comparisons")
        parser.add_argument("--xmin", dest="xmin", type=float,
                            help="xmin to plot")
        parser.add_argument("--xmax", dest="xmax", type=float,
                            help="xmax to plot")
        parser.add_argument("-m", "--mode", dest="plot_mode", type=int, default=1,
                            help="plot mode: 1 plots [duration] starting at 0, 2 plots entire seismogram")
        parser.add_argument("-dur", "--duration", dest="plot_duration", type=float,
                            default=100, help="seismogram duration to plot, default is 100s")
        parser.add_argument("--orientation", dest="orientations",
                            help="orientation for the 2 or 3 components, default: 0.0, 90.0, UP")
        parser.add_argument("--plot-title", "--title", dest="plot_title",
                            help="plot title")
        parser.add_argument('input_files', nargs='*')
        args = parser.parse_args()

        return args
        
    def run(self):
        """
        Run PlotSeismogram module
        """
        # Parse command-line options
        args = self.parse_arguments()

        # Make sure we have something to do
        if len(args.input_files) == 0:
            print("[ERROR]: Must specify at least one input file/directory!")
            sys.exit(1)

        # Set comparison mode
        if not args.plot_all and not args.plot_acc and not args.plot_vel and not args.plot_dis:
            self.mode = ["acc", "vel" ,"dis"]
        else:
            self.mode = []
        if args.plot_acc is True:
            self.mode.append("acc")
        if args.plot_vel is True:
            self.mode.append("vel")
        if args.plot_dis is True:
            self.mode.append("dis")
        if args.plot_all is True:
            self.mode = []
            self.mode.append("dis")
            self.mode.append("vel")
            self.mode.append("acc")

        # Set number of components
        self.n_comp = 3
        if args.two_comp:
            self.n_comp = 2

        # Check orientations
        self.orientations = None
        if args.orientations:
            orientations = args.orientations
            orientations = [val.strip() for val in orientations.split(",")]
            if len(orientations) == 2:
                orientations.append("UP")
            if len(orientations) != 3:
                print("[ERROR]: orientation must include 2 or 3 labels!")
                sys.exit(-1)
            self.orientations = orientations

        # Check for plot limits
        xmin = args.xmin
        xmax = args.xmax
        plot_duration = args.plot_duration
        plot_mode = args.plot_mode
        if plot_mode == 2:
            # Mode overrides duration
            plot_duration = None
        if xmin is None:
            xmin = 0.0
        if xmax is None:
            if plot_duration is not None:
                xmax = xmin + plot_duration
            else:
                xmax = None

        # Plot title
        plot_title = None
        if args.plot_title:
            plot_title = args.plot_title

        # Look at paths
        input_dir = ""
        output_dir = ""
        if args.output_dir:
            output_dir = os.path.abspath(args.output_dir)
        if args.input_dir:
            input_dir = os.path.abspath(args.input_dir)
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
                if len(self.mode) > 1:
                    suffix = "seis"
                else:
                    suffix = "%s_seis" % (self.mode[0])
                if args.comp_label:
                    output_file = "%s%s_%s.png" % (args.comp_label,
                                                   args.station_id,
                                                   suffix)
                else:
                    output_file = "%s_%s.png" % (args.station_id, suffix)
            output_file = os.path.join(output_dir, output_file)
            input_files = [os.path.join(input_dir, input_file) for input_file in input_files]
            self.run_single_station(input_files, labels,
                                    output_file, args.station_id,
                                    xmin, xmax, plot_title)
        elif args.batch_file:
            # Batch file mode
            self.run_batch_mode(args.batch_file, input_files,
                                labels, output_dir, args.comp_label,
                                xmin, xmax, plot_title)
        elif args.station_list:
            # Run through the station list
            self.run_station_mode(args.station_list, input_files,
                                  labels, output_dir, args.comp_label,
                                  xmin, xmax, plot_title)
        else:
            print("[ERROR]: Must include station_id, batch_file, or station_list!")
            sys.exit(1)

    def run_single_station(self, input_files, labels,
                           output_file, station_name,
                           xmin, xmax, plot_title=None):
        """
        Generates seismogram comparison plots for a single station
        """
        print("[PlotSeismograms]: Generating seismogram comparison plot for station %s" %
              (station_name))
        if plot_title is None:
            if len(input_files) > 1:
                plot_title = "Seismogram comparison for station: %s" % (station_name)
            else:
                plot_title = "Seismogram for station: %s" % (station_name)
        plot_overlay_timeseries(input_files, labels,
                                self.mode, self.n_comp,
                                output_file, xmin, xmax,
                                self.orientations,
                                plot_title=plot_title)
        
    def run_batch_mode(self, batch_file, input_dirs,
                       labels, output_dir, comp_label,
                       xmin, xmax, plot_title):
        """
        Generated seismogram comparison plots for stations in a batch file
        """
        # Open batch file
        input_list = open(batch_file, 'r')
        for line in input_list:
            line = line.strip()
            if not line:
                continue

            station_name = line

            if plot_title is None:
                if len(input_dirs) > 1:
                    plot_title = "Seismogram comparison for station %s" % (station_name)
                else:
                    plot_title = "Seismogram for station %s" % (station_name)

            self.run_directory_mode(station_name, input_dirs,
                                    labels, output_dir, comp_label,
                                    xmin, xmax, plot_title)

        input_list.close()

    def run_station_mode(self, station_file, input_dirs,
                         labels, output_dir, comp_label,
                         xmin, xmax, plot_title):
        """
        Generates seismogram comparison plots for stations in a station list
        """
        stations = StationList(station_file)
        station_list = stations.get_station_list()

        # Loop through stations
        for station in station_list:
            station_name = station.scode

            if plot_title is None:
                if len(input_dirs) > 1:
                    plot_title = "Seismogram comparison for station %s" % (station_name)
                else:
                    plot_title = "Seismogram for station %s" % (station_name)

            self.run_directory_mode(station_name, input_dirs,
                                    labels, output_dir, comp_label,
                                    xmin, xmax, plot_title)

    def run_directory_mode(self, station_name,
                           input_dirs, labels,
                           output_dir, comp_label,
                           xmin, xmax, plot_title):
        """
        Used by both station_mode and batch_mode, finds files matching
        the station name and generates comparison plot
        """
        if "acc" in self.mode:
            extension = "acc.bbp"
        elif "vel" in self.mode:
            extension = "vel.bbp"
        elif "dis" in self.mode:
            extension = "dis.bbp"
        else:
            print("[ERROR]: Unknown mode %s!" % (self.mode))
            sys.exit(-1)

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
        if len(self.mode) > 1:
            suffix = "seis"
        else:
            suffix = "%s_seis" % (self.mode[0])
        if comp_label:
            output_file = "%s%s_%s.png" % (comp_label,
                                           station_name,
                                           suffix)
        else:
            output_file = "%s_%s.png" % (station_name, suffix)
        output_file = os.path.join(output_dir, output_file)

        self.run_single_station(input_files, labels,
                                output_file, station_name,
                                xmin, xmax, plot_title)
            
if __name__ == '__main__':
    print("Running module: %s" % (os.path.basename(sys.argv[0])))
    ME = PlotSeismograms()
    ME.run()
