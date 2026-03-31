#IronPython
#Get room data from revit
#DOES NOT handle eliptical shapes (splines)

import clr

clr.AddReferenceByPartialName('PresentationCore')
clr.AddReferenceByPartialName('AdWindows')
clr.AddReferenceByPartialName("PresentationFramework")
clr.AddReferenceByPartialName('System')
clr.AddReferenceByPartialName('System.Windows.Forms')


import Autodesk
import Autodesk.Windows as aw
from Autodesk.Revit import DB
from Autodesk.Revit import UI

uiapp = __revit__
uidoc = uiapp.ActiveUIDocument
doc = uiapp.ActiveUIDocument.Document

import GetSetParameters
import arc_segment_conversion

def get_start_end_point(segment):    
    line = segment.GetCurve()
    s_point_x = line.GetEndPoint(0).Multiply(304.8).X
    s_point_y = line.GetEndPoint(0).Multiply(304.8).Y
    e_point_x = line.GetEndPoint(1).Multiply(304.8).X
    e_point_y = line.GetEndPoint(1).Multiply(304.8).Y
    return (s_point_x, s_point_y, e_point_x, e_point_y)

def generate_endpoints(segment,is_outer):
    #if segment is an arc, convert the arc and return a list of endpoint coordinates representing the arc
    if segment.GetCurve().GetType() == Autodesk.Revit.DB.Arc:     
        endpoints = arc_segment_conversion.arc_segment_conversion(segment,full_circle=False,is_outer_boundary = is_outer)     
        return endpoints
    
    #if segment is a straight line return a list containing one endpoint
    endpoints = [list(get_start_end_point(segment)[-2:])]
    return endpoints

def get_room_shapes(rooms, parameters, outside_boundary_only=True):
    """_summary_

    Args:
        rooms (_type_): _description_
        outside_boundary_only (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    output = {}
    for room in rooms:
        room_data = {}
        boundary_locations = []
        outer_boundary = True #boolean required for coordinate order of arc segment conversion

        #Get room parameters from revit
        for param in parameters:
            try:
                if GetSetParameters.get_parameter_type(room.LookupParameter(param)) == "Double":
                    room_data[param] = str(room.LookupParameter(param).AsDouble()) if room.LookupParameter(param).AsDouble() != None else ""
                else:
                    room_data[param] = room.LookupParameter(param).AsValueString() if room.LookupParameter(param).AsValueString() != None else ""
            except:
                room_data[param] = ""

        #Get room shapes from revit
        boundary_segments = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())

        #convert room shapes from revit to sets of polygons formed from coordinates
        for boundary_segment in boundary_segments:

            #if the boundary segment is a full circle, convert to a loop of coordinates representing the circle
            if boundary_segment[0].GetCurve().GetType() == Autodesk.Revit.DB.Arc:            
                closed_loop = arc_segment_conversion.arc_segment_conversion(boundary_segment[0])

            #if the boundary segment is not a circle generate coordinates
            else:  
                #get_start_end_point returns a tuple of length 4, the first two correspond to x,y of starting point, the last two correspond to x,y of ending point    
                starting_point = list(get_start_end_point(boundary_segment[0])[:2]) #get x,y of starting point of line at first boundary segment
                closed_loop = [starting_point] + [endpoints for segment in boundary_segment for endpoints in generate_endpoints(segment,outer_boundary)] #get x,y coord of ending point of line of remaining segments
            
            #order of coordinates must be reversed, Revit provides coordinates in the opposite order needed for a proper geojson/topojson file
            boundary_locations.append(closed_loop[::-1])

            #if outside boundary only, stop after first element of boundary_segments array
            if outside_boundary_only:
                outer_boundary = False #required for arc segment conversions for order of coordinates
                break            

        # print(boundary_locations)
        room_data["geometry"] = boundary_locations
        output[str(room.Id.IntegerValue)] = room_data

    return output
