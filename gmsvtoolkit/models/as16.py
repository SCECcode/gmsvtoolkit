#!/usr/bin/env python3
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
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import math
import argparse

# Import GMSV Toolkit modules
from core import gmsvtoolkit_config
from core.station_list import StationList
from utils.src_utilities import parse_src_file

# Import Pynga and its utilities
from models.pynga import utils as putils

def calculate_as16(m, r, mech, vs30, z1, cj):
    """
    This function implements the Afshari and Stewart (2016) GMPE for
    significant duration

    Input parameters:
    M: Magnitude
    R: Rupture distance (km)
    Mech: Rupture mechanism (0=unknown, 1=Normal, 2=Reverse, 3=Strike-slip)
    Vs30: Time-averaged shear wave velocity of the upper 30m of the site (m/s)
    z1: Basin depth, depth to shear wave velovity of 1000 m/s isosurface (m)
    Enter -999 if unknown
    CJ: Enter 0 for California, and 1 for Japan, Enter -999 otherwise

    Output: 5-75, 5-95, and 20-80 significant duration, 5-75, 5-95, and 20-80
    between-event standard deviation (tau), 5-75, 5-95, and 20-80 within-event
    standard deviation.
    """

    # Calculating differential basin depth
    if cj == 0:
        muz1 = math.exp(-7.15/4.0*math.log((vs30**4+570.94**4) /
                                           (1360.0**4+570.94**4)) -
                        math.log(1000))
    else:
        muz1 = math.exp(-5.23/2.0*math.log((vs30**2+412.39**2) /
                                           (1360.0**2+412.39**2)) -
                        math.log(1000))
    if z1 == -999:
        dz1 = 0.0
    else:
        dz1 = z1 - muz1

    if cj == -999:
        dz1 = 0.0

    # 5-75 significant duration
    # Parameters
    # Source
    m1 = 5.35
    m2 = 7.15
    b00 = 1.280
    b01 = 1.555
    b02 = 0.7806
    b03 = 1.279
    b10 = 5.576
    b11 = 4.992
    b12 = 7.061
    b13 = 5.578
    b2 = 0.9011
    b3 = -1.684
    mstar = 6

    # Path
    c1 = 0.1159
    rr1 = 10.0
    rr2 = 50.0
    c2 = 0.1065
    c3 = 0.0682

    # Site
    c4 = -0.2246
    vref = 368.2
    v1 = 600.0
    c5 = 0.0006
    dz1ref = 200.0

    if mech == 0:
        b1 = b10
        b0 = b00
    elif mech == 1:
        b1 = b11
        b0 = b01
    elif mech == 2:
        b1 = b12
        b0 = b02
    elif mech == 3:
        b1 = b13
        b0 = b03

    if m < m2:
        ds = math.exp(b1+b2*(m-mstar))
    else:
        ds = math.exp(b1+b2*(m2-mstar)+b3*(m-m2))

    # Stress drop term
    lnsd = ds
    lnsd = lnsd / (10**(1.5*m+16.05))
    lnsd = lnsd**(-1.0/3.0)
    source = lnsd / (3.2*4.9*1000000)

    if m < m1:
        source = b0

    # Path term
    if r < rr1:
        path = c1 * r
    elif r < rr2:
        path = c1 * rr1 + c2 * (r-rr1)
    else:
        path = c1 * rr1 + c2 * (rr2-rr1) + c3 * (r-rr2)

    # Site term
    if vs30 < v1:
        site = c4 * math.log(vs30 / vref)
    else:
        site = c4 * math.log(v1 / vref)

    if dz1 <= dz1ref:
        site = site + c5 * dz1
    else:
        site = site + c5 * dz1ref

    lnsd = math.log(source + path) + site
    sd575 = math.exp(lnsd)

    # 5-95 significant duration
    # Parameters
    # Source
    m1 = 5.2
    m2 = 7.4
    b00 = 2.182
    b01 = 2.541
    b02 = 1.612
    b03 = 2.302
    b10 = 3.628
    b11 = 3.170
    b12 = 4.536
    b13 = 3.467
    b2 = 0.9443
    b3 = -3.911
    mstar = 6
    # Path
    c1 = 0.3165
    # ee1 = 10.0
    rr1 = 10.0
    rr2 = 50.0
    c2 = 0.2539
    c3 = 0.0932
    # Site
    c4 = -0.3183
    vref = 369.9
    v1 = 600.0
    c5 = 0.0006
    dz1ref = 200.0

    if mech == 0:
        b1 = b10
        b0 = b00
    elif mech == 1:
        b1 = b11
        b0 = b01
    elif mech == 2:
        b1 = b12
        b0 = b02
    elif mech == 3:
        b1 = b13
        b0 = b03

    if m < m2:
        ds = math.exp(b1+b2*(m-mstar))
    else:
        ds = math.exp(b1+b2*(m2-mstar)+b3*(m-m2))

    # Stress drop term
    lnsd = ds
    lnsd = lnsd / (10**(1.5*m+16.05))
    lnsd = lnsd**(-1.0/3.0)
    source = lnsd / (3.2*4.9*1000000)

    if m < m1:
        source = b0

    if r < rr1:
        path = c1 * r
    elif r < rr2:
        path = c1 * rr1 + c2 * (r-rr1)
    else:
        path = c1 * rr1 + c2 * (rr2-rr1) + c3 * (r-rr2)

    # Path term
    if vs30 < v1:
        site = c4 * math.log(vs30 / vref)
    else:
        site = c4 * math.log(v1 / vref)

    if dz1 <= dz1ref:
        site = site + c5 * dz1
    else:
        site = site + c5 * dz1ref

    # Site term
    lnsd = math.log(source + path) + site
    sd595 = math.exp(lnsd)

    # 20-80 significant duration
    # Parameters
    # Source
    m1 = 5.2
    m2 = 7.4
    b00 = 0.8822
    b01 = 1.409
    b02 = 0.7729
    b03 = 0.8804
    b10 = 6.182
    b11 = 4.778
    b12 = 6.579
    b13 = 6.188
    b2 = 0.7414
    b3 = -3.164
    mstar = 6.0
    # Path
    c1 = 0.0646
    rr1 = 10.0
    rr2 = 50.0
    c2 = 0.0865
    c3 = 0.0373
    # Site
    c4 = -0.4237
    vref = 369.6
    v1 = 600.0
    c5 = 0.0005
    dz1ref = 200.0

    if mech == 0:
        b1 = b10
        b0 = b00
    elif mech == 1:
        b1 = b11
        b0 = b01
    elif mech == 2:
        b1 = b12
        b0 = b02
    elif mech == 3:
        b1 = b13
        b0 = b03

    if m < m2:
        ds = math.exp(b1+b2*(m-mstar))
    else:
        ds = math.exp(b1+b2*(m2-mstar)+b3*(m-m2))

    # Stress drop term
    lnsd = ds
    lnsd = lnsd / (10**(1.5*m+16.05))
    lnsd = lnsd**(-1.0/3.0)
    source = lnsd / (3.2*4.9*1000000)

    if m < m1:
        source = b0

    if r < rr1:
        path = c1 * r
    elif r < rr2:
        path = c1 * rr1 + c2 * (r-rr1)
    else:
        path = c1 * rr1 + c2 * (rr2-rr1) + c3 * (r-rr2)

    # Path term
    if vs30 < v1:
        site = c4 * math.log(vs30 / vref)
    else:
        site = c4 * math.log(v1 / vref)

    if dz1 <= dz1ref:
        site = site + c5 * dz1
    else:
        site = site + c5 * dz1ref

    # Site term
    lnsd = math.log(source + path) + site
    sd2080 = math.exp(lnsd)

    # within-site standard deviation
    # Parameters
    phi1575 = 0.54
    phi2575 = 0.41
    phi1595 = 0.43
    phi2595 = 0.35
    phi12080 = 0.56
    phi22080 = 0.45

    if m < 5.5:
        phi575 = phi1575
        phi595 = phi1595
        phi2080 = phi12080
    elif m < 5.75:
        phi575 = phi1575 + (phi2575-phi1575)*(m-5.5)/(5.75-5.5)
        phi595 = phi1595 + (phi2595-phi1595)*(m-5.5)/(5.75-5.5)
        phi2080 = phi12080 + (phi22080-phi12080)*(m-5.5)/(5.75-5.5)
    else:
        phi575 = phi2575
        phi595 = phi2595
        phi2080 = phi22080

    # Between-site standard deviation
    # Parameters
    tau1575 = 0.28
    tau2575 = 0.25
    tau1595 = 0.25
    tau2595 = 0.19
    tau12080 = 0.3
    tau22080 = 0.19

    if m < 6.5:
        tau575 = tau1575
        tau595 = tau1595
        tau2080 = tau12080
    elif m < 7.0:
        tau575 = tau1575 + (tau2575-tau1575)*(m-6.5)/(7.0-6.5)
        tau595 = tau1595 + (tau2595-tau1595)*(m-6.5)/(7.0-6.5)
        tau2080 = tau12080 + (tau22080-tau12080)*(m-6.5)/(7.0-6.5)
    else:
        tau575 = tau2575
        tau595 = tau2595
        tau2080 = tau22080

    return (sd575, sd595, sd2080,
            tau575, tau595, tau2080,
            phi575, phi595, phi2080)

