from pathlib import Path

from myterial import orange
from rich import print

from brainrender import Scene


# Create a brainrender scene
scene = Scene(title="brain regions", atlas_name="allen_mouse_50um")

# Add brain regions
scene.add_brain_region("HIP")
print(scene.get_actors()[0])
print(scene.get_actors()[1])
# You can specify color, transparency...

# Render!
scene.render()
