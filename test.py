"""Create the Convex Hull of a Mesh or a set of input points"""
from vedo import *
from vtk.util import numpy_support

settings.default_font = 'Bongas'
settings.use_depth_peeling = True
vol_index = 29
slice_index = 0

_vtk_obj = Mesh(f'temp/vase/1/fractured_{3}/piece.obj')
_vtk_obj_29_0 = Mesh(f'temp/vase/1/fractured_{3}/piece_{3}.obj')
_vtk_obj_12 = Mesh(f'temp/vase/1/fractured_{1}/piece_{3}.obj')
_vtk_obj_13 = Mesh(f'temp/vase/1/fractured_{1}/piece_{1}.obj')


def top_bottom(_mesh):        
    _planes_in_bounding_box = _mesh.box().triangulate().split()
    _planes_in_bounding_box.sort(key=lambda x: (x.area()), reverse=True)
    y_of_first_plane = numpy_support.vtk_to_numpy(_planes_in_bounding_box[0].dataset.GetPoints().GetData())[0][1]
    y_of_second_plane = numpy_support.vtk_to_numpy(_planes_in_bounding_box[1].dataset.GetPoints().GetData())[0][1]

    if y_of_first_plane < y_of_second_plane:
        _planes_in_bounding_box[0], _planes_in_bounding_box[1] = _planes_in_bounding_box[1], _planes_in_bounding_box[0]
    
    return _planes_in_bounding_box[0], _planes_in_bounding_box[1]

top_1, bottom_1  = top_bottom(_vtk_obj_29_0)
top_2, bottom_2  = top_bottom(_vtk_obj_12)
#print(_vtk_obj_29_0.box().center_of_mass())
#print(top.vertex_normals[0])

#print(top_pcs.vertices)
# Get the point IDs on the boundary of the mesh
pids_1_top = _vtk_obj_29_0.boundaries().cut_with_plane(_vtk_obj_29_0.center_of_mass(),top_1.vertex_normals[0])
pids_1_btm = _vtk_obj_29_0.boundaries().cut_with_plane(_vtk_obj_29_0.center_of_mass(),-top_1.vertex_normals[0])
#pids_2_top = _vtk_obj_12.boundaries().cut_with_plane(_vtk_obj_12.center_of_mass(),top_2.vertex_normals[0])
#pids_2_btm = _vtk_obj_12.boundaries().cut_with_plane(_vtk_obj_12.center_of_mass(),-top_2.vertex_normals[0])
#print(pids_top)
print(len(pids_1_top.vertices))
#print(pids_1_top.dataset.densify(0.1, nclosest=10, niter=1))
#pids_1_top_100 = Mesh([pids_1_top.vertices[np.random.choice(pids_1_top.vertices.shape[0], 100, replace=False) ]]).c("r").ps(10)
#pids_2_btm_100 = Mesh([pids_2_btm.vertices[np.random.choice(pids_2_btm.vertices.shape[0], 100, replace=False) ]]).c("r").ps(10)
#row_indices = np.random.choice(pids_top.shape[0], 100, replace=False) 
#selected_rows = pids_top[row_indices]
#print(np.random.choice(pids_1_top.vertices.shape[0], 100, replace=False))
#print(pids_1_top.vertices[np.random.choice(pids_1_top.vertices.shape[0], 100, replace=False) ])
#print(selected_rows)
# Create a Points object to represent the boundary points
#pts = Points(_vtk_obj_29_0.vertices[pids]).c('red5').cut_with_scalar
#pts_top = [a  for a in pts.vertices if a[1] > np.mean(pts.vertices[:,1])]
#print(np.min(pts.vertices[:,1]), np.mean(pts.vertices[:,1]), np.max(pts.vertices[:,1]))
#print(np.min(pids_1_top_100.vertices,axis=0),np.mean(pids_1_top_100.vertices,axis=0),np.max(pids_1_top_100.vertices,axis=0))

#print(np.mean(pids_1_top_100.distance_to(pids_2_btm_100,signed=False),axis=0))
show( _vtk_obj, _vtk_obj.box(), pids_1_top, pids_1_btm, axes=1).close()