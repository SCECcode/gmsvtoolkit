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

Plots GMPE GoF
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import argparse
import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('Agg') # Disables use of Tk/X11
import pylab

# Imports needed from the GMSVToolkit
from core.station_list import StationList
from models import gmpe_config
from plots import plot_config

# Constants
MIN_Y_AXIS = -1.75
MAX_Y_AXIS = 1.75
MAX_PERIOD = 10.0
XTICK_LOC_0_01 = [0.01, 0.02, 0.05,
                  0.1, 0.2, 0.5,
                  1.0, 2.0, 5.0, 10.0]
XTICK_LABEL_0_01 = ['0.01', '0.02', '0.05',
                    '0.1', '0.2', '0.5',
                    '1', '2', '5', '10']
XTICK_FREQ_LOC_0_01 = [100.0, 50.0, 20.0, 10.0,
                       5.0, 2.0, 1.0, 0.5, 0.2,
                       0.1, 0.05, 0.02, 0.01]
XTICK_FREQ_LABEL_0_01 = ['100', '50', '20',
                         '10', '5', '2',
                         '1', '0.5', '0.2',
                         '0.1', '0.05', '0.02', '0.01']

def read_data(datafile, min_period, max_period=MAX_PERIOD):
    """
    Read in response spectra data from specified datafile
    """
    data = [[], [],]

    # Read input file
    in_file = open(datafile, "r")
    for line in in_file:
        if line.startswith("#") or line.startswith("%"):
            continue
        tmp = line.split()
        period = float(tmp[0])
        # Extract subset of period values
        if ((period >= min_period) and
            (period <= max_period)):
            data[0].append(float(tmp[0]))
            data[1].append(float(tmp[1]))
    # Close file
    in_file.close()
    # Return data
    return data

