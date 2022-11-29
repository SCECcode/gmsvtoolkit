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

OS utility functions used in the GMSVToolkit
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import traceback
import subprocess

# GMSVToolkit files
from core import exceptions

# Set to the maximum allows filename in the GP codebase
GP_MAX_FILENAME = 256
# Set to the maximum allowed filename in the SDSU codebase
SDSU_MAX_FILENAME = 256

def runprog(cmd, print_cmd=True, abort_on_error=False):
    """
    Run a program on the command line and capture the output and print
    the output to stdout
    """
    # Check if we have a binary to run
    if not os.access(cmd.split()[0], os.X_OK) and cmd.startswith("/"):
        raise exceptions.GMSVToolkitExternalError("%s does not seem an executable path!" %
                                                  (cmd.split()[0]))

    try:
        if print_cmd:
            print("Running: %s" % (cmd))
        proc = subprocess.Popen(cmd, shell=True)
        proc.wait()
    except KeyboardInterrupt:
        print("Interrupted!")
        sys.exit(1)
    except:
        print("Unexpected error returned from Subprocess call: ",
              sys.exc_info()[0])

    if abort_on_error:
        # If we got a non-zero exit code, abort
        if proc.returncode != 0:
            # Check if interrupted
            if proc.returncode is None:
                raise exceptions.GMSVToolkitExternalError("%s\n" %
                                                          (traceback.format_exc()) +
                                                          "%s failed!" %
                                                          (cmd))
            raise exceptions.GMSVToolkitExternalError("%s\n" %
                                                      (traceback.format_exc()) +
                                                      "%s returned %d" %
                                                      (cmd, proc.returncode))

    return proc.returncode

def get_command_output(cmd, output_on_stderr=False, abort_on_error=False):
    """
    Get the output of the command from the shell. Adapted from CSEP's
    commandOutput function in Environment.py
    """
    # Execute command using the UNIX shell
    child = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    child_data, child_error = child.communicate()

    if child_error and output_on_stderr is False:
        if abort_on_error:
            error_msg = ("Child process '%s' failed with error code %s" %
                         (cmd, child_error))
            raise exceptions.GMSVToolkitExternalError("%s\n" %
                                                      (traceback.format_exc()) +
                                                      "%s" % (error_msg))
        else:
            return ""

    # Check for non-empty result string from the command
    if ((child_data is None or len(child_data) == 0) and
        output_on_stderr is False):
        if abort_on_error:
            error_msg = "Child process '%s' returned no data!" % (cmd)
            raise exceptions.GMSVToolkitExternalError("%s\n" %
                                                      (traceback.format_exc()) +
                                                      "%s" % (error_msg))
        else:
            return ""

    # If command output is on stderr
    if output_on_stderr is True:
        child_data = child_error

    return child_data

def mkdirs(list_of_dirs, print_cmd=True):
    """
    Creates all directories specified in the list_of_dirs
    """
    for my_dir in list_of_dirs:
        cmd = "mkdir -p %s" % (my_dir)
        runprog(cmd, print_cmd=print_cmd, abort_on_error=True)

def relpath(path, start=os.curdir):
    """
    Return a relative version of a path
    (from Python 2.6 os.path.relpath() implementation)
    """
    sep = os.sep
    if not path:
        raise ValueError("no path specified")

    start_list = os.path.abspath(start).split(sep)
    path_list = os.path.abspath(path).split(sep)

    # Work out how much of the filepath is shared by start and path.
    i = len(os.path.commonprefix([start_list, path_list]))

    rel_list = [os.pardir] * (len(start_list) - i) + path_list[i:]
    if not rel_list:
        return '.'
    return os.path.join(*rel_list)

def check_path_lengths(variables, max_length):
    """
    This function checks each variable in the variables list and makes
    sure their path lenghts are less than max_length. It raises a
    ValueError exception otherwise.
    """
    for var in variables:
        if len(var) > max_length:
            raise ValueError("Path len for %s " % (var) +
                             " is %d characters long, maximum is %d" %
                             (len(var), max_length))

def list_subdirs(d):
    """
    This function returns all subdirectories inside the directory d
    """
    # Return empty array if d is None
    if d is None:
        return []
    # Use list comprehension
    return [sub for sub in os.listdir(d) if os.path.isdir(os.path.join(d, sub))]

if __name__ == "__main__":
    print("Testing: %s" % (sys.argv[0]))
    CMD = "/bin/date"
    RESULT = runprog(CMD)
    if RESULT != 0:
        print("Error running cmd: %s" % (CMD))
    else:
        print("Success!")
