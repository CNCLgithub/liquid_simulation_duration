import bpy
#import numpy as np
import mathutils
import os
import random
import itertools
import datetime
import argparse
import sys

class ArgumentParserForBlender(argparse.ArgumentParser):
    """
    This class is identical to its superclass, except for the parse_args
    method (see docstring). It resolves the ambiguity generated when calling
    Blender from the CLI with a python script, and both Blender and the script
    have arguments. E.g., the following call will make Blender crash because
    it will try to process the script's -a and -b flags:
    >>> blender --python my_script.py -a 1 -b 2

    To bypass this issue this class uses the fact that Blender will ignore all
    arguments given after a double-dash ('--'). The approach is that all
    arguments before '--' go to Blender, arguments after go to the script.
    The following calls work fine:
    >>> blender --python my_script.py -- -a 1 -b 2
    >>> blender --python my_script.py --
    """

    def _get_argv_after_doubledash(self):
        """
        Given the sys.argv as a list of strings, this method returns the
        sublist right after the '--' element (if present, otherwise returns
        an empty list).
        """
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx+1:] # the list after '--'
        except ValueError as e: # '--' not in the list:
            return []

    # overrides superclass
    def parse_args(self):
        """
        This method is expected to behave identically as in the superclass,
        except that the sys.argv list will be pre-processed using
        _get_argv_after_doubledash before. See the docstring of the class for
        usage examples and details.
        """
        return super().parse_args(args=self._get_argv_after_doubledash())

parser = ArgumentParserForBlender()
parser.add_argument("-s", "--scene", type=str,
                    help="scene_dir")
parser.add_argument("-n", "--num", type=str,
                    help="num_of_box")
args = parser.parse_args()
scene_dir = args.scene
total_box=int(args.num)
total_box = total_box+9

############parameters that need to be changed########################
frame_num = 75
start_frame_num = 1
main_dir = '/home/ccn/Downloads/SPlisHSPlasH/bin/output/'
#######################set up working dir###############################
wd_rb = main_dir + scene_dir + '/obj/'
wd_bgeo = main_dir + scene_dir + '/output/'
wd_render = main_dir + scene_dir+'/blender/'
if not os.path.exists(wd_render):
    os.mkdir(wd_render)

#################remove defaults####################
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_all()
bpy.ops.object.delete()
##################add background####################
scn = bpy.context.scene

# Get the environment node tree of the current scene
node_tree = scn.world.node_tree
tree_nodes = node_tree.nodes

# Clear all nodes
tree_nodes.clear()

# Add Background node
node_background = tree_nodes.new(type='ShaderNodeBackground')

# Add Environment Texture node
node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
# Load and assign the image to the node property
#node_environment.image = bpy.data.images.load("/gpfs/milgram/pi/yildirim/yz932/singularity_images/blender-2.83.18-linux-x64/Chelsea_Stairs_3k.hdr")
node_environment.image = bpy.data.images.load("/home/ccn/Downloads/Chelsea_Stairs_3k.hdr")

node_environment.location = -300,0

# Add Output node
node_output = tree_nodes.new(type='ShaderNodeOutputWorld')
node_output.location = 200,0

# Link all nodes
links = node_tree.links
link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])

################add outer bounding box#######################
bpy.ops.mesh.primitive_cube_add(size=40, enter_editmode=False, align='WORLD', location=(0, 0, 0))
#bpy.ops.mesh.primitive_plane_add(size=40, enter_editmode=False, align='WORLD', location=(0.0, 0.0, -2.042830467224121))

#################add area light and change watts#############
bpy.ops.object.light_add(type='AREA', radius=1, align='WORLD', location=(-0.42797398567199707, -0.37127411365509033, 9.654523849487305))
bpy.context.object.data.energy = 5000

