#!/usr/bin/env python2

from mapnik import *

mapfile = 'mapnik_style.xml'
map_output = 'mymap.png'

m = Map(4*1024,2*1024)
load_map(m, mapfile)


bbox=(Box2d(30.1760,59.9184,30.3082,59.9660))

m.zoom_to_box(bbox)




print "Scale = " , m.scale()
render_to_file(m, map_output)