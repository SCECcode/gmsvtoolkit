# Frequently Asked Questions (FAQ) for the SCEC GMSV Toolkit

* What it the most recent version of the GMSV Toolkit?
  * The most recent version of the GMSV Toolkit software is posted GitHub's releases page. We expect to make new releases of the GMSV Toolkit every 6-12 months.
  
* When I try to compile the GMSV Toolkit, I get errors saying I don't have the FFTW library installed on my system, how can I fix this?
  * In order to compile the GMSV Toolkit you will need to install the FFTW library. If there's no package available for your system, you can download and compile it yourself, just make sure you have both single and double precision libraries installed on your system.

* I have compiled my FFTW libraries, but I still cannot get the GMSV Toolkit to compile on my system. What should I do?
  * It is likely the compiler is not able to find the libraries that you compiled. You can use the following commands to tell the GMSV Toolkit makefiles know where to look for them:
  
  ```bash
    export FFTW_INCDIR=/home/sarah/fftw-3.3.8/include
    export FFTW_LIBDIR=/home/sarah/fftw-3.3.8/lib
  ```