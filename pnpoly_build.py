
from cffi import FFI
ffibuilder = FFI()

ffibuilder.cdef("int pnpoly(int, float *, float *, float, float );")

ffibuilder.set_source("pnpoly",
r"""
    static int pnpoly(int nvert, float *vertx, float *verty, float testx, float testy)
    {
        int i, j, c = 0;
        for (i = 0, j = nvert-1; i < nvert; j = i++) {
        if ( ((verty[i]>testy) != (verty[j]>testy)) && (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]) )
            c = !c;
        }
    return c;
    }
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)