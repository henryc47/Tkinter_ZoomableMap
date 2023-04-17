#zoom_map.py
#A python package to create a zoomable map (like Google Maps) using tkinter

#dependencies
import tkinter as tk


#this class is the zoomable map
class ZoomMap:
    #create the map
    def __init__(self,map_width,map_height,window,background="white",zoom_control="<MouseWheel>",drag_start_control='<ButtonPress-1>',drag_end_control="<B1-Motion>",print_warnings=True,scroll_gain=1):
        self.map_width = map_width #width (horizontal length) of the map display in pixels
        self.map_height = map_height #height (vertical length) of the map display in pixels
        self.map_center_x = int(self.map_width/2) #midpoint of the map in pixels, horizontal
        self.map_center_y = int(self.map_height/2) #midpoint of the map in pixels, vertical
        self.window = window #tk object in which the canvas is drawn
        self.background = background #background object, at the moment only supports tk colours
        self.print_warnings = print_warnings #do we print warning and error messages
        self.scroll_gain = scroll_gain #how fast is panning and zooming
        #create the canvas object
        self.map = tk.Canvas(self.window,bg=self.background,width=self.map_width,height=self.map_height)
        #bind the canvas to the controls to zoom and drag the image
        #try blocks catch invalid keybindings and replace them with the defaults
        #bind zoom and drag
        try:
            self.canvas.bind(zoom_control,self.zoom_map)
        except:
            if self.print_warnings:
                print("WARNING : ",zoom_control,' not a valid keybinding for tkinter. Defaulting to  "<MouseWheel>", for zoom keybinding')
            self.canvas.bind("<MouseWheel>",self.zoom_map)
        #bind starting to drag the map
        try:
            self.canvas.bind(drag_start_control,self.drag_start_map)
        except:
            if self.print_warnings:
                print("WARNING : ",drag_start_control,' not a valid keybinding for tkinter. Defaulting to  "<ButtonPress-1>", for drag start keybinding')
            self.canvas.bind("<ButtonPress-1>",self.drag_start_map)
        #bind stopping a drag
        try:
            self.canvas.bind(drag_end_control,self.drag_end_map)
        except:
            if self.print_warnings:
                print("WARNING : ",drag_end_control,' not a valid keybinding for tkinter. Defaulting to  "<B1-Motion>", for drag end keybinding')
            self.canvas.bind("<B1-Motion>",self.drag_end_map)
        
        #create containers for objects to be displayed on the map
        #two types of objects we support at the moment
        self.init_nodes() #containers to store nodes
        self.init_lines() #containers to store lines
        self.init_compound_lines() #containers to store compound lines
        self.init_pie_nodes() #containers to store pie nodes

    #print a warning if warnings enabled
    def warning_print(self,message):
        if self.print_warnings==True:
            print("WARNING: ",message)

    #containers for displayed objects

    #create containers to store nodes
    def init_nodes(self):
        #nodes, these are filled circles created using the tk oval object
        self.num_nodes = 0 #number of nodes stored
        #arrays of node properties
        self.nodes_x_coords = [] #horizontal position in global coordinates of the centre of the node
        self.nodes_y_coords = [] #vertical position in global coordinates of the centre of the node
        self.nodes_x = [] #horizontal position in pixel coordinates of the centre of the node
        self.nodes_y = [] #vertical position in pixel coordinates of the centre of the node
        self.nodes_radii = []  #radius of the node, pixels
        self.nodes_colours = [] #colour of the nodes
        self.nodes_name = [] #name of the each node 
        self.node_canvas_ids = [] #id of the node object within the canvas
        #flags
        self.nodes_assigned_flag = False #have nodes been stored yet

    #create containers to store lines
    def init_lines(self):
        #lines, these are well, lines
        self.num_lines = 0 #number of lines stored
        #arrays of line properties
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
        self.lines_width = [] #width of the line, pixels
        #flags
        self.lines_assigned_flag = False #have lines been stored yet

    #create containers to store compound lines
    def init_compound_lines(self):
        #flags
        self.compound_lines_assigned_flag = False #have lines been stored yet
        self.num_compound_lines = 0 #number of compound lines stored
        #arrays of compound line properties
        #global coordinate arrays

    #create containers to store pie chart nodes
    def init_pie_nodes(self):
        #flags
        self.pie_nodes_assigned_flag = False #have lines been stored yet
        self.num_pie_nodes = 0 #number of pie nodes stored
        

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
        x = -(longitude_offset)*self.pixels_per_unit #multiply by -1 as positive pixels are left, but positive coords are west
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
        units_east_west = extreme_west-extreme_east #how much distance between east and west in global coordinate frame
        start_x = extreme_east + units_east_west*border_fraction_x*0.5#starting x position (west-most) in global coordinates accounting for requested border (half as other half will be on other side)
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
        if self.nodes_assigned_flag==True #if we have assigned nodes
            extreme_north,extreme_south,extreme_east,extreme_west = self.get_extreme_nodes() #get the extreme positions of the nodes
            extremes_defined = True #we have defined extremes which we can compare to
        #compare with 
        if self.lines_assigned_flag==True #if we have assigned lines
            if extremes_defined==True: #and we have already measured extremes, compare the extremes and select the most extreme
                new_extreme_north,new_extreme_south,new_extreme_east,new_extreme_west = self.get_extreme_lines() #get the new extreme positions from the lines
                extreme_north = max(extreme_north,new_extreme_north)
                extreme_south = min(extreme_south,new_extreme_south)
                extreme_east = min(extreme_east,new_extreme_east)
                extreme_west = max(extreme_west,new_extreme_west)
            else: #if extremes not yet found, extremes are the new extremes
                extreme_north,extreme_south,extreme_east,extreme_west = self.get_extreme_lines() #get the extreme positions of the lines
                extremes_defined = True #we have defined extremes which we can compare to
        #compare with compound lines if they exist
        if self.compound_lines_assigned_flag==True #if we have assigned compound lines
            if extremes_defined==True: #and we have already measured extremes, compare the extremes and select the most extreme
                new_extreme_north,new_extreme_south,new_extreme_east,new_extreme_west = self.get_extreme_compound_lines() #get the new extreme positions from the compound lines
                extreme_north = max(extreme_north,new_extreme_north)
                extreme_south = min(extreme_south,new_extreme_south)
                extreme_east = min(extreme_east,new_extreme_east)
                extreme_west = max(extreme_west,new_extreme_west)
            else: #if extremes not yet found, extremes are the new extremes
                extreme_north,extreme_south,extreme_east,extreme_west = self.get_extreme_compound_lines() #get the extreme positions of the compound lines
                extremes_defined = True #we have defined extremes which we can compare to
        #compare with pie nodes if they exist
        if self.compound_lines_assigned_flag==True #if we have assigned compound lines
            if extremes_defined==True: #and we have already measured extremes, compare the extremes and select the most extreme
                new_extreme_north,new_extreme_south,new_extreme_east,new_extreme_west = self.get_extreme_pie_nodes() #get the new extreme positions from the pie_nodes lines
                extreme_north = max(extreme_north,new_extreme_north)
                extreme_south = min(extreme_south,new_extreme_south)
                extreme_east = min(extreme_east,new_extreme_east)
                extreme_west = max(extreme_west,new_extreme_west)
            else: #if extremes not yet found, extremes are the new extremes
                extreme_north,extreme_south,extreme_east,extreme_west = self.get_extreme_pie_nodes() #get the extreme positions of the pie_nodes lines
                extremes_defined = True #we have defined extremes which we can compare to

        #return whether we have found extremes and the extremes (or placeholder if we have not found the extremes)
        return extremes_defined,extreme_north,extreme_south,extreme_east,extreme_west                

    #private tools for operating on nodes

    #create new nodes and replace the existing nodes
    def create_nodes(self,nodes_x_coords,nodes_y_coords,nodes_radii,nodes_colours,nodes_names):
        self.init_nodes() #remove the storage of the existing nodes
        self.num_nodes = len(nodes_x_coords) #get the number of nodes
        self.assign_nodes_positions(nodes_x_coords,nodes_y_coords)  #assign the position of the new nodes
        self.assign_nodes_radii(nodes_radii) #assign the nodes radii
        self.assign_nodes_colours(nodes_colours) #assign the nodes colours
        self.assign_nodes_names(nodes_names) #assign the nodes names
        self.nodes_assigned_flag = True
      

    #assign the nodes new x/y coordinates in the global coordinate frame
    def assign_nodes_positions(self,nodes_x_coords,nodes_y_coords):
        self.nodes_x_coords = nodes_x_coords
        self.nodes_y_coords = nodes_y_coords

    #assign the nodes new radii
    def assign_nodes_radii(self,nodes_radii):
        self.node_radii = nodes_radii

    #assign the nodes new colours
    def assign_nodes_colours(self,nodes_colours):
        self.node_colours = nodes_colours

    #assign the nodes new names
    def assign_nodes_names(self,nodes_names):
        self.nodes_names = nodes_names

    #find and return the most extreme coordinates found in the list of nodes
    def get_extreme_nodes(self):
        extreme_north = max(self.nodes_y_coords) #northernmost node has largest y coordinate
        extreme_south = min(self.nodes_y_coords) #southernmost node has smallest y coordinate
        extreme_east = min(self.nodes_x_coords) #easternmost point has smallest x coordinate
        extreme_west = max(self.nodes_x_coords) #westernmost point has largest x coordinate
        return extreme_north,extreme_south,extreme_east,extreme_west

    #calculate node positions in unzoomed pixel coordinates
    def calculate_node_pixel_coordinates(self):
        for i in range(self.num_nodes): #go through each node
            self.nodes_x[i],self.nodes_y[i] = self.convert_coords_to_pixels(self.nodes_x_coords[i],self.nodes_y_coords[i]) #calculate the position in unzoomed pixel coordinates of each node
        
    #private tools for operating on lines

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
    def calculate_line_pixel_coordinates(self):
        for i in range(self.num_lines): #go through each line
            self.lines_start_x[i],self.lines_start_y[i] = self.convert_coords_to_pixels(self.lines_start_x_coord[i],self.lines_start_y_coord[i])  #calculate the position in unzoomed pixel coordinates of line start
            self.lines_end_x[i],self.lines_end_y[i] = self.convert_coords_to_pixels(self.lines_end_x_coord[i],self.lines_end_y_coord[i])  #calculate the position in unzoomed pixel coordinates of line end

    #private tools for operating on compound lines

    #find and return the most extreme coordinates found in the list of compound lines
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
    def zoom_control(self,event):
        pass #placeholder for now

    #start dragging the map
    def drag_start_control(self,event):
        self.map.scan_mark(event.x,event.y) #record the position at the start of the movement

    #stop dragging the map
    def drag_end_control(self,event):
        self.map.scan_dragto(event.x,event.y,gain=self.scroll_gain) #move the "camera" in accordance with the users drag





    