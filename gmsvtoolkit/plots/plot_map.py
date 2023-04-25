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

This module plots station map and fault trace
"""
from __future__ import division, print_function

# Import Python Modules
import os
import sys
import struct
import argparse
import numpy as np
import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('Agg') # Disables use of Tk/X11
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.ticker import FormatStrFormatter
import pylab

# Import plot config file
from core import gmsvtoolkit_config
from utils import fault_utilities
from plots import plot_config

# GMT "bf" native binary header and format
GMT_HDR_FORMAT = '<3i10d80s80s80s80s320s160s'
GMT_DATA_FORMAT = '<f'
# Note: this script uses the "bf" native C float format
# The existing GMT topo grid in NetCDF format can be
# converted to this format with the following command:
# $ grdreformat calTopo18.grd calTopo18.test=bf -V

def in_region(point, plotregion):
    """
    Returns true if point falls within the plotregion
    """
    if ((point[0] >= plotregion[0]) and
        (point[0] < plotregion[1]) and
        (point[1] >= plotregion[2]) and
        (point[1] < plotregion[3])):
        return True
    else:
        return False

def read_fault(filename):
    """
    Read in fault file
    """
    fault_x = []
    fault_y = []
    fault_file = open(filename, 'r')

    for segment in fault_file:
        x, y = segment.split()
        fault_x.append(float(x))
        fault_y.append(float(y))

    fault_file.close()

    return fault_x, fault_y

def read_stations(filename):
    """
    Read in station list
    """
    sta_x = []
    sta_y = []
    station_file = open(filename, 'r')

    for station in station_file:
        x, y, _ = station.split()
        sta_x.append(float(x))
        sta_y.append(float(y))

    station_file.close()

    return sta_x, sta_y

def read_coastal(filename, plotregion):
    """
    Read in coastal geometry as a list of lists of polygon segments
    """
    # Initialize all variables
    coast_x = []
    coast_y = []
    poly_x = []
    poly_y = []
    segnum = 0
    segments = 0

    # Read in file
    polygons = open(filename, 'r')

    # Parse polygons
    for line in polygons:
        tokens = line.split()
        if (tokens[0] == 'P') or (tokens[0] == 'L'):
            if (len(poly_x) > 0):
                coast_x.append(poly_x)
                coast_y.append(poly_y)
            poly_x = []
            poly_y = []
            segnum = 0
            segments = int(tokens[2])
        else:
            if (segnum >= segments):
                print("Invalid number of segments in " +
                      "polygon from file %s" % (filename))
                return([], [])
            segnum = segnum + 1
            x = float(tokens[0])
            y = float(tokens[1])
            if (in_region([x, y], plotregion)):
                poly_x.append(x)
                poly_y.append(y)
            else:
                if (len(poly_x) > 0):
                    coast_x.append(poly_x)
                    coast_y.append(poly_y)
                poly_x = []
                poly_y = []

    # Remember to close file
    polygons.close()

    return coast_x, coast_y

def read_topo(filename, plotregion):
    """
    Reads in topo data that is saved in GMT format:
    bf GMT native, C-binary format (float)
    Header size is 892 bytes
    """
    # Open input file
    topo_file = open(filename, 'rb')

    # Parse header
    buf = topo_file.read(struct.calcsize(GMT_HDR_FORMAT))
    header = struct.unpack(GMT_HDR_FORMAT, buf)
    topo_dims = [header[0], header[1]]
    topo_region = [header[3], header[4], header[5], header[6]]

    # Read elevation values
    data = np.arange(topo_dims[0] * topo_dims[1],
                     dtype=float).reshape(topo_dims[1],
                                          topo_dims[0])

    buf = topo_file.read(topo_dims[0] * topo_dims[1] *
                         struct.calcsize(GMT_DATA_FORMAT))
    topo_file.close()

    # Data is x-fast
    for y in range(0, topo_dims[1]):
        for x in range(0, topo_dims[0]):
            offset = ((y * topo_dims[0] + x) *
                      struct.calcsize(GMT_DATA_FORMAT))
            data[y][x] = struct.unpack(GMT_DATA_FORMAT,
                                       buf[offset:offset + 4])[0]

    # Pull out sub-matrix for plotregion, and invert y-axis
    x0 = int((plotregion[0] - topo_region[0]) / header[9])
    y1 = topo_dims[1] - int((plotregion[2] -
                             topo_region[2]) / header[10])
    x1 = int((plotregion[1] - topo_region[0]) / header[9])
    y0 = topo_dims[1] - int((plotregion[3] -
                             topo_region[2]) / header[10])
    subdata = np.arange((x1 - x0) * (y1 - y0),
                        dtype=float).reshape(y1 - y0, x1 - x0)

    for y in range(y0, y1):
        for x in range(x0, x1):
            if ((y >= 0) and (y < topo_dims[1]) and
                (x >= 0) and (x < topo_dims[0])):
                subdata[y - y0][x - x0] = data[y][x]

    # Mask array to hide NaNs
    masked = np.ma.masked_invalid(subdata)

    # All done
    return masked

def plot_station_map(plottitle, plotregion, topo, coastal, border,
                     fault, sta, map_prefix, hypocenter_list=None):
    """
    Genereate the station map plot
    """
    # Read in topo data
    topo_points = read_topo(topo, plotregion)

    # Read in fault data
    fault_x, fault_y = read_fault(fault)

    # Read in station data
    sta_x, sta_y = read_stations(sta)

    # Read coastlines
    coast_x, coast_y = read_coastal(coastal, plotregion)

    # Read borders
    bord_x, bord_y = read_coastal(border, plotregion)

    # Set up ticks to match matplotlib 1.x style
    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['ytick.direction'] = 'in'
    mpl.rcParams['xtick.top'] = True
    mpl.rcParams['ytick.right'] = True
    mpl.rcParams['patch.force_edgecolor'] = True
    mpl.rcParams['patch.facecolor'] = 'b'

    # Set plot dims
    pylab.gcf().set_size_inches(6, 6)
    pylab.gcf().clf()

    # Adjust title y-position
    t = pylab.title(plottitle, size=12)
    t.set_y(1.06)

    # Setup color scale
    cmap = cm.gist_earth
    norm = mcolors.Normalize(vmin=-1000.0, vmax=3000.0)

    # Plot basemap
    pylab.imshow(topo_points, cmap=cmap, norm=norm,
                 extent=plotregion, interpolation='nearest')

    # Freeze the axis extents
    pylab.gca().set_autoscale_on(False)

    # Plot coast lines
    for i in range(0, len(coast_x)):
        pylab.plot(coast_x[i], coast_y[i], linestyle='-', color='0.5')

    # Plot borders
    for i in range(0, len(bord_x)):
        pylab.plot(bord_x[i], bord_y[i], linestyle='-', color='0.75')

    # Plot fault trace
    pylab.plot(fault_x, fault_y, linestyle='-', color='k', linewidth=1.0)

    # Plot stations
    pylab.plot(sta_x, sta_y, marker='o', color='r', linewidth=0, markersize=4)

    # Plot hypocenter if provided
    if hypocenter_list is not None:
        hypo_lat = []
        hypo_lon = []
        for hypocenter in hypocenter_list:
            hypo_lat.append(hypocenter['lat'])
            hypo_lon.append(hypocenter['lon'])
        pylab.plot(hypo_lon, hypo_lat, marker='*',
                   markersize=12, color='y', linewidth=0)

    # Set degree formatting of tick values
    majorFormatter = FormatStrFormatter(u'%.1f\u00b0')
    pylab.gca().xaxis.set_major_formatter(majorFormatter)
    pylab.gca().yaxis.set_major_formatter(majorFormatter)

    # Turn on ticks for both sides of axis
    for tick in pylab.gca().xaxis.get_major_ticks():
        tick.label1On = True
        tick.label2On = True
    for tick in pylab.gca().yaxis.get_major_ticks():
        tick.label1On = True
        tick.label2On = True

    # Set font size
    for tick in pylab.gca().get_xticklabels():
        tick.set_fontsize(8)
    for tick in pylab.gca().get_yticklabels():
        tick.set_fontsize(8)

    print("==> Creating Plot: %s.png" % (map_prefix))
    pylab.savefig('%s.png' % (map_prefix), format="png",
                  transparent=False, dpi=plot_config.dpi)
    pylab.close()

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    parser = argparse.ArgumentParser(description="Generates station map plot.")
    parser.add_argument("--input-dir", dest="input_dir",
                        help="input directory")
    parser.add_argument("--output-dir", dest="output_dir",
                        help="output directory")
    parser.add_argument("--src-file", "--src", dest="src_file",
                        help="source description file (SRC or SRF file)")
    parser.add_argument("--station-list", "-s", dest="station_list",
                        help="station list")
    parser.add_argument("--plot-title", "--title", dest="plot_title",
                        help="set plot title")
    args = parser.parse_args()

    return args

def run():
    """
    Generate station plot
    """
    args = parse_arguments()

    # Look at paths
    input_dir = ""
    output_dir = ""
    plot_title = "Fault Trace with Stations"
    if args.output_dir:
        output_dir = args.output_dir
    if args.input_dir:
        input_dir = args.input_dir
    if args.plot_title:
        plot_title = args.plot_title

        # Needed parameters
    if not args.src_file:
        print("[ERROR]: Please specify a source description file!")
        sys.exit(1)
    # Make sure we have a src or srf file
    if (args.src_file is None or args.src_file == "" or
        (not args.src_file.endswith(".srf") and
         not args.src_file.endswith(".src"))):
        # We need a SRC or SRF file to get the fault geometry
        print("[ERROR]: Please specify a .src or .srf source description file!")
        sys.exit(1)
    if not args.station_list:
        print("[ERROR]: Please specify station list!")
        sys.exit(1)
    # Set up paths for station file and src_file
    if input_dir:
        station_list = os.path.join(input_dir, args.station_list)
        src_file = os.path.join(input_dir, args.src_file)
    else:
        station_list = os.path.abspath(args.station_list)
        src_file = os.path.abspath(args.src_file)
    # All good, create map plot
    plot_map(station_list, src_file, plot_title, output_dir)

def plot_map(station_file, src_file, plot_title, output_dir):
    """
    Generate map plot with stations and and fault
    """
    # Find plotting data files
    install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()

    # Define boundaries to plot using the stations in the station file
    (north, south,
     east, west) = fault_utilities.set_boundaries_from_stations(station_file,
                                                                src_file)
    trace_file = os.path.join(output_dir,
                              "%s.trace" %
                              (os.path.basename(src_file)))
    simple_station_file = os.path.join(output_dir,
                                       "%s.simple" %
                                       (os.path.basename(station_file)))
    map_prefix = os.path.join(output_dir, "station_map")

    if src_file.endswith(".srf"):
        fault_utilities.write_fault_trace(src_file, trace_file)
    else:
        fault_utilities.write_simple_trace(src_file, trace_file)
    fault_utilities.write_simple_stations(station_file, simple_station_file)

    # Get hypo_lon, hypo_lat from src/srf file
    hypo_coord = {}
    hypo_lon, hypo_lat = fault_utilities.calculate_epicenter(src_file)
    hypo_coord['lat'] = hypo_lat
    hypo_coord['lon'] = hypo_lon

    plot_region = [west, east, south, north]
    topo = os.path.join(install.PLOT_DATA_DIR, 'calTopo18.bf')
    coastal = os.path.join(install.PLOT_DATA_DIR, 'gshhs_h.txt')
    border = os.path.join(install.PLOT_DATA_DIR, 'wdb_borders_h.txt')

    plot_station_map(plot_title, plot_region, topo, coastal,
                     border, trace_file, simple_station_file,
                     map_prefix, [hypo_coord])

if __name__ == '__main__':
    run()
