Users have the option to install the GMSV Toolkit on their Linux systems, or use the GMSV Toolkit inside a Docker container.

## Setting up GMSV Toolkit on a Linux computer

Installing the GMSV Toolkit involves obtaining a copy of the code and building the required executables. You can either download the tar.gz platform from the GMSV Toolkit's GitHub releases page or check the code out of GitHub directly.

### Software Dependencies

The GMSV Tolkit has the following software dependencies in order to compile and run:

* Python v3.8.18+ with
  * Matplotlib 3.7.5+
  * NumPy 1.24.4+
  * SciPy 1.10.1+
 * GNU compilers (gcc, gfortran) 13.3+
  * FFTW library 3.3.8

Please make sure they are installed in your computer before you continue with the GMSV Toolkit installation process. Depending on the specific NumPy, SciPy, and Matplotlib versions users installed in their systems, they may experience certain "Future Warning" messages while running the GMSV Toolkit. In this case, upgrading NumPy, SciPy, and/or Matplotlib will usually make the warning messages disappear. We used the package versions listed above to run the Unit tests.

### Installation

 We recommend that users that want to use the GMSV Toolkit download the tar.gz file available on GitHub's release page. For advanced users, who would like to make modifications to the GMSV Toolkit and contribute these modifications back to us, we recommend they clone our repository so that it is easier to track their changes to the software.

To install the GMSV Toolkit on your computer, please follow these steps:

* Create a directory on your computer where you want all GMSV Toolkit packages to be installed:

```bash
  $ cd /home/sarah
  $ mkdir gmsvtoolkit
  $ cd /home/sarah/gmsvtoolkit
```

Then, users can use one of the two method below to obtain a copy of the GMSV Toolkit software distribution:

#### Downloading the tar file from GitHub

As mentioned above, one option to obtain the GMSV Toolkit source distribution is to download a release 'tar.gz' or 'zip' file directly from GitHub's releases page.

* Download the .tar.gz file from GitHub's releases page into the recently-created directory
* Uncompress the downloaded file

```bash
  $ tar -xzf gmsvtoolkit-26.8.0.tar.gz
```

* Delete the tar.gz file as it will not be needed anymore (optional)

#### Cloning the GMSV Toolkit repository from GitHub

Another option is for users to clone the GMSV Toolkit repository from GitHub using the following command:

```bash
 $ git clone https://github.com/SCECcode/gmsvtoolkit.git gmsvtoolkit-26.8.0
```

Either way, after one of the steps above users should have the GMSV Toolkit source distribution downloaded into their computers. Then, the next steps are:

```bash
  $ cd gmsvtoolkit-26.8.0/gmsvtoolkit/src
  $ make
```

The commands above will compile the codes in the GMSV Toolkit source distribution. Please refer to the [FAQ page](./FAQ.md) if you have issues compiling the GMSV Toolkit software on your system. You will also need to set up the GMSVTOOLKIT_DIR environment variable so that it points to the root folder in the gmsvtoolkit package. This is the folder that has all the other software modules, like metrics, stats, plots, etc. You can set it up by using a command like:

```bash
 $ export GMSVTOOLKIT_DIR=/home/sarah/gmsvtoolkit-26.8.0/gmsvtoolkit
 $ export PYTHONPATH=$GMSVTOOLKIT_DIR:$PYTHONPATH
```
You should consider adding this to your bash_profile so that you don't have to retype them every time you want to use the GMSV Toolkit.

After installing the GMSV Toolkit on their systems, users should confirm the code is built correctly by [running Unit Tests](./Running-Tests.md) before starting to use the code for research purposes.

## Using the GMSV Toolkit inside a Docker Container

The latest release of the GMSV Toolkit is also available as a Docker image. The dockerized version of this software can be retrieved from SCEC's Dockerhub this way:

```bash
$ docker run -p 8888:8888 sceccode/gmsvtoolkit_jupyter:latest
```

Once you start the container, point your web browser to the URL provided by the 'docker run' command above. You should see two Jupyter notebooks, one containing the workflow for PSA metric calculations and comparisons and one for FAS. Please select one of the notebooks and start interacting with the GMSV Toolkit codes.