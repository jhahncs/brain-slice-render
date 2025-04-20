from vedo import *
import random
from matplotlib import colormaps
from vedo.colors import colors
from operator import itemgetter
import os
from vtk.util import numpy_support
import multiprocessing
from utils import slice_util



def process_task(_dir_surfix, num_of_slices, vol_index):
    global _vol_norm
    global DEBUG


    _dir = f'{_dir_surfix}/fractured_{vol_index}'    
    os.makedirs(_dir, exist_ok=True)
    print(_dir)
    v = vector(random.random(),random.random(), random.random())
    p = vector(0, 0, 0)  # axis passes through this point


    _vol_norm_rotated = _vol_norm.clone().rotate(random.randint(1,90), axis=v, point=p).color('blue5', 0.5)
    slice_util._normalize(_vol_norm_rotated)


    [xmin,xmax, ymin,ymax, zmin,zmax] = _vol_norm_rotated.bounds()
    slice_tickness = (ymax-ymin)/num_of_slices


    if DEBUG:


        print('rotated')
        print('max', np.max(numpy_support.vtk_to_numpy(_vol_norm_rotated.dataset.GetPoints().GetData()), axis=0) )
        print('min', np.min(numpy_support.vtk_to_numpy(_vol_norm_rotated.dataset.GetPoints().GetData()), axis=0) )

        mesh_obj_dict = {}
        mesh_obj_dict[vol_index] = {}
        mesh_obj_dict[vol_index]['original'] = _vol_norm_rotated
        print('bounds',[xmin,xmax, ymin,ymax, zmin,zmax] )
        mesh_obj_dict[vol_index]['flat'] = []
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


            if DEBUG:
                mesh_obj_dict[vol_index]['cut_plane'].append(top_box_bottom_plane.alpha(0.4))
                mesh_obj_dict[vol_index]['box'].append(top_box.color('r').alpha(0.4))
        elif  slice_index == num_of_slices - 1:
            _vol_norm_rotated_slice = _vol_norm_rotated.clone().cut_with_mesh(bottom_box, invert=True).color(_color, slice_color_alpha)
            if DEBUG:
                mesh_obj_dict[vol_index]['cut_plane'].append(bottom_box_top_plane.alpha(0.4))
                mesh_obj_dict[vol_index]['box'].append(bottom_box.color('b').alpha(0.4))

        else:
            _vol_norm_rotated_slice = _vol_norm_rotated.clone().cut_with_mesh(top_box, invert=True).cut_with_mesh(bottom_box, invert=True).color(_color, slice_color_alpha)
            if DEBUG:
                mesh_obj_dict[vol_index]['cut_plane'].append(top_box_bottom_plane.alpha(0.4))
                mesh_obj_dict[vol_index]['box'].append(top_box.color('g').alpha(0.4))

        if DEBUG:
            mesh_obj_dict[vol_index]['slice'].append(_vol_norm_rotated_slice.clone())
        
        _points = numpy_support.vtk_to_numpy(_vol_norm_rotated_slice.dataset.GetPoints().GetData())

        _points = slice_util.make_boundary_xyz_flat(_points)
        #Points(_points).write(f'{_dir}/piece_flat_pcd_{slice_index}.obj')
        if DEBUG:
            mesh_obj_dict[vol_index]['flat'].append( Points(_points) )
        #_vol_norm_rotated_slice.write(f'{_dir}/piece_{slice_index}.obj')

        print(f'{_dir}/piece_{slice_index}.obj')
        #print(slice_index, np.max(numpy_support.vtk_to_numpy(_vol_norm_rotated_slice.dataset.GetPoints().GetData()), axis=0) )
        #print(slice_index, np.min(numpy_support.vtk_to_numpy(_vol_norm_rotated_slice.dataset.GetPoints().GetData()), axis=0) )
        #slice_list.append(_vol_norm_rotated_slice)
        slice_util.pcd_2_mesh(f'{_dir}/piece_flat_pcd_{slice_index}.obj',f'{_dir}/piece_flat_pcd_{slice_index}.ply')

    if DEBUG:
        return mesh_obj_dict
    
sorted_colors1 = sorted(colors.items(), key=itemgetter(1))
_cmaps = []
for sc in sorted_colors1:
    cname = sc[0]
    # Skip the color if it doesn't end in a number
    if cname[-1] not in "123456789":
        continue
    _cmaps.append(cname)

settings.tiff_orientation_type = 4 
random.seed(42)
random.shuffle(_cmaps)


if True:
    #meshes = load_obj('resources/allen_mouse_100um_v1.2.obj')[0]
    #meshes = load_obj('C:/Users/jhahn/.brainglobe/allen_mouse_100um_v1.2/meshes/1089.obj')[0]
    #meshes = load_obj('C:/Users/jhahn/.brainglobe/allen_mouse_100um_v1.2/meshes/375.obj')[0]
    meshes = load_obj('resources/1089_8.obj')[0]
    print(meshes)


    #meshes = meshes.tomesh()
    print(meshes)
    save(meshes,'resources/reduced.obj',binary=False)

    '''
    bb_ids = meshes.boundaries(non_manifold_edges=True, boundary_edges=True, return_cell_ids=True)
    print(bb_ids)
    meshes = meshes.delete_cells(bb_ids).clean()
    meshes = meshes.fill_holes(size=50)
    '''

    print('obj loaded')
    _vol = meshes.normalize().wireframe().binarize()
    save(_vol, 'resources/reduced_vol.vti',binary=True)
    print('converted into voxel')

