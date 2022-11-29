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

Creates a distance gof plot for a list of periods
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import argparse
import matplotlib as mpl
if (mpl.get_backend() != 'agg'):
    mpl.use('Agg') # Disables use of Tk/X11
import pylab

# Imports needed from the GMSVToolkit
from core import exceptions
from plots import plot_config

# Constants
MIN_Y_AXIS = -1.75
MAX_Y_AXIS = 1.75
COMP_EXT_RD50 = 'rotd50'
COMP_TITLE_RD50 = 'RotD50'
DIST_PERIODS = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]

def read_resid(resid_file, component, period, summary_output):
    """
    Reads the residual file resid_file and returns all data for the
    requested periods
    """
    # Start empty
    data = []
    distance = []

    # Read residuals file and get information we need
    input_file = open(resid_file, 'r')
    # Look over header and figure out which column contains the period
    # we need to plot
    header = input_file.readline()
    header = header.strip()
    items = header.split()
    index = -1
    for idx, item in enumerate(items):
        try:
            val = float(item)
            if val == period:
                # Found period, save index
                index = idx
                break
        except:
            pass

    if index < 0:
        # If we don't have this period, nothing to do
        print("Residuals file %s does not have data for period %f" %
              (resid_file, period))
        # Close input file
        input_file.close()
        # Return empty sets
        return data, distance

    # Index #7 has distance
    # Index #12 has component
    # Indexes #10 and #11 have period range for valid data

    # Read the rest of the file
    for line in input_file:
        items = line.split()
        comp = items[12]
        dist = items[7]
        tmin = items[10]
        tmax = items[11]
        value = items[index]
        # Skip components we don't know
        if comp != component:
            continue
        if period >= float(tmin) and period <= float(tmax):
            # Data within range, take it
            data.append(float(value))
            distance.append(float(dist))

    # Done reading the file
    input_file.close()

    # Write summary output for later processing
    output_file = open(summary_output, 'w')
    for dist, val in zip(distance, data):
        output_file.write("%f %f\n" % (dist, val))
    output_file.close()

    # Return the data we found
    return data, distance

def plot_dist_gof(resid_file, comp_label, input_dir,
                  output_dir, plot_title=None,
                  plot_periods=None, component=COMP_EXT_RD50):
    """
    Reads data from resid_file and plots a gof distance plot all
    periods
    """
    if plot_title is None:
        plot_title = ("GOF Comparison for %s" % (comp_label))

    if plot_periods is None:
        plot_periods = DIST_PERIODS

    # Collect all the data
    all_data = []
    all_distances = []
    # Read the residuals data
    for period in plot_periods:
        summary_output = os.path.join(input_dir, "%s-resid-%.3f-%s.txt" %
                                      (comp_label, period, component))
        data, distance = read_resid(resid_file, component, period, summary_output)
        all_data.append(data)
        all_distances.append(distance)

    # Now create the 2 plots, 1 linear and 1 log
    dist_linear_file = os.path.join(output_dir, "gof-dist-linear-%s-%s.png" %
                                    (comp_label, component))
    create_dist_gof(all_data, all_distances, plot_title,
                    plot_periods, comp_label, dist_linear_file)

    dist_log_file = os.path.join(output_dir, "gof-dist-log-%s-%s.png" %
                                 (comp_label, component))
    create_dist_gof(all_data, all_distances, plot_title,
                    plot_periods, comp_label, dist_log_file, log_scale=True)

