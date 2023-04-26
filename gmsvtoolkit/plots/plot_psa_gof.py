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

Plots Goodness of Fit bias +/- sigma
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
import matplotlib.gridspec as gridspec

# Imports needed from the GMSVToolkit
from core import exceptions
from plots import plot_config

# Constants
MIN_Y_AXIS = -1.75
MAX_Y_AXIS = 1.75
MIN_Y_AXIS_RATIO = -0.5
MAX_Y_AXIS_RATIO = 0.5
MAX_PERIOD = 10.0
XTICK_LOC = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
XTICK_LABEL = ['0.1', '0.2', '0.5', '1', '2', '5', '10']
XTICK_LOC_0_01 = [0.01, 0.02, 0.05,
                  0.1, 0.2, 0.5,
                  1.0, 2.0, 5.0, 10.0]
XTICK_LABEL_0_01 = ['0.01', '0.02', '0.05',
                    '0.1', '0.2', '0.5',
                    '1', '2', '5', '10']
XTICK_FREQ_LOC = [10.0, 5.0, 2.0, 1.0, 0.5, 0.2, 0.1]
XTICK_FREQ_LABEL = ['10', '5', '2', '1', '0.5', '0.2', '0.1']
XTICK_FREQ_LOC_0_01 = [100.0, 50.0, 20.0, 10.0,
                       5.0, 2.0, 1.0, 0.5, 0.2,
                       0.1, 0.05, 0.02, 0.01]
XTICK_FREQ_LABEL_0_01 = ['100', '50', '20',
                         '10', '5', '2',
                         '1', '0.5', '0.2',
                         '0.1', '0.05', '0.02', '0.01']

# Component extentions
COMP_EXT_RD50 = ['psa5n', 'psa5e', 'rotd50']
COMP_EXT_RD100 = ['rotd100', 'rotd50', 'ratio']

# Component titles
COMP_TITLE_RD50 = ['PSA North 5%', 'PSA East 5%', 'RotD50']
COMP_TITLE_RD100 = ['RotD100', 'RotD50', 'RotD100/RotD50']

# Component subplot locations
COMP_OFFSET = [312, 313, 311]

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

def plot_single_component_gof(plottitle, gof_fileroot, indir, outdir,
                              cutoff=0, min_period=0.01, colorset=None,
                              lfreq=None, hfreq=None):
    """
    Creates a single component GOF plot (e.g. RotD50)
    """
    # Convert min/max frequencies to periods
    if lfreq is None:
        pmax = None
    else:
        pmax = 1.0 / float(lfreq)

    if hfreq is None:
        pmin = None
    else:
        pmin = 1.0 / float(hfreq)

    # Pick components and labels
    if min_period == 0.01:
        xtick_loc = XTICK_LOC_0_01
        xtick_label = XTICK_LABEL_0_01
    elif min_period == 0.1:
        xtick_loc = XTICK_LOC
        xtick_label = XTICK_LABEL
    else:
        raise exceptions.ParameterError("invalid min_period: %f" %
                                        (min_period))

    comp_ext = COMP_EXT_RD50

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
    pylab.gcf().set_size_inches(6, 2.8)
    pylab.gcf().clf()

    pylab.subplots_adjust(left=0.10)
    pylab.subplots_adjust(right=0.97)
    pylab.subplots_adjust(top=0.77)
    pylab.subplots_adjust(bottom=0.13)
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
        #print("Reading component files %s.*" % (filenamebase))
        period[compnum], bias[compnum] = read_data("%s.bias" %
                                                   (filenamebase),
                                                   min_period)
        period[compnum], m90[compnum] = read_data("%s.m90" %
                                                  (filenamebase),
                                                  min_period)
        period[compnum], p90[compnum] = read_data("%s.p90" %
                                                  (filenamebase),
                                                  min_period)
        period[compnum], sigma[compnum] = read_data("%s.sigma" %
                                                    (filenamebase),
                                                    min_period)
        period[compnum], sigma0[compnum] = read_data("%s.sigma0" %
                                                     (filenamebase),
                                                     min_period)

        # Compute bias and conf interval lower/upper bounds
        for i in range(0, len(bias[compnum])):
            bias_l[compnum].append(bias[compnum][i] - sigma0[compnum][i])
            bias_h[compnum].append(bias[compnum][i] + sigma0[compnum][i])
            conf_l[compnum].append(m90[compnum][i])
            conf_h[compnum].append(p90[compnum][i])

    # Make sure all components have same number of data points
    npts = [len(component) for component in period]
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
    compnum = 2
    comp = 'rotd50'

    pylab.subplot(111)
    pylab.title('RotD50', size='small')
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
    pylab.ylim(min_y, max_y)
    pylab.xlabel("Period (sec)", size=8)
    pylab.ylabel("ln (data/model)", size=8)
    pylab.xscale('log')
    pylab.xticks(xtick_loc, xtick_label)
    pylab.tick_params(labelsize=8)

    if pmin is not None:
        pylab.vlines(pmin, min_y, max_y,
                     color='violet', linestyles='--')
    if pmax is not None:
        pylab.vlines(pmax, min_y, max_y,
                     color='r', linestyles='--')

    if cutoff == 0:
        pylab.suptitle('%s' % (plottitle), size=11)
    else:
        pylab.suptitle('%s\nR < %d km' % (plottitle, cutoff), size=11)
    outfile = os.path.join(outdir, "gof-%s.png" % (gof_fileroot))
    print("==> Created GoF plot: %s" % (outfile))
    pylab.savefig(outfile, format="png",
                  transparent=False, dpi=plot_config.dpi)
    pylab.close()

