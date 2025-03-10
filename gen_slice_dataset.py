from vedo import *
import random
from matplotlib import colormaps
from vedo.colors import colors
from operator import itemgetter
import os
from vtk.util import numpy_support


def _normalize(_vol):
    _data = _vol.dataset.GetPoints().GetData()
    _data_np = numpy_support.vtk_to_numpy(_data)
    _data_np = _data_np / np.max(_data_np, axis=0)
    #return numpy_support.numpy_to_vtk(_data_np)
    _vol.dataset.GetPoints().SetData(numpy_support.numpy_to_vtk(_data_np))
    #return _vol


    
sorted_colors1 = sorted(colors.items(), key=itemgetter(1))
_cmaps = []
for sc in sorted_colors1:
    # Get the color name
    cname = sc[0]
    # Skip the color if it doesn't end in a number
    if cname[-1] not in "123456789":
        continue
    _cmaps.append(cname)
#_cmaps = list(colors.keys())
#_cmaps = ['blue5']
settings.tiff_orientation_type = 4 
random.seed(42)
random.shuffle(_cmaps)


_vol = Volume(dataurl + 'vase.vti')
#_vol.dataset.GetPoints().SetData(_normalize(_vol.dataset.GetPoints().GetData()))



_vol_norm = _vol.clone().isosurface(4, flying_edges=False).pos(0,0,0).color('yellow5', 0.5)

_normalize(_vol_norm)
'''
_data = _vol_norm.dataset.GetPoints().GetData()
_data_np = numpy_support.vtk_to_numpy(_data)
_data_np = _data_np / np.max(_data_np, axis=0)
#print(np.max(_data_np, axis=0))
_vol_norm.dataset.GetPoints().SetData(numpy_support.numpy_to_vtk(_data_np))
'''
print( np.max(numpy_support.vtk_to_numpy(_vol_norm.dataset.GetPoints().GetData()), axis=0) )


num_of_slices = 5

mesh_obj_dict = {}

#for vol_index in range(100):
for vol_index in range(3):
    _dir = f'temp/vase/1/fractured_{vol_index}'
    #_dir = f'/home/greenbaum-gpu/jhahn/data/shape_dataset/data/shape/vase/1/fractured_{vol_index}'
    print(_dir)
    #_dir = f'temp'
    os.makedirs(_dir, exist_ok=True)

    v = vector(random.random(),random.random(), random.random())
    p = vector(0, 0, 0)  # axis passes through this point


    _vol_norm_rotated = _vol_norm.clone().rotate(random.randint(1,90), axis=v, point=p).color('blue5', 0.5)



    mesh_obj_dict[vol_index] = {}
    mesh_obj_dict[vol_index]['original'] = _vol_norm_rotated
    #l = Line(-v+p, v+p).lw(3).c('red')

    _vol_norm_rotated.write(f'{_dir}/piece.obj')
    #num_of_slices = random.randint(10,20)
    num_of_slices = 5
    
    [xmin,xmax, ymin,ymax, zmin,zmax] = _vol_norm_rotated.bounds()
    slice_tickness = (ymax-ymin)/num_of_slices
    slice_size = (xmax-xmin, slice_tickness, zmax-zmin)
    print(xmin,xmax, ymin,ymax, zmin,zmax)

    #_cmaps = ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds','YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu','GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
    slice_list = []
    mesh_obj_dict[vol_index]['slice'] = []
    mesh_obj_dict[vol_index]['cut_plane'] = []
    mesh_obj_dict[vol_index]['box'] = []
    slice_color_alpha = 0.8
    for slice_index in range(num_of_slices):
        
        #slice_index = 3
        _color = _cmaps[slice_index]
        #_color = 'red5'
        bottom_box = Box(pos=(xmin,ymin,zmin), size=((xmax-xmin)*2, (slice_index*slice_tickness)*2, (zmax-zmin)*2))
        #bottom_box.color('green5', 0.5)
        top_box = Box(pos=(xmin,ymax ,zmin), size=((xmax-xmin)*2, ( (num_of_slices-slice_index-1)*slice_tickness)*2, (zmax-zmin)*2))

        top_box_bottom_plane = Plane(pos=[ (xmax - xmin)/2 + xmin, ymax-( (num_of_slices-slice_index-1)*slice_tickness)+0.001, (zmax - zmin)/2 + zmin], normal=[0,1.0,0],
                                     s=[(xmax-xmin),(zmax-zmin)])
        bottom_box_top_plane = Plane(pos=[(xmax - xmin)/2 + xmin, ymin+(slice_index*slice_tickness), (zmax - zmin)/2 + zmin], normal=[0,1.0,0],
                                     s=[(xmax-xmin),(zmax-zmin)])
        #top_box.color('red5', 0.5).

        #top_box.project_on_plane('y')
        if slice_index == 0:
            _vol_norm_rotated_slice = _vol_norm_rotated.clone().cut_with_mesh(top_box, invert=True).color(_color, slice_color_alpha)
            mesh_obj_dict[vol_index]['cut_plane'].append(top_box_bottom_plane.alpha(0.4))
            mesh_obj_dict[vol_index]['box'].append(top_box.color('g').alpha(0.4))
        elif  slice_index == num_of_slices - 1:
            _vol_norm_rotated_slice = _vol_norm_rotated.clone().cut_with_mesh(bottom_box, invert=True).color(_color, slice_color_alpha)
            mesh_obj_dict[vol_index]['cut_plane'].append(bottom_box_top_plane.alpha(0.4))
            mesh_obj_dict[vol_index]['box'].append(bottom_box.color('g').alpha(0.4))

        else:
            _vol_norm_rotated_slice = _vol_norm_rotated.clone().cut_with_mesh(top_box, invert=True).cut_with_mesh(bottom_box, invert=True).color(_color, slice_color_alpha)
            mesh_obj_dict[vol_index]['cut_plane'].append(top_box_bottom_plane.alpha(0.4))
            mesh_obj_dict[vol_index]['box'].append(top_box.color('g').alpha(0.4))

        mesh_obj_dict[vol_index]['slice'].append(_vol_norm_rotated_slice.clone())

        _vol_norm_rotated_slice.write(f'{_dir}/piece_{slice_index}.obj')
        #print( np.max(numpy_support.vtk_to_numpy(_vol_norm_rotated_slice.dataset.GetPoints().GetData()), axis=0) )
        slice_list.append(_vol_norm_rotated_slice)



        #if True:
        #    break
        
