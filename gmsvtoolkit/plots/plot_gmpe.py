#!/bin/env python
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

This module contains functions to plot GMPE results
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import glob
import argparse
import matplotlib as mpl
mpl.use('AGG')
import pylab

# Import GMSVToolkit modules
from core.station_list import StationList
from plots import plot_config
from models import gmpe_config

def plot_gmpe(stat, comp_file, gmpe_file, gmpe_labels, label1, label2, outfile):
    """
    This function generates comparison plots between the simulated
    results and the gmpe data
    """
    periods1 = []
    rd50_aa1 = []

    periods2 = []
    gmpe_ri50 = []

    # Read data from comp_file if it was provided
    if comp_file is not None:
        # Read simulated rd50 data file
        compfile = open(comp_file, 'r')
        for line in compfile:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#") or line.startswith("%"):
                continue
            pieces = line.split()
            periods1.append(float(pieces[0]))
            rd50_aa1.append(float(pieces[3]))
        compfile.close()

        if periods1 == []:
            print("Input file %s is missing data! Aborting..." % (comp_file))
            sys.exit(1)

    # Read gmpe data file
    subplot_titles = []
    gmpefile = open(gmpe_file, 'r')
    for line in gmpefile:
        if line.startswith("#") or line.startswith("%"):
            continue
        pieces = line.split()
        periods2.append(float(pieces[0]))
        # Figure out if we need to create list
        if not gmpe_ri50:
            for item in pieces[1:]:
                gmpe_ri50.append([])
        for item, dst in zip(pieces[1:], gmpe_ri50):
            dst.append(float(item))
    gmpefile.close()

    if not periods2:
        print("Input file %s is missing data! Aborting..." % (gmpe_file))
        sys.exit(1)

    subplot_titles = gmpe_labels

    # Start plot
    num_plots = len(gmpe_ri50)
    if len(gmpe_ri50) % 2:
        num_plots = num_plots + 1
    num_columns = num_plots // 2
    fig, axs = pylab.plt.subplots(2, num_columns)
    fig.set_size_inches(8, 7)
    pylab.subplots_adjust(left=0.075)
    pylab.subplots_adjust(right=0.975)
    pylab.subplots_adjust(hspace=0.3)

    # Figure out min and max values
    if comp_file is not None:
        min_x = min([min((periods1)), min(periods2)])
        max_x = max([max((periods1)), max(periods2)])
        min_y = min([min(gmpe_values) for gmpe_values in gmpe_ri50]) / 1.1
        max_y_gmpes = max([max(gmpe_values) for gmpe_values in gmpe_ri50])
        max_y = 1.1 * max(max_y_gmpes, max(rd50_aa1))
    else:
        # comparison file was not provided, use only the values from the GMPEs
        min_x = min(periods2)
        max_x = max(periods2)
        min_y = min([min(gmpe_values) for gmpe_values in gmpe_ri50]) / 1.1
        max_y_gmpes = max([max(gmpe_values) for gmpe_values in gmpe_ri50])
        max_y = 1.1 * max_y_gmpes

    # Convert to list
    subfigs = []
    for y_subplot in range(0, 2):
        for x_subplot in range(0, num_columns):
            subfigs.append(axs[y_subplot, x_subplot])

    # Now walk through each subfig, if we have more subfigs that we
    # have data for, the for loop will only create enough subfigs to
    # cover the data, ignoring the extra one
    for subfig, subplot_title, gmpe_values in zip(subfigs,
                                                  subplot_titles,
                                                  gmpe_ri50):
        subfig.set_xlim(min_x, max_x)
        subfig.set_ylim(min_y, max_y)
        subfig.set_title("%s" % subplot_title, fontsize='small')
        if comp_file is not None:
            subfig.plot(periods1, rd50_aa1, label=str(label1))
        subfig.plot(periods2, gmpe_values, label=str(label2))
        subfig.set_ylabel("PSA (g)")
        subfig.set_xlabel("Period (s)")
        subfig.legend(prop=mpl.font_manager.FontProperties(size=8))
        subfig.set_xscale('log')
        subfig.grid()

    # All done, label and save it!
    fig.suptitle('GMPE Comparison for station %s' %
                 (stat), size=14)
    fig.savefig(outfile, format="png", dpi=plot_config.dpi)
    pylab.close()

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    gmpe_groups = [item for item in gmpe_config.GMPES]
    parser = argparse.ArgumentParser(description="Generate GMPE Comparison plots")

    parser.add_argument("--gmpe-dir", dest="gmpe_dir", required=True,
                        help="input directory with GMPE data")
    parser.add_argument("--comp-dir", dest="comp_dir",
                        help="input directory with comparison files")
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
    parser.add_argument("--run-prefix", dest="run_prefix",
                        help="prefix to be added to the comparison files")
    parser.add_argument("--gmpe-group", dest="gmpe_group", required=True,
                            help="GMPE group %s" % (gmpe_groups))
    args = parser.parse_args()

    return args

