from brainrender import Animation, Scene, settings
from pathlib import Path

settings.SHOW_AXES = False

scene = Scene(atlas_name="allen_mouse_25um")

regions = (
    "CTX",
    "HPF",
    "STR",
    "CB",
    "MB",
    "TH",
    "HY",
)
scene.add_brain_region(*regions, silhouette=True)


def slc(scene, framen, totframes):
    # Get new slicing plane
    fact = framen / totframes
    shape_um = scene.atlas.shape_um
    # Multiply by fact to move the plane, add buffer to go past the brain
    point = [(shape_um[0] + 500) * fact, shape_um[1] // 2, shape_um[2] // 2]
    plane = scene.atlas.get_plane(pos=point, norm=(1, 0, 0))

    scene.slice(plane)


anim = Animation(
    scene, Path.cwd(), "brainrender_animation_callback", size=None
)

# Specify camera pos and zoom at some key frames`
anim.add_keyframe(0, camera="frontal", zoom=1, callback=slc)

# Make videos
#anim.make_video(duration=5, fps=10, fix_camera=True)
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
scene.render(interactive=True, camera=camera, zoom=zoom)