######################add camera######################
#bpy.ops.object.camera_add(location=(-13.545211791992188, -6.5608062744140625, 4.068312644958496), rotation=(1.3240665197372437, 0.05913066491484642, -1.151856780052185))
#bpy.ops.object.camera_add(location=(0.0, -20.101789474487305, -0.20164763927459717), rotation=(1.5448718070983887, 0.0, 6.2876996994018555))
bpy.ops.object.camera_add(location=(0.0, -20, -0.2), rotation=(1.5448718070983887, 0, 6.2876996994018555))
#bpy.ops.object.camera_add(location=(0.0, -16.93344497680664, 0.5), rotation=(1.5448718070983887, 0, 6.2876996994018555))


bpy.context.scene.camera = bpy.context.object
print('######################################')
print('#######Finished with setting up#######')
print('######################################')

for i in range(start_frame_num,frame_num):
    print('frame no.'+str(i))
    for j in range(1,total_box+1):
        p = wd_rb+'rb_data_'+str(j)+'_'+str(i)+'.obj'
        bpy.ops.import_scene.obj(filepath=p)
    
    fluid_file = wd_bgeo+'ParticleData_Fluid_0_'+str(i)+'.ply'
    current_fluid = bpy.ops.import_mesh.ply(filepath=fluid_file)

    #get the tag for each element
    fluid = os.path.basename(fluid_file).replace('.ply','')

    bpy.data.objects[fluid].rotation_euler[0] = 1.5708
    print('######################################')
    print('##Finished with loading and rotating##')
    print('######################################')

    ###################select flow and flow_emitter for changing material####################
    #for fluid
    mat = bpy.data.materials.new("fluid_material")
    mat.use_nodes = True
    mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Principled BSDF'))#Note that the default material needs to be removed
    material_output = mat.node_tree.nodes.get('Material Output')
    BSDF = mat.node_tree.nodes.new('ShaderNodeBsdfGlass')
    BSDF.inputs['Roughness'].default_value = 0.0
    BSDF.inputs['IOR'].default_value = 4/3
    BSDF.inputs['Color'].default_value = (0.194646, 0.888, 1, 1)
    mat.node_tree.links.new(material_output.inputs[0], BSDF.outputs[0])

    #after making sure that the material is fine, assign it to the object
    bpy.context.view_layer.objects.active = bpy.data.objects[fluid] #set active element
    obj = bpy.context.active_object
    if len(obj.material_slots) == 0:
        bpy.ops.object.material_slot_add()

    obj.material_slots[0].material = mat

    ###################select rigid bodies for changing material####################
    for k in range(1,total_box+1):
        mat_name = "box_material_"+str(k)
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        material_output = mat.node_tree.nodes.get('Material Output')
        principled = mat.node_tree.nodes.get('Principled BSDF')#Note that the default material needs to be removed
        principled.inputs['Base Color'].default_value = (0.042, 1, 0.122, 1)
        principled.inputs['Roughness'].default_value = 0.5
        mat.node_tree.links.new(material_output.inputs[0], principled.outputs[0])
        #after making sure that the material is fine, assign it to the object
        box_name = 'rb_data_'+str(k)+'_'+str(i)
        bpy.context.view_layer.objects.active = bpy.data.objects[box_name]
        obj = bpy.context.active_object
        if len(obj.material_slots) == 0:
            bpy.ops.object.material_slot_add()
        obj.material_slots[0].material = mat



    print('######################################')
    print('###Finished with changing materials###')
    print('######################################')

    #####################switch to cycle####################
    bpy.context.scene.render.engine = 'CYCLES'

    #######################render!#########################
    scene = bpy.context.scene
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath = wd_render + str(i)+'.png'
    bpy.ops.render.render(write_still=1)

    ########remove objects to prepare for next frame#########
    #collection = [box,box_2,box_3,box_4,base,fluid]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[fluid].select_set(True)
    bpy.ops.object.delete()
    bpy.ops.object.select_all(action='DESELECT')
    for q in range(1,total_box+1):
        n = 'rb_data_'+str(q)+'_'+str(i)
        bpy.data.objects[n].select_set(True)

    bpy.ops.object.delete()

