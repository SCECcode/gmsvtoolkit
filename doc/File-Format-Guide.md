This page describes the format for the files used by the GMSV Toolkit processing tools. The simple source description (SRC) and the station list (STL) files are inputs many GMSV Toolkit codes. Time history (BBP) files include acceleration, velocity, or displacement seismograms for a particular station.

### Simple Source Description (SRC) file

Below is a sample SRC file, used to describe the 1989 Loma Prieta earthquake in Northern California:

```
#
# Loma Prieta source file
#
MAGNITUDE = 6.94
FAULT_LENGTH = 40.0
FAULT_WIDTH = 17.5
DEPTH_TO_TOP = 3.85
STRIKE = 128
RAKE = 145
DIP = 70
LAT_TOP_CENTER = 37.0789
LON_TOP_CENTER = -121.8410
HYPO_ALONG_STK = 0.0
HYPO_DOWN_DIP =  14.75
#
# Model specific parameters
#
DWID = 0.1
DLEN = 0.1
CORNER_FREQ = 0.04
CORNER_FREQ_1 = 0.04
CORNER_FREQ_2 = 1.0
#
# Alternative SEEDS create alternative .srf
#
SEED = 2379646
```

In the SRC file, lines starting with '#' are considered comments and are ignored by the GMSV Toolkit.
* The first few parameters are used to specify the event magnitude and describe the rupture.
* Magnitude (Mw) is the moment magnitude of the earthquake.
* FAULT_LENGTH (km) is used to specify the extent of the fault plane in the along strike direction.
* FAULT_WIDTH (km) specifies the dimension of the fault plane in the down dip direction.
* DEPTH_TO_TOP (km, positive) specifies how deep the fault plane is located (zero means a surface rupture).
* LAT_TOP_CENTER (decimal degrees) and LON_TOP_CENTER (decimal degrees) specify the location of the top center point of the fault plane.
* HYPO_ALONG_STK (km positive or negative) and HYPO_DOWN_DIP (km positive) specify the hypocenter location within the fault plane, with the (0, 0) coordinate being the TOP_CENTER of the fault plane. Therefore, HYPO_ALONG_STK goes from -(FAULT_LENGTH / 2) to (FAULT_LENGTH / 2), with zero being the mid-point of the fault plane. HYPO_DOWN_DIP starts at zero (top of the plane) and goes down to FAULT_WIDTH. All distances should be provided in kilometers (km).

##### Strike and Rake

STRIKE, RAKE, and DIP are used to describe the fault mechanism and should be provided in decimal degrees.

As per Rob Graves, strike and rake are defined using Aki & Richards format:

Stand over the fault, straddling it with one foot on each side of the fault, such that the hanging wall is on your right (under right foot) and the footwall is on the left (under left foot). Look towards the horizon, then

* strike direction is the angle between North and the direction you are looking
* slip direction is defined as the direction of motion of the hanging wall relative to the footwall
* rake is the angle between the strike direction and the slip direction measured in the plane of the footwall

If the fault has dip=90 (vertical), then simply choose one side to be the "hanging" wall and follow the same rules as above.

##### Miscellaneous parameters

In the second part of the file, where model-specific parameters are located, DWID and DLEN are used to provide the step interval (again, in kilometers) for the rupture creation. Smaller values will result in increased computation time. The SEED parameter enables randomization in the code (e.g. it allows different slip distributions to be generated). By using the same SEED parameter, users can generate reproducible results in the Broadband Platform.

##### UCSB parameters

Finally, the CORNER_FREQ parameters are only used by the UCSB method. In Broadband 22.4, users will need to set up both CORNER_FREQ_1 and CORNER_FREQ_2. Additionally, for BBP 22.4, users should set up CORNER_FREQ to match CORNER_FREQ_1. We expect to revise the UCSB pipeline and remove the need to duplicate the first value in our next Broadband Platform release. Please refer to the UCSB method documentation for more details on how to set up the two corner frequency values.

### Station List (STL) file

Below is a sample STL file, with the stations used in the 1989 Loma Prieta earthquake:

