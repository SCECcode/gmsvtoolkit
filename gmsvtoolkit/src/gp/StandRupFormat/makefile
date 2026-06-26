HEADS = include.h structure.h function.h defs.h
GETPAR = ../getpar/lib
INCPAR = -I ../getpar/include
OBJS = srf_subs.o misc.o iofunc.o geoproj_subs.o

ifdef FFTW_INCDIR
FFTW_INCFLAGS = -I ${FFTW_INCDIR}
endif
ifdef FFTW_LIBDIR
FFTW_LIBFLAGS = -L ${FFTW_LIBDIR}
endif

LIBS = -lm ${GETPAR}/libget.a
LDLIBS = ${LIBS} ${FFTW_INCFLAGS} ${FFTW_LIBFLAGS} -lfftw3 -lfftw3f

# use following for large file capability
LF_FLAGS = -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64
#LF_FLAGS = 
UFLAGS = -O3

CC = gcc

CFLAGS = ${UFLAGS} ${LF_FLAGS} ${FFTW_INCFLAGS}

##### make options

all : srf_gethypo srf2moment

srf_gethypo : srf_gethypo.c ${OBJS}
	${CC} ${CFLAGS} -o srf_gethypo srf_gethypo.c ${OBJS} ${LDLIBS} ${INCPAR}
	cp srf_gethypo ../bin/.

srf2moment : srf2moment.c ${OBJS}
	${CC} ${CFLAGS} -o srf2moment srf2moment.c ${OBJS} ${LDLIBS} ${INCPAR}
	cp srf2moment ../bin/

${OBJS} : ${HEADS}

clean :
	-rm -f *.o srf_gethypo srf2moment
