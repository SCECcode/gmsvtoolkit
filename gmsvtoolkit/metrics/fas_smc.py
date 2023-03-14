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

This module includes functions to use Boore's FAS tools
"""
from __future__ import division, print_function

# Import Python modules
import sys

def create_boore_asc2smc(control_file, input_file,
                         data_column, num_headers,
                         extension_string):
    """
    This function creates the control file for the asc2smc converter tool
    """
    ctl_file = open(control_file, 'w')
    ctl_file.write("!Control file for ASC2SMC      ! first line\n")
    ctl_file.write("! Revision of program involving a change in the "
                   "control file on this date:\n")
    ctl_file.write("   02/02/12\n")
    ctl_file.write("!Name of summary file:\n")
    ctl_file.write(" asc2smc.sum\n")
    ctl_file.write("!n2skip (-1=headers preceded by !; 0=no headers; "
                   "otherwise number of headers to skip)\n")
    ctl_file.write(" %d\n" % (num_headers))
    ctl_file.write("!write headers to smc file "
                   "(even if n2skip > 0)? (Y/N)\n")
    ctl_file.write(" Y\n")
    ctl_file.write("!sps (0.0 = obtain from input file)\n")
    ctl_file.write(" 0\n")
    ctl_file.write("!N columns to read, column number for "
                   "time and data columns \n")
    ctl_file.write("!  (for files made using blpadflt, period is in "
                   "column 1 and sd, pv, pa, rv, \n")
    ctl_file.write("!  aa are in columns 2, 3, 4, 5, 6, respectively)\n")
    ctl_file.write("! Note: if sps .ne. 0.0, then column number for time "
                   "is ignored (but a placeholder is\n")
    ctl_file.write("! still needed--e.g., 1 1 1 (read one column, which "
                   "contains the data; 1 20 1 would be the same)\n")
    ctl_file.write("! But note: if the data are not in the first column, "
                   "but only the data column is to be read\n")
    ctl_file.write("! (because sps will be used to establish "
                   "the time values),\n")
    ctl_file.write("! then ncolumns must be the column corresponding to "
                   "the data.  For example, assume that\n")
    ctl_file.write("! the data are in column 3 and that columns 1 and 2 "
                   "contain time and some other variable, but\n")
    ctl_file.write("! the time column is not to be used (perhaps because "
                   "accumulated error in creating the column\n")
    ctl_file.write("! leads to a slight shift in the time values).  "
                   "Then the input line should be:\n")
    ctl_file.write("!  3 1 3\n")
    ctl_file.write("!\n")
    ctl_file.write("! This program assumes one data point per row; if "
                   "there are more points (as, for example,\n")
    ctl_file.write("! in files with N points per line), "
                   "use the program wrapped2asc).\n")
    ctl_file.write("!\n")
    ctl_file.write(" 3 1 %d\n" % (data_column))
    ctl_file.write("!Xfactr\n")
    ctl_file.write(" 1.0\n")
    ctl_file.write("!Read input format (used if the format is such that "
                   "the values are not separated by spaces,\n")
    ctl_file.write("!in which case a free format cannot be "
                   "used for input)?\n")
    ctl_file.write("  N\n")
    ctl_file.write("!If yes, specify a format; if not, "
                   "still need a placeholder\n")
    ctl_file.write(" (3e13.5)\n")
    ctl_file.write("!For output, use old (standard) smc format or new\n")
    ctl_file.write('!higher precision format.   Specify "high" for\n')
    ctl_file.write("!high precision; any other word defaults to standard\n")
    ctl_file.write("!precision (but some word is needed as "
                   "a placeholder, even if\n")
    ctl_file.write("!standard precision is desired).\n")
    ctl_file.write(" high\n")
    ctl_file.write("!String to append to input file name "
                   "for the output filename.\n")
    ctl_file.write(" %s\n" % (extension_string))
    ctl_file.write('!Input file name (time,data pairs; "stop" in any '
                   'column to quit):\n')
    ctl_file.write("%s\n" % (input_file))
    ctl_file.write("STOP\n")
    ctl_file.close()

def create_boore_smc2fs2(control_file, input_file, name_string):
    """
    This function creates the control file for the smc2fs2 FAS tool
    """
    ctl_file = open(control_file, 'w')
    ctl_file.write('!Control file for program SMC2FS2\n')
    ctl_file.write('! Revision of program involving a change in the control '
                   'file on this date:\n')
    ctl_file.write('   03/10/10\n')
    ctl_file.write('! As many comment lines as desired, each '
                   'starting with "!"\n')
    ctl_file.write('! The string "pp:" indicates a new set '
                   'of processing parameters\n')
    ctl_file.write('! to be applied to the following smc files.  '
                   'The parameters are given on the\n')
    ctl_file.write('! lines following "pp:", until the next "pp:" line '
                   'or until "stop" is \n')
    ctl_file.write('! encountered.\n')
    ctl_file.write('! NOTE: Use the tapers with caution, '
                   'choosing them so that important signal\n')
    ctl_file.write('! is not reduced by the tapering.  '
                   'This can be particularly a problem with \n')
    ctl_file.write('! analog data from relatively small earthquakes '
                   'that triggered near the \n')
    ctl_file.write('! S-wave arrival.  \n')
    ctl_file.write('!\n')
    ctl_file.write('! -----------------------------------------'
                   '------------------------------------\n')
    ctl_file.write('!\n')
    ctl_file.write('! Meaning of smoothing input parameters\n')
    ctl_file.write('!\n')
    ctl_file.write('! NO SMOOTHING\n')
    ctl_file.write('! itype = 0\n')
    ctl_file.write('! SMOOTHING OVER EQUALLY SPACED FREQUENCIES\n')
    ctl_file.write('! itype = 1: box weighting function\n')
    ctl_file.write('!   smooth_param = width of box weighting function (Hz)\n')
    ctl_file.write('! itype = 2: triangular weighting function\n')
    ctl_file.write('!   smooth_param = width of triangular '
                   'weighting function (Hz)\n')
    ctl_file.write('! SMOOTHING OVER LOGARITHMICALLY SPACED FREQUENCIES\n')
    ctl_file.write('! itype = 3: box weighting function\n')
    ctl_file.write('!   smooth_param = xi, which is the fraction of '
                   'a decade for the\n')
    ctl_file.write('!                  box weighting function \n')
    ctl_file.write('! itype = 4: triangular weighting function\n')
    ctl_file.write('!   smooth_param = xi, which is the fraction of '
                   'a decade for the\n')
    ctl_file.write('!                  triangular weighting function \n')
    ctl_file.write('! itype = 5: Konno and Ohmachi weighting function '
                   '(see BSSA 88, 228-241)\n')
    ctl_file.write('!   smooth_param = xi, which is the fraction '
                   'of a decade for which\n')
    ctl_file.write('!                  the Konno and Ohmachi weighting '
                   'function is greater\n')
    ctl_file.write('!                  than 0.043.(it is related to\n')
    ctl_file.write('!                  their smoothing parameter b '
                   'by the equation\n')
    ctl_file.write('!                  b = 4.0/smooth_param, so we have '
                   'this correspondence between\n')
    ctl_file.write('!                  b and smooth_param\n')
    ctl_file.write('!                         b smooth_param \n')
    ctl_file.write('!                        10         0.40\n')
    ctl_file.write('!                        20         0.20\n')
    ctl_file.write('!                        40         0.10\n')
    ctl_file.write('!                  \n')
    ctl_file.write('!                  b = 40 seems to be commonly used, '
                   'but I do not think that it\n')
    ctl_file.write('!                  gives enough smoothing; '
                   'I PREFER SMOOTH_PARAM = 0.2, \n')
    ctl_file.write('!                  corresponding to b = 20. \n')
    ctl_file.write('!\n')
    ctl_file.write('! ipow = power of FAS to be smoothed '
                   '(2 = smoothing energy spectrum)\n')
    ctl_file.write('!\n')
    ctl_file.write('! df_smooth: Note: need df_smooth for '
                   'linearly-spaced smoothers, \n')
    ctl_file.write('! and generally it should be the df from the fft.  '
                   'For general x data, it is\n')
    ctl_file.write('! the spacing between x values, assumed to be constant,  '
                   'The reason for\n')
    ctl_file.write('! including it as an input parameter is to "fool" the\n')
    ctl_file.write('! program to do smoothing over a specified '
                   'number of points by\n')
    ctl_file.write('! setting df_smooth = 1 and smooth_param = number '
                   'of points (including \n')
    ctl_file.write('! points with zero weight at ends; e.g., '
                   'smooth_param = 5 will \n')
    ctl_file.write('! give a smoother with weights 0, 1/4, 2/4, 1/4, 0; '
                   'smooth_param\n')
    ctl_file.write('! should be odd).\n')
    ctl_file.write('!\n')
    ctl_file.write('! ------------------------------------'
                   '-----------------------------------------\n')
    ctl_file.write('! Meaning of frequency specification parameters:\n')
    ctl_file.write('!\n')
    ctl_file.write('!SPECIFY_FREQUENCIES? (y/n):\n')
    ctl_file.write('! <enter Y or N>\n')
    ctl_file.write('!FREQUENCY SPECIFICATION: \n')
    ctl_file.write('!  If specify_frequencies = Y, then enter the \n')
    ctl_file.write('!    number of frequencies, freq(1), freq(2)..., '
                   'freq(nfreq)\n')
    ctl_file.write('!  If specify_frequencies = N, then enter \n')
    ctl_file.write('!    f_low, f_high, log-spaced (0=N, 1=Y), freq_param\n')
    ctl_file.write('!         if freq_param = 0.0, there is no interpolation, '
                   'and the FFT frequencies \n')
    ctl_file.write('!            are used between f_low and f_high '
                   '(log-spaced is ignored).\n')
    ctl_file.write('!         if freq_param /= 0.0 and log-spaced = 0, '
                   'then freq_param is the spacing of the\n')
    ctl_file.write('!            interpolated frequencies '
                   'between f_low and f_high\n')
    ctl_file.write('!         if freq_param /= 0.0 and log-spaced = 1, '
                   'then freq_param is the number of \n')
    ctl_file.write('!            interpolated frequencies between f_low and '
                   'f_high (NOTE: f_low must be > 0.0)\n')
    ctl_file.write('! ---------------------------------------'
                   '--------------------------------------\n')
    ctl_file.write('!\n')
    ctl_file.write('!Name of summary file:\n')
    ctl_file.write(' smc2fs2.sum\n')
    ctl_file.write('PP: new set of parameters\n')
    ctl_file.write('!tskip, tlength\n')
    ctl_file.write('   0.0 2000.0\n')
    ctl_file.write('!dc_remove?\n')
    ctl_file.write('  .true.        \n')
    ctl_file.write('!Length of taper at beginning and end of time series, '
                   'before adding zeros\n')
    ctl_file.write('! to make the number of points in '
                   'the record a power of two.\n')
    ctl_file.write(' 0.0 0.0\n')
    ctl_file.write('!signnpw2(<0, backup for npw2, no zpad):\n')
    ctl_file.write(' +1.0\n')
    ctl_file.write('!smoothing: itype, ipow, df_smooth '
                   '(0 = FFT df), smooth_param\n')
    ctl_file.write('! (see above for the meaning of these input parameters):\n')
    ctl_file.write('   0 1 0.0 0.20\n')
    ctl_file.write('!SPECIFY_FREQUENCIES? (y/n):\n')
    ctl_file.write('  N\n')
    ctl_file.write('!FREQUENCY SPECIFICATION\n')
    ctl_file.write('   0.01 100.0 0 0.0 \n')
    ctl_file.write('!character string to append to filename:\n')
    ctl_file.write('   %s\n' % (name_string))
    ctl_file.write('!Output in smc format (Y,N)?\n')
    ctl_file.write('! ***IMPORTANT NOTE: Output cannot be in smc '
                   'format if use log-spaced \n')
    ctl_file.write('! frequencies because programs such as smc2asc '
                   'have not been modified\n')
    ctl_file.write('! to deal with log-spaced frequency.\n')
    ctl_file.write(' n\n')
    ctl_file.write('!Files to process:\n')
    ctl_file.write('%s\n' % (input_file))
    ctl_file.write('stop\n')
    ctl_file.close()

if __name__ == '__main__':
    sys.exit(0)
