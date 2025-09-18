from vedo import *
import random
from matplotlib import colormaps
from vedo.colors import colors
from operator import itemgetter
import os
from vtk.util import numpy_support
import multiprocessing
from utils import slice_util
import trimesh
def gen_random_rotated_vol(_vol_norm, max_rotation_x_angle = 20):
    #print('gen_random_rotated_vol')
    
    _vol_norm_rotated = _vol_norm.clone() #.rotate(_angle, axis=v, point=p).color('blue5', 0.5)
    LT = LinearTransform(); LT.rotate_x(90); LT.move(_vol_norm_rotated)
    LT1 = LinearTransform();
    _rotate_x = random.randint(0, max_rotation_x_angle); 
    _rotate_y = random.randint(0, max_rotation_x_angle); 
    _rotate_z = random.randint(0, max_rotation_x_angle); 
    LT1.rotate_x(_rotate_x , rad=False ); 
    LT1.rotate_y(_rotate_y , rad=False ); 
    LT1.rotate_z(_rotate_z , rad=False ); 
    LT1.move(_vol_norm_rotated)
    print('_rotate_x',_rotate_x,_rotate_y,_rotate_z)
    _points_vol_norm_rotated = numpy_support.vtk_to_numpy(_vol_norm_rotated.dataset.GetPoints().GetData())
    _translate = np.min(-_points_vol_norm_rotated, axis=0)
    #print(_translate)
    #_translate = np.array([_translate[0]-100, _translate[1], _translate[2]-100])
    #print(_translate)
    #LT3 = LinearTransform(); LT3.translate(np.min(-_points_vol_norm_rotated, axis=0)); LT3.move(_vol_norm_rotated)
    LT3 = LinearTransform(); LT3.translate(_translate); LT3.move(_vol_norm_rotated)
    _points_vol_norm_rotated = numpy_support.vtk_to_numpy(_vol_norm_rotated.dataset.GetPoints().GetData())
    #print('gen_random_rotated_vol')
    #print(_vol_norm_rotated)
    #print(np.max(_points_vol_norm_rotated, axis=0))
    #print(np.min(_points_vol_norm_rotated, axis=0))

    [xmin,xmax, ymin,ymax, zmin,zmax] = _vol_norm_rotated.bounds()
    return _vol_norm_rotated, [xmin,xmax, ymin,ymax, zmin,zmax] 

def create_slicing_box(bounds , num_of_slices, slice_index, slice_tickness, max_slice_tickness, smallest_tickness):
    top_missing = 0
    bottom_missing = 0
    if max_slice_tickness > 0:
        top_missing = random.uniform(0, slice_tickness - max_slice_tickness)        
        bottom_missing = slice_tickness - top_missing - max_slice_tickness
    #print('top_missing',top_missing)
    #print('bottom_missing',bottom_missing)
    
    if top_missing == 0.0:
        top_missing = smallest_tickness
    if bottom_missing == 0.0:
        bottom_missing = smallest_tickness
    
    #_color = 'red5'
    [xmin,xmax, ymin,ymax, zmin,zmax] = bounds
    # slice_index == 0: # the bottom object
    top_box = Box(pos=(xmin,ymax ,zmin), size=((xmax-xmin)*2, ( (num_of_slices-slice_index-1)*slice_tickness + top_missing)*2 , (zmax-zmin)*2))
    bottom_box = Box(pos=(xmin,ymin,zmin), size=((xmax-xmin)*2, (slice_index*slice_tickness + bottom_missing)*2 , (zmax-zmin)*2))
    return top_box, bottom_box
def cal_slice_tickness(bounds, num_of_slices):
    [_,_, ymin,ymax, _,_] = bounds
    slice_tickness = (ymax-ymin)/num_of_slices
    return slice_tickness

def get_flat_pcd(_vol):
    
    _points = numpy_support.vtk_to_numpy(_vol.dataset.GetPoints().GetData())
    #print('tickness',abs(np.max(_points, axis=0)[1]-np.min(_points, axis=0)[1]))   
    _points = slice_util.make_boundary_xyz_flat(_points)
    return _points