else:
    _vol = Volume('resources/reduced_vol.vti')
data_home_dir = '/data/jhahn/data/shape_dataset/data/brain_block'

#_vol.dataset.GetPoints().SetData(_normalize(_vol.dataset.GetPoints().GetData()))

_vol_norm = _vol.clone().isosurface(4, flying_edges=False).pos(0,0,0).color('yellow5', 0.5)
slice_util._normalize(_vol_norm)
#plt = Plotter(size=(600,400), bg='GhostWhite')
#plt.show(_vol_norm, axes=1, title="matplotlib colors", interactive=False)
#plt.interactive()
#plt.close()
#exit()
'''
_data = _vol_norm.dataset.GetPoints().GetData()
_data_np = numpy_support.vtk_to_numpy(_data)
_data_np = _data_np / np.max(_data_np, axis=0)
#print(np.max(_data_np, axis=0))
_vol_norm.dataset.GetPoints().SetData(numpy_support.numpy_to_vtk(_data_np))
'''
print('normalized')
print('max', np.max(numpy_support.vtk_to_numpy(_vol_norm.dataset.GetPoints().GetData()), axis=0) )
print('min', np.min(numpy_support.vtk_to_numpy(_vol_norm.dataset.GetPoints().GetData()), axis=0) )



DEBUG = False
num_of_slices = 20
if DEBUG:
    mesh_obj_dict = process_task("output",num_of_slices,0)
else:
    
    num_of_slices_list = []
    vol_index_list = []
    dir_surfix_list = []
    #for num_of_slices in range(6,15):


    #for surfix, vol_index in [('train',1000),('val',100)]:
    for surfix, vol_index in [('val',10)]:
        for num_of_slices in [20]:
            _dir_surfix = f'{data_home_dir}/{num_of_slices}_parts_{surfix}'
            os.makedirs(_dir_surfix, exist_ok=True)
            
            for _vol_index in range(vol_index):    
            #for vol_index in [0]:
                dir_surfix_list.append(_dir_surfix)
                num_of_slices_list.append(num_of_slices)
                vol_index_list.append(_vol_index)

        
        
    print(f'the number of jobs:{len(dir_surfix_list)}')
    with multiprocessing.Pool(processes=64) as pool: # Use a pool of 4 processes
        pool.starmap(process_task, zip(dir_surfix_list, num_of_slices_list, vol_index_list))


exit()

settings.immediate_rendering = False
cam = dict(
    position=(3,3,3),
    focal_point=(0.5, 0.5, 0.5),
    viewup=(0,1,0),
    distance=1.562,
    clipping_range=(2.53177, 4.93023),
)
FLAT_MODE = True
slice_list = []
for i in range(len(mesh_obj_dict)):
    slice_list.append(mesh_obj_dict[i]['original'])

    plt = Plotter(size=(600,400), bg='GhostWhite')

    #plt.show(mesh_obj_dict[i]['original'], axes=1, interactive=False)

    for slice_index in range(num_of_slices):  
        #print(mesh_obj_dict[i]['flat'][slice_index])  
        if slice_index == num_of_slices-1:
            if FLAT_MODE:
                plt.show(
                    mesh_obj_dict[i]['flat'][slice_index],
                    mesh_obj_dict[i]['cut_plane'][slice_index], 
                    axes=1,
                    title="matplotlib colors", interactive=False)
            else:
                plt.show(
                    mesh_obj_dict[i]['slice'][slice_index],
                    mesh_obj_dict[i]['cut_plane'][slice_index], 
                    mesh_obj_dict[i]['slice'][slice_index].box().color('g').alpha(0.4),
                    axes=1,
                    title="matplotlib colors", interactive=False)
        else:
            if FLAT_MODE:
                plt.show(
                    mesh_obj_dict[i]['flat'][slice_index],
                    mesh_obj_dict[i]['cut_plane'][slice_index], 
                    axes=1,
                    title="matplotlib colors", interactive=False)
            else:
                plt.show(
                    mesh_obj_dict[i]['slice'][slice_index],
                    mesh_obj_dict[i]['cut_plane'][slice_index], 
                    mesh_obj_dict[i]['slice'][slice_index].box().color('g').alpha(0.4),
                    mesh_obj_dict[i]['slice'][slice_index+1].intersect_with(mesh_obj_dict[i]['cut_plane'][slice_index]).color('p'), 
                    axes=1,
                    title="matplotlib colors", interactive=False)


    #plt.screenshot(filename=f'output/brain{i}.png')
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
