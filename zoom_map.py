#zoom_map.py
#A python package to create a zoomable map (like Google Maps) using tkinter

#dependencies
import tkinter as tk


#this class is the zoomable map
class ZoomMap:
    #create the map
    def __init__(self,map_width,map_height,window,background="white",zoom_control="<MouseWheel>",drag_start_control='<ButtonPress-1>',drag_end_control="<B1-Motion>",print_warnings=True,scroll_gain=1,zoom_gain=0.01):
        print('foo')
        self.map_width = map_width #width (horizontal length) of the map display in pixels
        self.map_height = map_height #height (vertical length) of the map display in pixels
        self.map_center_x = int(self.map_width/2) #midpoint of the map in pixels, horizontal
        self.map_center_y = int(self.map_height/2) #midpoint of the map in pixels, vertical
        self.window = window #tk object in which the canvas is drawn
        self.background = background #background object, at the moment only supports tk colours
        self.print_warnings = print_warnings #do we print warning and error messages
        self.scroll_gain = scroll_gain #how fast is panning
        self.zoom_gain = zoom_gain #how fast is zooming
        #create the canvas object
        self.map = tk.Canvas(self.window,bg=self.background,width=self.map_width,height=self.map_height)
        self.map.pack(side = tk.RIGHT)
        #bind the canvas to the controls to zoom and drag the image
        #try blocks catch invalid keybindings and replace them with the defaults
        #bind zoom and drag
        try:
            self.map.bind(zoom_control,self.zoom_map)
        except:
            if self.print_warnings:
                print("WARNING : ",zoom_control,' not a valid keybinding for tkinter. Defaulting to  "<MouseWheel>", for zoom keybinding')
            self.map.bind("<MouseWheel>",self.zoom_map)
        #bind starting to drag the map
        try:
            self.map.bind(drag_start_control,self.drag_start)
        except:
            if self.print_warnings:
                print("WARNING : ",drag_start_control,' not a valid keybinding for tkinter. Defaulting to  "<ButtonPress-1>", for drag start keybinding')
            self.canvas.bind("<ButtonPress-1>",self.drag_start)
        #bind stopping a drag
        try:
            self.map.bind(drag_end_control,self.drag_end)
        except:
            if self.print_warnings:
                print("WARNING : ",drag_end_control,' not a valid keybinding for tkinter. Defaulting to  "<B1-Motion>", for drag end keybinding')
            self.map.bind("<B1-Motion>",self.drag_end)
        
        #create containers for objects to be displayed on the map
        self.init_objects()
        
       

    #print a warning if warnings enabled
    def warning_print(self,message):
        if self.print_warnings==True:
            print("WARNING: ",message)

    #create empty containers to store displayed objects in
    def init_objects(self):
        self.init_nodes() #containers to store nodes
        self.init_pie_nodes() #containers to store pie nodes
        self.init_lines() #containers to store lines
        self.init_compound_lines() #containers to store compound lines
    
    #private tools to work on these containers, we will later add on a public interface as well, which will be the same but with more checking
    
    #after objects has been assigned, determine correct scale
    def determine_scale(self,scale_mode='automatic',pixels_per_unit=1,start_x=0,start_y=0,extra_x=1,extra_y=1,border_fraction_x=0.1,border_fraction_y=0.1):
        if scale_mode=='automatic': #automatic scaling mode, fit in all the nodes
            self.pixels_per_unit,self.start_x,self.start_y = self.get_automatic_scaling_boundaries(border_fraction_x,border_fraction_y)
        elif scale_mode=='manual': #full manual scaling, manually set start_x and start_y coordinates in the global frame, and the scale between global coordinates between pixels
            self.pixels_per_unit = pixels_per_unit
            self.start_x = start_x
            self.start_y = start_y
        elif scale_mode=='semi-automatic': #semi-automatic scaling, manually set start_x and start_coordinates in the global frame and determine pixel scale automatically from requested extra_x and extra_y space in global coordinates
            self.start_x = start_x
            self.start_y = start_y
            self.pixels_per_unit = self.get_semi_automatic_scaling_boundaries(extra_x,extra_y)
        else:
            warning_message = 'scale_mode ' + scale_mode + ' is not a valid scale mode\n' + 'Valid modes are "automatic", "manual", "semi-automatic" \n Defaulting to automatic scaling' 
            self.warning_print(warning_message)
            self.pixels_per_unit,self.start_x,self.start_y = self.get_automatic_scaling_boundaries(border_fraction_x,border_fraction_y)


    #automatically calculate and store the position of all objects in the (unzoomed) pixel coordinate system
    def calculate_pixel_coordinates(self):
        #convert the coordinates for every object that exists
        if self.nodes_assigned_flag==True:
            self.calculate_node_pixel_coordinates()
        if self.lines_assigned_flag==True:
            self.calculate_line_pixel_coordinates()
        if self.compound_lines_assigned_flag==True:
            self.calculate_compound_line_pixel_coordinates()
        if self.pie_nodes_assigned_flag==True:
            self.calculate_pie_nodes_pixel_coordinates()

    #convert global coordinates to unzoomed pixel coordinates
    def convert_coords_to_pixels(self,coord_x,coord_y):
        latitude_offset = coord_y-self.start_y #units between upper-left and position, y axis
        longitude_offset = coord_x-self.start_x #units between upper left and position, x axis
        y = -(latitude_offset)*self.pixels_per_unit #multiply by -1 as positive pixels are down, but positive coords are north
        x = (longitude_offset)*self.pixels_per_unit 
        return x,y

    #automatically calculate the scale of the map
    def get_automatic_scaling_boundaries(self,border_fraction_x,border_fraction_y):
        extremes_defined,extreme_north,extreme_south,extreme_east,extreme_west = self.get_extreme_positions() #get the extreme positions in global coordinates
        #if we could not find any extremes (likely due to their being objects), warn the user
        if extremes_defined==False:
            message = "extreme positions not found among " + str(self.num_nodes) + " nodes, " + str(self.num_lines) + " lines, " + str(self.num_compound_lines) + " compound lines, " + str(self.num_pie_nodes) + "pie nodes "
            self.warning_print(message)
            self.warning_print("reverting to default extremes of +- 1 units")
        units_north_south = extreme_north-extreme_south #how much distance between north and south in global coordinate frame
        units_east_west = extreme_east-extreme_west #how much distance between east and west in global coordinate frame
        start_x = extreme_west - units_east_west*border_fraction_x*0.5#starting x position (west-most) in global coordinates accounting for requested border (half as other half will be on other side)
        start_y = extreme_north + units_north_south*border_fraction_y*0.5 #starting x position (north-most) in global coordinates accounting for requested border (half as other half will be on other side)
        units_north_south = (units_north_south)*(1+border_fraction_y) #account for the requested border in the needed length
        units_east_west = (units_east_west)*(1+border_fraction_x) #account for the requested border in the needed length
        pixels_per_unit_x = self.map_width/units_east_west #maximum number of pixels per unit to achieve requested extra x space
        pixels_per_unit_y = self.map_height/units_north_south #minimum number of pixels per unit to achieve requested extra y space
        pixels_per_unit = min(pixels_per_unit_x,pixels_per_unit_y) #minima allows us to achieve requested extra space along both axes
        return pixels_per_unit,start_x,start_y #return the pixel density along with the starting position in global coordinates accounting for the requested border


    #semi-automatically calculate the scale of the map
    def get_semi_automatic_scaling_boundaries(self,extra_x,extra_y):
        pixels_per_unit_x = self.map_width/extra_x #maximum number of pixels per unit to achieve requested extra x space
        pixels_per_unit_y = self.map_height/extra_y #minimum number of pixels per unit to achieve requested extra y space
        pixels_per_unit = min(pixels_per_unit_x,pixels_per_unit_y) #minima allows us to achieve requested extra space along both axes
        return pixels_per_unit
        

    #get extreme positions from all types of objects being rendered
    def get_extreme_positions(self):
        #placeholders for extremes
        extreme_north = 1
        extreme_south = -1
        extreme_east = -1
        extreme_west = 1
        extremes_defined = False #have we determined extreme positions yet
        if self.nodes_assigned_flag==True: #if we have assigned nodes
            extreme_north,extreme_south,extreme_east,extreme_west = self.get_extreme_nodes() #get the extreme positions of the nodes
            extremes_defined = True #we have defined extremes which we can compare to
        #compare with 
        if self.lines_assigned_flag==True: #if we have assigned lines
            if extremes_defined==True: #and we have already measured extremes, compare the extremes and select the most extreme
                new_extreme_north,new_extreme_south,new_extreme_east,new_extreme_west = self.get_extreme_lines() #get the new extreme positions from the lines
                extreme_north = max(extreme_north,new_extreme_north)
                extreme_south = min(extreme_south,new_extreme_south)
                extreme_east = max(extreme_east,new_extreme_east)
                extreme_west = min(extreme_west,new_extreme_west)
            else: #if extremes not yet found, extremes are the new extremes
                extreme_north,extreme_south,extreme_east,extreme_west = self.get_extreme_lines() #get the extreme positions of the lines
                extremes_defined = True #we have defined extremes which we can compare to
        #compare with compound lines if they exist
        if self.compound_lines_assigned_flag==True: #if we have assigned compound lines
            if extremes_defined==True: #and we have already measured extremes, compare the extremes and select the most extreme
                new_extreme_north,new_extreme_south,new_extreme_east,new_extreme_west = self.get_extreme_compound_lines() #get the new extreme positions from the compound lines
                extreme_north = max(extreme_north,new_extreme_north)
                extreme_south = min(extreme_south,new_extreme_south)
                extreme_east = max(extreme_east,new_extreme_east)
                extreme_west = min(extreme_west,new_extreme_west)
            else: #if extremes not yet found, extremes are the new extremes
                extreme_north,extreme_south,extreme_east,extreme_west = self.get_extreme_compound_lines() #get the extreme positions of the compound lines
                extremes_defined = True #we have defined extremes which we can compare to
        #compare with pie nodes if they exist
        if self.pie_nodes_assigned_flag==True: #if we have assigned pie nodes
            if extremes_defined==True: #and we have already measured extremes, compare the extremes and select the most extreme
                new_extreme_north,new_extreme_south,new_extreme_east,new_extreme_west = self.get_extreme_pie_nodes() #get the new extreme positions from the pie_nodes lines
                extreme_north = max(extreme_north,new_extreme_north)
                extreme_south = min(extreme_south,new_extreme_south)
                extreme_east = max(extreme_east,new_extreme_east)
                extreme_west = min(extreme_west,new_extreme_west)
            else: #if extremes not yet found, extremes are the new extremes
                extreme_north,extreme_south,extreme_east,extreme_west = self.get_extreme_pie_nodes() #get the extreme positions of the pie_nodes lines
                extremes_defined = True #we have defined extremes which we can compare to

        #return whether we have found extremes and the extremes (or placeholder if we have not found the extremes)
        print('extreme east ',extreme_east)
        print('extreme west ',extreme_west)
        print('extreme north ',extreme_north)
        print('extreme south ',extreme_south)
        return extremes_defined,extreme_north,extreme_south,extreme_east,extreme_west                

    #private tools for operating on nodes
    #create containers to store nodes
    def init_nodes(self):
        #nodes, these are filled circles created using the tk oval object
        self.num_nodes = 0 #number of nodes stored
        self.node_info_type = 'none' #type of info stored
        self.node_info_name = 'none' #name of info stored
        #arrays of node properties
        self.nodes_x_coords = [] #horizontal position in global coordinates of the centre of the node
        self.nodes_y_coords = [] #vertical position in global coordinates of the centre of the node
        self.nodes_x = [] #horizontal position in pixel coordinates of the centre of the node
        self.nodes_y = [] #vertical position in pixel coordinates of the centre of the node
        self.nodes_x_original = [] #copy of self.nodes_x without zoom applied
        self.nodes_y_original = [] #copy of self.nodes_y without zoom applied
        self.nodes_radii = []  #radius of the node, pixels
        self.nodes_colours = [] #colour of the nodes
        self.nodes_name = [] #name of the each node
        self.nodes_info = [] #additional info about each node 
        self.node_canvas_ids = [] #id of the node object within the canvas
        #flags
        self.nodes_assigned_flag = False #have nodes been stored yet

    #render the nodes
    def render_nodes(self):
        for i in range(self.num_nodes):
            x = self.nodes_x[i]
            y = self.nodes_y[i]
            radius = self.nodes_radii[i]
            colour = self.nodes_colours[i]
            if self.node_canvas_ids[i]!='blank':
                #delete the old oval object if one exists
                self.map.delete(self.node_canvas_ids[i])
            id = self.map.create_oval(x-radius,y-radius,x+radius,y+radius,fill=colour) #draw a circle to represent the node
            self.node_canvas_ids[i] = id #store the id so we can delete the object later

    #create new nodes and replace the existing nodes
    def create_nodes(self,nodes_x_coords,nodes_y_coords,nodes_radii,nodes_colours,nodes_names,info_type='none',info_name='none',nodes_info=[]):
        self.init_nodes() #remove the storage of the existing nodes
        self.num_nodes = len(nodes_x_coords) #get the number of nodes
        self.assign_nodes_positions(nodes_x_coords,nodes_y_coords)  #assign the position of the new nodes
        self.assign_nodes_radii(nodes_radii) #assign the nodes radii
        self.assign_nodes_colours(nodes_colours) #assign the nodes colours
        self.assign_nodes_names(nodes_names) #assign the nodes names
        self.assign_nodes_info(info_type,info_name,nodes_info) #assign info the nodes
        self.nodes_assigned_flag = True  
            
    #assign the nodes new x/y coordinates in the global coordinate frame
    def assign_nodes_positions(self,nodes_x_coords,nodes_y_coords):
        self.nodes_x_coords = nodes_x_coords
        self.nodes_y_coords = nodes_y_coords

    #assign the nodes new radii
    def assign_nodes_radii(self,nodes_radii):
        self.nodes_radii = nodes_radii

    #assign the nodes new colours
    def assign_nodes_colours(self,nodes_colours):
        self.nodes_colours = nodes_colours

    #assign the nodes new names
    def assign_nodes_names(self,nodes_names):
        self.nodes_names = nodes_names

    #assign info about the nodes
    def assign_nodes_info(self,info_type,info_name,nodes_info):
        #at the moment we only handle no node info
        if info_type=='none':
            self.assign_nodes_none_info()
        else:
            message = 'Node Info Type : ' + info_type + " not yet supported, defaulting to none"
            self.warning_print(message)
            self.assign_nodes_none_info()

    def assign_nodes_none_info(self):
        self.node_info_type='none'
        self.node_info_name='none'

    #find and return the most extreme coordinates found in the list of nodes
    def get_extreme_nodes(self):
        extreme_north = max(self.nodes_y_coords) #northernmost node has largest y coordinate
        extreme_south = min(self.nodes_y_coords) #southernmost node has smallest y coordinate
        extreme_east = max(self.nodes_x_coords) #easternmost point has smallest x coordinate
        extreme_west = min(self.nodes_x_coords) #westernmost point has largest x coordinate
        return extreme_north,extreme_south,extreme_east,extreme_west

    #calculate node positions in unzoomed pixel coordinates
    def calculate_node_pixel_coordinates(self):
        for i in range(self.num_nodes): #go through each node
            node_x,node_y = self.convert_coords_to_pixels(self.nodes_x_coords[i],self.nodes_y_coords[i]) #calculate the position in unzoomed pixel coordinates of each node
            #append this info to existing coordinate lists
            self.nodes_x.append(node_x)
            self.nodes_y.append(node_y)
        #make a copy of pixel position to store the original position before zooming
        self.nodes_x_original = self.nodes_x
        self.nodes_y_original = self.nodes_y    
        self.node_canvas_ids = ['blank']*self.num_nodes #canvas ids for the nodes themsleves
    
    #private tools for operating on pie_nodes
    
    #create containers to store pie chart nodes
    def init_pie_nodes(self):
        #pie nodes, these are filled circles representing a pie chart, created using tk arc objects
        self.num_pie_nodes = 0 #number of pie nodes stored
        self.pie_node_info_type = 'none' #type of info stored
        self.pie_node_info_name = 'none' #name of info stored
        self.pie_node_info_subtypes_names = [] #list of all types of info displayed, in order
        #arrays of pie_node properties
        self.pie_nodes_x_coords = [] #horizontal position in global coordinates of the centre of the pie node
        self.pie_nodes_y_coords = [] #vertical position in global coordinates of the centre of the pie node
        self.pie_nodes_x = [] #horizontal position in pixel coordinates of the centre of the pie node
        self.pie_nodes_y = [] #vertical position in pixel coordinates of the centre of the pie node
        self.pie_nodes_x_original = [] #copy of self.pie_nodes_x without zoom applied
        self.pie_nodes_y_original = [] #copy of self.pie_nodes_y without zoom applied
        self.pie_nodes_radii = []  #radius of the pie_node, pixels
        self.pie_nodes_colours = [] #colour of the pie_nodes, list of lists
        self.pie_nodes_colour_lengths = [] #length of each of the pie_nodes colour section, list of lists
        self.pie_nodes_name = [] #name of the each node
        self.pie_node_infos = [] #additional info about each pie_node, list of lists with one subentry for each pie slice 
        self.pie_node_canvas_ids = [] #id of the arc objects that make up the pie_nodes, as a list of lists
        #flags
        self.pie_nodes_assigned_flag = False #have pie nodes been stored yet

    #render the pie nodes PLACEHOLDER
    def render_pie_nodes(self):
        pass

    #create new pie nodes and replace the existing pie nodes
    def create_pie_nodes(self,pie_nodes_x_coords,pie_nodes_y_coords,pie_nodes_radii,pie_nodes_colours,pie_nodes_colours_lengths,pie_nodes_names,info_type='none',info_name='none',info_subtype_names=[],pie_nodes_infos=[]):
        self.init_pie_nodes() #remove the storage of the existing nodes
        self.num_pie_nodes = len(pie_nodes_x_coords) #get the number of pie nodes
        self.assign_pie_nodes_positions(pie_nodes_x_coords,pie_nodes_y_coords)  #assign the position of the new pie nodes
        self.assign_pie_nodes_radii(pie_nodes_radii) #assign the pie nodes radii
        self.assign_pie_nodes_colours(pie_nodes_colours) #assign the pie nodes colours
        self.assign_pie_nodes_colours_lengths(pie_nodes_colours_lengths) #assign the length of each colour segments
        self.assign_pie_nodes_names(pie_nodes_names) #assign the pie nodes names
        self.assign_pie_nodes_info(info_type,info_name,info_subtype_names,pie_nodes_infos) #assign info to the pie nodes
        self.pie_nodes_assigned_flag = True  

    #assign the pie nodes new x/y coordinates in the global coordinate frame
    def assign_pie_nodes_positions(self,pie_nodes_x_coords,pie_nodes_y_coords):
        self.pie_nodes_x_coords = pie_nodes_x_coords
        self.pie_nodes_y_coords = pie_nodes_y_coords

    #assign the pie nodes new radii
    def assign_pie_nodes_radii(self,pie_nodes_radii):
        self.pie_nodes_radii = pie_nodes_radii

    #assign the pie nodes new colours
    def assign_pie_nodes_colours(self,pie_nodes_colours):
        self.pie_nodes_colours = pie_nodes_colours

    #assign the length of the colour segment of each pie node
    def assign_pie_nodes_colours(self,pie_nodes_colours_lengths):
        self.pie_nodes_colours_lengths = pie_nodes_colours_lengths

    #assign the nodes new names
    def assign_pie_nodes_names(self,pie_nodes_names):
        self.pie_nodes_names = pie_nodes_names

    #assign info about the nodes
    def assign_pie_nodes_info(self,info_type,info_name,info_subtype_names,pie_nodes_info):
        #at the moment we only handle blank nodes
        if info_type=='none':
            self.assign_pie_nodes_none_info()
        else:
            message = 'Pie Node Info Type : ' + info_type + " not yet supported, defaulting to none"
            self.warning_print(message)
            self.assign_pie_nodes_none_info()

    def assign_pie_nodes_none_info(self):
        self.pie_node_info_type='none'
        self.pie_node_info_name='none'

    #find and return the most extreme coordinates found in the list of nodes
    def get_extreme_pie_nodes(self):
        extreme_north = max(self.pie_nodes_y_coords) #northernmost node has largest y coordinate
        extreme_south = min(self.pie_nodes_y_coords) #southernmost node has smallest y coordinate
        extreme_east = max(self.pie_nodes_x_coords) #easternmost point has smallest x coordinate
        extreme_west = min(self.pie_nodes_x_coords) #westernmost point has largest x coordinate
        return extreme_north,extreme_south,extreme_east,extreme_west

    #private tools for operating on lines

    #create containers to store lines
    def init_lines(self):
        #lines, these are well, lines
        self.num_lines = 0 #number of lines stored
        self.line_info_name = 'none' #name of the info stored with the lines
        self.line_info_type = 'none' #type of the info stored with the lines
        #arrays of line properties
        #relating to nodes
        self.lines_start_node_type = [] #what type of node is at the start of the line (valid are 'none','node' and 'pie')
        self.lines_start_node_index = [] #index of the starting node, if it exists
        self.lines_start_node_type = [] #what type of node is at the end of the line (valid are 'none','node' and 'pie')
        self.lines_start_node_index= [] #index of the ending node, if it exists
        #global coordinate arrays
        self.lines_start_x_coord = [] #horizontal position in global coordinates of the start of the line
        self.lines_start_y_coord = [] #vertical position in global coordinates of the start of the line
        self.lines_end_x_coord = [] #horizontal position in global coordinates of the end of the line
        self.lines_end_y_coord = [] #vertical position in global coordinates of the end of the line
        #pixel coordinate arrays
        self.lines_start_x = [] #horizontal position in pixel coordinates of the start of the line
        self.lines_start_y = [] #vertical position in pixel coordinates of the start of the line
        self.lines_end_x = [] #horizontal position in pixel coordinates of the end of the line
        self.lines_end_y = [] #vertical position in pixel coordinates of the end of the line
        self.lines_midpoint_x = [] #horizontal midpoint in pixel coordinates of the line, used for text display
        self.lines_midpoint_y = [] #vertical midpoint in pixel coordinates of the line, used for text display
        #copy of pixel coordinate arrays before zoom has been applied
        self.lines_start_x_original = []
        self.lines_start_y_original = []
        self.lines_end_x_original = []
        self.lines_end_y_original = []
        self.lines_midpoint_x_original = [] 
        self.lines_midpoint_y_original = []
        #other line properties 
        self.lines_width = [] #width of the line, pixels
        self.lines_colour = [] #colour of the line
        self.lines_name = [] #name of all the lines
        self.lines_canvas_ids = [] #id of the line, so we can delete it later
        #flags
        self.lines_assigned_flag = False #have lines been stored yet

    #render the lines PLACEHOLDER
    def render_lines(self):
        pass
    
    #create new lines and replace the existing lines #note this must be done after node creation if using nodes to define line start/end points 
    def create_lines(self,lines_width,lines_colour,lines_name,info_name,info_type,lines_info,lines_start_node_type='none',lines_start_node_index=-1,lines_end_node_type='none',lines_end_node_index=-1,line_coords_prefer=False,lines_start_x_coord=0,lines_start_y_coord=0,lines_end_x_coord=0,lines_end_y_coord=0):
        self.init_lines() #reset line storage, removing all existing lines
        self.num_lines = len(lines_width) #number of lines
        self.assign_lines_width(lines_width) #assign width of all lines
        self.assign_lines_colour(lines_colour) #assign colour of all lines
        self.assign_lines_names(lines_name) #assign name to the lines
        self.assign_lines_info(info_name,info_type,lines_info)
        self.assign_lines_nodes_and_positions(lines_start_node_type,lines_start_node_index,lines_end_node_type,lines_end_node_index,line_coords_prefer,lines_start_x_coord,lines_start_y_coord,lines_end_x_coord,lines_end_y_coord)

    #assign the width of all the lines
    def assign_lines_width(self,lines_width):
        self.lines_width = lines_width

    #assign the colour of all the lines
    def assign_lines_colour(self,lines_colour):
        self.lines_colour = lines_colour

    #assign the name of all the lines
    def assign_lines_names(self,lines_name):
        self.lines_name = lines_name

    #assign info to the lines
    def assign_lines_info(self,info_name,info_type,lines_info):
        #at the moment we only handle no node info
        if info_type=='none':
            self.assign_lines_none_info()
        else:
            message = 'Lines Info Type : ' + info_type + " not yet supported, defaulting to none"
            self.warning_print(message)
            self.assign_lines_none_info()

    #assign no info to the lines
    def assign_lines_none_info(self):
        self.line_info_type='none'
        self.line_info_name='none'

    #assign nodes and positions to determine the start and end of lines
    def assign_lines_nodes_and_positions(self,lines_start_node_type=[],lines_start_node_index=-1,lines_end_node_type=[],lines_end_node_index=-1,line_coords_prefer=False,lines_start_x_coord=[],lines_start_y_coord=[],lines_end_x_coord=[],lines_end_y_coord=[]):
        #empty list for node type indicates we are not using node types, all lines are generated from explicit positions (note this selection can be made independently for starting and ending nodes)
        self.lines_start_x_coord,self.lines_start_y_coord,self.lines_start_node_type,self.lines_start_node_index = self.extract_position_nodes_for_lines(self,lines_start_node_type,lines_start_node_index,line_coords_prefer,lines_start_x_coord,lines_start_y_coord) #assign nodes and positions for start of line
        self.lines_end_x_coord,self.lines_end_y_coord,self.lines_end_node_type,self.lines_end_node_index = self.extract_position_nodes_for_lines(self,lines_end_node_type,lines_end_node_index,line_coords_prefer,lines_end_x_coord,lines_end_y_coord) #assign nodes and positions for end of line

    #extract the position and nodes of lines
    def extract_position_nodes_for_lines(self,node_type,node_index,line_coords_prefer,lines_x_coord,lines_y_coord):
        if len(node_type)==0 and len(lines_x_coord)>0: #we are not using nodes for any positions     
            list_x_coord = lines_x_coord #we use this as is in this mode
            list_y_coord = lines_y_coord
            list_node_type = ['none']*self.num_lines #we are not using node for position
            list_node_index = [-1]*self.num_lines #placeholder for node index
        else:
            list_x_coord = [] #we must assign to this from each node in this mode
            list_y_coord = []
            list_node_index = node_index #we can use this as is
            list_node_type = node_type
            if len(node_type)>0 and len(lines_x_coord)==0: #we are not using explicit positions, only nodes provided
                for i in range(self.num_lines): #go through all the lines
                    new_x,new_y = self.extract_node_position(node_type[i],node_index[i]) #extract the x and y position of the requested node
                    list_x_coord.append(new_x) #and append these positions to the list of positions
                    list_y_coord.append(new_y)
            elif len(node_type)>0 and len(lines_x_coord)==0: #we have access to both nodes and positions (though potentially not all might be nodes)
                for i in range(self.num_lines): #go through all the lines
                    if node_type[i]=='none':
                        #we don't have a node, so use provided coordinates
                        list_x_coord.append(lines_x_coord[i])
                        list_y_coord.append(lines_y_coord[i])
                    else: #if we do have a node
                        #check if we have a non-blank position
                        if lines_x_coord=='none': #if there is no coordinate for this position
                            #we must use the node
                            new_x,new_y = self.extract_node_position(node_type[i],node_index[i]) #extract the x and y position of the requested node
                            list_x_coord.append(new_x)
                            list_y_coord.append(new_y)
                        else: #if we have both a coordinate and a node
                            if line_coords_prefer==True: #we will use the coordinates if possible
                                list_x_coord.append(lines_x_coord[i])
                                list_y_coord.append(lines_y_coord[i])
                            elif line_coords_prefer==False: #we will use nodes if possible
                                new_x,new_y = self.extract_node_position(node_type[i],node_index[i]) #extract the x and y position of the requested node
                                list_x_coord.append(new_x)
                                list_y_coord.append(new_y)

            else:
                message = "You must either define the nodes to make up the lines or the coordinates for the lines themsleves \n returning blank data as default"
                self.warning_print(message)
                list_x_coord = []
                list_y_coord = []
                list_node_index = []
                list_node_type = []

        #return the position and linked nodes of the lines
        return list_x_coord,list_y_coord,list_node_type,list_node_index

    #extract x/y global position from a created node
    def extract_node_position(self,node_type,node_index):
        if node_type=='node':
            x = self.nodes_x_coords[node_index]
            y = self.nodes_y_coords[node_index]
        elif node_type=='pie_node':
            x = self.pie_nodes_x_coords[node_index]
            y = self.pie_nodes_y_coords[node_index]
        else:
            message = "Node Type : " + node_type + " Not a supported node type for position extraction, valid types are 'node' and 'pie_node' \n Returning default position of 0/0"  
            self.warning_print(message)
            x = 0
            y = 0
        return x,y

    #find and return the most extreme coordinates found in the list of lines
    def get_extreme_lines(self):
        #get the extremes for the starting points
        extreme_north_start = max(self.lines_start_y_coord) #northernmost node has largest y coordinate
        extreme_south_start = min(self.lines_start_y_coord) #southernmost node has smallest y coordinate
        extreme_east_start = min(self.lines_start_x_coord) #easternmost point has smallest x coordinate
        extreme_west_start = max(self.lines_start_x_coord) #westernmost point has largest x coordinate
        #get the extremes for the ending points
        extreme_north_end = max(self.lines_end_y_coord) #northernmost node has largest y coordinate
        extreme_south_end = min(self.lines_end_y_coord) #southernmost node has smallest y coordinate
        extreme_east_end = min(self.lines_end_x_coord) #easternmost point has smallest x coordinate
        extreme_west_end = max(self.lines_end_x_coord) #westernmost point has largest x coordinate
        #the most extreme for each category is the extreme point
        extreme_north = max(extreme_north_start,extreme_north_end)
        extreme_south = min(extreme_south_end,extreme_south_start)
        extreme_east = min(extreme_east_end,extreme_east_start)
        extreme_west = max(extreme_west_end,extreme_west_start)
        return extreme_north,extreme_south,extreme_east,extreme_west

    #calculate line positions in unzoomed pixel coordinates
    #currently supports nodes and pie nodes
    def calculate_line_pixel_coordinates(self):      
        for i in range(self.num_lines): #go through each line
            line_start_x,line_start_y = self.convert_coords_to_pixels(self.lines_start_x_coord[i],self.lines_start_y_coord[i])  #calculate the position in unzoomed pixel coordinates of line start
            line_end_x,line_end_y = self.convert_coords_to_pixels(self.lines_end_x_coord[i],self.lines_end_y_coord[i])  #calculate the position in unzoomed pixel coordinates of line end
            #append this info to the existing coordinate lists
            self.lines_start_x.append(line_start_x)
            self.lines_start_y.append(line_start_y)
            self.lines_end_x.append(line_end_x)
            self.lines_end_y.append(line_end_y)      
        #create a copy of these positions to store positions before zoom is applied
        self.lines_start_x_original = self.lines_start_x
        self.lines_start_y_original = self.lines_start_y
        self.lines_end_x_original = self.lines_end_x
        self.lines_end_y_original = self.lines_end_y

    #private tools for operating on compound lines

    #find and return the most extreme coordinates found in the list of compound lines
    #create containers to store compound lines
    def init_compound_lines(self):
        self.num_compound_lines = 0 #number of compound lines stored
        #arrays of compound line properties
        #relating to nodes
        self.compound_lines_start_node_type = [] #what type of node is at the start of the line (valid are 'none','node' and 'pie')
        self.compound_lines_start_node_index = [] #index of the starting node, if it exists
        self.compound_lines_start_node_type = [] #what type of node is at the end of the line (valid are 'none','node' and 'pie')
        self.compound_lines_start_node_index= [] #index of the ending node, if it exists
        #global coordinate arrays, list of list of line points from start to finsh
        self.compound_line_points_x_coords = [] #horizontal position of points that make up the line in global coordinates
        self.compound_line_points_y_coords = [] #vertical position of points that make up the line in global coordinates
        #pixel coordinate arrays
        self.compound_line_points_x = [] #horizontal position of points that make up the line in pixel coordinates
        self.compound_line_points_y = [] #vertical position of points that make up the line in pixel coordinates
        self.compound_lines_midpoint_x = [] #horizontal midpoint in pixel coordinates of the line, used for text display
        self.compound_lines_midpoint_y = [] #vertical midpoint in pixel coordinates of the line, used for text display
        #copy of pixel coordinate arrays before zoom has been applied
        self.compound_line_points_x_original = []
        self.compound_line_points_y_original = []
        self.compound_lines_midpoint_x_original = [] 
        self.compound_lines_midpoint_y_original = []
        #other line properties
        self.compound_lines_width = [] #width of the compound lines, pixels
        self.compound_lines_colour = [] #colour of the compound line
        self.lines_canvas_ids = [] #id of the line components, so we can delete it later
        #flags
        self.compound_lines_assigned_flag = False #have lines been stored yet


    def get_extreme_compound_lines(self):
        pass #placeholder

    #calculate compound line positions in unzoomed pixel coordinates
    def calculate_compound_line_pixel_coordinates(self):
        pass #placeholder

    #private tools for operating on pie nodes

    #find and return the most extreme coordinates found in the list of pie nodes
    def get_extreme_pie_nodes(self):
        pass #placeholder

    #calculate pie node positions in unzoomed pixel coordinates
    def calculate_pie_nodes_pixel_coordinates(self):
        pass #placeholder

    #tools to control overall movement of the map

    #zoom the map in/out
    def zoom_map(self,event):
        mouse_x = event.x #mouse x position
        mouse_y = event.y #mouse y position
        zoom_delta = self.zoom_gain*event.delta
        self.current_zoom = self.current_zoom*(1+zoom_delta) #update the accumulated zoom level
        self.current_zoom_offset_x = self.current_zoom_offset_x*(1+zoom_delta) - mouse_x*zoom_delta#calculate the new offset for x
        self.current_zoom_offset_y = self.current_zoom_offset_y*(1+zoom_delta) - mouse_y*zoom_delta#calculate the new offset for y
        self.apply_correct_zoom(zoom_delta,mouse_x,mouse_y) #perform the zoom on all objects in the map
        

    #recreate existing objects in the correctly zoomed positions
    def apply_correct_zoom(self,zoom_delta,mouse_x,mouse_y):
        pass

    #start dragging the map
    def drag_start(self,event):
        self.map.scan_mark(event.x,event.y) #record the position at the start of the movement

    #stop dragging the map
    def drag_end(self,event):
        self.map.scan_dragto(event.x,event.y,gain=self.scroll_gain) #move the "camera" in accordance with the users drag





    