def cut_with_bounds(_vol, top_box, bottom_box):
    _cut = _vol.clone()

    _pts = numpy_support.vtk_to_numpy(_cut.dataset.GetPoints().GetData())
    #np.save('test.npy',_vol_norm_rotated_slice_popints)

    _condition = (_pts[:, 1] >=  bottom_box.bounds()[3]) & (_pts[:, 1] <= top_box.bounds()[2])

    _cut.dataset.GetPoints().SetData(numpy_support.numpy_to_vtk(_pts[_condition]))
    return _cut

    global _vol_norm
def process_task(_dir_surfix, num_of_slices, vol_index, max_slice_tickness, smallest_tickness = 1, max_rotation_x_angle = 20, ply_gen=False):
    global DEBUG


    _dir = f'{_dir_surfix}_{vol_index}/fractured_0'    
    os.makedirs(_dir, exist_ok=True)
    print(_dir)


    
    _vol_norm_rotated, bounds = gen_random_rotated_vol(_vol_norm, max_rotation_x_angle)   
    [xmin,xmax, ymin,ymax, zmin,zmax] = bounds
    
    slice_tickness = cal_slice_tickness(bounds, num_of_slices)

    if DEBUG:
        print('slice_tickness',slice_tickness)
        print('max_slice_tickness',max_slice_tickness)

        vol_index = 0
        #print('rotated')
        #print('max', np.max(numpy_support.vtk_to_numpy(_vol_norm_rotated.dataset.GetPoints().GetData()), axis=0) )
        #print('min', np.min(numpy_support.vtk_to_numpy(_vol_norm_rotated.dataset.GetPoints().GetData()), axis=0) )

        mesh_obj_dict = {}
        mesh_obj_dict[vol_index] = {}
        mesh_obj_dict[vol_index]['original'] = _vol_norm_rotated
        #print('bounds',[xmin,xmax, ymin,ymax, zmin,zmax] )
        mesh_obj_dict[vol_index]['flat'] = []
        mesh_obj_dict[vol_index]['slice'] = []
        mesh_obj_dict[vol_index]['slice_original'] = []
        mesh_obj_dict[vol_index]['cut_plane'] = []
        mesh_obj_dict[vol_index]['box'] = []

    
    slice_color_alpha = 0.8


    for slice_index in range(num_of_slices):
        
        #slice_index = 3
        _color = _cmaps[slice_index]
        #print(f'{_dir}/piece_{slice_index}.obj')

        top_box, bottom_box = create_slicing_box(bounds, num_of_slices, slice_index, slice_tickness, max_slice_tickness, smallest_tickness)
        #_points_top_box = numpy_support.vtk_to_numpy(top_box.dataset.GetPoints().GetData())
        #_points_bottom_box = numpy_support.vtk_to_numpy(top_box.dataset.GetPoints().GetData())
        #top_box.scale(s=(1,0.8,1))
        #print('top',top_box.ybounds)
        #print('bottom',bottom_box.ybounds)
        #print('top-bottom', abs(np.max(_points_top_box, axis=0)[1]-np.min(_points_bottom_box, axis=0)[1]))   
        

        '''
        bottom_box_top_plane = Plane(pos=[(xmax - xmin)/2 + xmin, 
                                          ymin+(slice_index*slice_tickness)+ 0.001 - max_slice_tickness, 
                                          (zmax - zmin)/2 + zmin], normal=[0,1.0,0],
                                    s=[(xmax-xmin),(zmax-zmin)]).color('p')
        
        if slice_index == 0: # the bottom object
            _vol_norm_rotated_slice = _vol_norm_rotated.clone().cut_with_mesh(top_box, invert=True).color(_color, slice_color_alpha)

            if DEBUG:
                mesh_obj_dict[vol_index]['cut_plane'].append(top_box_bottom_plane.alpha(0.4))
                mesh_obj_dict[vol_index]['box'].append(top_box.color('r').alpha(0.4))
        elif  slice_index == num_of_slices - 1:  # the top object
            _vol_norm_rotated_slice = _vol_norm_rotated.clone().cut_with_mesh(bottom_box, invert=True).color(_color, slice_color_alpha)
            if DEBUG:
                mesh_obj_dict[vol_index]['cut_plane'].append(bottom_box_top_plane.alpha(0.4))
                mesh_obj_dict[vol_index]['box'].append(bottom_box.color('b').alpha(0.4))
        
        else:
        '''
        _vol_norm_rotated_slice = cut_with_bounds(_vol_norm_rotated,top_box,bottom_box)#.cut_with_box(top_box.bounds(), invert=True).cut_with_box(bottom_box.bounds(), invert=True).color('red5', 0.8)
        _vol_norm_rotated_slice_pts = numpy_support.vtk_to_numpy(_vol_norm_rotated_slice.dataset.GetPoints().GetData())
        _vol_norm_rotated_slice = Points(_vol_norm_rotated_slice_pts).color(_color, slice_color_alpha)
        #_vol_norm_rotated_slice = _vol_norm_rotated.clone().cut_with_mesh(top_box, invert=True).cut_with_mesh(bottom_box, invert=True).color(_color, slice_color_alpha)
        if DEBUG:

            top_box_original = Box(pos=(xmin,ymax ,zmin), size=((xmax-xmin)*2, ( (num_of_slices-slice_index-1)*slice_tickness )*2 , (zmax-zmin)*2))
            bottom_box_original = Box(pos=(xmin,ymin,zmin), size=((xmax-xmin)*2, (slice_index*slice_tickness)*2 + smallest_tickness , (zmax-zmin)*2))

            _vol_norm_rotated_slice_original = _vol_norm_rotated.clone().cut_with_mesh(top_box_original, invert=True).cut_with_mesh(bottom_box_original, invert=True).color(_color, 0.1)
            top_box_bottom_plane = Plane(pos=[ (xmax - xmin)/2 + xmin, 
                                    ymax-( (num_of_slices-slice_index-1)*slice_tickness) - smallest_tickness , 
                                    (zmax - zmin)/2 + zmin], normal=[0,1.0,0],
                            s=[(xmax-xmin),(zmax-zmin)]).color('y')

            mesh_obj_dict[vol_index]['cut_plane'].append(top_box_bottom_plane.alpha(0.4))
            mesh_obj_dict[vol_index]['box'].append(top_box.color('g').alpha(0.4))
            #mesh_obj_dict[vol_index]['slice'].append(_vol_norm_rotated_slice.clone())
            mesh_obj_dict[vol_index]['slice'].append(_vol_norm_rotated_slice)
            mesh_obj_dict[vol_index]['slice_original'].append(_vol_norm_rotated_slice_original.clone())
        
        #_points = get_flat_pcd(_vol_norm_rotated_slice)
        
        
        if DEBUG:
            pass
            #print('tickness',abs(np.max(_points, axis=0)[1]-np.min(_points, axis=0)[1]))   
            #mesh_obj_dict[vol_index]['flat'].append( Points(_points).color(_color, slice_color_alpha) )
        else:
            #_vol_norm_rotated_slice.write(f'{_dir}/piece_{slice_index}.obj')
            #Points(_points).write(f'{_dir}/piece_flat_pcd_{slice_index}.obj')
            
            #print(slice_index, np.max(numpy_support.vtk_to_numpy(_vol_norm_rotated_slice.dataset.GetPoints().GetData()), axis=0) )
            #print(slice_index, np.min(numpy_support.vtk_to_numpy(_vol_norm_rotated_slice.dataset.GetPoints().GetData()), axis=0) )
            #slice_list.append(_vol_norm_rotated_slice)
            xyz_list = numpy_support.vtk_to_numpy(_vol_norm_rotated_slice.dataset.GetPoints().GetData())
            point_cloud = trimesh.PointCloud(vertices=np.array(xyz_list))

            #print(f"Exporting to binary GLB format at '{glb_path}'...")
            # 'export' handles the conversion to a self-contained binary file
            point_cloud.export(file_obj=f'{_dir}/{slice_index}.glb')
            
            #if ply_gen:
            #    print(f'{_dir}/piece_{slice_index}.ply')
            #    slice_util.pcd_2_mesh(f'{_dir}/piece_{slice_index}.obj',f'{_dir}/piece_{slice_index}.ply')

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
random.seed(81)
random.shuffle(_cmaps)


