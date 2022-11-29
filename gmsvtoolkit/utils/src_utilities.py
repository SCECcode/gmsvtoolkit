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

Utility functions for reading SRC files
"""
from __future__ import division, print_function

# Import Python modules
import re
from core.exceptions import ParameterError

# Compile regular expressions
re_parse_property = re.compile(r'([^:= \t]+)\s*[:=]?\s*(.*)')

def parse_properties(filename):
    """
    This function reads all properties from filename and returns a
    dictionary containing all key=value pairs found in the file
    """
    my_file = open(filename, 'r')
    props = {}

    for line in my_file:
        # Strip tabs, spaces and newlines from both ends
        line = line.strip(' \t\n')
        # Skip comments
        if line.startswith('#'):
            continue
        # Remove inline comments
        line = line.split('#')[0]
        # Skip empty lines
        if len(line) == 0:
            continue
        result = re_parse_property.search(line)
        if result:
            # Property parsing successful
            key = result.group(1)
            val = result.group(2)
            # Make key lowercase
            key = key.lower()
            props[key] = val

    # Don't forget to close the file
    my_file.close()

    # All done!
    return props

def parse_src_file(a_srcfile):
    """
    Function parses the SRC file and checks for needed keys. It
    returns a dictionary containing the keys found in the src file.
    """
    src_keys = parse_properties(a_srcfile)
    required_keys = ["magnitude", "fault_length", "fault_width", "dlen",
                     "dwid", "depth_to_top", "strike", "rake", "dip",
                     "lat_top_center", "lon_top_center"]
    for key in required_keys:
        if key not in src_keys:
            raise ParameterError("key %s missing in src file" % (key))
    # Convert keys to floats
    for key in src_keys:
        src_keys[key] = float(src_keys[key])

    return src_keys
