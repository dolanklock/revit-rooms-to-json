import math

# This function gets just one pair of coordinates based on the angle theta
def get_circle_coord(theta, x_center, y_center, radius):
    x = radius * math.cos(theta) + x_center
    y = radius * math.sin(theta) + y_center
    return [x,y]

# This function gets all the pairs of coordinates
def get_all_circle_coords(x_center, y_center, radius, n_points):
    tau = 6.283185
    thetas = [i/float(n_points) * tau for i in range(n_points)]
    circle_coords = [get_circle_coord(theta, x_center, y_center, radius) for theta in thetas]
    return circle_coords+[circle_coords[0]]

#CHECKS IF REVIT SHAPE IS A CIRCLE, IF SO RETURNS A POLYGON READABLE BY GEOJSON
def circle_check(shape ,curr_boundary_outer= False):
    
    # return shape
    if len(shape) != 3:
        return shape
    
    edge_1 = shape[0][0]
    edge_2 = shape[1][0]
    rad = (edge_2 - edge_1)/2
    center_x = edge_1 + rad
    center_y = shape[0][1]

    #If outer boundary, need to reverse order of coordinates
    if curr_boundary_outer:
        return get_all_circle_coords(center_x, center_y,abs(rad),32)[::-1]
    return get_all_circle_coords(center_x, center_y,abs(rad),32)

        
    