if True:
    #meshes = load_obj('resources/allen_mouse_100um_v1.2.obj')[0]
    #meshes = load_obj('C:/Users/jhahn/.brainglobe/allen_mouse_100um_v1.2/meshes/1089.obj')[0]
    #meshes = load_obj('C:/Users/jhahn/.brainglobe/allen_mouse_100um_v1.2/meshes/375.obj')[0]
    meshes = load_obj('resources/root_HIP.obj')[0]
    #print(meshes)


    #meshes = meshes.tomesh()
    #print(meshes)
    save(meshes,'resources/reduced.obj',binary=False)

    '''
    bb_ids = meshes.boundaries(non_manifold_edges=True, boundary_edges=True, return_cell_ids=True)
    print(bb_ids)
    meshes = meshes.delete_cells(bb_ids).clean()
    meshes = meshes.fill_holes(size=50)
    '''

    #print('obj loaded')
    #_vol = meshes.normalize().wireframe().binarize()
    _vol = meshes.wireframe().binarize(dims=[500,500,500])
    save(_vol, 'resources/reduced_vol.vti',binary=True)
    #print('converted into voxel')



else:
    _vol = Volume('resources/reduced_vol.vti')
data_home_dir = '/data/jhahn/data/shape_dataset/data/atlas_mouse_brain_50mm'
num_of_slices = 20
max_slice_tickness = 50
max_rotation_x_angle = 20
slice_index = 0
smallest_tickness = 1
#_vol.dataset.GetPoints().SetData(_normalize(_vol.dataset.GetPoints().GetData()))