def multi_plot(plottitle, gof_fileroot, indir,
               outdir, legends, num_stations, mode="P"):
    """
    Creates several GOF plots using the files specified in the
    gof_fileroot array. mode selects periods (P) or frequencies (F)
    for the X axis.
    """
    mode = mode.upper()
    if mode != "P" and mode != "F":
        print("Invalid mode, must specify 'P' for periods or 'F' for frequencies!")
        return
    # Pick components and labels
    if mode == "P":
        xtick_loc = XTICK_LOC_0_01
        xtick_label = XTICK_LABEL_0_01
    elif mode == "F":
        xtick_loc = XTICK_FREQ_LOC_0_01
        xtick_label = XTICK_FREQ_LABEL_0_01

    # Initialize data arrays
    freqs = [[] for _ in range(len(gof_fileroot))]
    periods = [[] for _ in range(len(gof_fileroot))]
    bias = [[] for _ in range(len(gof_fileroot))]
    m90 = [[] for _ in range(len(gof_fileroot))]
    p90 = [[] for _ in range(len(gof_fileroot))]
    sigma = [[] for _ in range(len(gof_fileroot))]
    sigma0 = [[] for _ in range(len(gof_fileroot))]

    bias_l = [[] for _ in range(len(gof_fileroot))]
    bias_h = [[] for _ in range(len(gof_fileroot))]
    conf_l = [[] for _ in range(len(gof_fileroot))]
    conf_h = [[] for _ in range(len(gof_fileroot))]

    # Read data from all input files
    for compnum in range(0, len(gof_fileroot)):
        filenamebase = os.path.join(indir, gof_fileroot[compnum])
        #print("Reading component files %s.*" % (filenamebase))
        periods[compnum], bias[compnum] = read_data("%s.bias" %
                                                    (filenamebase),
                                                    0.01)
        periods[compnum], m90[compnum] = read_data("%s.m90" %
                                                   (filenamebase),
                                                   0.01)
        periods[compnum], p90[compnum] = read_data("%s.p90" %
                                                   (filenamebase),
                                                   0.01)
        periods[compnum], sigma[compnum] = read_data("%s.sigma" %
                                                     (filenamebase),
                                                     0.01)
        periods[compnum], sigma0[compnum] = read_data("%s.sigma0" %
                                                      (filenamebase),
                                                      0.01)

        # Compute bias and conf interval lower/upper bounds
        for i in range(0, len(bias[compnum])):
            bias_l[compnum].append(bias[compnum][i] - sigma0[compnum][i])
            bias_h[compnum].append(bias[compnum][i] + sigma0[compnum][i])
            conf_l[compnum].append(m90[compnum][i])
            conf_h[compnum].append(p90[compnum][i])

        if mode == "F":
            # Add extra point for T=100s
            for i in range(0, len(bias[compnum])):
                bias[compnum].append(0.0)
                bias_l[compnum].append(0.0)
                bias_h[compnum].append(0.0)
                conf_l[compnum].append(0.0)
                conf_h[compnum].append(0.0)
                bias[compnum].append(0.0)
                bias_l[compnum].append(0.0)
                bias_h[compnum].append(0.0)
                conf_l[compnum].append(0.0)
                conf_h[compnum].append(0.0)
                periods[compnum].append(10.01)
                periods[compnum].append(100.0)

    num_periods = len(periods[0])
    for comp in periods:
        if len(comp) != num_periods:
            print("Number of data points unequal across components")
            return

    # Calculate frequencies
    for freq, period in zip(freqs, periods):
        for item in period:
            freq.append(1.0 / item)

    # Construct baseline
    baseline = [0.0 for _ in periods[0]]

    # Find max, min values
    if mode == "P":
        min_x = min([min(comp) for comp in periods])
        max_x = max([max(comp) for comp in periods])
    elif mode == "F":
        min_x = min(freqs[0])
        max_x = max(freqs[0])
        for comp in freqs:
            min_x = min(min_x, min(comp))
            max_x = max(max_x, max(comp))
    min_y = MIN_Y_AXIS
    max_y = MAX_Y_AXIS

    # Set up ticks to match matplotlib 1.x style
    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['ytick.direction'] = 'in'
    mpl.rcParams['xtick.top'] = True
    mpl.rcParams['ytick.right'] = True

    # Start plots
    num_plots = len(gof_fileroot)
    # Make 1 column of "num_plots" rows
    fig, axs = pylab.plt.subplots(num_plots, 1)
    # Set plot dims
    fig.set_size_inches(6, 10)
    fig.subplots_adjust(left=0.1)
    fig.subplots_adjust(right=0.97)
    fig.subplots_adjust(top=0.92)
    fig.subplots_adjust(bottom=0.07)
    fig.subplots_adjust(hspace=0.4)
    fig.subplots_adjust(wspace=0.5)

    # Add subplots in a list
    subfigs = []
    for idx in range(0, num_plots):
        subfigs.append(axs[idx])

    # Now walk through each subfig
    for (subfig, subplot_title,
         cur_period, cur_freq,
         cur_bias, cur_bias_h, cur_bias_l,
         cur_conf_h, cur_conf_l) in zip(subfigs,
                                        legends,
                                        periods,
                                        freqs,
                                        bias,
                                        bias_h,
                                        bias_l,
                                        conf_h,
                                        conf_l):
        subfig.set_xlim(min_x, max_x)
        subfig.set_ylim(min_y, max_y)
        if mode == "P":
            x_comp = cur_period
        elif mode == "F":
            x_comp = cur_freq
        subfig.set_title("%s" % subplot_title, size=10)
        subfig.plot(x_comp, cur_bias, color='red',
                    label='_nolegend_', linewidth=1.0)
        subfig.fill_between(x_comp, cur_bias_h,
                            cur_bias_l, color='cyan',
                            label='_nolegend_')
        subfig.fill_between(x_comp, cur_conf_h,
                            cur_conf_l, color='yellow',
                            label='_nolegend_')
        subfig.plot(x_comp, baseline, color='grey',
                    label='_nolegend_', linewidth=1.0)
        if mode == "P":
            subfig.set_xlabel("Period (sec)", size=8)
        elif mode == "F":
            subfig.set_xlabel("Frequency (Hz)", size=8)
        subfig.set_ylabel("ln (data/model)", size=8)
        subfig.set_xscale('log')
        # Old way to do it
        # subfig.set_xticks(xtick_loc, xtick_label)
        subfig.set_xticks(xtick_loc)
        subfig.set_xticklabels(xtick_label)
        subfig.tick_params(labelsize=8)
        subfig.minorticks_on()

    fig.suptitle('%s\nNumber of stations: %d' % (plottitle, num_stations),
                 size=12)
    # Figure out output filename
    outfile = gof_fileroot[0]
    outfile = outfile[:outfile.rfind("-")]
    if mode == "P":
        outfile = os.path.join(outdir, "gof-%s.png" % (outfile))
    elif mode == "F":
        outfile = os.path.join(outdir, "gof-%s-freq.png" % (outfile))
    print("==> Created GoF plot: %s" % (outfile))
    fig.savefig(outfile, format="png",
                transparent=False, dpi=plot_config.dpi)
    pylab.close()

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    gmpe_groups = [item for item in gmpe_config.GMPES]
    
    parser = argparse.ArgumentParser(description="Generates GMPE GoF comparison plot.")
    parser.add_argument("--input-dir", dest="input_dir",
                        help="input directory with residuals files")
    parser.add_argument("--output-dir", dest="output_dir",
                        help="output directory")
    parser.add_argument("--comp-label", dest="comp_label", required=True,
                        help="comparison label used for the output file prefix")
    parser.add_argument("--gmpe-group", dest="gmpe_group", required=True,
                            help="GMPE group %s" % (gmpe_groups))
    parser.add_argument("--run-prefix", dest="run_prefix",
                            help="prefix to be added to the comparison files")
    parser.add_argument("--station-list", "-s", dest="station_list", required=True,
                            help="station list")
    parser.add_argument("--plot-title", "--title", dest="plot_title",
                        default="GOF GMPE Comparison Plot",
                        help="select plot title for the GoF plot")
    args = parser.parse_args()
    
    return args