def plot_single_component_freq_gof(plottitle, gof_fileroot, indir, outdir,
                                   cutoff=0, min_period=0.01, colorset=None,
                                   lfreq=None, hfreq=None):
    """
    Creates a single component GOF plot using frequencies instead of periods
    """
    # Pick components and labels
    if min_period == 0.01:
        xtick_loc = XTICK_FREQ_LOC_0_01
        xtick_label = XTICK_FREQ_LABEL_0_01
    elif min_period == 0.1:
        xtick_loc = XTICK_FREQ_LOC
        xtick_label = XTICK_FREQ_LABEL
    else:
        raise exceptions.ParameterError("invalid min_period: %f" %
                                        (min_period))

    comp_ext = COMP_EXT_RD50

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
    pylab.gcf().set_size_inches(6, 2.8)
    pylab.gcf().clf()

    pylab.subplots_adjust(left=0.10)
    pylab.subplots_adjust(right=0.97)
    pylab.subplots_adjust(top=0.77)
    pylab.subplots_adjust(bottom=0.13)
    pylab.subplots_adjust(hspace=0.35)
    pylab.subplots_adjust(wspace=0.5)

    freq = [[], [], []]
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
        #print("Reading component files %s.*" % (filenamebase))
        period[compnum], bias[compnum] = read_data("%s.bias" %
                                                   (filenamebase),
                                                   min_period)
        period[compnum], m90[compnum] = read_data("%s.m90" %
                                                  (filenamebase),
                                                  min_period)
        period[compnum], p90[compnum] = read_data("%s.p90" %
                                                  (filenamebase),
                                                  min_period)
        period[compnum], sigma[compnum] = read_data("%s.sigma" %
                                                    (filenamebase),
                                                    min_period)
        period[compnum], sigma0[compnum] = read_data("%s.sigma0" %
                                                     (filenamebase),
                                                     min_period)

        # Compute bias and conf interval lower/upper bounds
        for i in range(0, len(bias[compnum])):
            bias_l[compnum].append(bias[compnum][i] - sigma0[compnum][i])
            bias_h[compnum].append(bias[compnum][i] + sigma0[compnum][i])
            conf_l[compnum].append(m90[compnum][i])
            conf_h[compnum].append(p90[compnum][i])

    # Add extra point for T=100s
    for compnum in range(0, len(comp_ext)):
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
        period[compnum].append(10.01)
        period[compnum].append(100.0)

    # Calculate frequencies
    for freqs, periods in zip(freq, period):
        for item in periods:
            freqs.append(1.0 / item)

    # Make sure all components have same number of data points
    npts = [len(component) for component in freq]
    if npts[1:] != npts[:-1]:
        print("Number of data points unequal across components")
        return

    # Construct baseline
    baseline = []
    for _ in range(0, len(freq[0])):
        baseline.append(0.0)

    # Find max, min values
    min_x = min(freq[0])
    max_x = max(freq[0])
    for comp in freq:
        min_x = min(min_x, min(comp))
        max_x = max(max_x, max(comp))
    min_y = MIN_Y_AXIS
    max_y = MAX_Y_AXIS

    # Draw each component
    compnum = 2
    comp = 'rotd50'

    pylab.subplot(111)
    pylab.title('RotD50 PSA', size='small')
    pylab.plot(freq[compnum], bias[compnum],
               color=BIAS_COLORS[colorset_idx],
               label='_nolegend_', linewidth=1.0)
    pylab.fill_between(freq[compnum], bias_h[compnum],
                       bias_l[compnum],
                       color=BIAS_LH_COLORS[colorset_idx],
                       label='_nolegend_')
    pylab.fill_between(freq[compnum], conf_h[compnum],
                       conf_l[compnum],
                       color=CONF_LH_COLORS[colorset_idx],
                       label='_nolegend_')
    pylab.plot(freq[compnum], baseline, color='grey',
               label='_nolegend_', linewidth=1.0)
    pylab.xlim(min_x, max_x)
    pylab.ylim(min_y, max_y)
    pylab.xlabel("Frequency (Hz)", size=8)
    pylab.ylabel("ln (data/model)", size=8)
    pylab.xscale('log')
    pylab.xticks(xtick_loc, xtick_label)
    pylab.tick_params(labelsize=8)

    if lfreq is not None:
        pylab.vlines(lfreq, min_y, max_y,
                     color='r', linestyles='--')
    if hfreq is not None:
        pylab.vlines(hfreq, min_y, max_y,
                     color='violet', linestyles='--')

    if cutoff == 0:
        pylab.suptitle('%s' % (plottitle), size=11)
    else:
        pylab.suptitle('%s\nR < %d km' % (plottitle, cutoff), size=11)
    outfile = os.path.join(outdir, "gof-%s-freq.png" % (gof_fileroot))
    print("==> Created GoF plot: %s" % (outfile))
    pylab.savefig(outfile, format="png",
                  transparent=False, dpi=plot_config.dpi)
    pylab.close()

