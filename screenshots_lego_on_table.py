## Import all relevant libraries
import bpy
import os
import numpy as np
import math as m
import random
import colorsys

image_filepath = '/home/toto/dataset_lego/gen_4/images/'
label_filepath = '/home/toto/dataset_lego/gen_4/labels/'
version = 'v4'

obj_list = ['X1-Y1-Z2',
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

COLORS = [  (0.7, 0.0, 0.0, 1.0),   #RED
            (0.0, 0.5, 0.0, 1.0),   #GREEN
            (0.0, 0.4, 1.0, 1.0),   #BLUE
            (0.0, 0.7, 0.7, 1.0),   #MINT
            (0.0, 0.05, 1.0, 1.0),  #DARKBLUE
            (1.0, 1.0, 0.0, 1.0),   #YELLOW
            (0.3, 0.0, 0.3, 1.0),   #MAGN
            (0.2, 0.0, 0.1, 1.0),   #CHA
            (1.0, 0.2, 0.0, 1.0)]   #ORAN

# --------------------------------------------------------------------------------------------------

class Render:

    def __init__(self):
        # Scene information
        self.scene = bpy.data.scenes['Scene']
        self.camera = bpy.data.objects['Camera']       
        self.axis = bpy.data.objects['Main Axis']
        self.light_1 = bpy.data.objects['Light1']
        self.light_2 = bpy.data.objects['Light2']            
        self.objects = self.create_objects(obj_list)
        self.colors = self.create_materials(color_list)
        self.render_counter = 0

    def set_random_pose(self, obj):
        rand = random.randint(1, 4)
        if rand == 1:
            # UP
            obj.rotation_euler = (0, 0, 0)
            obj.location.z = 0
        elif rand == 2:
            # DOWN
            obj.rotation_euler = (0, m.radians(180), 0)
            obj.location.z = obj.dimensions.z
        elif rand == 3:
            # SIDE LEFT
            obj.rotation_euler = (0, m.radians(-90), 0)
            obj.location.z = obj.dimensions.x / 2
        else:
            # SIDE RIGHT
            obj.rotation_euler = (0, m.radians(90), 0)
            obj.location.z = obj.dimensions.x / 2
        obj.rotation_euler.z = m.radians(random.randint(0, 360))

    def set_random_location(self, objects):
        random.seed(random.randint(1,1000))

        # Set every obj out of scope
        for obj in objects:
            obj.location = (-2, -2, obj.location.z)

        # Set each obj in scope
        for obj in objects:
            isCollision = True
            while isCollision:
                # Set random location
                print('Finding random location for:', obj.name)
                obj.location.x = random.uniform(-1, 1)
                obj.location.y = random.uniform(-1, 1)
                if obj.location.x > 0.7 and obj.location.y > 0.5:
                    obj.location.x = 0.7
                    obj.location.y = 0.5
                # Check collision
                count_collision = 0
                for obj_other in objects:
                    # Skip itself
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

    def hide(self, obj, visible):
        obj.hide_viewport = visible
        obj.hide_render = visible
        obj.hide_set(visible)
        
    def set_random_lighting(self):
        random.seed(random.randint(1,1000))
        energy1 = random.randint(50, 100)
        self.light_1.data.energy = energy1
        self.light_1.location.y = random.uniform(-1, 1)
        energy2 = random.randint(50, 100)
        self.light_2.data.energy = energy2
        self.light_2.location.y = random.uniform(-1, 1)

    def set_random_color(self):
        random.seed(random.randint(1,1000))
        for color in self.colors:
            color.use_nodes = True
            principled = color.node_tree.nodes['Principled BSDF']
            h = random.random()
            s = 1.0
            v = 1.0
            principled.inputs['Base Color'].default_value = colorsys.hsv_to_rgb(h, s, v) + (1.0,)

    def show_object(self, main_obj):
        for obj in self.objects:
            self.hide(obj, True)
        # Show only main object
        self.hide(main_obj, False)

    def render_image(self, n_output):
        self.n_renders = n_ouput        

        for i in range(self.n_renders):
            self.set_random_color()
            self.set_random_lighting()
            self.set_random_location(self.objects)
            for obj in self.objects:
                self.set_random_pose(obj)
            self.render_counter += 1

            # Display demo information
            print("On render:", version, self.render_counter)

            # Define cam
            self.xpix = 1280
            self.ypix = 720
            self.percentage = 100   #random.randint(90, 100)
            self.samples = 50       #random.randint(25, 50)
            # Render images
            image_name = version + '_' + str(self.render_counter) + '.png'
            self.export_render(self.xpix, self.ypix, self.percentage, self.samples, image_filepath, image_name)

            # Output Labels
            
            text_file_name = label_filepath + version + '_' + str(self.render_counter) + '.txt'
            text_file = open(text_file_name, 'w+') # Open .txt file of the label
            # Get formatted coordinates of the bounding boxes of all the objects in the scene
            # Display demo information - Label construction
            print("---> Label Construction")
            text_coordinates = self.get_all_coordinates()
            splitted_coordinates = text_coordinates.split('\n')[:-1] # Delete last '\n' in coordinates
            text_file.write('\n'.join(splitted_coordinates)) # Write the coordinates to the text file
            text_file.close() # Close the .txt file corresponding to the label

            ## Show progress on batch of renders
            print('Progress =', str(self.render_counter) + '/' + str(self.n_renders))


    def export_render(self, res_x, res_y, res_per, samples, file_path, file_name):
        # Set all scene parameters
        bpy.context.scene.cycles.samples = samples
        self.scene.render.resolution_x = res_x
        self.scene.render.resolution_y = res_y
        self.scene.render.resolution_percentage = res_per
        self.scene.render.filepath =  file_path + '/' + file_name

        # Take picture of current visible scene
        bpy.ops.render.render(write_still=True)

    def create_objects(self, obj_list):  # This function creates a list of all the <bpy.data.objects>
        objs = []
        for obj in obj_list:
            objs.append(bpy.data.objects[obj])
        return objs

    def create_materials(self, mat_list):  # This function creates a list of all the <bpy.data.objects>
        mats = []
        for mat in mat_list:
            mats.append(bpy.data.materials[mat])
        return mats

    def get_all_coordinates(self):
        '''
        This function takes no input and outputs the complete string with the coordinates
        of all the objects in view in the current image
        '''
        main_text_coordinates = '' # Initialize the variable where we'll store the coordinates
        for i, objct in enumerate(self.objects): # Loop through all of the objects

            if objct.visible_get():
                print("     On object:", objct)
                b_box = self.find_bounding_box(objct) # Get current object's coordinates
                if b_box: # If find_bounding_box() doesn't return None
                    print("         Initial coordinates:", b_box)
                    text_coordinates = self.format_coordinates(b_box, i) # Reformat coordinates to YOLOv3 format
                    print("         YOLO-friendly coordinates:", text_coordinates)
                    main_text_coordinates = main_text_coordinates + text_coordinates # Update main_text_coordinates variables whith each
                                                                                    # line corresponding to each class in the frame of the current image
                else:
                    print("         Object not visible")
                    pass

        return main_text_coordinates # Return all coordinates

    def format_coordinates(self, coordinates, classe):
        '''
        This function takes as inputs the coordinates created by the find_bounding box() function, the current class,
        the image width and the image height and outputs the coordinates of the bounding box of the current class
        '''
        # If the current class is in view of the camera
        if coordinates: 
            ## Change coordinates reference frame
            x1 = (coordinates[0][0])
            x2 = (coordinates[1][0])
            y1 = (1 - coordinates[1][1])
            y2 = (1 - coordinates[0][1])

            ## Get final bounding box information
            width = (x2-x1)  # Calculate the absolute width of the bounding box
            height = (y2-y1) # Calculate the absolute height of the bounding box
            # Calculate the absolute center of the bounding box
            cx = x1 + (width/2) 
            cy = y1 + (height/2)

            ## Formulate line corresponding to the bounding box of one class
            txt_coordinates = str(classe) + ' ' + str(cx) + ' ' + str(cy) + ' ' + str(width) + ' ' + str(height) + '\n'

            return txt_coordinates
        # If the current class isn't in view of the camera, then pass
        else:
            pass

    def find_bounding_box(self, obj):
        """
        Returns camera space bounding box of the mesh object.

        Gets the camera frame bounding box, which by default is returned without any transformations applied.
        Create a new mesh object based on self.carre_bleu and undo any transformations so that it is in the same space as the
        camera frame. Find the min/max vertex coordinates of the mesh visible in the frame, or None if the mesh is not in view.

        :param scene:
        :param camera_object:
        :param mesh_object:
        :return:
        """

        """ Get the inverse transformation matrix. """
        matrix = self.camera.matrix_world.normalized().inverted()
        """ Create a new mesh data block, using the inverse transform matrix to undo any transformations. """
        mesh = obj.to_mesh(preserve_all_data_layers=True)
        mesh.transform(obj.matrix_world)
        mesh.transform(matrix)

        """ Get the world coordinates for the camera frame bounding box, before any transformations. """
        frame = [-v for v in self.camera.data.view_frame(scene=self.scene)[:3]]

        lx = []
        ly = []

        for v in mesh.vertices:
            co_local = v.co
            z = -co_local.z

            if z <= 0.0:
                """ Vertex is behind the camera; ignore it. """
                continue
            else:
                """ Perspective division """
                frame = [(v / (v.z / z)) for v in frame]

            min_x, max_x = frame[1].x, frame[2].x
            min_y, max_y = frame[0].y, frame[1].y

            x = (co_local.x - min_x) / (max_x - min_x)
            y = (co_local.y - min_y) / (max_y - min_y)

            lx.append(x)
            ly.append(y)


        """ Image is not in view if all the mesh verts were ignored """
        if not lx or not ly:
            return None

        min_x = np.clip(min(lx), 0.0, 1.0)
        min_y = np.clip(min(ly), 0.0, 1.0)
        max_x = np.clip(max(lx), 0.0, 1.0)
        max_y = np.clip(max(ly), 0.0, 1.0)

        """ Image is not in view if both bounding points exist on the same side """
        if min_x == max_x or min_y == max_y:
            return None

        """ Figure out the rendered image size """
        render = self.scene.render
        fac = render.resolution_percentage * 0.01
        dim_x = render.resolution_x * fac
        dim_y = render.resolution_y * fac
        
        ## Verify there's no coordinates equal to zero
        coord_list = [min_x, min_y, max_x, max_y]
        if min(coord_list) == 0.0:
            indexmin = coord_list.index(min(coord_list))
            coord_list[indexmin] = coord_list[indexmin] + 0.0000001

        return (min_x, min_y), (max_x, max_y)

# -------------------------------------------------------------------------------------------- 

## Run data generation
if __name__ == '__main__':
    print('------------------------------------------------------')
    print('image_filepath: ' + image_filepath)
    print('label_filepath: ' + label_filepath + '\n')
    
    n_ouput = int(input('Enter number of output: '))
    render = Render()
    render.render_image(n_ouput)
