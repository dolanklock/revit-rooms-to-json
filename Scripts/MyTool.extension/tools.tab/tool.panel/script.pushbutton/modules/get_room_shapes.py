#IronPython
#Get room data from revit

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
import circle_check

def get_start_end_point(segment):
    line = segment.GetCurve()
    s_point_x = line.GetEndPoint(0).Multiply(304.8).X
    s_point_y = line.GetEndPoint(0).Multiply(304.8).Y
    e_point_x = line.GetEndPoint(1).Multiply(304.8).X
    e_point_y = line.GetEndPoint(1).Multiply(304.8).Y
    return (s_point_x, s_point_y, e_point_x, e_point_y)


def get_room_shapes(rooms, parameters, outside_boundary_only=True):
    """_summary_

    Args:
        rooms (_type_): _description_
        outside_boundary_only (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    # all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
    # all_rooms_placed = [room for room in all_rooms if room.Area != 0]
    output = {}
    for room in rooms:
        room_data = {}
        boundary_locations = []
        outer_boundary = True #boolean required for circle check, needs to know if working with outer boundary or not

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
        for boundary_segment in boundary_segments:
            #get_start_end_point returns a tuple of length 4, the first two correspond to x,y of starting point, the last two correspond to x,y of ending point    
            starting_point = list(get_start_end_point(boundary_segment[0])[:2]) #get x,y of starting point of line at first boundary segment
            closed_loop = [starting_point] + [list(get_start_end_point(segment)[-2:]) for segment in boundary_segment] #get x,y coord of ending point of line of remaining boundary
                            
            #order of coordinates must be reversed, revit provides coordinates in the opposite order needed for a proper geojson/topojson file
            boundary_locations.append(circle_check.circle_check(closed_loop[::-1],outer_boundary))

            outer_boundary = False #required for circle check, once the first boundary is created, outer_boundary is false for the rest of the boundaries of the polygon

            #if outside boundary only, stop after first element of boundary_segments array
            if outside_boundary_only:
                break            

        # print(boundary_locations)
        room_data["geometry"] = boundary_locations
        output[str(room.Id.IntegerValue)] = room_data

        # if outside_boundary_only:
        #     for segment in boundary_segments[0]:
        #         s_point_x, s_point_y, e_point_x, e_point_y = get_start_end_point(segment)
        #         boundary_locations.append([s_point_x, s_point_y])
        #         boundary_locations.append([e_point_x, e_point_y])
        #     print('BOUNDARIES OUTER ONLY', boundary_locations)

        #     room_data["geometry"] = boundary_locations
        #     output[str(room.Id.IntegerValue)] = room_data
        # else:
        #     for boundary_segment in boundary_segments:
        #         for segment in boundary_segment:
        #             s_point_x, s_point_y, e_point_x, e_point_y = get_start_end_point(segment)
        #             boundary_locations.append([s_point_x, s_point_y])
        #             boundary_locations.append([e_point_x, e_point_y])

        #     print('BOUNDARIES ALL', boundary_locations)
        #     room_data["geometry"] = boundary_locations
        #     output[str(room.Id.IntegerValue)] = room_data
    return output
