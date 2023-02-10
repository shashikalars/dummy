all: dras
CFLAGS= -O2 -Wall -W -Wmissing-prototypes -Wno-main -Wno-unused-parameter -Wno-unused-value -Wno-sign-compare
dras: dras.o
dras.o: dhcp.h dras.h dras.c
dras: 
	gcc ${CFLAGS}  -o dras  dras.o
.c.o:
	${CC} ${CFLAGS} -c $<
clean:
	rm -f dras *.o
