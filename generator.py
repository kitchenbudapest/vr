## INFO ##
## INFO ##

import bpy

scenes = bpy.data.scenes
meshes = bpy.data.meshes

## Remove all objects from all scenes
## and remove all scenes as well
#for scene in scenes:
#    for object in scene.objects:
#        meshes.remove(object)
#    scenes.remove(scene)
## check: http://blenderscripting.blogspot.hu/2012/03/deleting-objects-from-scene.html

# Create a new scene
bpy.ops.scene.new(type='EMPTY')
scene = scenes[-1]
print(scene)
