from vedo import *
meshes = load_obj('C:/Users/jhahn/.brainglobe/allen_mouse_100um_v1.2/meshes/1089.obj')
show(meshes[0].tetralize().tomesh(fill=False))