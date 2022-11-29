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

Fault utilities used in the GMSVToolkit
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import math
import shutil
import tempfile

# Import Broadband modules
from core import gmsvtoolkit_config
from core import exceptions
from utils import os_utilities
from utils import srf_utilities
from utils import src_utilities
from core.station_list import StationList

# Use an extra buffer to plot the region around all stations (in degrees)
BUFFER_LATITUDE = 0.25
BUFFER_LONGITUDE = 0.25

def calculate_hypo_depth(srcfile):
    """
    Calculates the hypocenter depth using the SRC file parameters
    """
    cfgdict = src_utilities.parse_properties(srcfile)

    # Look for the needed keys in the SRC file
    try:
        depth_to_top = cfgdict["depth_to_top"]
    except KeyError:
        exceptions.ParameterError("SRC file missing DEPTH_TO_TOP parameter!")
    depth_to_top = float(depth_to_top)

    try:
        dip = cfgdict["dip"]
    except KeyError:
        exceptions.ParameterError("SRC file missing DIP parameter!")
    dip = float(dip)

    try:
        hypo_down_dip = cfgdict["hypo_down_dip"]
    except KeyError:
        exceptions.ParameterError("SRC file missing HYPO_DOWN_DIP parameter!")
    hypo_down_dip = float(hypo_down_dip)

    # Now, calculate the hypocenter depth
    hypo_depth = depth_to_top + hypo_down_dip * math.sin(math.radians(dip))

    # Done
    return hypo_depth

def calculate_epicenter(input_file):
    """
    This function returns the epicenter of an event using either a SRC
    file or a SRF file to look for the hypocenter location. It uses
    Rob Graves' xy2ll utility to convert the coordinates to lat/lon.
    """
    # If we have a SRF file, we already have a function that does this
    if input_file.endswith(".srf"):
        # Get information from srf file
        hypo_lon, hypo_lat, _ = srf_utilities.get_hypocenter(input_file)
        return hypo_lon, hypo_lat

    # If we don't have a SRC file, we should print an error here
    if not input_file.endswith(".src"):
        exceptions.ParameterError("input file should be a SRC or SRF file!")

    # Ok, we have a SRC file
    # Get information from SRC file
    cfgdict = src_utilities.parse_properties(input_file)

    try:
        strike = cfgdict["strike"]
    except KeyError:
        exceptions.ParameterError("SRC file missing STRIKE parameter!")
    strike = float(strike)

    try:
        dip = cfgdict["dip"]
    except KeyError:
        exceptions.ParameterError("SRC file missing DIP parameter!")
    dip = float(dip)

    try:
        hypo_down_dip = cfgdict["hypo_down_dip"]
    except KeyError:
        exceptions.ParameterError("SRC file missing "
                                  "HYPO_DOWN_DIP parameter!")
    hypo_down_dip = float(hypo_down_dip)

    try:
        hypo_along_strike = cfgdict["hypo_along_stk"]
    except KeyError:
        exceptions.ParameterError("SRC file missing "
                                  "HYPO_ALONG_STK parameter!")
    hypo_along_strike = float(hypo_along_strike)

    try:
        lat_top_center = cfgdict["lat_top_center"]
    except KeyError:
        exceptions.ParameterError("SRC file missing "
                                  "LAT_TOP_CENTER parameter!")
    lat_top_center = float(lat_top_center)

    try:
        lon_top_center = cfgdict["lon_top_center"]
    except KeyError:
        exceptions.ParameterError("SRC file missing "
                                  "LON_TOP_CENTER parameter!")
    lon_top_center = float(lon_top_center)

    # Ok, we have all the parameters that we need!
    hypo_perpendicular_strike = hypo_down_dip * math.cos(math.radians(dip))

    # Now call xy2ll program to convert it to lat/long
    # Create temp directory to avoid any race conditions
    tmpdir = tempfile.mkdtemp(prefix="bbp-")
    hypfile = os.path.join(tmpdir, "src_hypo.tmp")
    install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
    cmd = ('echo "%f %f" | %s mlat=%f mlon=%f xazim=%f > %s' %
           (hypo_along_strike, hypo_perpendicular_strike,
            os.path.join(install.GP_BIN_DIR, "xy2ll"),
            lat_top_center, lon_top_center, strike, hypfile))
    os_utilities.runprog(cmd, print_cmd=False)
    src_hypo_fp = open(hypfile, 'r')
    src_hypo_data = src_hypo_fp.readline()
    src_hypo_fp.close()
    src_hypo = [float(val) for val in src_hypo_data.split()]
    # Delete temp directory
    shutil.rmtree(tmpdir)

    # Return calculated lon/lat
    return src_hypo[0], src_hypo[1]