```
# BBP Station List for Loma Prieta
# Lon    Lat    StationId  Vs30(m/s)  LP_Freq(Hz)  HP_Freq(Hz)
-121.803 37.050  8001-CLS   462 0.1875  32.0000
-122.010 37.172  8002-LGP   515 0.1250  10.0000
-121.991 37.202  8003-LEX  1070 0.1000  23.9998
-122.031 37.255  8004-STG   387 0.1250  30.3998
-122.009 37.262  8005-WVC   387 0.1250  30.3998
-121.572 36.973  8006-G01  1428 0.0750  40.0000
-121.568 36.973  8007-GIL   730 0.1250  28.0002
-121.984 37.047  8008-BRN   353 0.1250  10.0000
-121.569 37.009  8009-GOF   387 0.2250  30.3998
-121.536 36.987  8010-G03   350 0.1250  26.3999
-121.803 37.210  8011-SJTE  672 0.0375  23.9998
-121.995 36.972  8012-WAH   390 0.1000  56.0004
-121.397 36.848  8013-HSP   306 0.0875  18.3999
-122.062 37.001  8014-UC2   714 0.1250  40.0000
-121.434 37.033  8015-GMR   334 0.1625  28.0002
-122.060 37.001  8016-LOB   714 0.1500  32.0000
-122.210 37.420  8017-SLC   425 0.1250  22.3999
-121.395 36.753  8018-SG3   609 0.0625  20.0000
-122.258 37.429  8019-WDS   454 0.1000  20.0000
-121.484 37.026  8020-G06   663 0.1625  24.7997
-121.628 37.166  8021-ADL   489 0.1750  25.6003
-121.628 37.166  8022-AND   489 0.1000  32.0000
-121.807 37.452  8023-CLR   540 0.0875  20.0000
-121.642 36.671  8024-SJW   353 0.1250  22.3999
-121.446 36.765  8025-SGI   748 0.1250  24.7997
-121.550 37.118  8026-CYC   540 0.1625  24.7997
-121.184 36.573  8027-BVF   353 0.3750  16.0000
-122.361 37.529  8028-XSP   782 0.1250  16.0000
-122.391 37.786  8029-RIN   873 0.1250  32.0000
-122.061 37.657  8030-A3E   517 0.1250  23.9998
-122.513 37.778  8031-CFH   782 0.1375  17.6001
-121.880 37.597  8032-SUF   401 0.1250  16.0000
-121.043 36.569  8033-BVU   390 0.2500  16.0000
-122.249 37.876  8034-BRK   609 0.1250  14.4001
-122.476 37.808  8035-GGB   653 0.1625  17.6001
-121.249 36.658  8036-BVW   331 0.1125  16.0000
-121.932 37.709  8037-DFS   353 0.1000  10.4000
-121.143 36.532  8038-BVR   304 0.1625  18.3999
-122.527 37.822  8039-PTB  1316 0.0750  16.0000
-122.308 37.512  8040-BES   628 0.1000  17.6001
```

Each line in the station list (STL) file contains information about one station used in the simulation. Lines starting with '#' are comments and are ignored by the GMSV Toolkit. Each line should contain at least 3 parameters, but can also optionally include a total of 4 or 6 parameters. The first 3 parameters (required) are longitude, latitude, and station name. Latitude and longitude should be provided in decimal degrees (if converting from degrees, minutes, and seconds, the latitude of 37 degrees, 30 minutes, and 0 seconds should be specified as 37.5). The station name is an identifier for the station and should contain between 3 and 10 characters. These 3 parameters form the minimum set required for each of the stations. Optionally, a station can include a 4th parameter, the Vs30 (specified in meters per second) for the particular location where the station is located. Also optionally, each station can include 2 more parameters that specify the frequency range (in Hertz) where recordings for a specific station are valid. These 2 values, used only when the platform runs in validation mode, are used to filter untrusted data out of the Goodness of Fit (GoF) plots. Please note that it is not possible to include the frequency ranges without including the Vs30 parameter. If the frequency range is not specified, the Broadband Platform will use the entire 0.1Hz to 100Hz range for the GoF plots.

### Time History (BBP) file

Below is a sample time series (BBP) file:

```
% --------------------------------------------------
% synthetic broadband seismogram (Mai&Olsen 2008)   
% N = 8 header lines
% site:  5017-A-GLP
% NPTS, DT:  10922 0.009372998029
%
% time(s)    NS (cm/s)      EW(cm/s)       UP (cm/s)
% --------------------------------------------------
  0.00000    0.00000E+00    0.00000E+00    0.00000E+00
  0.00937    0.00000E+00    0.00000E+00    0.00000E+00
  0.01875    0.00000E+00    0.00000E+00    0.00000E+00
  0.02812    0.00000E+00    0.00000E+00    0.00000E+00
  0.03749    0.00000E+00    0.00000E+00    0.00000E+00
…
  4.82709    0.13824E-01   -0.44237E-02   -0.41983E-02
  4.83647    0.64276E-01   -0.24146E-01   -0.31487E-01
  4.84584    0.10083E+00   -0.45090E-01   -0.74688E-01
  4.85521    0.93571E-01   -0.50971E-01   -0.10271E+00
  4.86459    0.74907E-01   -0.51622E-01   -0.12331E+00
  4.87396    0.55531E-01   -0.51775E-01   -0.14432E+00
…
102.32502    0.11583E+00    0.26702E-01    0.93545E-01
102.33439    0.11322E+00    0.26290E-01    0.92550E-01
102.34377    0.11017E+00    0.25777E-01    0.91201E-01
102.35314    0.10671E+00    0.25165E-01    0.89504E-01
102.36251    0.10283E+00    0.24455E-01    0.87463E-01
```