def run():
    """
    Parse command-line options and run GMPE plot code
    """
    # Parse command-line options
    args = parse_arguments()

    # Look at paths
    input_dir = ""
    output_dir = ""
    if args.output_dir:
        output_dir = args.output_dir
    if args.input_dir:
        input_dir = args.input_dir
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)
    station_file = os.path.abspath(args.station_list)
    
    # Plot GMPE GOF plot
    plot_title = "Comparison between GMPEs and %s" % (args.comp_label)

    plot_gmpe_gof(station_file, args.gmpe_group, args.comp_label,
                  plot_title, input_dir, output_dir, args.run_prefix)
    
def plot_gmpe_gof(station_file, gmpe_group,
                  comp_label, plot_title,
                  input_dir, output_dir,
                  run_prefix=None):
    """
    Generate GMPE GoF plot
    """
    stations = StationList(station_file)
    site_list = stations.get_station_list()
    gmpe_group = gmpe_config.GMPES[gmpe_group]
    gmpe_labels = gmpe_group["labels"]
    gmpe_models = gmpe_group["models"]

    # Where to find residuals information
    if run_prefix is not None:
        fileroot = "%s-GMPE-%s_r%d-all-rd50-" % (comp_label,
                                                 str(run_prefix), 0)
    else:
        fileroot = "%s-GMPE_r%d-all-rd50-" % (comp_label, 0)

    dataroot = ["%s%s" % (fileroot, model.lower()) for model in gmpe_models]
    multi_plot(plot_title, dataroot, input_dir,
               output_dir, gmpe_labels, len(site_list),
               mode="P")
    multi_plot(plot_title, dataroot, input_dir,
               output_dir, gmpe_labels, len(site_list),
               mode="F")

if __name__ == '__main__':
    run()
