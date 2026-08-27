The GMSV Toolkit includes a set of Unit Tests that are designed to check the functionality of the various codes included in this package. Unit tests are designed to test each module separately, using a set of input files, and compare the results against known outputs. They verify that each module has been built and is working correctly.

### Running Unit Tests

In order to run the unit tests, users should go to the tests directory (which should be found at $GMSVTOOLKIT_DIR/tests), for example:

```bash
 $ cd /home/sarah/gmsvtoolkit/tests
```

You can run the Unit tests with the following command:

```bash
 $ ./UnitTests.py
```

The tests should begin and will take between 5-20 minutes to run, depending on your computer speed. At the end of each test, a "ok" should be printed if the test was successful. At the end, the program will print the number of tests that passed and the number of tests that failed. If a test has failed, first check that you have built the executables. You can rerun just the specific test that failed (test_<module>.py). If you can't determine the reason for the failure, contact scec-software [at] usc.edu for support.

Unit test results on a Linux system will look like this:

```
$ ./UnitTests.py 
test_pynga_ngae (test_pynga.TestPyNGA.test_pynga_ngae)
Test PyNGA NGAE ... ok
test_pynga_ngaw1 (test_pynga.TestPyNGA.test_pynga_ngaw1)
Test PyNGA NGAW1 ... ok
test_pynga_ngaw2 (test_pynga.TestPyNGA.test_pynga_ngaw2)
Test PyNGA NGAW2 ... ok
test_bbp2peer (test_peer_formatter.TestPEERFormat.test_bbp2peer)
Test for the bbp2peer converter ... ok
test_peer2bbp (test_peer_formatter.TestPEERFormat.test_peer2bbp)
Test for the peer2bbp converter ... ok
test_rotdxx (test_rotdxx.TestRotDXX.test_rotdxx)
Test the rotdxx module ... ok
test_plot_rotdxx (test_plot_rotdxx.TestPlotRotDXX.test_plot_rotdxx)
Test the plot_rotdxx module ... ok
test_psa_gof (test_psa_gof.TestPSAGoF.test_psa_gof)
Test the psa_gof module ... ok
test_plot_dist_gof (test_plot_psa_gof.TestPlotPSAGoF.test_plot_dist_gof)
Test the plot_dist_gof module ... ok
test_plot_map_gof (test_plot_psa_gof.TestPlotPSAGoF.test_plot_map_gof)
Test the plot_map_gof module ... ok
test_plot_psa_gof (test_plot_psa_gof.TestPlotPSAGoF.test_plot_psa_gof)
Test the plot_psa_gof module ... ok
test_plot_vs30_gof (test_plot_psa_gof.TestPlotPSAGoF.test_plot_vs30_gof)
Test the plot_vs30_gof module ... ok
test_plot_map (test_plot_map.TestPlotMap.test_plot_map)
Test the plot_map module ... ok
test_plot_fas (test_plot_fas.TestPlotFAS.test_plot_fas)
Test the plot_fas module with single plot ... ok
test_plot_fas_batch (test_plot_fas.TestPlotFAS.test_plot_fas_batch)
Test the plot_fas module with batch mode ... ok
test_plot_fas_station (test_plot_fas.TestPlotFAS.test_plot_fas_station)
Test the plot_fas module with station list ... ok
test_plot_fas_comparison (test_plot_fas_comparison.TestPlotFASComparison.test_plot_fas_comparison)
Test the plot_fas_comparison module with single station ... ok
test_plot_fas_comparison_batch (test_plot_fas_comparison.TestPlotFASComparison.test_plot_fas_comparison_batch)
Test the plot_fas_comparison module with batch mode ... ok
test_plot_fas_comparison_station (test_plot_fas_comparison.TestPlotFASComparison.test_plot_fas_comparison_station)
Test the plot_fas_comparison module with station list ... ok
test_fas_nga (test_fas.TestFAS.test_fas_nga)
Test the NGA scenario with the fas.py module ... ok
test_fas_scenario (test_fas.TestFAS.test_fas_scenario)
Test the scenario mode in the fas.py module ... ok
test_fas_validation (test_fas.TestFAS.test_fas_validation)
Test the validation mode in the fas.py module ... ok
test_fas_eas_gof (test_fas_gof.TestFASGoF.test_fas_eas_gof)
Test the fas_eas_gof module ... ok
test_fas_seas_gof (test_fas_gof.TestFASGoF.test_fas_seas_gof)
Test the fas_seas_gof module ... ok
test_plot_fas_eas_gof (test_plot_fas_gof.TestPlotFASGoF.test_plot_fas_eas_gof)
Test the plot_fas_eas_gof module ... ok
test_plot_fas_seas_gof (test_plot_fas_gof.TestPlotFASGoF.test_plot_fas_seas_gof)
Test the plot_fas_seas_gof module ... ok
test_calc_gmpe (test_calc_gmpe.TestCalcGMPE.test_calc_gmpe)
Test the calc_gmpe module ... ok
test_plot_gmpe_batch (test_plot_gmpe.TestPlotGMPE.test_plot_gmpe_batch)
Test the plot_gmpe module in batch mode ... ok
test_plot_gmpe_single (test_plot_gmpe.TestPlotGMPE.test_plot_gmpe_single)
Test the plot_gmpe module single station mode ... ok
test_plot_gmpe_station_list (test_plot_gmpe.TestPlotGMPE.test_plot_gmpe_station_list)
Test the plot_gmpe module with a station list ... ok
test_gmpe_gof (test_gmpe_gof.TestGMPEGoF.test_gmpe_gof)
Test the gmpe_gof module ... ok
test_plot_gmpe_gof (test_plot_gmpe_gof.TestPlotGMPEGoF.test_plot_gmpe_gof)
Test the plot_gmpe_gof module ... ok
test_anderson_gof (test_anderson_gof.TestAndersonGoF.test_anderson_gof)
Run the Anderson GOF test ... ok
test_plot_seismograms_batch (test_plot_seismograms.TestPlotSeismograms.test_plot_seismograms_batch)
Test the plot_seismograms module in batch mode ... ok
test_plot_seismograms_single (test_plot_seismograms.TestPlotSeismograms.test_plot_seismograms_single)
Test the plot_seismograms module single station mode ... ok
test_plot_seismograms_station_list (test_plot_seismograms.TestPlotSeismograms.test_plot_seismograms_station_list)
Test the plot_seismograms module with a station list ... ok
test_gmsvtools_batch (test_gmsv_tools.TestGMSVTools.test_gmsvtools_batch)
Test the gmsv_tools in batch mode ... ok
test_gmsvtools_differentiate (test_gmsv_tools.TestGMSVTools.test_gmsvtools_differentiate)
Test the gmsv_tools differentiation code ... ok
test_gmsvtools_integrate (test_gmsv_tools.TestGMSVTools.test_gmsvtools_integrate)
Test the gmsv_tools integreation code ... ok
test_gmsvtools_station (test_gmsv_tools.TestGMSVTools.test_gmsvtools_station)
Test the gmsv_tools in station mode ... ok
test_timeseries_differentiate (test_timeseries.TestTimeseries.test_timeseries_differentiate)
Test timeseries differentiation ... ok
test_timeseries_integrate (test_timeseries.TestTimeseries.test_timeseries_integrate)
Test timeseries integration ... ok
test_timeseries_interpolate (test_timeseries.TestTimeseries.test_timeseries_interpolate)
Test timeseries interpolation ... ok
test_timeseries_plot (test_timeseries.TestTimeseries.test_timeseries_plot)
Test timeseries plotting function ... ok
test_timeseries_rotate (test_timeseries.TestTimeseries.test_timeseries_rotate)
Test timeseries rotation ... ok
test_as16 (test_as16.TestAS16.test_as16)
Run the AS16 GMPE test ... ok
test_as16_testcases (test_as16.TestAS16.test_as16_testcases)
Run the AS16 test suite ... ok
test_rzz2015_gmpe (test_rzz2015gmpe.TestRZZ2015GMPE.test_rzz2015_gmpe)
Run the RZZ2015 GMPE test ... ok
test_rzz2015 (test_rzz2015.TestRZZ2015.test_rzz2015)
Run the RZZ2015 test ... ok

----------------------------------------------------------------------
Ran 49 tests in 236.275s

OK
```