_vol_norm = _vol.clone().isosurface(4, flying_edges=False).pos(0,0,0).color('blue5', 0.5)

'''
plt = Plotter(size=(600,400), bg='GhostWhite')
plt.show(_vol_norm.color('red5', 0.8), axes=1, title="matplotlib colors", interactive=False)
plt.interactive()
plt.close()
exit()
'''
'''
_vol_norm_rotated, bounds = gen_random_rotated_vol(_vol_norm, max_rotation_x_angle)   
[xmin,xmax, ymin,ymax, zmin,zmax] = bounds
slice_tickness = cal_slice_tickness(bounds, num_of_slices)
top_box, bottom_box = create_slicing_box(bounds, num_of_slices, slice_index, slice_tickness, max_slice_tickness, smallest_tickness)
top_box = top_box.c('green5').alpha(0.2)
bottom_box = bottom_box.c('blue5').alpha(0.2)
_points_top = numpy_support.vtk_to_numpy(top_box.dataset.GetPoints().GetData())
_points_bottom = numpy_support.vtk_to_numpy(bottom_box.dataset.GetPoints().GetData())
print('gap',abs(np.min(_points_top, axis=0)[1]-np.max(_points_bottom, axis=0)[1]))   
 
print('top_box',np.min(_points_top, axis=0),np.max(_points_top, axis=0))   
print('bottom_box',np.min(_points_bottom, axis=0),np.max(_points_bottom, axis=0))   
print('top_box_bounds', top_box.bounds())   
print('bottom_box_bounds', bottom_box.bounds())   

#_vol_norm_rotated_slice = _vol_norm_rotated.clone().cut_with_mesh(top_box, invert=True).cut_with_mesh(bottom_box, invert=True).color('red5', 0.8)

_vol_norm_rotated_slice = cut_with_bounds(_vol_norm_rotated,top_box,bottom_box)#.cut_with_box(top_box.bounds(), invert=True).cut_with_box(bottom_box.bounds(), invert=True).color('red5', 0.8)
#_vol_norm_rotated_slice = _vol_norm_rotated_slice.color('red5', 0.8)

_vol_norm_rotated_slice_popints = numpy_support.vtk_to_numpy(_vol_norm_rotated_slice.dataset.GetPoints().GetData())
print('tickness',abs(np.max(_vol_norm_rotated_slice_popints, axis=0)[1]-np.min(_vol_norm_rotated_slice_popints, axis=0)[1]))  
#print('rr',np.min(_vol_norm_rotated_slice_popints, axis=0),np.max(_vol_norm_rotated_slice_popints, axis=0))   

_points = Points(get_flat_pcd(_vol_norm_rotated_slice)).color('red5', 0.8)

plt = Plotter(size=(600,400), bg='GhostWhite')
plt.show(Points(_vol_norm_rotated_slice_popints).color('red5', 0.8), top_box,bottom_box, axes=1, title="matplotlib colors", interactive=False)
#plt.show( _points, axes=1, title="matplotlib colors", interactive=False)
plt.interactive()
plt.close()
exit()
'''

'''
_data = _vol_norm.dataset.GetPoints().GetData()
_data_np = numpy_support.vtk_to_numpy(_data)
_data_np = _data_np / np.max(_data_np, axis=0)
#print(np.max(_data_np, axis=0))
_vol_norm.dataset.GetPoints().SetData(numpy_support.numpy_to_vtk(_data_np))


'''
#print('normalized')
#print('max', np.max(numpy_support.vtk_to_numpy(_vol_norm.dataset.GetPoints().GetData()), axis=0) )
#print('min', np.min(numpy_support.vtk_to_numpy(_vol_norm.dataset.GetPoints().GetData()), axis=0) )



