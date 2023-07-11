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

GMPEs for the six parameters in Rezaeian (2010)
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import math
import argparse
from scipy.stats import norm, beta, gamma
import numpy as np
import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('Agg') # Disable use of Tk/X11
import pylab

# Import GMSV Toolkit modules
from plots import plot_config
from core import gmsvtoolkit_config
from core.station_list import StationList
from utils.src_utilities import parse_src_file

# Import Pynga and its utilities
from models.pynga import utils as putils

class RZZ2015GMPE(object):
    """
    This class implements the GMPEs for the six parameters in
    Rezaeian-Zhong-Zareian 2015
    """
    # Regression data

    # From combo_beta_NlinearRegressionWRndEffect_u1.mat
    beta1 = [-2.2962, 2.9440, -0.0707, -1.3564, -0.2654]
    beta2 = [-6.1946, 0.9703, -0.7034, 0.0087, -0.0007]
    beta3 = [-5.0105, 0.6625, -0.3450, 0.0139, -0.0002]
    beta4 = [2.2525, -0.2586, -0.0808, -0.0084, 0.0000]
    beta5 = [-2.4886, 0.3440, 0.0441, 0.0026, -0.0001]
    beta6 = [-0.2583, 0.1293, -0.4772, -0.0115, 0.0004]

    # From combo_sigma_tau_NlinearRegressionWRndEffect_u1.mat
    sigma1 = 0.5937
    sigma2 = 0.5688
    sigma3 = 0.4145
    sigma4 = 0.7228
    sigma5 = 0.9529
    sigma6 = 0.7601
    tau1 = 0.2738
    tau2 = 0.4574
    tau3 = 0.5114
    tau4 = 0.6918
    tau5 = 0.1286
    tau6 = 0.6815

    # From combo_corrcoef_NlinearRegressionWRndEffect_u1.mat
    rho_intererror = [[1.0000, 0.0323, 0.3603, -0.2583, 0.4515, 0.4272],
                      [0.0323, 1.0000, 0.6982, -0.1200, -0.2291, -0.2902],
                      [0.3603, 0.6982, 1.0000, -0.2973, -0.2542, -0.1387],
                      [-0.2583, -0.1200, -0.2973, 1.0000, 0.0973, 0.3336],
                      [0.4515, -0.2291, -0.2542, 0.0973, 1.0000, 0.1105],
                      [0.4272, -0.2902, -0.1387, 0.3336, 0.1105, 1.0000]]
    rho_intraerror = [[1.0000, -0.4682, -0.1486, -0.0994, 0.0951, -0.1673],
                      [-0.4682, 1.0000, 0.6420, -0.0411, -0.1323, -0.0249],
                      [-0.1486, 0.6420, 1.0000, -0.0188, -0.2400, 0.0649],
                      [-0.0994, -0.0411, -0.0188, 1.0000, -0.3118, 0.1555],
                      [0.0951, -0.1323, -0.2400, -0.3118, 1.0000, -0.0522],
                      [-0.1673, -0.0249, 0.0649, 0.1555, -0.0522, 1.0000]]
    rho_totalerror = [[1.0000, -0.3555, 0.0066, -0.1545, 0.1341, -0.0078],
                      [-0.3555, 1.0000, 0.6729, -0.1303, -0.1576, -0.1958],
                      [0.0066, 0.6729, 1.0000, -0.2761, -0.1977, -0.2188],
                      [-0.1545, -0.1303, -0.2761, 1.0000, -0.2034, 0.2814],
                      [0.1341, -0.1576, -0.1977, -0.2034, 1.0000, -0.0137],
                      [-0.0078, -0.1958, -0.2188, 0.2814, -0.0137, 1.0000]]

    number_of_samples = 100

    def __init__(self):
        """
        Initilize class variables
        """
        pass

    def slpinv(self, fx, a, b, c, xmin, xmax):
        """
        Evaluates inversecfg of Fx, where x is a value of SlpFreq within
        [xmin=-2, xmax=0.5] parameters of the cdf are a, b, c
        """

        fx0 = (c / b) * (1 - math.exp(b * xmin)) # Value of cdf at x=0

        if fx == 0:
            x = xmin
        elif fx < fx0:
            x = (1.0 / b) * math.log(fx * b / c + math.exp(b * xmin))
        elif fx >= fx0:
            x = ((-1.0 / a) *
                 math.log(((c / b) * (1 - math.exp(b * xmin)) - fx) * (a / c) + 1))
        else:
            x = xmax

        return x

    def calculate_mean_values(self, rrup, vs30, mag, fault_type):
        """
        This function calculates the mean values for each parameter

        """
        # Mean values of parameters in the standard normal space: ui
        u1 = (self.beta1[0] + self.beta1[1] * (mag / 7.0) +
              self.beta1[2] * fault_type + self.beta1[3] * math.log(rrup / 25.0) +
              self.beta1[4] * math.log(vs30 / 750.0))
        u2 = (self.beta2[0] + self.beta2[1] * mag +
              self.beta2[2] * fault_type + self.beta2[3] * rrup +
              self.beta2[4] * vs30)
        u3 = (self.beta3[0] + self.beta3[1] * mag +
              self.beta3[2] * fault_type + self.beta3[3] * rrup +
              self.beta3[4] * vs30)
        u4 = (self.beta4[0] + self.beta4[1] * mag +
              self.beta4[2] * fault_type + self.beta4[3] * rrup +
              self.beta4[4] * vs30)
        u5 = (self.beta5[0] + self.beta5[1] * mag +
              self.beta5[2] * fault_type + self.beta5[3] * rrup +
              self.beta5[4] * vs30)
        u6 = (self.beta6[0] + self.beta6[1] * mag +
              self.beta6[2] * fault_type + self.beta6[3] * rrup +
              self.beta6[4] * vs30)

        # Transform parameters ui from standardnormal to the physical space:
        # thetai (constraint: tmid < d_5_95, removed)
        theta1 = norm.ppf(norm.cdf(u1), -4.8255, 1.4318)
        theta2 = 5.0 + (45 - 5) * beta.ppf(norm.cdf(u2), 1.1314, 2.4474)
        theta3 = 0.5 + (40 - 0.5) * beta.ppf(norm.cdf(u3), 1.5792, 3.6405)
        theta4 = gamma.ppf(norm.cdf(u4), 4.0982, scale=1.4330)
        theta5 = self.slpinv(norm.cdf(u5), 17.095, 6.7729, 4.8512, -2, 0.5)
        theta6 = 0.02 + (1 - 0.02) * beta.ppf(norm.cdf(u6), 1.4250, 5.7208)

        # All done, return values
        return math.exp(theta1), theta2, theta3, theta4, theta5, theta6

    def plot(self, stat, output_plot, rrup, fault_type, vs30, mag,
             ai, d595, tmid, wmid, wslp, zeta,
             ai_mean, d595_mean, tmid_mean, wmid_mean, wslp_mean, zeta_mean):
        """
        This function plots the results of the RZZ2015GMPE for a single station
        """
        ai_mean = [ai_mean] * len(ai)
        d595_mean = [d595_mean] * len(d595)
        tmid_mean = [tmid_mean] * len(tmid)
        wmid_mean = [wmid_mean] * len(wmid)
        wslp_mean = [wslp_mean] * len(wslp)
        zeta_mean = [zeta_mean] * len(zeta)

        # Create fig
        fig, axs = pylab.plt.subplots(2, 3)
        fig.set_size_inches(17, 8.5)
        fig.suptitle("RZZ2015GMPE - "
                     "%s - M=%2.2f - F=%d - R=%7.3f km - Vs30=%7.2f m/s" %
                     (stat, mag, int(fault_type), rrup, vs30), size=16)
        fig.subplots_adjust(hspace=0.4)
        fig.subplots_adjust(left=0.05)
        fig.subplots_adjust(right=0.98)

        # Plot arias intensity
        subfig = axs[0][0]
        subfig.set_title("Arias Intensity", size=14)
        subfig.plot(ai, color='red', marker='o', linestyle='')
        subfig.plot(ai_mean, color='black')
        subfig.set_ylabel("sec.g^2", size=10)
        subfig.grid(True)
        subfig.minorticks_on()

        # Plot d_595
        subfig = axs[0][1]
        subfig.set_title("D595", size=14)
        subfig.plot(d595, color='red', marker='o', linestyle='')
        subfig.plot(d595_mean, color='black')
        subfig.set_ylabel("Sec", size=10)
        subfig.grid(True)
        subfig.minorticks_on()

        # Plot tmid
        subfig = axs[0][2]
        subfig.set_title("tMid", size=14)
        subfig.plot(tmid, color='red', marker='o', linestyle='')
        subfig.plot(tmid_mean, color='black')
        subfig.set_ylabel("Sec", size=10)
        subfig.grid(True)
        subfig.minorticks_on()

        # Plot wmid
        subfig = axs[1][0]
        subfig.set_title("wMid", size=14)
        subfig.plot(wmid, color='red', marker='o', linestyle='')
        subfig.plot(wmid_mean, color='black')
        subfig.set_ylabel("Hz", size=10)
        subfig.grid(True)
        subfig.minorticks_on()

        # Plot wslp
        subfig = axs[1][1]
        subfig.set_title("wSlp", size=14)
        subfig.plot(wslp, color='red', marker='o', linestyle='')
        subfig.plot(wslp_mean, color='black')
        subfig.set_ylabel("Hz/Sec", size=10)
        subfig.grid(True)
        subfig.minorticks_on()

        # Plot zeta
        subfig = axs[1][2]
        subfig.set_title("zeta", size=14)
        subfig.plot(zeta, color='red', marker='o', linestyle='')
        subfig.plot(zeta_mean, color='black')
        subfig.set_ylabel("ratio", size=10)
        subfig.grid(True)
        subfig.minorticks_on()

        # All done! Save plot!
        fig.savefig(output_plot, format='png', transparent=False,
                    dpi=plot_config.dpi)

        # Close image, to save memory
        pylab.plt.close(fig)

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
        parser.add_argument("--plot-prefix", dest="plot_prefix",
                            help="prefix used for each plot")
        parser.add_argument("--disable-plots", dest="disable_plots", action="store_true",
                            default=False, help="disable plot generation")
        args = parser.parse_args()

        return args
        
    def run(self):
        """
        Parses command-line options and runs the GMPEs
        for the six parameters in Rezaeian (2015)
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

        output_file = os.path.abspath(args.output_file)
        create_plots = not args.disable_plots
        if not args.plot_prefix:
            plot_prefix = "rzz2015gmpe"
        else:
            plot_prefix = args.plot_prefix
        
        self.run_rzz2015_gmpe(station_list, src_file,
                              output_file, plot_prefix=plot_prefix,
                              plots=create_plots)

    def run_rzz2015_gmpe(self, a_station_list, a_src_file,
                         a_output_file, plot_prefix="rzz2015gmpe",
                         plots=True):
        """
        Runs the GMPEs for the six parameters in Rezaeian (2015)
        """
        src_keys = parse_src_file(a_src_file)

        # Get station list
        stations = StationList(a_station_list)
        station_list = stations.get_station_list()

        # Initialize random seed
        np.random.seed(int(src_keys['seed']))

        # Create output file, add header
        out_file = open(a_output_file, 'w')
        out_file.write("#station, r_rup, vs_30,"
                       " ai_mean, d595_mean, tmid_mean,"
                       " wmid_mean, wslp_mean, zeta_mean,"
                       " ai_stddev, d595_stddev, tmid_stddev,"
                       " wmid_stddev, wslp_stddev, zeta_stddev\n")

        # Go through each station
        for station in station_list:
            stat = station.scode
            print("==> Processing station: %s" % (stat))

            # Calculate Rrup
            origin = (src_keys['lon_top_center'],
                      src_keys['lat_top_center'])
            dims = (src_keys['fault_length'], src_keys['dlen'],
                    src_keys['fault_width'], src_keys['dwid'],
                    src_keys['depth_to_top'])
            mech = (src_keys['strike'], src_keys['dip'],
                    src_keys['rake'])

            site_geom = [float(station.lon), float(station.lat), 0.0]
            (fault_trace1, up_seis_depth,
             low_seis_depth, ave_dip,
             dummy1, dummy2) = putils.FaultTraceGen(origin, dims, mech)
            _, rrup, _ = putils.DistanceToSimpleFaultSurface(site_geom,
                                                             fault_trace1,
                                                             up_seis_depth,
                                                             low_seis_depth,
                                                             ave_dip)

            vs30 = station.vs30
            mag = src_keys['magnitude']
            # Fault type is 1 (Reverse) unless condition below is met
            # Then it is 0 (Strike-pp)
            fault_type = 1
            rake = src_keys['rake']
            if ((rake >= -180 and rake < -150) or
                (rake >= -30 and rake <= 30) or
                (rake > 150 and rake <= 180)):
                fault_type = 0

            [ai_mean, d595_mean,
             tmid_mean, wmid_mean,
             wslp_mean, zeta_mean] = self.calculate_mean_values(rrup, vs30,
                                                                mag, fault_type)

            # Randomize parameters using standard deviations and correlations
            sta_ai = []
            sta_d595 = []
            sta_tmid = []
            sta_wmid = []
            sta_wslp = []
            sta_zeta = []

            # Simulate number_of_samples realizations of the error
            # term for each parameter
            for _ in range(0, self.number_of_samples):

                # Covariance matrix
                std1 = np.sqrt(self.sigma1**2 + self.tau1**2)
                std2 = np.sqrt(self.sigma2**2 + self.tau2**2)
                std3 = np.sqrt(self.sigma3**2 + self.tau3**2)
                std4 = np.sqrt(self.sigma4**2 + self.tau4**2)
                std5 = np.sqrt(self.sigma5**2 + self.tau5**2)
                std6 = np.sqrt(self.sigma6**2 + self.tau6**2)

                s_total_error = [[std1**2,
                                  std1*std2*self.rho_totalerror[0][1],
                                  std1*std3*self.rho_totalerror[0][2],
                                  std1*std4*self.rho_totalerror[0][3],
                                  std1*std5*self.rho_totalerror[0][4],
                                  std1*std6*self.rho_totalerror[0][5]],
                                 [std2*std1*self.rho_totalerror[1][0],
                                  std2**2,
                                  std2*std3*self.rho_totalerror[1][2],
                                  std2*std4*self.rho_totalerror[1][3],
                                  std2*std5*self.rho_totalerror[1][4],
                                  std2*std6*self.rho_totalerror[1][5]],
                                 [std3*std1*self.rho_totalerror[2][0],
                                  std3*std2*self.rho_totalerror[2][1],
                                  std3**2,
                                  std3*std4*self.rho_totalerror[2][3],
                                  std3*std5*self.rho_totalerror[2][4],
                                  std3*std6*self.rho_totalerror[2][5]],
                                 [std4*std1*self.rho_totalerror[3][0],
                                  std4*std2*self.rho_totalerror[3][1],
                                  std4*std3*self.rho_totalerror[3][2],
                                  std4**2,
                                  std4*std5*self.rho_totalerror[3][4],
                                  std4*std6*self.rho_totalerror[3][5]],
                                 [std5*std1*self.rho_totalerror[4][0],
                                  std5*std2*self.rho_totalerror[4][1],
                                  std5*std3*self.rho_totalerror[4][2],
                                  std5*std4*self.rho_totalerror[4][3],
                                  std5**2,
                                  std5*std6*self.rho_totalerror[4][5]],
                                 [std6*std1*self.rho_totalerror[5][0],
                                  std6*std2*self.rho_totalerror[5][1],
                                  std6*std3*self.rho_totalerror[5][2],
                                  std6*std4*self.rho_totalerror[5][3],
                                  std6*std5*self.rho_totalerror[5][4],
                                  std6**2]]
                # Matlab returns upper-triangular while Python returns
                # lower-triangular by default -- no need to transpose later!
                r_total_error = np.linalg.cholesky(s_total_error)
                y_total_error = np.random.normal(0, 1, 6)
                total_error = np.dot(r_total_error, y_total_error)

                # Generate randomize parameters in the standardnormal space: ui
                u1 = (self.beta1[0] + self.beta1[1] * (mag / 7.0) +
                      self.beta1[2] * fault_type +
                      self.beta1[3] * math.log(rrup / 25.0) +
                      self.beta1[4] * math.log(vs30 / 750.0)) + total_error[0]
                u2 = (self.beta2[0] + self.beta2[1] * mag +
                      self.beta2[2] * fault_type + self.beta2[3] * rrup +
                      self.beta2[4] * vs30) + total_error[1]
                u3 = (self.beta3[0] + self.beta3[1] * mag +
                      self.beta3[2] * fault_type + self.beta3[3] * rrup +
                      self.beta3[4] * vs30) + total_error[2]
                u4 = (self.beta4[0] + self.beta4[1] * mag +
                      self.beta4[2] * fault_type + self.beta4[3] * rrup +
                      self.beta4[4] * vs30) + total_error[3]
                u5 = (self.beta5[0] + self.beta5[1] * mag +
                      self.beta5[2] * fault_type + self.beta5[3] * rrup +
                      self.beta5[4] * vs30) + total_error[4]
                u6 = (self.beta6[0] + self.beta6[1] * mag +
                      self.beta6[2] * fault_type + self.beta6[3] * rrup +
                      self.beta6[4] * vs30) + total_error[5]

                # Transform parameters ui from standardnormal to the physical space:
                # thetai (constraint: tmid < d_5_95, removed)
                theta1 = norm.ppf(norm.cdf(u1), -4.8255, 1.4318)
                theta2 = 5.0 + (45 - 5) * beta.ppf(norm.cdf(u2), 1.1314, 2.4474)
                theta3 = 0.5 + (40 - 0.5) * beta.ppf(norm.cdf(u3), 1.5792, 3.6405)
                theta4 = gamma.ppf(norm.cdf(u4), 4.0982, scale=1.4330)
                theta5 = self.slpinv(norm.cdf(u5), 17.095, 6.7729, 4.8512, -2, 0.5)
                theta6 = 0.02 + (1 - 0.02) * beta.ppf(norm.cdf(u6), 1.4250, 5.7208)

                sta_ai.append(math.exp(theta1))
                sta_d595.append(theta2)
                sta_tmid.append(theta3)
                sta_wmid.append(theta4)
                sta_wslp.append(theta5)
                sta_zeta.append(theta6)

            # Write output to gmpe file
            out_file.write("%s, %7.4f, %7.2f, " % (stat, rrup, vs30) +
                           "%7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f, " %
                           (ai_mean, d595_mean, tmid_mean,
                            wmid_mean, wslp_mean, zeta_mean) +
                           "%7.4f, %7.4f, %7.4f, %7.4f, %7.4f, %7.4f\n" %
                           (np.std(sta_ai), np.std(sta_d595), np.std(sta_tmid),
                            np.std(sta_wmid), np.std(sta_wslp),
                            np.std(sta_zeta)))

            # Generate Plots
            if plots:
                # Create path for our plot and output file
                output_dir = os.path.dirname(a_output_file)
                output_plot = os.path.join(output_dir,
                                           '%s.%s.png' %
                                           (plot_prefix, stat))

                self.plot(stat, output_plot, rrup,
                          fault_type, vs30, mag,
                          sta_ai, sta_d595, sta_tmid,
                          sta_wmid, sta_wslp, sta_zeta,
                          ai_mean, d595_mean, tmid_mean,
                          wmid_mean, wslp_mean, zeta_mean)

        # Close output file
        out_file.close()

if __name__ == '__main__':
    print("Running module: %s" % (os.path.basename(sys.argv[0])))
    ME = RZZ2015GMPE()
    ME.run()