def plot_three_component_gof(plottitle, gof_fileroot, indir, outdir,
                             cutoff=0, min_period=0.01, mode=None, colorset=None,
                             lfreq=None, hfreq=None):
    """
    Creates a GOF plot with three subplots (e.g. RotD50/PSA5n/PSA5e)
    """
    # Convert min/max frequencies to periods
    if lfreq is None:
        pmax = None
    else:
        pmax = 1.0 / float(lfreq)

    if hfreq is None:
        pmin = None
    else:
        pmin = 1.0 / float(hfreq)

    # Pick components and labels
    if min_period == 0.01:
        xtick_loc = XTICK_LOC_0_01
        xtick_label = XTICK_LABEL_0_01
    elif min_period == 0.1:
        xtick_loc = XTICK_LOC
        xtick_label = XTICK_LABEL
    else:
        raise exceptions.ParameterError("invalid min_period: %f" %
                                        (min_period))

    if mode == "rd50":
        comp_ext = COMP_EXT_RD50
        comp_title = COMP_TITLE_RD50
    elif mode == "rd100":
        comp_ext = COMP_EXT_RD100
        comp_title = COMP_TITLE_RD100
    else:
        raise exceptions.ParameterError("plot mode %s unsupported" %
                                        (mode))

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
    pylab.gcf().set_size_inches(6, 8)
    pylab.gcf().clf()

    pylab.subplots_adjust(left=0.125)
    pylab.subplots_adjust(right=0.95)
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
        #print("Reading component files %s.*" % (filenamebase))
        period[compnum], bias[compnum] = read_data("%s.bias" %
                                                   (filenamebase),
                                                   min_period)
        period[compnum], m90[compnum] = read_data("%s.m90" %
                                                  (filenamebase),
                                                  min_period)
        period[compnum], p90[compnum] = read_data("%s.p90" %
                                                  (filenamebase),
                                                  min_period)
        period[compnum], sigma[compnum] = read_data("%s.sigma" %
                                                    (filenamebase),
                                                    min_period)
        period[compnum], sigma0[compnum] = read_data("%s.sigma0" %
                                                     (filenamebase),
                                                     min_period)

        # Compute bias and conf interval lower/upper bounds
        for i in range(0, len(bias[compnum])):
            bias_l[compnum].append(bias[compnum][i] - sigma0[compnum][i])
            bias_h[compnum].append(bias[compnum][i] + sigma0[compnum][i])
            conf_l[compnum].append(m90[compnum][i])
            conf_h[compnum].append(p90[compnum][i])

    # Make sure all components have same number of data points
    npts = [len(component) for component in period]
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
        offset = COMP_OFFSET[compnum]

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
        pylab.xlabel("Period (sec)", size=8)
        pylab.ylabel("ln (data/model)", size=8)
        pylab.xscale('log')
        pylab.xticks(xtick_loc, xtick_label)
        pylab.tick_params(labelsize=8)

        if pmin is not None:
            pylab.vlines(pmin, min_horiz_y, max_horiz_y,
                         color='violet', linestyles='--')
        if pmax is not None:
            pylab.vlines(pmax, min_horiz_y, max_horiz_y,
                         color='r', linestyles='--')

    if cutoff == 0:
        pylab.suptitle('%s' % (plottitle), size=11)
    else:
        pylab.suptitle('%s\nR < %d km' % (plottitle, cutoff), size=11)
    outfile = os.path.join(outdir, "gof-%s.png" % (gof_fileroot))
    print("==> Created GoF plot: %s" % (outfile))
    pylab.savefig(outfile, format="png",
                  transparent=False, dpi=plot_config.dpi)
    pylab.close()

