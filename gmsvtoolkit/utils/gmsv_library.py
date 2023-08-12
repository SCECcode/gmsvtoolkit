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

GMSV Toolkit seismogram processing library
"""
from __future__ import division, print_function

# Import Python modules
import math
import numpy as np
from scipy.integrate import cumtrapz
from scipy.signal import kaiser

def integrate(data, dt):
    """
    Integrated the input array data using SciPy's cumtrapz function,
    with the initial condition assumed 0, the result has same size as input

    Inputs:
        data - timeseries
        dt - delta t for the input timeseries
    Outputs:
        newdata - data array after integration
    """
    newdata = cumtrapz(data, dx=dt, initial=0) + data[0] * dt / 2.0

    return newdata

def differentiate(data, dt):
    """
    Computes the derivative of an numpy array

    Inputs:
        data - input timeseries array
        dt - delta t for the input timeseries
    Outputs:
        newdata - data array after differentiation
    """
    newdata = np.insert(data, 0, 0)
    newdata = np.diff(newdata) / dt

    return newdata

def taper(flag, m, samples):
    """
    Returns a Kaiser window created by a Besel function

    Inputs:
        flag - set to 'front', 'end', or 'all' to taper at the beginning,
               at the end, or at both ends of the timeseries
        m - number of samples for tapering
        samples - total number of samples in the timeseries
    Outputs:
        window - Taper window
    """
    window = kaiser(2*m+1, beta=14)

    if flag == 'front':
        # cut and replace the second half of window with 1s
        ones = np.ones(samples-m-1)
        window = window[0:(m+1)]
        window = np.concatenate([window, ones])

    elif flag == 'end':
        # cut and replace the first half of window with 1s
        ones = np.ones(samples-m-1)
        window = window[(m+1):]
        window = np.concatenate([ones, window])

    elif flag == 'all':
        ones = np.ones(samples-2*m-1)
        window = np.concatenate([window[0:(m+1)], ones, window[(m+1):]])

    # avoid concatenate error
    if window.size < samples:
        window = np.append(window, 1)

    if window.size != samples:
        print(window.size)
        print(samples)
        print("[ERROR]: taper and data do not have the same number of samples.")
        window = np.ones(samples)

    return window

def smooth(data, factor):
    """
    Smooth the data in the input array

    Inputs:
        data - input array
        factor - used to calculate the smooth factor

    Outputs:
        data - smoothed array
    """
    # factor = 3; c = 0.5, 0.25, 0.25
    # TODO: fix coefficients for factors other than 3
    c = 0.5 / (factor - 1)
    for i in range(1, data.size - 1):
        data[i] = 0.5 * data[i] + c * data[i - 1] + c * data[i + 1]
    return data

def get_points(samples):
    """
    Returns the least base-2 number that is greater than the max
    value in the samples array

    Inputs:
        samples - array with data
    Outputs:
        2**power - base-2 number that is greater than the max samples
    """
    power = int(math.log(max(samples), 2)) + 1
    return 2**power

def calculate_distance(location1, location2):
    """
    Calculates the distance between two pairs of lat, long coordinates
    using the Haversine formula

    Inputs:
        location1 - [lat, lon] array with first location
        location2 - [lat, lon] array with second location
    Outputs:
        distance - in kilometers
    """
    lat1 = math.radians(abs(location1[0]))
    lon1 = math.radians(abs(location1[1]))
    lat2 = math.radians(abs(location2[0]))
    lon2 = math.radians(abs(location2[1]))

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers
    r = 6371.0

    return c * r

def get_periods(tmin, tmax):
    """
    Return an array of period T

    Inputs:
        tmin - minimum period
        tmax - maximum period

    Outputs:
        periods - array of periods
    """
    # tmin = 1/fmax
    # tmax = 1/fmin
    a = np.log10(tmin)
    b = np.log10(tmax)

    periods = np.linspace(a, b, 20)
    periods = np.power(10, periods)

    return periods

