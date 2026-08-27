The Statewide California Earthquake Center (SCEC) Ground Motion Simulation Validation (GMSV) Toolkit is an open-source, Python-based software package designed to evaluate and validate earthquake ground motion models. Its primary purpose is to provide seismologists and structural engineers with a standardized framework to process simulated earthquake data and perform direct, "one-to-one" comparisons against real-world, historically recorded seismograms.

The toolkit consolidates over a decade of collaborative research and software development within the seismological community. Tthe GMSV Toolkit extracts and updates core validation modules from two primary SCEC ecosystems:

* [Broadband Platform](https://github.com/SCECcode/bbp): A framework used to simulate broadband earthquake ground motions.

* [TS-Process Package](https://github.com/SCECcode/ts-process): A standalone, independent seismogram data-processing library.

By decoupling separate codes into standalone Python scripts, developers can run individual validation routines directly via a Command-Line Interface (CLI) or integrate them into custom workflows using the modular Python API.