class AS16(object):
    """
    This class implements the AS16 GMPE
    """

    def __init__(self):
        """
        Initialize class variables
        """
        pass

    def parse_arguments(self):
        """
        This function takes care of parsing the command-line arguments and
        asking the user for any missing parameters that we need
        """
        parser = argparse.ArgumentParser(description="Calculates Afshari and Stewart (2016_ "
                                         " GMPE for significant duration.")
        parser.add_argument("--output-file", dest="output_file", required=True,
                            help="output file")
        parser.add_argument("--src-file", "--src", dest="src_file", required=True,
                            help="source description file (SRC file)")
        parser.add_argument("--station-list", "-s", dest="station_list", required=True,
                            help="station list")
        args = parser.parse_args()

        return args

        
    def run(self):
        """
        Run the AS16 validation for all stations
        """
        args = self.parse_arguments()
        
        # Check input parameters
        if not args.src_file:
            print("[ERROR]: Please specify source description file!")
            sys.exit(1)
        src_file = os.path.abspath(args.src_file)
        if not args.station_list:
            print("[ERROR]: Please specify station list!")
            sys.exit(1)
        station_list = os.path.abspath(args.station_list)

        self.run_as16(args.station_list, args.src_file,
                      args.output_file)


    def run_as16(self, a_station_list, a_src_file, a_output_file):
        """
        Reads src file and station list and computes the
        Afshari and Stewart (2016) significant duration GMPE

        Writes output to a_output_file
        """
        # Read SRC file and station list
        src_keys = parse_src_file(a_src_file)
        stations = StationList(a_station_list)
        station_list = stations.get_station_list()

        # Load information from SRC file
        origin = (src_keys['lon_top_center'], src_keys['lat_top_center'])
        dims = (src_keys['fault_length'], src_keys['dlen'],
                src_keys['fault_width'], src_keys['dwid'],
                src_keys['depth_to_top'])
        mech = (src_keys['strike'], src_keys['dip'],
                src_keys['rake'])

        # Set region to be unknown -- this has no effect in the AS16
        # method as z1 is not provided and that causes dz1 to be set
        # to zero and override the cj parameter
        cj = -999

        # Figure out what mechanism to use
        # 0 = unknown
        # 1 = normal
        # 2 = reverse
        # 3 = strike-slip
        rake = src_keys['rake']
        if abs(rake) <= 30 or abs(rake) >= 150:
            mechanism = 3
        elif rake > 30 and rake < 150:
            mechanism = 2
        elif rake < -30 and rake > -150:
            mechanism = 1
        else:
            print("Warning: unknown mechanism for rake = %f" % (rake))
            mechanism = 0

        # Create output file, add header
        out_file = open(a_output_file, 'w')
        out_file.write("#station, rrup, vs30, sd575, sd595, sd2080,"
                       " tau575, tau595, tau2080, phi575, phi595, phi2080\n")

        # Go through each station
        for station in station_list:
            stat = station.scode
            vs30 = float(station.vs30)

            # Calculate Rrup
            site_geom = [station.lon, station.lat, 0.0]
            (fault_trace1, up_seis_depth,
             low_seis_depth, ave_dip,
             dummy1, dummy2) = putils.FaultTraceGen(origin, dims, mech)
            _, rrup, _ = putils.DistanceToSimpleFaultSurface(site_geom,
                                                             fault_trace1,
                                                             up_seis_depth,
                                                             low_seis_depth,
                                                             ave_dip)

            results = calculate_as16(src_keys['magnitude'], rrup,
                                     mechanism, vs30, -999.0, cj)

            out_file.write("%s, %3.5f, %3.2f" % (stat, rrup, vs30))
            for piece in results:
                out_file.write(", %7.5f" % (piece))
            out_file.write("\n")

        # All done, close output file
        out_file.close()

if __name__ == '__main__':
    print("Running module: %s" % (os.path.basename(sys.argv[0])))
    ME = AS16()
    ME.run()