def write_simple_stations(station_file, out_file):
    """
    This function parses the station file and writes a simple
    version with just longitude, latitude, and station code
    """
    station_list = StationList(station_file).get_station_list()
    fp_out = open(out_file, 'w')
    for station in station_list:
        fp_out.write("%f %f %s\n" % (station.lon, station.lat, station.scode))
    fp_out.flush()
    fp_out.close()

def write_fault_trace(srf_file, out_file):
    """
    This function reads the srf file and outputs a trace file
    """
    all_points = []

    # Figure out SRF file version
    version, num_segments , nstk = srf_utilities.get_srf_info(srf_file)

    # Reads the points for each segment
    for segment in range(0, num_segments):
        seg_points = srf_utilities.read_srf_trace(srf_file, segment, nstk[segment])
        all_points = all_points + seg_points

    # Now, open output file, and write the data
    trace_file = open(out_file, 'w')
    for point in all_points:
        trace_file.write("%f %f\n" % (point[0], point[1]))
    trace_file.flush()
    trace_file.close()

    # Return trace
    return all_points

def calculate_fault_edge(lat1, lon1, dist, bearing):
    """
    Given a start point, distance and bearing, calculate the
    destination point
    """
    radius = 6371.0
    to_rad = 0.0174532925

    lat2 = math.asin(math.sin(lat1*to_rad) * math.cos(dist/radius) +
                     math.cos(lat1*to_rad) * math.sin(dist/radius) *
                     math.cos(bearing*to_rad)) / to_rad

    lon2 = (lon1*to_rad +
            math.atan2(math.sin(bearing*to_rad) * math.sin(dist/radius) *
                       math.cos(lat1*to_rad), math.cos(dist/radius) -
                       math.sin(lat1*to_rad) *
                       math.sin(lat2*to_rad))) / to_rad
    return lat2, lon2

def is_new_point_south_east(lat, lon, new_lat, new_lon):
    """
    Returns true if new_lat/new_lon is south/east of lat/lon
    """
    if lat is None or lon is None:
        return True
    if new_lon < lon:
        return False
    if new_lon > lon:
        return True
    if new_lat < lat:
        return True
    return False

def calculate_fault_edges_from_srf(srf_file):
    """
    Calculates the edges of the fault plane from the SRF file
    """
    # Get number of segments
    num_segments = srf_utilities.get_srf_num_segments(srf_file)

    # Read SRF parameters
    params = []
    for segment in range(0, num_segments):
        params.append(srf_utilities.get_srf_params(srf_file, segment))

    # Now compute what we need
    se_lat = None
    se_lon = None
    nw_lat = None
    nw_lon = None
    for segment in params:
        dist = segment["fault_len"] / 2.0
        strike = segment["azimuth"]
        p_lat1, p_lon1 = calculate_fault_edge(segment["lat"], segment["lon"],
                                          dist, strike)
        # Reverse direction
        if strike >= 180:
            strike = strike - 180
        else:
            strike = strike + 180
        p_lat2, p_lon2 = calculate_fault_edge(segment["lat"], segment["lon"],
                                          dist, strike)

        # Update current coordinates
        if is_new_point_south_east(p_lat1, p_lon1, p_lat2, p_lon2):
            s_lat = p_lat2
            s_lon = p_lon2
            n_lat = p_lat1
            n_lon = p_lon1
        else:
            s_lat = p_lat1
            s_lon = p_lon1
            n_lat = p_lat2
            n_lon = p_lon2

        if se_lat is None or se_lon is None:
            se_lat = s_lat
            se_lon = s_lon
        elif is_new_point_south_east(se_lat, se_lon, s_lat, s_lon):
            se_lat = s_lat
            se_lon = s_lon

        if nw_lat is None or nw_lon is None:
            nw_lat = n_lat
            nw_lon = n_lon
        elif not is_new_point_south_east(nw_lat, nw_lon, n_lat, n_lon):
            nw_lat = n_lat
            nw_lon = n_lon

    return se_lat, se_lon, nw_lat, nw_lon