def create_dist_gof(all_data, all_distances, plot_title,
                    plot_periods, comp_label, dist_gof_file, log_scale=False):
    """
    Creates a gof distance plots for all the data and distances
    provided
    """
    # Create figure
    num_plots = len(plot_periods)
    if len(plot_periods) % 2:
        num_plots = num_plots + 1
    num_columns = num_plots // 2
    fig, axs = pylab.plt.subplots(2, num_columns)
    fig.set_size_inches(18, 8)
    fig.subplots_adjust(left=0.05)
    fig.subplots_adjust(right=0.95)
    fig.subplots_adjust(hspace=0.25)

    # Find max, min values for x_axis
    if log_scale:
        min_x = 1
    else:
        min_x = 0
    max_x = 0
    for dist in all_distances:
        # Check if not empty
        if len(dist):
            max_x = max(max_x, max(dist))
    # If no data, set it to 90 (will get rounded to 100)
    if max_x == 0:
        max_x = 90
    # Round to the next 10'
    max_x = max_x + (10 - (max_x % 10))
    if log_scale and max_x > 100:
        # Round to the next 100'
        max_x = max_x + (100 - (max_x % 100))
    # y-axis is fixed
    min_y = MIN_Y_AXIS
    max_y = MAX_Y_AXIS

    # Convert to list
    subfigs = []
    for y_subplot in range(0, 2):
        for x_subplot in range(0, num_columns):
            subfigs.append(axs[y_subplot, x_subplot])

    # Good, now walk through each subfig
    for subfig, data, dist, period in zip(subfigs,
                                          all_data,
                                          all_distances,
                                          plot_periods):
        subfig.set_xlim(min_x, max_x)
        subfig.set_ylim(min_y, max_y)
        subfig.set_title("Period = %.3f s" % (period), size=8)
        subfig.set_ylabel("ln (data/model)", size=8)
        subfig.tick_params(labelsize=7)
        subfig.plot(dist, data, 'o', color='black',
                    label='_nolegend_')
        subfig.plot([min_x, max_x], [0.0, 0.0],
                    color='grey', label='_nolegend_')
        if log_scale:
            subfig.set_xscale('log')
        subfig.set_xlabel("Distance (km)", size=8)

    fig.suptitle('%s' % (plot_title), size=12)
    print("==> Created Distance GoF plot: %s" % (dist_gof_file))
    fig.savefig(dist_gof_file, format="png", transparent=False, dpi=plot_config.dpi)
    pylab.close()

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    parser = argparse.ArgumentParser(description="Generates PSA distance  comparison "
                                     " GoF plots.")
    parser.add_argument("--input-dir", dest="input_dir",
                        help="input directory")
    parser.add_argument("--output-dir", dest="output_dir",
                        help="output directory")
    parser.add_argument("--comp-label", dest="comp_label",
                        help="comparison label used for the output file prefix")
    parser.add_argument("--rotd100", dest="rotd100", action="store_true",
                        help="select RotD100 comparison")
    parser.add_argument("--rotd50", dest="rotd50", action="store_true",
                        help="select RotD50 comparison (default)")
    parser.add_argument("--plot-title", "--title", dest="plot_title",
                        help="set plot title")
    args = parser.parse_args()

    return args

def run():
    """
    Generate PSA Distance GoF plot
    """
    # Parse command-line options
    args = parse_arguments()

    # Look at paths
    input_dir = ""
    output_dir = ""
    plot_title = None
    if args.output_dir:
        output_dir = args.output_dir
    if args.input_dir:
        input_dir = args.input_dir
    if args.plot_title:
        plot_title = args.plot_title

    # Set mode
    mode = "rotd50"
    extension = "rd50"
    comps = ["psa5n", "psa5e", "rotd50"]
    if args.rotd100 and args.rotd50:
        print("[ERROR]: Please specify --rotd50 or --rotd100, not both!")
        sys.exit(1)
    if args.rotd100:
        mode = "rotd100"
        extension = "rd100"
        comps = ["rotd50", "rotd100", "ratio"]

    # Other plot parameters
    if not args.comp_label:
        print("[ERROR]: Please specify comp-label prefix!")
        sys,exit(1)

    # Select the residuals file
    resid_file = os.path.join(input_dir, "%s.%s-resid.txt" %
                              (args.comp_label, extension))
    plot_dist_gof(resid_file, args.comp_label, input_dir,
                  output_dir, plot_title)

if __name__ == '__main__':
    run()
