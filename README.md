# liquid_simulation

This repository contains the pipeline for simulating and rendering liquid.

# Get started with simulation
To get started, first git clone this repository to your local laptop.
Then add the absoluate path to this repository to `ENV[base]` in `default.conf`. (Please note that you would need to include the backslash in this absolute path)

Then run `setup.sh` to setup the simulation environment.

To run each simulation, first cd to /bin in the SPlisHSPlasH simulation folder. Then run `MESA_GL_VERSION_OVERRIDE=3.3 ./SPHSimulator ../json/[scene_name].json --no-gui --no-initial-pause --stopAt 4`.

# Get started with rendering
To render the scene, first run `setup_blender.sh` to setup Blender. Then cd into Blender folder and run `./blender --background --python ../blender/render_planks_with_box_fine_sim_pegs_more.py -- -s "[scene_name]" -n "10"`
