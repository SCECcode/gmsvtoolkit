In this page we describe how the different software modules provided in the GMSV Toolkit are organized, and explain how to use them using both command-line and Python API.

## Package Organization

The GMSV Toolkit software modules are organized in a few packages:

```sh
gmsvtoolkit/
├── core/
├── metrics/
├── models/
├── plots/
├── src/
├── stats/
├── tests/
└── utils/
```

Most of the codes are split into 4 packages: metrics, models, plots, and stats. The tests folder includes [unit tests](Running-Tests) and reference files needed to verify if the package was installed correctly. The src folder includes C/C++/Fortran codes that are used by the Python packages; the core folder includes basic functionality that is used by most codes, and the utils folder includes miscellaneous codes.

### Metrics

The metrics package includes a number of tools for computing metrics on timeseries files, and are described in more detail in the [Metrics page](./Metrics-Calculation). The codes can be used to calculate GMPEs for a set of stations or to compute FAS, RotD50/RotD100, and the RZZ2015 metrics for a set of acceleration timeseries.

```sh
gmsvtoolkit/
├── core/
├── metrics/
│   ├── calc_gmpe.py
│   ├── fas.py
│   ├── rotdxx.py
│   └── rzz2015.py
├── models/
├── plots/
├── src/
├── stats/
├── tests/
└── utils/
```

### Models

The models package implements several GMPEs. The codes implement the Afshari and Stewart (2016) GMPE for significant duration, the RZZ2015 GMPEs, and the NGA West 1, NGA West 2, and CENA 1 GMPEs (in the PyNGA package).

```sh
gmsvtoolkit/
├── core/
├── metrics/
├── models/
│   ├── pynga/
│   ├── as16.py
│   └── rzz2015_gmpe.py
├── plots/
├── src/
├── stats/
├── tests/
└── utils/
```

### Plots

The plots package contains a number of plotting utilities that can be used to generate various plots. Several tools can be used on the results produced by the packages from the metrics and/or stats packages. These tools are described in more detail in the [Plotting page](./Plotting).

```sh
gmsvtoolkit/
├── core/
├── metrics/
├── models/
├── plots/
│   ├── data/
│   ├── plot_config.py
│   ├── plot_dist_gof.py
│   ├── plot_fas.py
│   ├── plot_fas_comparison.py
│   ├── plot_fas_eas_gof.py
│   ├── plot_fas_seas_gof.py
│   ├── plot_gmpe.py
│   ├── plot_gmpe_gof.py
│   ├── plot_map.py
│   ├── plot_map_gof.py
│   ├── plot_map_gof.py
│   ├── plot_rotdxx.py
│   ├── plot_seas.py
│   ├── plot_seismograms.py
│   └── plot_vs30_gof.py
├── src/
├── stats/
├── tests/
└── utils/
```

### Stats

The stats package includes several codes that can be used to aggregate per-station information produced by the metrics modules. The output of these tools can be used by the plotting package to generate Goodness-of-Fit (GoF) plots. These tools are described in more detail in the [Statistics Page](./Statistics-Computation).

```sh
gmsvtoolkit/
├── core/
├── metrics/
├── models/
├── plots/
├── src/
├── stats/
│   ├── anderson_gof.py
│   ├── fas_eas_gof.py
│   ├── fas_seas_gof.py
│   ├── gmpe_gof.py
│   ├── psa_gof.py
│   └── resid2uncer.py
├── tests/
└── utils/
```

### Command-line Interface

The GMSV Toolkit includes number of different tools that allow users to process timeseries and other files and generate metrics, statistics, and plots.

Several tools provide users with a number of different ways to interact with the tool. For example, the rotdxx.py metric computation code, allows users to compute RotD50 and/or RotD100 for a single acceleration timeseries, for example:

```bash
$ rotdxx.py --input-file sims/2354660.2001-SCE.acc.bbp --output-file 2354660.2001-SCE.rd50 --output-dir output_data
```

This command will read the acceleration timeseries and output the results in the specified folder and output file.

Users can also process timeseries from multiple stations at the same time. In this later case, users can provide either a station list or a batch file (described in detail in the [File Format page](./File-Format-Guide)). For example to use a station list, users can call the code as follows:

```bash
$ rotdxx.py --station-list bbp_inputs/nr_stations.stl --input-dir bbp_results --output-dir output_data
```

The command above will read the station list file provided, and will look for one input file for each of the stations. It will read the corresponding acceleration timeseries and output the RotD50 file in the specified output folder.

### Python API

The Python API provides the same functionality available from the command-line, but allows users to call these codes from within their Python scripts.

While using the Python API, users will first import the corresponding module into their code, and then (depending on the code), either call functions directly, or create the required object and run the codes.

Here's an example for creating a station map with a fault and stations:

```python
# Import required package
from plots.plot_map import plot_map

# My inputs and outputs are defined here
station_file = "nr-stations.stl"
src_file = "northridge_1994.src"
output_dir = "my_output_folder"
plot_title = "Northridge Fault Trace with all Stations"
all_stations_map = "nr_station_map.png"

# Call the plot_map function
plot_map(station_file, src_file, plot_title, output_dir, output_file=all_stations_map
```
