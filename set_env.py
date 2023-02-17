import bpy
import numpy as np
import math as m
import random

scene = bpy.data.scenes['Scene']
camera = bpy.data.objects['Camera']        
axis = bpy.data.objects['Main Axis']
light_1 = bpy.data.objects['Light1']
light_2 = bpy.data.objects['Light2']


obj_names =   [ 'X1-Y1-Z2',
                'X1-Y2-Z1',
                'X1-Y2-Z2',
                'X1-Y2-Z2-CHAMFER',
                'X1-Y2-Z2-TWINFILLET',
                'X1-Y3-Z2',
                'X1-Y3-Z2-FILLET',
                'X1-Y4-Z1',
                'X1-Y4-Z2',
                'X2-Y2-Z2',
                'X2-Y2-Z2-FILLET']
objects = []                 
for obj in obj_names:
    objects.append(bpy.data.objects[obj])

# background_list = [ 'Plane1',
#                     'Plane2',
#                     'Plane3',
#                     'Plane4',
#                     'Plane5']
# backgrounds = []
# for obj in background_list:
#     backgrounds.append(bpy.data.objects[obj])

color_list = [  'color1',
                'color2',
                'color3',
                'color4',
                'color5',
                'color6',
                'color7',
                'color8',
                'color9',
                'color10',
                'color11']
colors = []

COLORS = [  (0.7, 0.0, 0.0, 1.0),   #RED
            (0.0, 0.5, 0.0, 1.0),   #GREEN
            (0.0, 0.4, 1.0, 1.0),   #BLUE
            (0.0, 0.7, 0.7, 1.0),   #MINT
            (0.0, 0.05, 1.0, 1.0),  #DARKBLUE
            (1.0, 1.0, 0.0, 1.0),   #YELLOW
            (0.3, 0.0, 0.3, 1.0),   #MAGN
            (0.2, 0.0, 0.1, 1.0),   #CHA
            (1.0, 0.2, 0.0, 1.0)]   #ORAN

for color in color_list:
    colors.append(bpy.data.materials[color])

def hide(obj, visible):
        obj.hide_viewport = visible
        obj.hide_render = visible
        obj.hide_set(visible)

def show_object(main_obj):
        for obj in objects:
            hide(obj, True)
        # Show only main object
        hide(main_obj, False)

def set_random_color():
        # random.seed(random.randint(1,1000))
        for color in colors:
            color.use_nodes = True
            principled = color.node_tree.nodes['Principled BSDF']
            red = random.random()
            green = random.random()
            blue = random.random()
            principled.inputs['Base Color'].default_value = (red, green, blue, 1.0)

def set_random_location(objects):
        random.seed(random.randint(1,1000))

        # Set every obj out of scope
        for obj in objects:
            obj.location = (-2, -2, obj.location.z)

        # Set each obj in scope
        for obj in objects:
            isCollision = True
            while isCollision:
                # Set random location
                obj.location.x = random.uniform(-1, 1)
                obj.location.y = random.uniform(-1, 1)
                obj.rotation_euler.z = m.radians(random.randint(0, 360))
                # Check collision
                count_collision = 0
                for obj_other in objects:
                    # Skip it                    
                    if obj.name == obj_other.name:
                        continue
                    # Compare x, y
                    abs_x = abs(obj.location.x - obj_other.location.x)
                    abs_y = abs(obj.location.y - obj_other.location.y)
                    dim_x = obj.dimensions.x + obj_other.dimensions.x
                    dim_y = obj.dimensions.y + obj_other.dimensions.y
                    max_dim = max(dim_x, dim_y)
                    if abs_x < max_dim/2 + 0.07 and abs_y < max_dim/2 + 0.07:
                        count_collision += 1
                        break
                # Set no collision
                if count_collision == 0:
                    isCollision = False

def set_random_background():
    # random.seed(random.randint(1,1000))
    rand = random.randint(0, len(backgrounds)-1)
    for i in range(0, len(backgrounds)):
        backgrounds[i].scale = (6.0, 6.0, 6.0)
        if i == rand:
            hide(backgrounds[i], False)
            continue
        hide(backgrounds[i], True)

def set_random_lighting():
        # random.seed(random.randint(1,1000))
        energy1 = random.randint(50, 100)
        light_1.data.energy = energy1
        energy2 = random.randint(50, 100)
        light_2.data.energy = energy2

# ----------------------------------------------------------------------------------------------

for obj in objects:
    hide(obj, False)

set_random_lighting()
set_random_location(objects)
set_random_color()

# for obj in backgrounds:
#     hide(obj, False)




