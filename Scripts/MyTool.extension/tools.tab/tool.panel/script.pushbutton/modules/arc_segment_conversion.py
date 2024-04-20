import math

#copied from get_room_shapes - get start and end poitns of a curve
def get_start_end_point(segment):    
    line = segment.GetCurve()
    s_point_x = line.GetEndPoint(0).Multiply(304.8).X
    s_point_y = line.GetEndPoint(0).Multiply(304.8).Y
    e_point_x = line.GetEndPoint(1).Multiply(304.8).X
    e_point_y = line.GetEndPoint(1).Multiply(304.8).Y
    return (s_point_x, s_point_y, e_point_x, e_point_y)

# Generate pair of coordinates based on the angle theta
def get_circle_coord(theta, x_center, y_center, radius):
    x = radius * math.cos(theta) + x_center
    y = radius * math.sin(theta) + y_center
    return [x,y]

# Get Arc length based on start angle, end angle and a radius
def get_arc_length(theta1, theta2, radius):
    return abs(theta2 - theta1) * radius

# Generate all coordinates representing arc
def get_all_circle_coords(segment,n_points = 32,full_circle = True):
    tau = 2*math.pi
    radius = segment.GetCurve().Radius * 304.8
    x_center = segment.GetCurve().Center.Multiply(304.8).X
    y_center = segment.GetCurve().Center.Multiply(304.8).Y         

    #if full circle, generate thetas for circle based on n points
    if full_circle:
        ##THETAS GENERATED HERE ##
        thetas = [i/float(n_points) * tau for i in range(n_points)]
    
    #if not closed circle generate thetas from start and end point based on n points
    else:
        x_start,y_start,x_end,y_end = get_start_end_point(segment)
        arc_length = segment.GetCurve().ApproximateLength * 304.8
        start_theta = math.atan2(y_start - y_center, x_start - x_center)
        end_theta = math.atan2(y_end - y_center, x_end - x_center)
        
        # Calculate lengths of both possible arcs with current endpoints
        # Determine which possible arc is closest to the desired length
        # Swap arc if needed (convex vs concave)
        arc_length_start = get_arc_length(start_theta, end_theta, radius)
        arc_length_end = tau * radius - arc_length_start
        if abs(arc_length_start - arc_length) > abs(arc_length_end - arc_length):
            end_theta += tau
        step_theta = (end_theta - start_theta) / n_points

        ##THETAS GENERATED HERE ##
        thetas = [start_theta + i * step_theta for i in range(n_points + 1)]

    circle_coords = [get_circle_coord(theta, x_center, y_center, radius) for theta in thetas]
    closed_loop_coord = [circle_coords[0]] if full_circle else [] #if full circle need to close the loop by having the same endpoint at start and end of loop
    return circle_coords + closed_loop_coord
    
#CONVERTS ARC TO COORDINATES REPRESENTING SEGMENTS CLOSEST TO THE ARC SHAPE
def arc_segment_conversion(segment,is_outer_boundary=False,full_circle=True): 
    circle_boundary = get_all_circle_coords(segment,full_circle=full_circle)    
    
    if is_outer_boundary:
        return circle_boundary
    #If not the outer boundary, need to reverse order of coordinates to be consistent with the rest of the coordinates from Revit
    return circle_boundary[::-1]
