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

This module calculates Smoothed EAS from a FAS file
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import numpy as np

# Import GMSVToolkit modules
from utils import file_utilities

def ko98_smoothing(freqs, data, delta_freq, bexp):
    """
    # ** smoothing of a function y (equally-spaced, dx) with the "Konno-Ohmachi"
    # ** function sin (alog10(f/fc)^exp) / alog10(f/fc)^exp) ^^4
    # ** where fc is the frequency around which the smoothing is performed
    # ** exp determines the exponent 10^(1/exp) is the half-width of the peak
    # ** cf Konno & Ohmachi, 1998, BSSA 88-1, pp. 228-241
    """

    nx = len(freqs)
    data_smooth = np.zeros(nx)
    fratio = np.power(10., (2.5 / bexp))
    data_smooth[0] = data[0]

    for index in range(1, nx):
        freq = freqs[index]
        # Added check to avoid division by zero later and NaNs in the output file
        if freq == 0.0:
            data_smooth[index] = data[index]
            continue
        fc1 = freq / fratio
        fc2 = freq * fratio
        index1 = int(fc1 / delta_freq)
        index2 = int((fc2 / delta_freq) + 1)
        if index1 <= 1:
            index1 = 0
        if index2 >= nx:
            index2 = nx
        a1 = 0.0
        a2 = 0.0
        for j in range(index1, index2):
            if j != index:
                # Extra check to avoid NaNs in output file
                if freqs[j] == 0.0:
                    data_smooth[index] = data[index]
                    break
                c1 = bexp * np.log10(freqs[j] / freq)
                c1 = np.power(np.sin(c1) / c1, 4.0)
                a2 = a2 + c1
                a1 = a1 + c1 * data[j]
            else:
                a2 = a2 + 1.0
                a1 = a1 + data[index]
            data_smooth[index] = a1 / a2

    return data_smooth

def calculate_smoothed_eas(ns_file, ew_file, output_file=None):
    """
    Calculates the smoothed EAS at the same frequencies as specified in
    the input files
    """
    b_param = 188.5 # cm/s

    # Read data
    freqs, ns_data = file_utilities.read_fas_file(ns_file)
    _, ew_data = file_utilities.read_fas_file(ew_file)
    eas_data = []

    # Calculate EAS
    for ns_comp, ew_comp in zip(ns_data, ew_data):
        eas_data.append(np.sqrt(0.5*(pow(ns_comp, 2) + pow(ew_comp, 2))))

    # Calculate Smoothed EAS
    smoothed_eas = ko98_smoothing(freqs, eas_data,
                                  freqs[1]-freqs[0],
                                  b_param)

    # Write data file if output_file is provided
    if output_file is not None:
        out_file = open(output_file, 'w')
        out_file.write("# Freq(Hz)\t FAS H1 (cm/s)\t FAS H2 (cm/s)\t "
                       "EAS (cm/s)\t Smoothed EAS, b=%f (cm/s)\n" %
                       (b_param))
        for freq, fas_h1, fas_h2, eas, s_eas in zip(freqs, ns_data,
                                                    ew_data, eas_data,
                                                    smoothed_eas):
            out_file.write("%2.7E\t%2.7E\t%2.7E\t%2.7E\t%2.7E\n" %
                           (freq, fas_h1, fas_h2, eas, s_eas))
        out_file.close()

    # All done!
    return freqs, ns_data, ew_data, eas_data, smoothed_eas

if __name__ == '__main__':
    sys.exit(0)