DEBUG = False



if DEBUG:
    mesh_obj_dict = process_task("output", num_of_slices = num_of_slices, vol_index = 0, max_slice_tickness = max_slice_tickness)
else:

    num_of_slices_list = []
    vol_index_list = []
    dir_surfix_list = []
    max_tickness_list = []
    ply_gen_mode_list = []
    smallest_tickness_list = []
    max_rotation_x_angle_list = []
    #for num_of_slices in range(6,15):


    #for surfix, vol_index in [('train',1000),('val',100)]:
    #for surfix, num_of_samples, ply_gen_mod in [('train',1000, False),('val',100, False),('test',100, True)]:
    for num_of_samples in [100]:
        for max_tickness in [50]:
            for num_of_slices in [20]:
                _dir_surfix = f'{data_home_dir}/sliced_on_1_0_0_0.003_True_5_100_True_209_HIP'
                os.makedirs(_dir_surfix, exist_ok=True)
                for vol_index in range(num_of_samples):
                    dir_surfix_list.append(_dir_surfix)
                    num_of_slices_list.append(num_of_slices)
                    vol_index_list.append(vol_index)
                    max_tickness_list.append(max_tickness)
                    smallest_tickness_list.append(1)
                    max_rotation_x_angle_list.append(80)
                    ply_gen_mode_list.append(True)

                    
                #for _vol_index in range(vol_index):    
                #for vol_index in [0]:


        
    print(f'the number of jobs:{len(dir_surfix_list)}')
    with multiprocessing.Pool(processes=64) as pool: # Use a pool of 4 processes
        pool.starmap(process_task, zip(dir_surfix_list, num_of_slices_list, vol_index_list, max_tickness_list,smallest_tickness_list,max_rotation_x_angle_list,ply_gen_mode_list))


exit()

settings.immediate_rendering = False
cam = dict(
    position=(3,3,3),
    focal_point=(0.5, 0.5, 0.5),
    viewup=(0,1,0),
    distance=1.562,
    clipping_range=(2.53177, 4.93023),
)





slice_list = []

for i in range(len(mesh_obj_dict)):
    for slice_index in range(num_of_slices):  
        slice_list.append(mesh_obj_dict[i]['slice'][slice_index])
        slice_list.append(mesh_obj_dict[i]['slice_original'][slice_index])


plt = Plotter(size=(800,600), bg='GhostWhite')
plt.show(slice_list, axes=1,title="matplotlib colors")
#plt.screenshot(filename=f'output/brain{i}.png')
plt.interactive()
plt.close()



exit()

FLAT_MODE = False
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
                    #mesh_obj_dict[i]['cut_plane'][slice_index], 
                    axes=1,
                    title="matplotlib colors", interactive=False)
            else:
                
                plt.show(
                    mesh_obj_dict[i]['slice'][slice_index],
                    mesh_obj_dict[i]['slice_original'][slice_index],
                    #mesh_obj_dict[i]['cut_plane'][slice_index], 
                    #mesh_obj_dict[i]['slice'][slice_index].box().color('g').alpha(0.4),
                    axes=1,
                    title="matplotlib colors", interactive=False)
        else:
            if FLAT_MODE:
                plt.show(
                    mesh_obj_dict[i]['flat'][slice_index],
                    #mesh_obj_dict[i]['cut_plane'][slice_index], 
                    axes=1,
                    title="matplotlib colors", interactive=False)
            else:
                plt.show(
                    mesh_obj_dict[i]['slice'][slice_index],
                    mesh_obj_dict[i]['slice_original'][slice_index],
                    #mesh_obj_dict[i]['cut_plane'][slice_index], 
                    #mesh_obj_dict[i]['slice'][slice_index].box().color('g').alpha(0.4),
                    #mesh_obj_dict[i]['slice'][slice_index].intersect_with(mesh_obj_dict[i]['cut_plane'][slice_index]).color('p'), 
                    axes=1,
                    title="matplotlib colors", interactive=False)

    #plt.screenshot(filename=f'output/brain{i}.png')
    plt.interactive()
    plt.close()


