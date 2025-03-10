from pathlib import Path
from brainrender._io import load_mesh_from_file
from myterial import orange
from rich import print
from brainglobe_atlasapi import BrainGlobeAtlas
from brainrender import Scene

print(f"[{orange}]Running example: {Path(__file__).name}")

bg_atlas = BrainGlobeAtlas("allen_mouse_100um", check_latest=False)
bg_atlas.lookup_df.acronym.values
region = 'TH'
obj_file = str(bg_atlas.meshfile_from_structure(region))


mesh = load_mesh_from_file(obj_file, alpha=0.2, color="green")




# Create a brainrender scene
#scene = Scene(title="slice")
scene = Scene(title="Left hemisphere", atlas_name="allen_mouse_25um")
# Add brain regions
th = scene.add_brain_region("TH")

# You can specify color, transparency...
mos, ca1 = scene.add_brain_region("MOs", "CA1", alpha=0.2, color="green")

# Slice actors with frontal plane
scene.slice("frontal", actors=[th])

# Slice with a custom plane
plane = scene.atlas.get_plane(pos=mos.center_of_mass(), norm=(1, 1, 0))
scene.slice(plane, actors=[mos, ca1])


# Set up a camera. Can use string, such as "sagittal".
# During render runtime, press "c" to print the current camera parameters.
camera = {
    "pos": (8777, 1878, -44032),
    "viewup": (0, -1, 0),
    "clipping_range": (24852, 54844),
    "focal_point": (7718, 4290, -3507),
    "distance": 40610,
}
zoom = 2.5


# If you only want a screenshot and don't want to move the camera
# around the scene, set interactive to False.
scene.render(interactive=False, camera=camera, zoom=zoom)

# Set the scale, which will be used for screenshot resolution.
# Any value > 1 increases resolution, the default is in brainrender.settings.
# It is easiest integer scales (non-integer can cause crashes).
scale = 2

# Take a screenshot - passing no name uses current time
# Screenshots can be also created during runtime by pressing "s"
scene.screenshot(name="output/1.png", scale=scale)

scene.close()
