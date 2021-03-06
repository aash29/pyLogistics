
from cffi import FFI
ffibuilder = FFI()

ffibuilder.cdef("int pnpoly(int, double *, double *, double, double);")

ffibuilder.set_source("pnpoly_module",
r"""
    static int pnpoly(int nvert, double *vertx, double *verty, double testx, double testy)
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