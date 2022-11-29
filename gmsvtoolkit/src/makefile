all: version
	cd gp; make -f makefile;
	cd ucb; make -f makefile;
	cd usgs; make -f makefile;

version:
	gcc --version > gcc.version
	gfortran --version > gfortran.version

clean:
	rm -f gcc.version gfortran.version
	cd gp; make -f makefile clean;
	cd ucb; make -f makefile clean;
	cd usgs; make -f makefile clean;