def calculate_fault_edges_from_src(a_src_file):
    """
    Calculates the edges of the fault plane
    """
    # Read data from SRC file
    cfg_dict = src_utilities.parse_properties(a_src_file)
    if not "fault_length" in cfg_dict:
        raise exceptions.ParameterError("SRC file missing fault_length!")
    if not "strike" in cfg_dict:
        raise exceptions.ParameterError("SRC file missing strike!")
    if not "lat_top_center" in cfg_dict:
        raise exceptions.ParameterError("SRC file missing lat_top_center!")
    if not "lon_top_center" in cfg_dict:
        raise exceptions.ParameterError("SRC file missing lon_top_center!")
    fault_length = float(cfg_dict["fault_length"])
    strike = float(cfg_dict["strike"])
    lat_top_center = float(cfg_dict["lat_top_center"])
    lon_top_center = float(cfg_dict["lon_top_center"])
    dist = fault_length / 2
    # Calculate 1st edge
    lat1, lon1 = calculate_fault_edge(lat_top_center, lon_top_center,
                                      dist, strike)
    # Reverse direction
    if strike >= 180:
        strike = strike - 180
    else:
        strike = strike + 180
    # Calculate 2nd edge
    lat2, lon2 = calculate_fault_edge(lat_top_center, lon_top_center,
                                      dist, strike)

    return lat1, lon1, lat_top_center, lon_top_center, lat2, lon2

def write_simple_trace(a_src_file, out_file):
    """
    This function reads the SRC file and calculates the fault trace
    """
    points = []

    (lat1, lon1, lat_top_center,
     lon_top_center, lat2, lon2) = calculate_fault_edges_from_src(a_src_file)

    points.append([lon1, lat1])
    points.append([lon_top_center, lat_top_center])
    points.append([lon2, lat2])

    # Now, open output file, and write the data
    trace_file = open(out_file, 'w')
    for point in points:
        trace_file.write("%f %f\n" % (point[0], point[1]))
    trace_file.flush()
    trace_file.close()
    # Save trace
    return points

def set_boundaries_from_stations(station_file, a_input_file):
    """
    This function sets the north, south, east, and west boundaries
    of the region we should plot, using the stations' locations in
    the station file
    """
    # Start without anything
    north = None
    south = None
    east = None
    west = None

    if a_input_file.endswith(".src"):
        # Read fault information from SRC file
        lat1, lon1, _, _, lat2, lon2 = calculate_fault_edges_from_src(a_input_file)
    elif a_input_file.endswith(".srf"):
        # Read fault information from SRF file
        lat1, lon1, lat2, lon2 = calculate_fault_edges_from_srf(a_input_file)
    else:
        exceptions.ParameterError("Cannot determine input_file format!")

    # First we read the stations
    stations = StationList(station_file).get_station_list()
    # Now go through each one, keeping track of its locations
    for station in stations:
        # If this is the first station, use its location
        if north is None:
            north = station.lat
            south = station.lat
            east = station.lon
            west = station.lon
            # Next station
            continue
        if station.lat > north:
            north = station.lat
        elif station.lat < south:
            south = station.lat
        if station.lon > east:
            east = station.lon
        elif station.lon < west:
            west = station.lon

    # Make sure fault is there too
    if min(lat1, lat2) < south:
        south = min(lat1, lat2)
    if max(lat1, lat2) > north:
        north = max(lat1, lat2)
    if min(lon1, lon2) < west:
        west = min(lon1, lon2)
    if max(lon1, lon2) > east:
        east = max(lon1, lon2)

    # Great, now we just add a buffer on each side
    if north < (90 - BUFFER_LATITUDE):
        north = north + BUFFER_LATITUDE
    else:
        north = 90
    if south > (-90 + BUFFER_LATITUDE):
        south = south - BUFFER_LATITUDE
    else:
        south = -90
    if east < (180 - BUFFER_LONGITUDE):
        east = east + BUFFER_LONGITUDE
    else:
        east = 180
    if west > (-180 + BUFFER_LONGITUDE):
        west = west - BUFFER_LONGITUDE
    else:
        west = -180

    return north, south, east, west
