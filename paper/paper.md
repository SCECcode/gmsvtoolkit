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

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

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