def run():
    """
    Plots gmpe comparison
    """
    # Parse command-line options
    args = parse_arguments()

    # Figure out gmpe labels
    gmpe_groups = [item for item in gmpe_config.GMPES]
    gmpe_group_name = args.gmpe_group.lower()
    if gmpe_group_name not in gmpe_groups:
        print("[ERROR]: gmpe-group must be %s" % (gmpe_groups))
        sys.exit(1)
    gmpe_group = gmpe_config.GMPES[gmpe_group_name]
    gmpe_labels = gmpe_group["labels"]

    # Look at paths
    output_dir = ""
    if args.output_dir:
        output_dir = args.output_dir
    output_dir = os.path.abspath(output_dir)
    gmpe_dir = os.path.abspath(args.gmpe_dir)
    comp_dir = None
    if args.comp_dir:
        comp_dir = os.path.abspath(args.comp_dir)

    if args.station_id:
        # Single comparison mode
        if args.output_file:
            output_file = args.output_file
        else:
            if args.comp_label:
                if args.run_prefix is not None:
                    output_file = "%s_%s_%s_gmpe.png" % (args.comp_label,
                                                         args.run_prefix,
                                                         args.station_id)
                else:
                    output_file = "%s_%s_gmpe.png" % (args.comp_label,
                                                      args.station_id)
            else:
                output_file = "%s_gmpe.png" % (args.station_id)
        output_file = os.path.join(output_dir, output_file)

        run_single_station(args.station_id, gmpe_dir, comp_dir,
                           output_file, gmpe_labels)
    elif args.batch_file:
        # Batch file mode
        batch_file = os.path.abspath(args.batch_file)
        run_batch_mode(batch_file, gmpe_dir, comp_dir,
                       output_dir, gmpe_labels,
                       args.comp_label, args.run_prefix)
    elif args.station_list:
        # Run through the station list mode
        station_file = os.path.abspath(args.station_list)
        run_station_mode(station_file, gmpe_dir, comp_dir,
                         output_dir, gmpe_labels,
                         args.comp_label, args.run_prefix)
    else:
        print("[ERROR]: Must include station_id, batch_file, or station_list!")
        sys.exit(1)
    
def run_single_station(station_name, gmpe_dir, comp_dir,
                       output_file, gmpe_labels):
    """
    Create a GMPE comparison plot for a single station
    """
    print("[PLOTGMPE]: Generating GMPE comparison plot for station %s" % (station_name))

    # Find input files for this station
    gmpe_files = glob.glob("%s%s*%s*.ri50" %
                           (gmpe_dir, os.sep,
                            station_name))
    if len(gmpe_files) != 1:
        print("[ERROR]: Can't find GMPE file for station %s" % (station_name))
        sys.exit(1)
    gmpe_file = gmpe_files[0]

    if comp_dir is not None:
        comp_files = glob.glob("%s%s*%s*.rd50" %
                               (comp_dir, os.sep,
                                station_name))
        if len(comp_files) != 1:
            print("[ERROR]: Can't find comparison file for station %s" % (station_name))
            sys.exit(1)
        comp_file = comp_files[0]
    else:
        comp_file = None

    # Now plot GMPE comparison plot
    label1 = "Comp"
    label2 = "GMM"
    plot_gmpe(station_name, comp_file, gmpe_file, gmpe_labels, label1, label2, output_file)

def run_batch_mode(batch_file, gmpe_dir,
                   comp_dir, output_dir,
                   gmpe_labels,
                   comp_label, run_prefix):
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

        run_directory_mode(station_name, gmpe_dir,
                           comp_dir, output_dir,
                           gmpe_labels,
                           comp_label=comp_label,
                           run_prefix=run_prefix)

    input_list.close()

def run_station_mode(station_file, gmpe_dir,
                     comp_dir, output_dir,
                     gmpe_labels,
                     comp_label, run_prefix):
    """
    Generates GMPE comparison plots for a list of stations
    """
    stations = StationList(station_file)
    station_list = stations.get_station_list()

    # Loop through stations
    for station in station_list:
        station_name = station.scode

        run_directory_mode(station_name, gmpe_dir,
                           comp_dir, output_dir,
                           gmpe_labels,
                           comp_label=comp_label,
                           run_prefix=run_prefix)

def run_directory_mode(station_name, gmpe_dir, comp_dir,
                       output_dir, gmpe_labels,
                       comp_label=None,
                       run_prefix=None):
    """
    Used by both station_mode and batch_mode, finds files matching
    the station name and generates comparison plot
    """
    # Set up output file
    if comp_label:
        if run_prefix:
            output_file = "%s_%s_%s_gmpe.png" % (comp_label,
                                                 run_prefix,
                                                 station_name)
        else:
            output_file = "%s_%s_gmpe.png" % (comp_label,
                                              station_name)
    else:
        output_file = "%s_gmpe.png" % (station_name)
    output_file = os.path.join(output_dir, output_file)

    run_single_station(station_name, gmpe_dir, comp_dir,
                       output_file, gmpe_labels)

if __name__ == '__main__':
    run()