#show( mesh_obj_dict[0]['slice'], mesh_obj_dict[0]['cut_plane'], axes=1).close()
#show( mesh_obj_dict[1]['slice'], mesh_obj_dict[1]['cut_plane'], axes=1).close()
#show(slice_list, __doc__, axes=1)
settings.immediate_rendering = False
#_camera={'pos':(0.116346, 0.608809, 0.05899), 'viewup':(0,1,0),'distance ':3.26406 ,'focal_point ':(0.116346, 0.608809, 0.694924), 'thickness':2.33231, 'view_angle':30}
cam = dict(
    position=(3,3,3),
    focal_point=(0.5, 0.5, 0.5),
    viewup=(0,1,0),
    distance=1.562,
    clipping_range=(2.53177, 4.93023),
)


slice_list = []
for i in range(len(mesh_obj_dict)):
    slice_list.append(mesh_obj_dict[i]['original'])

    plt = Plotter(size=(600,400), bg='GhostWhite')
    plt.show(mesh_obj_dict[i]['slice'][3], mesh_obj_dict[i]['cut_plane'][3], mesh_obj_dict[i]['slice'][3].box().color('g').alpha(0.4),
             mesh_obj_dict[i]['slice'][3].intersect_with(mesh_obj_dict[i]['cut_plane'][2]).color('p'), axes=1,
            title="matplotlib colors", interactive=False)
    #plt.show(mesh_obj_dict[i]['slice'], axes=0,
    #        title="matplotlib colors", interactive=False, camera=cam)
    plt.screenshot(filename=f'vase{i}.png')
    #print(plt.camera)
    plt.interactive()
    plt.close()



exit()
v = vector(0,1,0)
p = vector(0, 0, 0)  # axis passes through this point
for i in range(len(mesh_obj_dict[0]['slice'])):
    plt = Plotter(size=(600,400), bg='GhostWhite')

    _slice = mesh_obj_dict[0]['slice'][i].clone()
    [xmin,xmax, ymin,ymax, zmin,zmax] = _slice.bounds()
    #_slice = _slice.rotate(random.randint(40,160), axis=(xmax-xmin,ymax-ymin+1.0,zmax-zmin), point=(xmax-xmin,ymax-ymin,zmax-zmin))
    #_slice = _slice.rotate_y(random.randint(40,160))
    plt.show( _slice, _slice.box().color('g').alpha(0.4), axes=0,
            title="matplotlib colors", interactive=False, camera=cam)
    plt.screenshot(filename=f'vase{i}.png')
    #print(plt.camera)
    plt.interactive()
    plt.close()

exit()
