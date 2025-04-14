from vedo import *
from vtk.util import numpy_support
import random
from utils import slice_util
cam = dict(
    position=(3,3,3),
    focal_point=(0.5, 0.5, 0.5),
    viewup=(0,1,0),
    distance=10.562,
    clipping_range=(2.53177, 4.93023),
)

mesh = load_obj('output/fractured_0/piece_9.obj')[0].color('b')


_data = mesh.dataset.GetPoints().GetData()
_data_np = numpy_support.vtk_to_numpy(_data)
print(_data_np.shape)
print(np.max(_data_np, axis=0))
print(np.min(_data_np, axis=0))
xyz_list = slice_util.make_boundary_xyz_flat(_data_np)
print(xyz_list.shape)
print(np.max(xyz_list, axis=0))
print(np.min(xyz_list, axis=0))
#Points(xyz_list).show(axes=1).close()

plt = Plotter(size=(600,400))
plt.show(mesh.alpha(0.1), Points(xyz_list).c('r'), axes=1, title="matplotlib colors", interactive=True).close()