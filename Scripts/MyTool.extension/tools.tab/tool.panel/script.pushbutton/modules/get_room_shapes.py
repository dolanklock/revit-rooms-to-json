#IronPython

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
        for param in parameters:
            try:
                if GetSetParameters.get_parameter_type(room.LookupParameter(param)) == "Double":
                    room_data[param] = str(room.LookupParameter(param).AsDouble()) if room.LookupParameter(param).AsDouble() != None else ""
                else:
                    room_data[param] = room.LookupParameter(param).AsValueString() if room.LookupParameter(param).AsValueString() != None else ""
            except:
                room_data[param] = ""
        boundary_segments = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
        if outside_boundary_only:
            for segment in boundary_segments[0]:
                s_point_x, s_point_y, e_point_x, e_point_y = get_start_end_point(segment)
                boundary_locations.append([s_point_x, s_point_y])
                boundary_locations.append([e_point_x, e_point_y])
            print('BOUNDARIES OUTER ONLY', boundary_locations)
            room_data["geometry"] = boundary_locations
            output[str(room.Id.IntegerValue)] = room_data
        else:
            for boundary_segment in boundary_segments:
                for segment in boundary_segment:
                    s_point_x, s_point_y, e_point_x, e_point_y = get_start_end_point(segment)
                    boundary_locations.append([s_point_x, s_point_y])
                    boundary_locations.append([e_point_x, e_point_y])
            print('BOUNDARIES ALL', boundary_locations)
            room_data["geometry"] = boundary_locations
            output[str(room.Id.IntegerValue)] = room_data
    return output