In the BBP file, lines beginning with a '%' or '#' are considered comments and should be ignored. The comment section at the top of the file contains useful information about the BBP file. For example, it includes the station name corresponding to the data, as well as the number of points in the file and the DT used in the simulation.

The rest of the file is organized in 4 columns containing the actual time series data. As indicated in the file's header, the first column corresponds to the timestamp (in seconds), and the last 3 columns correspond to the 3 components - 2 horizontals (north/south and east/west), and 1 vertical (up/down). For a velocity time history, the units indicated at the top of the file will be cm/s and for an acceleration time history, they will be cm/s/s. Each line in the file corresponds to a data point, spaced DT seconds apart from the next point.

### PSA File (RotD50)

Below is a sample PSA file (.rd50):

```
#  Psa5_N Psa5_E RotD50
#  2354660.2001-SCE.peer_e.acc
#  2354660.2001-SCE.peer_n.acc
#     63    0.0500
  0.0100 .81784E+00 .76868E+00 .80786E+00
  0.0110 .81906E+00 .76928E+00 .80872E+00
  0.0120 .82045E+00 .76994E+00 .80968E+00
  0.0130 .82201E+00 .77063E+00 .81072E+00
  0.0150 .82577E+00 .77210E+00 .81274E+00
  0.0170 .83059E+00 .77351E+00 .81633E+00
  0.0200 .84120E+00 .77198E+00 .82372E+00
  0.0220 .85182E+00 .78984E+00 .82913E+00
  0.0250 .84842E+00 .77294E+00 .83882E+00
...
```

This file is generated by the rotdxx.py module and includes 4 columns. The first column lists a period (63 periods total) and the next three columns include PSA values for the two horizontals and the RotD50.

### PSA File (.ri50)

Below is a sample PSA file (.ri50)

```
#station: 2001-SCE
#period ASK BSSA CB CY
0.0100  0.460728        0.539691        0.494158        0.540223
0.0110  0.461000        0.539239        0.496663        0.541927
0.0120  0.461249        0.538827        0.498961        0.543487
0.0130  0.461478        0.538448        0.501084        0.544925
0.0150  0.461888        0.537770        0.504902        0.547507
0.0170  0.462246        0.537179        0.508266        0.549775
0.0200  0.462712        0.536412        0.512667        0.552735
0.0220  0.459226        0.538924        0.520201        0.563119
...
```

The .ri50 file is generated by the calc_gmpe.py module in the metrics package and consists of a first column with the period (in seconds) and a number of other columns, each with a different model. The file above is for the NGA-West 2 GMMs, which includes 4 models, ASK 2014, BSSA 2014, CB 2014, and CY 2014. 

### Fourier Amplitude Spectra (FAS) file

Below is a sample FAS file:

```
# Freq(Hz)      FAS H1 (cm/s/s)      FAS H2 (cm/s/s)      EAS (cm/s/s)
0.0000000E+00   7.1547358E-02   2.5824646E-03   2.5628468E-03
3.8146973E-04   7.1543992E-02   1.3416049E-02   2.6492666E-03
7.6293945E-04   7.1647310E-02   2.6703054E-02   2.9231951E-03
1.1444092E-03   7.2187580E-02   4.0548972E-02   3.4276329E-03
1.5258789E-03   7.3671870E-02   5.5085082E-02   4.2309553E-03
1.9073486E-03   7.6693394E-02   7.0445042E-02   5.4221903E-03
2.2888184E-03   8.1790123E-02   8.6718091E-02   7.1048258E-03
2.6702881E-03   8.9303394E-02   1.0394219E-01   9.3895372E-03
3.0517578E-03   9.9311881E-02   1.2210545E-01   1.2386296E-02
3.4332275E-03   1.1166497E-01   1.4115118E-01   1.6196360E-02
3.8146973E-03   1.2606879E-01   1.6098450E-01   2.0904674E-02
...
```

The file consists of four columns. The first one contains frequencies (Hz). The next three columns contain FAS data for each of the two horizontal components and the Effective Amplitude Spectra (all in cm/s/s). This file is produced by the fas.py package and used by the plot_fas.py and fas_eas_gof.py modules.

### Smoothed Effective Amplitude Spectra (SEAS) file

Below is a sample SEAS file:

```
# Freq(Hz)      Smoothed EAS (cm/s/s) b=188.5000
1.3182570E-02   5.9983180E-01
1.3489630E-02   6.1136708E-01
1.3803850E-02   6.2708670E-01
1.4125380E-02   6.4597593E-01
1.4454400E-02   6.6619743E-01
1.4791090E-02   6.8676520E-01
1.5135620E-02   7.0760806E-01
1.5488170E-02   7.2923004E-01
1.5848932E-02   7.5204527E-01
1.6218101E-02   7.7610033E-01
1.6595870E-02   8.0118768E-01
...
```

The file consists of two columns, one containing frequencies (Hz), and a second column containing the SEAS data (cm/s/s). This file is produced by the fas.py package and used by the plot_seas.py and fas_seas_gof.py modules.