def plot(plottitle, gof_fileroot, indir, outdir,
         cutoff=0, min_period=0.01, mode=None, colorset=None,
         lfreq=None, hfreq=None):
    """
    Creates the GOF plot
    """
    if mode == "rd50-single-freq":
        plot_single_component_freq_gof(plottitle, gof_fileroot,
                                       indir, outdir,
                                       cutoff=cutoff,
                                       min_period=min_period,
                                       colorset=colorset,
                                       lfreq=lfreq, hfreq=hfreq)
    elif mode == "rd50-single":
        plot_single_component_gof(plottitle, gof_fileroot,
                                  indir, outdir,
                                  cutoff=cutoff,
                                  min_period=min_period,
                                  colorset=colorset,
                                  lfreq=lfreq, hfreq=hfreq)
    elif mode == "rd50" or mode == "rd100":
        plot_three_component_gof(plottitle, gof_fileroot,
                                 indir, outdir,
                                 cutoff=cutoff,
                                 min_period=min_period,
                                 mode=mode, colorset=colorset,
                                 lfreq=lfreq, hfreq=hfreq)
    else:
        raise exceptions.ParameterError("plot mode %s unsupported" %
                                        (mode))

def parse_arguments():
    """
    This function takes care of parsing the command-line arguments and
    asking the user for any missing parameters that we need
    """
    parser = argparse.ArgumentParser(description="Generates PSA comparison GoF plot.")
    parser.add_argument("--input-dir", dest="input_dir",
                        help="input directory with residuals files")
    parser.add_argument("--output-dir", dest="output_dir",
                        help="output directory")
    parser.add_argument("-o", "--output", "--output-file",
                        dest="output_file",
                        help="output rd100 file")
    parser.add_argument("--comp-label", dest="comp_label", required=True,
                        help="comparison label used for the output file prefix")
    parser.add_argument("--plot-mode", dest="plot_mode", default="rd50",
                        help="plot mode [rd50, rd50-single, rd50-single-freq, rd100]")
    parser.add_argument("--max-cutoff", dest="max_cutoff", type=float, default=1000.0,
                        help="select max cutoff distance (km) for the comparison")
    parser.add_argument("--low-freq", "--lf", dest="lfreq",
                        help="adds vertical line at this low frequency corner")
    parser.add_argument("--high-freq", "--hf", dest="hfreq",
                        help="adds vertical line at this high frequency corner")
    parser.add_argument("--colorset", dest="colorset", default="single",
                        help="select colorset [single/combined] default single")
    parser.add_argument("--plot-limit", dest="plot_limit", type=float, default=0.01,
                        help="select GoF plot limit, default=0.01s")
    parser.add_argument("--plot-title", "--title", dest="plot_title",
                        default="GOF Comparison Plot",
                        help="select plot title for the GoF plot")
    args = parser.parse_args()
    
    return args

def run():
    """
    Generate PSA GoF plot
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

    plot_psa_gof(input_dir, output_dir,
                 args.plot_title, args.comp_label,
                 plot_mode=args.plot_mode.lower(),
                 min_period=args.plot_limit,
                 max_cutoff=args.max_cutoff,
                 colorset=args.colorset.lower(),
                 lfreq=args.lfreq, hfreq=args.hfreq)

def plot_psa_gof(input_dir, output_dir,
                 plot_title, comp_label,
                 plot_mode='rd50', min_period=0.01,
                 max_cutoff=1000.0, colorset='single',
                 lfreq=None, hfreq=None):
    """
    Calls the plotting code with the required parameters
    """
    # Check input parameters
    plot_mode = plot_mode.lower()
    colorset = colorset.lower()

    if colorset != "single" and colorset != "combined":
        print("[ERROR]: Please use only 'single' or 'combined' for colorset!")
        sys.exit(1)

    if plot_mode not in ['rd50', 'rd50-single', 'rd50-single-freq', 'rd100']:
        print("[ERROR]: Please select plot mode from [rd50, rd50-single, rd50-single-freq, rd100]")
        sys.exit(1)

    if plot_mode != 'rd100':
        extension = "rd50"
    else:
        extension = "rd100"

    # Where to find residuals information
    fileroot = '%s_r0-%d-%s' % (comp_label, max_cutoff, extension)

    # Create plot
    plot(plot_title, fileroot, input_dir, output_dir,
         cutoff=max_cutoff, min_period=min_period,
         mode=plot_mode, colorset=colorset.lower(),
         lfreq=lfreq, hfreq=hfreq)

if __name__ == '__main__':
    run()
