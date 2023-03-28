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

Plots FAS GoF
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
from plots import plot_config

# Constants
MIN_Y_AXIS = -1.75
MAX_Y_AXIS = 1.75
MIN_Y_AXIS_RATIO = -0.5
MAX_Y_AXIS_RATIO = 0.5
MAX_PERIOD = 10.0
XTICK_FAS_LOC_0_01 = [0.01, 0.02, 0.05,
                      0.1, 0.2, 0.5,
                      1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
XTICK_FAS_LABEL_0_01 = ['0.01', '0.02', '0.05',
                        '0.1', '0.2', '0.5',
                        '1', '2', '5', '10',
                        '20', '50', '100']

# Component extentions
COMP_EXT_FAS = ['fash1', 'fash2', 'seas']

# Component titles
COMP_TITLE_FAS = ['FAS North', 'FAS East', 'SEAS']

# Component subplot locations
COMP_OFFSET_FAS = [312, 313, 311]

# Colorsets for plots
COLORSETS = {"single": 0,
             "combined": 1}
BIAS_COLORS = ["red", "black"]
BIAS_LH_COLORS = ["cyan", (0.8, 0.8, 1)]
CONF_LH_COLORS = ["yellow", (1, 0.3, 0.9)]

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

def plot_fas_gof(plottitle, gof_fileroot, indir,
                 outdir, max_cutoff=0, colorset=None,
                 lfreq=None, hfreq=None):
    """
    Creates a FAS GOF plot with three subplots (SEAS, FAS_H1, FAS_H2)
    """
    # Pick components, labels, and colorset
    xtick_loc = XTICK_FAS_LOC_0_01
    xtick_label = XTICK_FAS_LABEL_0_01
    comp_ext = COMP_EXT_FAS
    comp_title = COMP_TITLE_FAS
    min_period = 0.01
    max_period = 100.0

    # Select colorset
    if colorset is None:
        colorset_idx = 0
    else:
        colorset_idx = COLORSETS[colorset]

    # Set up ticks to match matplotlib 1.x style
    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['ytick.direction'] = 'in'
    mpl.rcParams['xtick.top'] = True
    mpl.rcParams['ytick.right'] = True

    # Set plot dims
    pylab.gcf().set_size_inches(6, 9)
    pylab.gcf().clf()

    pylab.subplots_adjust(left=0.10)
    pylab.subplots_adjust(right=0.97)
    pylab.subplots_adjust(top=0.9)
    pylab.subplots_adjust(bottom=0.1)
    pylab.subplots_adjust(hspace=0.35)
    pylab.subplots_adjust(wspace=0.5)

    period = [[], [], []]
    bias = [[], [], []]
    m90 = [[], [], []]
    p90 = [[], [], []]
    sigma = [[], [], []]
    sigma0 = [[], [], []]

    bias_l = [[], [], []]
    bias_h = [[], [], []]
    conf_l = [[], [], []]
    conf_h = [[], [], []]

    for compnum in range(0, len(comp_ext)):
        comp = comp_ext[compnum]
        filenamebase = os.path.join(indir, "%s-%s" % (gof_fileroot, comp))
        # print("Reading component files %s.*" % (filenamebase))
        period[compnum], bias[compnum] = read_data("%s.bias" %
                                                   (filenamebase),
                                                   min_period,
                                                   max_period)
        period[compnum], m90[compnum] = read_data("%s.m90" %
                                                  (filenamebase),
                                                  min_period,
                                                  max_period)
        period[compnum], p90[compnum] = read_data("%s.p90" %
                                                  (filenamebase),
                                                  min_period,
                                                  max_period)
        period[compnum], sigma[compnum] = read_data("%s.sigma" %
                                                    (filenamebase),
                                                    min_period,
                                                    max_period)
        period[compnum], sigma0[compnum] = read_data("%s.sigma0" %
                                                     (filenamebase),
                                                     min_period,
                                                     max_period)

        # Compute bias and conf interval lower/upper bounds
        for i in range(0, len(bias[compnum])):
            bias_l[compnum].append(bias[compnum][i] - sigma0[compnum][i])
            bias_h[compnum].append(bias[compnum][i] + sigma0[compnum][i])
            conf_l[compnum].append(m90[compnum][i])
            conf_h[compnum].append(p90[compnum][i])

    # Make sure all components have same number of data points
    npts = [len(component) for component in period]
    #print(npts)
    if npts[1:] != npts[:-1]:
        print("Number of data points unequal across components")
        return

    # Construct baseline
    baseline = []
    for _ in range(0, len(period[0])):
        baseline.append(0.0)

    # Find max, min values
    min_x = min(period[0])
    max_x = max(period[0])
    for comp in period:
        min_x = min(min_x, min(comp))
        max_x = max(max_x, max(comp))
    min_y = MIN_Y_AXIS
    max_y = MAX_Y_AXIS

    # Draw each component
    for compnum in range(0, 3):
        comp = comp_ext[compnum]
        offset = COMP_OFFSET_FAS[compnum]

        pylab.subplot(offset)
        pylab.title(comp_title[compnum], size='small')
        pylab.plot(period[compnum], bias[compnum],
                   color=BIAS_COLORS[colorset_idx],
                   label='_nolegend_', linewidth=1.0)
        pylab.fill_between(period[compnum], bias_h[compnum],
                           bias_l[compnum],
                           color=BIAS_LH_COLORS[colorset_idx],
                           label='_nolegend_')
        pylab.fill_between(period[compnum], conf_h[compnum],
                           conf_l[compnum],
                           color=CONF_LH_COLORS[colorset_idx],
                           label='_nolegend_')
        pylab.plot(period[compnum], baseline, color='grey',
                   label='_nolegend_', linewidth=1.0)
        pylab.xlim(min_x, max_x)
        if comp == 'ratio':
            pylab.ylim(MIN_Y_AXIS_RATIO, MAX_Y_AXIS_RATIO)
            min_horiz_y = MIN_Y_AXIS_RATIO
            max_horiz_y = MAX_Y_AXIS_RATIO
        else:
            pylab.ylim(min_y, max_y)
            min_horiz_y = min_y
            max_horiz_y = max_y
        pylab.xlabel("Frequency (Hz)", size=8)
        pylab.ylabel("ln (data/model)", size=8)
        pylab.xscale('log')
        pylab.xticks(xtick_loc, xtick_label)
        pylab.tick_params(labelsize=8)

        if lfreq is not None:
            pylab.vlines(lfreq, min_horiz_y, max_horiz_y,
                         color='r', linestyles='--')
        if hfreq is not None:
            pylab.vlines(hfreq, min_horiz_y, max_horiz_y,
                         color='violet', linestyles='--')

    if max_cutoff == 0:
        pylab.suptitle('%s' % (plottitle), size=11)
    else:
        pylab.suptitle('%s\nR < %d km' % (plottitle, max_cutoff), size=11)
    outfile = os.path.join(outdir, "gof-%s.png" % (gof_fileroot))
    print("==> Created GoF plot: %s" % (outfile))
    pylab.savefig(outfile, format="png",
                  transparent=False, dpi=plot_config.dpi)
    pylab.close()

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    parser = argparse.ArgumentParser(description="Generates FAS GoF comparison plot.")
    parser.add_argument("--input-dir", dest="input_dir",
                        help="input directory with residuals files")
    parser.add_argument("--output-dir", dest="output_dir",
                        help="output directory")
    parser.add_argument("--comp-label", dest="comp_label",
                        help="comparison label used for the output file prefix")
    parser.add_argument("--max-cutoff", dest="max_cutoff", type=float, default=1000.0,
                        help="select max cutoff distance (km) for the comparison")
    parser.add_argument("--low-freq", "--lf", dest="lfreq",
                        help="adds vertical line at this low frequency corner")
    parser.add_argument("--high-freq", "--hf", dest="hfreq",
                        help="adds vertical line at this high frequency corner")
    parser.add_argument("--method", dest="method",
                        help="specify simulation method (for both low and high freq lines")
    parser.add_argument("--colorset", dest="colorset", default="single",
                        help="select colorset [single/combined] default single")
    parser.add_argument("--plot-limit", dest="plot_limit", type=float, default=0.01,
                        help="select GoF plot limit, default=0.01s")
    parser.add_argument("--plot-title", "--title", dest="plot_title",
                        default="GOF FAS Comparison Plot",
                        help="select plot title for the GoF plot")
    args = parser.parse_args()
    
    return args

def run():
    """
    Generate FAS GoF plot
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

    # Other plot parameters
    if not args.comp_label:
        print("[ERROR]: Please specify comp-label prefix!")
        sys,exit(1)
    max_cutoff = args.max_cutoff
    if args.colorset.lower() != "single" and args.colorset.lower() != "combined":
        print("[ERROR]: Please use only 'single' or 'combined' for colorset!")
        sys.exit(1)

    # Where to find residuals information
    fileroot = '%s_r0-%d-fas' % (args.comp_label, max_cutoff)

    # Check if user specified lfreq and hfreq
    lfreq = None
    hfreq = None

    # Use method-specific frequencies if specified by used
    if args.method is not None:
        method = args.method.lower()
        freq_ranges = plot_config.FAS_GOF_FREQ
        lfreq = freq_ranges[method]['freq_low']
        hfreq = freq_ranges[method]['freq_high']

    # But allow user to override one (or both) value(s) via command-line interface
    if args.lfreq is not None:
        lfreq = float(args.lfreq)
    if args.hfreq is not None:
        hfreq = float(args.hfreq)
    
    # Plot GOF for FAS data
    plot_fas_gof(args.plot_title, fileroot, input_dir,
                 output_dir, max_cutoff=max_cutoff,
                 colorset=args.colorset.lower(),
                 lfreq=lfreq, hfreq=hfreq)

if __name__ == '__main__':
    run()
