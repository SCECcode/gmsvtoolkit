---
title: 'The SCEC Ground Motioin Simulation Validation (GMSV) Toolkit: Open-Source Tools for Ground Motion Simulation Processing and Validation'
tags:
  - Python
  - seismology
  - ground motion
  - validation
  - goodness of fit
authors:
  - name: Fabio Silva
    orcid: 0000-0000-0000-0000
    corresponding: true
    equal-contrib: true
    affiliation: 1 
  - name: Christine A. Goulet
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 2
  - name: Philip J. Maechling
    affiliation: 1
affiliations:
 - name: Statewide California Earthquake Center, University of Southern California, USA
   index: 1
 - name: United State Geological Survey
   index: 2
date: 9 September 2023
bibliography: paper.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
# aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
# aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

The Statewide California Earthquake Center (SCEC) Ground Motion Simulation Validation (GMSV) software Toolkit aims to provide standardized and verified tools to a broad seismological and engineering community of researchers interested in ground motion simulations and their validation. The GMSV Toolkit leverages over a decade of scientific, engineering, and software development work completed by dozens of contributors, with software components coming from the SCEC Broadband Platform (BBP) and from a complementary, but independent, seismogram processing software distribution (TS Process). While the GMSV Toolkit includes basic seismogram processing tools, its functionality is focused on the uniform re-processing of recorded and/or simulated seismograms to allow 1) one-to-one comparisons in time and frequency domains, and 2) statistical computations of various validation metrics.

# Statement of need

Each code included in the GMSV Toolkit was redesigned to work in a standalone package so that its full capabilities are accessible for the validation of any simulated seismograms, without the need to install other software. For each code packaged in the GMSV Toolkit, we include both a command-line interface and a Python API. Each tool can therefore be run directly from the shell, allowing codes to be scripted together in a user-specified way, or with the Python API for use with other Python programs. We preserve full compatibility with the original codes from the BBP, and reproduce metric computation, statistics, and plot results obtained in previous BBP studies.

# Time Series Comparisons

The SCEC GMSV Toolkit provides a collection of seismogram processing, comparison, and plotting tools, such as: filtering, rotation, baseline correction, resampling, two, and three component comparison plots, etc.

Figure 1: Comparing two velocity timeseries (top left); side-by-side comparison of acceleration, velocity, and displacement timeseries (top-right); side-by-side acceleration, FAS, and PSA comparison (bottom).

# Metric Computation

The SCEC GMSV Toolkit contains most validation metrics available in the Broadband Platform, including:
*Arias Intensity and Arias Intensity Duration
*RotD50 PSA
*Fourier Amplitude Spectra (FAS)
*RZZ 2015 metrics
*GMM computations for RotD50 PSA (NGA-West 1 and NGA-West 2

# PSA Validation

Figure 2: In the PSA validation workflow, acceleration timeseries go through the RotDXX module where RotD50 is computed. This results is compared station by station with the plot_rotdxx module and aggregated across all stations and compared against a second data set with the PSA GoF tool. The PSA GoF Plot module generates different PSA GoF plots so users can see how two datasets match.

Figure 3: PSA values for the two horizontal components and RotD50 (right). The green line shows calculated data and the blue line shows PSA values for the recorded seismogram. The two vertical lines (purple and red) come from the station list and indicate limits for which the recorded data is valid for this particular station (top). Calculated fourier amplitude spectra (FAS) for the two horizontal components, along with Smoothed Effective Amplitude Spectra (SEAS) (right).

# Statistical Computation and Plot Generation

Multiple tools available for combined calculated per-station metrics and generating multiple Goodness-of-Fit comparison plots:
*Pseudo-Spectral Acceleration (PSA) GoF
*Fourier Amplitude Spectra (FAS) GoF
*Anderson 2004 GoF
*GMM GoF comparisons

Figure 4: Map PSA GoF plot (top left), showing per-station comparison of simulated against recorded data, useful for checking bias related to station location and directivity effects. Vs30 PSA GoF plot (bottom left), showing the same dataset plotted against each station Vs30 value. PSA GoF plot (right) showing how simulated data compares against recorded data at different periods. The solid red line shows the mean, the narrow band is the 90% confidence interval of the mean, and the wide band shows the standard deviation centered around the mean. Note that for periods between 1s and 5s the red line is close to zero, indicating the two sets are quite close. For periods < 1.0s (higher frequencies) the red line dips below zero, signaling the simulated data is overpredicting the recorded data.

# GMSV Toolkit Summary

*Makes well-verified and useful software available to a broad seismological and engineering community, leveraging over a decade of scientific, engineering, and software development by dozens of SCEC contributors 
*Provides a standalone tool with a command-line interface and Python APIs
*Available on GitHub along with extensive documentation and examples

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

# For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

# Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

# Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

The GMSV Toolkit software development is supported by the Statewide California Earthquake Center (SCEC), which is funded by NSF Cooperative Agreement EAR-1600087 and USGS Cooperative Agreement G22AC00070. Additional support was provided by Pacific Gas and Electric.

# References 
