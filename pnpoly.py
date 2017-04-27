# file "example.py"

from pnpoly_module import ffi, lib
import sys
import numpy
def pnpoly2(x, y, vx, vy):

    n = len(vx)


    vertx = ffi.cast("double *", ffi.from_buffer(vx))

    verty = ffi.cast("double *", ffi.from_buffer(vy))
    #verty = ffi.cast("float *", vy.ctypes.data)


    #for i in range(0,n-1):
    #    print vertx[i]
    #    print verty[i]

    #print(vertx[0])

    # vertx = ffi.new("float[]", n)
    # verty = ffi.new("float[]", n)
    # for i in range(0,n-1):
    #     vertx[i] = vx[i]
    #     verty[i] = vy[i]




    #return lib.pnpoly(n, ffi.from_buffer(vx), ffi.from_buffer(vy), x, y)
    return lib.pnpoly(n, vertx, verty, x, y)

vx = (numpy.zeros(13))
vy = (numpy.zeros(13))

vx[0] = 0
vy[0] = 0

vx[1] = 1
vy[1] = 1

vx[2] = 1
vy[2] = -1

vx[3] = -1
vy[3] = -1

vx[4] = -1
vy[4] = 1

vx[5] = 1
vy[5] = 1

vx[6] = 0
vy[6] = 0

vx[7] = 2
vy[7] = 2

vx[8] = 2
vy[8] = -2

vx[9] = -2
vy[9] = -2

vx[10] = -2
vy[10] = 2

vx[11] = 2
vy[11] = 2

vx[12] = 0
vy[12] = 0

print pnpoly2(0,0,vx,vy)
print pnpoly2(1.5,1.5,vx,vy)
print pnpoly2(2.5,2.5,vx,vy)
# vertx[0] = 0
# verty[0] = 0
#
# vertx[1] = 1
# verty[1] = 1
#
# vertx[2] = 1
# verty[2] = -1
#
# vertx[3] = -1
# verty[3] = -1
#
# vertx[4] = -1
# verty[4] = 1
#
# vertx[5] = 1
# verty[5] = 1
#
# vertx[6] = 0
# verty[6] = 0
#
# vertx[7] = 2
# verty[7] = 2
#
# vertx[8] = 2
# verty[8] = -2
#
# vertx[9] = -2
# verty[9] = -2
#
# vertx[10] = -2
# verty[10] = 2
#
# vertx[11] = 2
# verty[11] = 2
#
# vertx[12] = 0
# verty[12] = 0




#print result

