from pathlib import Path
from brainrender._io import load_mesh_from_file
from myterial import orange
from rich import print
from brainglobe_atlasapi import BrainGlobeAtlas
from brainrender import Scene
import brainrender
from brainrender.actors import Points, Line
import numpy as np


# Importing Image class from PIL module
from PIL import Image
 
def crop(filename, size):
        
    # Opens a image in RGB mode
    im = Image.open(filename)
    
    # Size of the image in pixels (size of original image)
    # (This is not mandatory)
    width, height = im.size
    
    # Setting the points for cropped image
    left = size
    top = 0
    right = width - size
    bottom = height
    
    # Cropped image of above dimension
    # (It will not change original image)
    im1 = im.crop((left, top, right, bottom))
    im1.save(filename)



print(f"[{orange}]Running example: {Path(__file__).name}")

bg_atlas = BrainGlobeAtlas("allen_mouse_100um", check_latest=False)
bg_atlas.lookup_df.acronym.values
region = 'TH'
obj_file = str(bg_atlas.meshfile_from_structure(region))


mesh = load_mesh_from_file(obj_file, alpha=0.2, color="green")


brainrender.settings.SHOW_AXES = True  # reset axes display
brainrender.settings.WHOLE_SCREEN = (
    False  # make the rendering window be smaller
)
output_dir = 'output'

#for cut_x in range(2000,11001,1000):
for cut_x in [0]:
        
    # Create a brainrender scene
    #scene = Scene(title="slice")
    scene = Scene(title="", atlas_name="allen_mouse_25um")
    # Add brain regions
    th = scene.add_brain_region("TH")
    #scene.add_label(th, "TH")
    # You can specify color, transparency...
    #mos, ca1 = scene.add_brain_region("MOs", "CA1", alpha=0.2, color="green")

    # Slice actors with frontal plane
    #scene.slice("frontal", actors=[th])

    # Slice with a custom plane
    center_of_cut_plane = [cut_x,0,0]
    #center_of_cut_plane = mesh.center_of_mass()
    plane = scene.atlas.get_plane(pos=center_of_cut_plane, norm=(1, 0, 0))
    scene.slice(plane)

    #print(mesh.center_of_mass())

    focal_point = (-1000, mesh.center_of_mass()[1],  -mesh.center_of_mass()[2])

    #points = Points(np.array([focal_point]), radius=100, colors="blue")
    #scene.add(points)

    # Set up a camera. Can use string, such as "sagittal".
    # During render runtime, press "c" to print the current camera parameters.
    camera = {
        "pos": (-20000, mesh.center_of_mass()[1],  -mesh.center_of_mass()[2]),
        "viewup": (0, -1, 0),
        "clipping_range": (-4000,2000),
        "focal_point": focal_point,
        "distance": 2000,
    }
    zoom = -1000

    # If you only want a screenshot and don't want to move the camera
    # around the scene, set interactive to False.
    scene.render(interactive=True)#, camera=camera)#, zoom=zoom)

    # Set the scale, which will be used for screenshot resolution.
    # Any value > 1 increases resolution, the default is in brainrender.settings.
    # It is easiest integer scales (non-integer can cause crashes).
    scale = 2
    filename = f"{output_dir}/{cut_x}.png"
    print(filename)
    # Take a screenshot - passing no name uses current time
    # Screenshots can be also created during runtime by pressing "s"
    scene.screenshot(name=filename, scale=scale)
    #scene.close()

    crop(filename,300)

import matplotlib.pyplot as plt
import os

fig, axs = plt.subplots(2,5,figsize=(15,5))
file_list = os.listdir(output_dir)
file_list.sort(key=lambda x : int(x.split(".")[0]))

row_index = 0
col_index = 0
for file in file_list:
    i = Image.open(output_dir+"/"+file)
    #iar = np.array(i)
    axs[row_index,col_index].imshow(i)
    axs[row_index,col_index].set_title(file.split(".")[0]+" um")
    axs[row_index,col_index].set_axis_off()
    col_index += 1
    if col_index >= 5:
        col_index = 0
        row_index += 1
plt.show()
fig.savefig('total.png', dpi=300, bbox_inches='tight', pad_inches=0)
#axs[0].plot(Y)
#axs[1].scatter(z['level_1'], z['level_0'],c=z[0])