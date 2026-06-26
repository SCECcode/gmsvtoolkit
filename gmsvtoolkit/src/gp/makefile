all:
	mkdir -p bin;
	cd getpar/src; make -f Makefile;
	cd StandRupFormat; make -f makefile;
	cd WccFormat; make -f makefile;
	cd ModelCords; make -f makefile;
	cd GoodFit; make -f makefile;

clean:
	rm -rf bin;
	cd getpar/src; make -f Makefile clean;
	cd StandRupFormat; make -f makefile clean;
	cd WccFormat; make -f makefile clean;
	cd ModelCords; make -f makefile clean;
	cd GoodFit; make -f makefile clean;
