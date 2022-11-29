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

Creates a map gof plot for a list of periods
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import argparse
import matplotlib as mpl
if (mpl.get_backend() != 'agg'):
    mpl.use('Agg') # Disables use of Tk/X11
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.ticker import FormatStrFormatter
import pylab

# Import GMSVToolkit modules
from core import gmsvtoolkit_config
from utils import fault_utilities
from plots import plot_map
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
    requested period
    """
    # Start empty
    sta_x_data = []
    sta_y_data = []
    sta_resid_data = []

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
        print ("Residuals file %s does not have data for period %f" %
               (resid_file, period))
        # Close input file
        input_file.close()
        # Return empty sets
        return sta_x_data, sta_y_data, sta_resid_data

    # Index #3 has lon, #4 has lat
    # Index #12 has component
    # Indexes #10 and #11 have period range for valid data

    # Read the rest of the file
    for line in input_file:
        items = line.split()
        comp = items[12]
        lon = items[3]
        lat = items[4]
        tmin = items[10]
        tmax = items[11]
        value = items[index]
        # Skip components we don't know
        if comp != component:
            continue
        if period >= float(tmin) and period <= float(tmax):
            # Data within range, take it
            sta_x_data.append(float(lon))
            sta_y_data.append(float(lat))
            sta_resid_data.append(float(value))

    # Done reading the file
    input_file.close()

    # Write summary output for later processing
    output_file = open(summary_output, 'w')
    for lon, lat, val in zip(sta_x_data, sta_y_data, sta_resid_data):
        output_file.write("%f %f %f\n" % (lon, lat, val))
    output_file.close()

    # Return the data we found
    return sta_x_data, sta_y_data, sta_resid_data

def plot_map_gof(src_file, station_file, resid_file, comp_label, input_dir,
                 output_dir, plot_title=None, plot_periods=None,
                 component=COMP_EXT_RD50):
    """
    Reads data from resid_file and plots a map gof plot with a number
    of periods
    """
    if plot_title is None:
        plot_title = ("GOF Comparison for %s" % (comp_label))

    if plot_periods is None:
        plot_periods = DIST_PERIODS

    # Make sure we have a src or srf file
    if (src_file is None or src_file == "" or
        (not src_file.endswith(".srf") and
         not src_file.endswith(".src"))):
        # We need a SRC or SRF file to get the fault geometry
        return

    # Find plotting data files
    install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
    
    # Define boundaries to plot using the stations in the station file
    (north, south,
     east, west) = fault_utilities.set_boundaries_from_stations(station_file,
                                                                src_file)
    trace_file = "%s.trace" % (src_file)
    simple_station_file = "%s.simple" % (station_file)

    if src_file.endswith(".srf"):
        fault_utilities.write_fault_trace(src_file, trace_file)
    else:
        fault_utilities.write_simple_trace(src_file, trace_file)
    fault_utilities.write_simple_stations(station_file, simple_station_file)

    # Get hypo_lon, hypo_lat from src/srf file
    hypo_lon, hypo_lat = fault_utilities.calculate_epicenter(src_file)

    plot_region = [west, east, south, north]
    topo = os.path.join(install.PLOT_DATA_DIR, 'calTopo18.bf')
    coastal = os.path.join(install.PLOT_DATA_DIR, 'gshhs_h.txt')
    border = os.path.join(install.PLOT_DATA_DIR, 'wdb_borders_h.txt')

    # Collect all the data from the residuals file
    all_sta_x_data = []
    all_sta_y_data = []
    all_sta_resid_data = []
    for period in plot_periods:
        summary_output = os.path.join(input_dir, "%s-resid-map-%.3f-%s.txt" %
                                      (comp_label, period, component))
        sta_x_data, sta_y_data, sta_resid_data = read_resid(resid_file,
                                                            component,
                                                            period,
                                                            summary_output)
        all_sta_x_data.append(sta_x_data)
        all_sta_y_data.append(sta_y_data)
        all_sta_resid_data.append(sta_resid_data)

    # Now create the map GOF
    map_gof_file = os.path.join(output_dir, "gof-map-%s-%s.png" %
                                (comp_label, component))
    create_map_gof(all_sta_x_data, all_sta_y_data, all_sta_resid_data,
                   plot_title, plot_region, topo, coastal, border, trace_file,
                   plot_periods, comp_label, map_gof_file, hypo_lat=hypo_lat,
                   hypo_lon=hypo_lon)

def create_map_gof(all_sta_x_data, all_sta_y_data, all_sta_resid_data,
                   plot_title, plot_region, topo, coastal, border, fault,
                   plot_periods, comp_label, map_gof_file,
                   hypo_lat=None, hypo_lon=None):
    """
    Creates a gof distance plots for all the data and distances
    provided
    """
    # Read in topo data
    topo_points = plot_map.read_topo(topo, plot_region)

    # Read in fault data
    fault_x, fault_y = plot_map.read_fault(fault)

    # Read coastlines
    coast_x, coast_y = plot_map.read_coastal(coastal, plot_region)

    # Read borders
    bord_x, bord_y = plot_map.read_coastal(border, plot_region)

    # Create figure
    num_plots = len(plot_periods)
    if len(plot_periods) % 2:
        num_plots = num_plots + 1
    num_columns = num_plots // 2
    fig, axs = pylab.plt.subplots(2, num_columns)
    fig.set_size_inches(12, 6.5)
    #fig.autofmt_xdate()

    # Setup color scale
    cmap = cm.gist_gray
    norm = mcolors.Normalize(vmin=-2000.0, vmax=3000.0)

    # Convert to list
    subfigs = []
    for y_subplot in range(0, 2):
        for x_subplot in range(0, num_columns):
            subfigs.append(axs[y_subplot, x_subplot])

    # Fixed vmin and vmax for all plots
    vmin = -1.5
    vmax = 1.5
#     # Find vmin and vmax for all plots
#     vmin = 0.0
#     vmax = 0.0
#     for sta_resid_data in all_sta_resid_data:
#         if len(sta_resid_data):
#             vmin = min(vmin, min(sta_resid_data))
#             vmax = max(vmax, max(sta_resid_data))
#     # But make it symmetrical
#     if abs(vmax) > abs(vmin):
#         vmin = -vmax
#     else:
#         vmax = -vmin

    # Good, now walk through each subfig
    for (subfig, sta_x_data, sta_y_data,
         sta_resid_data, period) in zip(subfigs, all_sta_x_data, all_sta_y_data,
                                        all_sta_resid_data, plot_periods):
        # Plot basemap
        subfig.imshow(topo_points, cmap=cmap, norm=norm,
                      extent=plot_region, interpolation='nearest')

        # Freeze the axis extents
        subfig.set_autoscale_on(False)

        # Plot coast lines
        for idx in range(0, len(coast_x)):
            subfig.plot(coast_x[idx], coast_y[idx], linestyle='-', color='0.75')

        # Plot borders
        for idx in range(0, len(bord_x)):
            subfig.plot(bord_x[idx], bord_y[idx], linestyle='-', color='0.75')

        # Plot fault trace
        subfig.plot(fault_x, fault_y, linestyle='-', color='k', linewidth=1.0)

        # If we don't have at least 1 station for this period, create
        # a fake station outside of the map area so that we can still
        # create the empty plot with the colobar to the right
        if not len(sta_x_data) or not len(sta_y_data):
            sta_x_data = [1000.0]
            sta_y_data = [1000.0]
            sta_resid_data = [0.0]

        # Plot hypocenter
        if hypo_lat is not None and hypo_lon is not None:
            hypo_lat = [hypo_lat]
            hypo_lon = [hypo_lon]
            subfig.scatter(hypo_lon, hypo_lat, marker=(5, 1, 0),
                           color='y', s=50)

        # Plot the stations
        im = subfig.scatter(sta_x_data, sta_y_data, s=20, c=sta_resid_data,
                            cmap=cm.jet_r, vmin=vmin, vmax=vmax,
                            marker='o', edgecolors='k')

        # Adding colorbars to the right of each row
#        if DIST_PERIODS.index(period) % num_columns == num_columns - 1:
#            subfig.figure.colorbar(im, ax=subfig)

        # Set degree formatting of tick values
        major_formatter = FormatStrFormatter(u'%.1f\u00b0')
        subfig.xaxis.set_major_formatter(major_formatter)
        subfig.yaxis.set_major_formatter(major_formatter)

#        # Turn on ticks for both sides of axis
#        for tick in subfig.xaxis.get_major_ticks():
#            tick.label1On = True
#            tick.label2On = True
#        for tick in subfig.yaxis.get_major_ticks():
#            tick.label1On = True
#            tick.label2On = True

        # Set font size
        for tick in subfig.get_xticklabels():
            tick.set_fontsize(6)
            tick.set_ha("right")
            tick.set_rotation(30)
        for tick in subfig.get_yticklabels():
            tick.set_fontsize(6)

        subfig.set_title("Period = %.3f s" % (period), size=8)

    fig.subplots_adjust(left=0.05, right=0.91, hspace=0.0,
                        top=0.95, bottom=0.05)
    colorbar_ax = fig.add_axes([0.93, 0.20, 0.02, 0.6])
    fig.colorbar(im, cax=colorbar_ax)
    fig.suptitle('%s' % (plot_title), size=12)
    print("==> Created Map GoF plot: %s" % (map_gof_file))
    fig.savefig(map_gof_file, format="png", transparent=False, dpi=plot_config.dpi)
    pylab.close()

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    parser = argparse.ArgumentParser(description="Generates PSA Vs30 comparison "
                                     " GoF plot.")
    parser.add_argument("--input-dir", dest="input_dir",
                        help="input directory")
    parser.add_argument("--output-dir", dest="output_dir",
                        help="output directory")
    parser.add_argument("--src-file", "--src", dest="src_file",
                        help="source description file (SRC file)")
    parser.add_argument("--station-list", "-s", dest="station_list",
                        help="station list")
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
    Generate PSA Vs30 GoF plot
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

    # Needed parameters
    if not args.src_file:
        print("[ERROR]: Please specify source description file!")
        sys.exit(1)
    src_file = os.path.join(input_dir, args.src_file)
    if not args.station_list:
        print("[ERROR]: Please specify station list!")
        sys.exit(1)
    station_file = os.path.join(input_dir, args.station_list)
    
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
    plot_map_gof(src_file, station_file, resid_file, args.comp_label,
                 input_dir, output_dir, plot_title)
    
if __name__ == '__main__':
    run()
