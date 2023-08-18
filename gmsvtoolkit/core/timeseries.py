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

GMSVToolkit seismogram processing tools
"""
from __future__ import division, print_function

# Import Python modules
import os
import copy
import math

import numpy as np
from scipy.signal import decimate
import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('Agg') # Disables use of Tk/X11
import matplotlib.pyplot as plt
import pylab

# Import GMSVToolkit modules
from core import gmsvtoolkit_config
from core.station_list import StationList
from plots import plot_config
from utils import os_utilities
from utils.file_utilities import read_bbp_file, read_bbp_dt
from utils import gmsv_library
from utils.gmsv_library import taper, smooth

VALID_FORMATS = ["acc", "vel", "dis"]
VALID_UNITS = ["cm", "cm/s", "cm/s/s"]
COMPS = [".000", ".090", ".ver"]
INSTALL = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()

class Timeseries(object):
    """
    Timeseries class
    """

    def __init__(self, input_file=None, data=[],
                 station_name="NoName", orientation=None,
                 latitude=None, longitude=None,
                 data_type=None, units=None):
        """
        Initializes class variables
        """
        self.input_file = input_file
        self.data_type = data_type
        self.units = units
        self.dt = None
        self.orientation = None
        self.station_name = station_name
        self.latitude = latitude
        self.longitude = longitude
        self.padding = 0
        self.data = data
        self.history = []

        # Check if data or file were provided
        if len(data) and input_file is not None:
            raise ValueError("[ERROR]: Please provide only one of data or filename!")

        if input_file is None and len(data) == 0:
            raise ValueError("[ERROR]: Please provide one of data or filename!")

        if len(data):
            # If user provided data, check if it is what we expect
            if len(data) != 4:
                raise ValueError("[ERROR]: data array needs to have 4 components!")

            if self.units is None:
                raise ValueError("[ERROR]: Please provide units!")
            else:
                self.units = self.units.lower()

            # Convert arrays to Numpy arrays, figure out dt
            self.data = [np.array(item) for item in data]
            self.dt = self.data[0][1] - self.data[0][0]

            if self.units == "cm":
                self.data_type = "dis"
            elif self.units == "cm/s":
                self.data_type = "vel"
            elif self.units == "cm/s/s":
                self.data_type = "acc"
            else:
                raise ValueError("[ERROR]: Unknown unit %s" % (self.units))
        
        # Check data type, if provided
        if self.data_type is not None:
            if self.data_type not in VALID_FORMATS:
                raise ValueError("[ERROR]: Unknown data type %s" % (self.units))

        # Check orientation, if provided
        if orientation is not None:
            if type(orientation) != list:
                raise TypeError("[ERROR]: Orientation must be a list!")
            if len(orientation) != 3:
                raise ValueError("[ERROR]: Orientation must contain three elements!")
            orientation[0] = float(orientation[0])
            orientation[1] = float(orientation[1])
            orientation[2] = orientation[2].lower()
            if orientation[2] != "up" and orientation[2] != "down":
                raise ValueError("[ERROR]: Vertical orientation must be up or down!")
        
        # Check file type
        if input_file is not None:
            file_extension = os.path.splitext(input_file)[1]
            if file_extension.lower() == ".bbp":
                self._read_bbp_file()
            else:
                raise ValueError("[ERROR]: Unknown file extension %s" % (file_extension))

        # Pick user orientation, if provided
        if orientation is not None:
            self.orientation = orientation
        else:
            # If no orientation was found, use N/E/up
            if self.orientation is None:
                self.orientation = [0.0, 90.0, 'up']

    def copy(self):
        """
        Make a copy of this class
        """
        return copy.deepcopy(self)

    def _read_bbp_file(self):
        """
        Reads BBP file and initializes class variables
        """
        self.units = self._read_bbp_units(self.input_file)
        self.data = list(read_bbp_file(self.input_file))
        self.dt = read_bbp_dt(self.input_file)
        self.orientation = self._read_bbp_orientation(self.input_file)

        # Check type
        if self.data_type is None:
            if self.units == "cm":
                self.data_type = "dis"
            elif self.units == "cm/s":
                self.data_type = "vel"
            elif self.units == "cm/s/s":
                self.data_type = "acc"
            else:
                raise ValueError("[ERROR]: Unknown unit %s" % (self.units))

        self.history.append("Loaded BBP file: %s" % (self.input_file))

    def _read_bbp_units(self, filename):
        """
        Get the units from the file's header
        Returns either "m" or "cm"
        """
        units = None

        input_file = open(filename, 'r')
        for line in input_file:
            if line.find("time(sec)") > 0:
                units = line.split()[2]
                break
        input_file.close()

        # Make sure we got something
        if units is None:
            raise ValueError("[ERROR]: Cannot find units in bbp file!")

        # Parse and figure what what we got
        units_start = units.find("(")
        units_end = units.find(")")
        if units_start < 0 or units_end < 0:
            raise ValueError("[ERROR]: Cannot parse units in bbp file!")

        units = units[units_start+1:units_end]

        # Check if we got what we needed
        if units == "cm" or units == "cm/s" or units == "cm/s/s":
            return units

        # Invalid units in this file
        raise ValueError("[ERROR]: Cannot parse units in bbp file!")

    def _read_bbp_orientation(self, filename):
        """
        Try to read units from a BBP file header

        Returns None, if none found
        """
        orientation = None

        input_file = open(filename, 'r')
        for line in input_file:
            if line.find("orientation=") > 0:
                line = line.strip()
                orientation = line[(line.find("=") + 1):]
                orientation = orientation.strip().split(",")
                orientation = [val.strip() for val in orientation]
                orientation[0] = float(orientation[0])
                orientation[1] = float(orientation[1])
                orientation[2] = orientation[2].lower()
                if orientation[2] != "up" and orientation[2] != "down":
                    raise ValueError("[ERROR]: Vertical orientation must be up or down!")
                break
        input_file.close()

        # All done!
        return orientation

    def write_bbp(self, filename,
                  long_headers=False,
                  write_history=False):
        """
        Write timeseries to a bbp file

        long headers  - outputs extra metadata about the timeseries

        write_history - outputs extra headers recording a history
                        of transformations made to the timeseries
        """
        # Open output file
        out_fp = open(filename, 'w')

        if write_history:
            # Write extra header lines with processing history
            for item in self.history:
                out_fp.write("# %s\n" % (item))

        if long_headers:
            # Write long header
            out_fp.write("#     Station= %s\n" % (self.station_name))
            out_fp.write("#         lon= %s\n" % (self.longitude))
            out_fp.write("#         lat= %s\n" % (self.latitude))
            out_fp.write("#       units= %s\n" % (self.units))
            out_fp.write("#     padding= %d\n" % (self.padding))
            out_fp.write("# orientation= %s\n" % (self.orientation))
            out_fp.write("#\n")
            out_fp.write("# Data fields are TAB-separated\n")
            out_fp.write("# Column 1: Time (s)\n")
            out_fp.write("# Column 2: H1 component "
                         "(+ is %s)\n" % str((self.orientation[0])))
            out_fp.write("# Column 3: H2 component "
                         "(+ is %s)\n" % str((self.orientation[1])))
            out_fp.write("# Column 4: V component "
                         "(+ is %s)\n" % (self.orientation[2]))
            out_fp.write("#\n")
        else:
            # Write short header
            out_fp.write("#    time(sec)      %s(%s)      %s(%s)      %s(%s)\n" %
                         (self.orientation[0], self.units,
                          self.orientation[1], self.units,
                          self.orientation[2], self.units))

        # Now, write timeseries in BBP format
        for time, comp_h1, comp_h2, comp_v in zip(self.data[0],
                                                  self.data[1],
                                                  self.data[2],
                                                  self.data[3]):
            out_fp.write("%1.9E %1.9E %1.9E %1.9E\n" %
                         (time, comp_h1, comp_h2, comp_v))

        # All done, close file
        out_fp.close()

    def convert_to_acc(self):
        """
        Differentiate timeseries until we get acceleration data
        """
        if self.data_type == "dis":
            self.differentiate()

        if self.data_type == "vel":
            self.differentiate()

    def convert_to_vel(self):
        """
        Convert timeseries to velocity, use integrate or differentiate
        """
        if self.data_type == "dis":
            self.differentiate()

        if self.data_type == "acc":
            self.integrate()

    def convert_to_dis(self):
        """
        Convert timeseries to displacement, integrate until we have displacement
        """
        if self.data_type == "acc":
            self.integrate()

        if self.data_type == "vel":
            self.integrate()

    def integrate(self):
        """
        Integrate the timeseries,
        update type and units accordingly
        """
        old_data_type = self.data_type
        
        if self.data_type == "dis":
            raise RuntimeError("[ERROR]: Cannot integrate displacement timeseries!")
        for i in range(1, 4):
            self.data[i] = gmsv_library.integrate(self.data[i], self.dt)
        if self.data_type == "acc":
            self.data_type = "vel"
            self.units = "cm/s"
        else:
            self.data_type = "dis"
            self.units = "cm"

        self.history.append("Integrated timeseries %s --> %s" % (old_data_type, self.data_type))

    def differentiate(self):
        """
        Calculate the derivative of the timeseries, update
        data type and units accordingly
        """
        old_data_type = self.data_type

        if self.data_type == "acc":
            raise RuntimeError("[ERROR]: Cannot differentiate acceleration timeseries!")

        for i in range(1, 4):
            self.data[i] = gmsv_library.differentiate(self.data[i], self.dt)
        if self.data_type == "vel":
            self.data_type = "acc"
            self.units = "cm/s/s"
        else:
            self.data_type = "vel"
            self.units = "cm/s"

        self.history.append("Differentiated timeseries %s --> %s" % (old_data_type, self.data_type))
        
    def rotate(self, rotation_angle):
        """
        The function rotates a timeseries

        Input:
            rotation_angle - angle to rotate the timeseries in degrees
        """
        # Check rotation angle
        if rotation_angle is None or rotation_angle == 0.0 or rotation_angle == 360.0:
            # Nothing to do!
            return

        if rotation_angle < 0 or rotation_angle > 360:
            raise ValueError("[ERROR]: rotate: Invalid rotation angle: %f" % (rotation_angle))

        # Make sure they all have the same number of points
        if len(self.data[0]) != len(self.data[1]) != len(self.data[2]) != len(self.data[3]):
            n_points = len(min(self.data), key=len)
            self.data[0] = self.data[0][0:n_points-1]
            self.data[1] = self.data[1][0:n_points-1]
            self.data[2] = self.data[2][0:n_points-1]
            self.data[3] = self.data[3][0:n_points-1]

        # Order the channels properly
        if self.orientation[0] > self.orientation[1]:
            temp = self.data[1]
            self.data[1] = self.data[2]
            self.data[2] = temp
            temp = self.orientation[1]
            self.orientation[1] = self.orientation[0]
            self.orientation[0] = temp

        # Calculate angle between components
        c_angle = self.orientation[0] - self.orientation[1]

        # We need two orthogonal channels
        if abs(c_angle) != 90 and abs(c_angle) != 270:
            raise RuntimeError("[ERROR]: rotate_timeseries: Need two orthogonal channels!")

        # Create rotation matrix
        if c_angle == 90:
            matrix = np.array([(math.cos(math.radians(rotation_angle)),
                                -math.sin(math.radians(rotation_angle))),
                               (math.sin(math.radians(rotation_angle)),
                                math.cos(math.radians(rotation_angle)))])
        else:
            # Angle is 270!
            matrix = np.array([(math.cos(math.radians(rotation_angle)),
                                +math.sin(math.radians(rotation_angle))),
                               (math.sin(math.radians(rotation_angle)),
                                -math.cos(math.radians(rotation_angle)))])

        # Rotate
        [self.data[1], self.data[2]] = matrix.dot([self.data[1],
                                                   self.data[2]])

        # Adjust orientation
        self.orientation[0] = self.orientation[0] - rotation_angle
        self.orientation[1] = self.orientation[1] - rotation_angle

        # Add 360 degrees if needed
        if self.orientation[0] < 0:
            self.orientation[0] = self.orientation[0] + 360
        if self.orientation[1] < 0:
            self.orientation[1] = self.orientation[1] + 360

        self.history.append("Rotated timeseries %3.2f degrees" % (rotation_angle))

    def interp(self, new_dt, fast=False, debug=False, debug_plot=None):
        """
        Calls the sinc interp method

        Inputs:
            new_dt - desired new delta t
            debug - debug flag, generates extra information and plot
            debug_plot - debug plot filename

        Outputs:
            timeseries with new dt
        """
        if debug:
            print("[INFO]: Interpolating timeseries: old_dt: %.3f - new_dt: %.3f" %
                  (self.dt, new_dt))

        if self.dt == new_dt:
            # Nothing to do!
            return

        # Quick interpolation rule for downsampling
        if new_dt % self.dt == 0.0 and fast:
            downsample_factor = int(new_dt // self.dt)
            for i in range(0, 4):
                self.data[i] = decimate(self.data[i], downsample_factor)

            self.history.append("Interpolated timeseries dt %3.2f --> %3.2f" % (self.dt, new_dt))
            self.dt = new_dt
            return

        samples = len(self.data[0])
        old_times = self.data[0]
        old_dt = self.dt
        old_data = self.data[1]
        new_times = np.arange(0, samples * self.dt, new_dt)

        sinc_matrix = (np.tile(new_times, (len(old_times), 1)) -
                   np.tile(old_times[:, np.newaxis], (1, len(new_times))))
        for i in range(1, 4):
            self.data[i] = np.dot(self.data[i], np.sinc(sinc_matrix / self.dt))
        self.data[0] = new_times
        self.dt = new_dt
        self.history.append("Interpolated timeseries dt %3.2f --> %3.2f" % (old_dt, new_dt))
        
        if debug:
            # Find data to plot, from t=10s until t=10s+50pts
            old_start_idx = int(10.0 // old_dt) + 1
            old_end_idx = old_start_idx + 50
            if len(old_times) < old_end_idx:
                print("[INFO]: Not enough data to create debug plot!")
                return
            new_start_idx = int(10.0 // new_dt) + 1
            new_end_idx = int(old_times[old_end_idx] // new_dt) + 1

            # Initialize plot
            fig, _ = plt.subplots()
            fig.clf()

            plt.plot(old_times[old_start_idx:old_end_idx],
                     old_data[1][old_start_idx:old_end_idx], 'o',
                     new_times[new_start_idx:new_end_idx],
                     self.data[1][new_start_idx:new_end_idx], 'x')
            plt.grid(True)
            plt.xlabel('Seconds')
            plt.title(os.path.splitext(os.path.basename(debug_plot))[0])
            plt.savefig(debug_plot, format='png',
                        transparent=False,
                        dpi=plot_config.dpi)
            pylab.close()

    def FAS(self, points, fmin, fmax, s_factor):
        """
        Calculates the FAS of the input array using NumPy's fft Library

        Inputs:
            points - length of the transformed axis in the fft output
            fmin - min frequency for results
            fmax - max frequency for results
            s_factor - smooth factor to be used for the smooth function
        Outputs:
            freq - frequency array
            afs - fas
        """
        afs = [abs(np.fft.fft(self.data[i], points)) * self.dt for i in range(1, 4)]
        freq = (1 / self.dt) * np.array(range(points)) / points

        deltaf = (1 / self.dt) / points

        inif = int(fmin / deltaf)
        endf = int(fmax / deltaf) + 1

        afs = [item[inif:endf] for item in afs]
        afs = [smooth(item, s_factor) for item in afs]

        freq = freq[inif:endf]
        return freq, afs[0], afs[1], afs[2]

    def appendzeros(self, flag, t_diff, m):
        """
        Adds zeros in the front or at the end of an numpy array,
        apply taper before adding

        Inputs:
            flag - 'front' or 'end' - tapering flag passed to
                    the taper function
            t_diff - how much time to add (in seconds)
            m - number of samples for tapering
        Outputs:
            timeseries - Output timeseries after processing
        """
        num = int(t_diff / self.dt)
        zeros = np.zeros(num)

        if flag == 'front':
            # applying taper in the front
            if m != 0:
                window = taper('front', m, len(self.data[0]))
                for i in range(1, 4):
                    self.data[i] = self.data[i] * window

            # adding zeros in front of data
            for i in range(1, 4):
                self.data[i] = np.append(zeros, self.data[i])

        elif flag == 'end':
            if m != 0:
                # applying taper in the end
                window = taper('end', m, len(self.data[0]))
                for i in range(1,4):
                    self.data[i] = self.data[i] * window

                for i in range(1, 4):
                    self.data[i] = np.append(self.data[i], zeros)

        # Recompute time array
        self.data[0] = np.arrange(0, len(self.data[1]) * self.dt, self.dt)

    def cutting(self, flag, t_diff, m):
        """
        Cuts data in the front or at the end of an numpy array
        apply taper after cutting
 
        Inputs:
            flag - 'front' or 'end' - flag to indicate from where to cut samples
            t_diff - how much time to cut (in seconds)
            m - number of samples for tapering
        Outputs:
            timeseries - Output timeseries after cutting
        """
        num = int(t_diff / self.dt)
        if num >= len(self.data[1]):
            raise RuntimeError("[ERROR]: fail to cut timeseries.")

        if flag == 'front' and num != 0:
            # cutting timeseries
            for i in range(1, 4):
                self.data[i] = self.data[i][num:]

            # applying taper at the front
            window = taper('front', m, len(self.data[1]))
            for i in range(1, 4):
                self.data[i] = self.data[i] * window

        elif flag == 'end' and num != 0:
            num *= -1
            # cutting timeseries
            for i in range(1, 4):
                self.data[i] = self.data[i][:num]

            # applying taper at the end
            window = taper('end', m, len(self.data[1]))
            for i in range(1, 4):
                self.data[i] = self.data[i] * window

        # Recompute time array
        self.data[0] = np.arrange(0, len(self.data[1]) * self.dt, self.dt)

    def plot(self, output_file, plot_title=None,
             xmin=0.0, xmax=None, style='k',
             label=None):
        """
        Generates timeseries plot
        """
        num_components = 3
        delta_t = self.dt
        xtmin = xmin
        xtmax = xmax
        if xtmin is None:
            xtmin = 0.0

        min_i = int(xtmin/delta_t)
        if xtmax is not None:
            max_i = int(xtmax/delta_t)
        else:
            max_i = len(self.data[0])
            xtmax = self.dt * len(self.data[0])

        if label is None:
            label = self.station_name
        labels = [label]

        # Create plot
        num_rows = num_components
        num_columns = 1
        f, axarr = plt.subplots(nrows=num_rows,
                                ncols=num_columns,
                                figsize=(14, 9))

        # Change array shape since NumPy doesn't make a distinction
        # between column and vector arrays
        if len(axarr.shape) == 1:
            axarr.shape = (axarr.shape[0], 1)
        
        # For each component: h1, h2, vertical
        for i in range(0, num_components):
            samples = len(self.data[0])

            # Get orientation
            orientation = self.orientation[i]
            if type(orientation) is not str:
                orientation = str(int(orientation))

            if self.data_type == "acc":
                title =  "Acceleration : %s" % (orientation)
            elif self.data_type == "vel":
                title = "Velocity : %s" % (orientation)
            elif self.data_type == "dis":
                title = "Displacement : %s" % (orientation)
            else:
                raise ValueError("[ERROR]: Invalid data_type %s, must be acc, vel, or dis!" %
                                 (self.data_type))

            vals = self.data[i+1]
            c_vals = vals[min_i:max_i]
            times = np.arange(xtmin, min(xtmax, (delta_t * samples)), delta_t)

            index = 0
            axarr[i][index].set_title(title)
            axarr[i][index].grid(True)
            axarr[i][index].plot(times, c_vals, style, lw=0.5)
            # Add labels to first plot
            if i == 0:
                axarr[i][index].legend(labels, prop={'size':6})
            axarr[i][index].set_xlim([xtmin, xtmax])
            index = index + 1

        # Make nice plots with tight_layout
        f.tight_layout()

        # Add overall title if provided
        if plot_title is not None:
            st = plt.suptitle(plot_title, fontsize=16)
            f.subplots_adjust(top=0.92)

        # All done, save plot
        if output_file.lower().endswith(".png"):
            fmt = 'png'
        elif output_file.lower().endswith(".pdf"):
            fmt = 'pdf'
        else:
            raise ValueError("[ERROR]: Invalid file format, supported formats are png and pdf!")

        plt.savefig(output_file, format=fmt,
                    transparent=False,
                    dpi=plot_config.dpi)
        plt.close()
