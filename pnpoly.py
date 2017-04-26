# file "example.py"

from pnpoly import ffi, lib

vertx = ffi.new("float[]", 15)
verty = ffi.new("float[]", 15)

vertx[0] = 0
verty[0] = 0

vertx[1] = 1
verty[1] = 1

vertx[2] = 1
verty[2] = -1

vertx[3] = -1
verty[3] = -1

vertx[4] = -1
verty[4] = 1

vertx[5] = 1
verty[5] = 1

vertx[6] = 0
verty[6] = 0

vertx[7] = 2
verty[7] = 2

vertx[8] = 2
verty[8] = -2

vertx[9] = -2
verty[9] = -2

vertx[10] = -2
verty[10] = 2

vertx[11] = 2
verty[11] = 2

vertx[12] = 0
verty[12] = 0


result = lib.pnpoly(13, vertx,verty, 1.5,1.5)

print result

