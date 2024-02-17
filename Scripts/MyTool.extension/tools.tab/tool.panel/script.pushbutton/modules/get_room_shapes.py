#IronPython

def get_room_shapes(rooms, outside_boundary_only=True):
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
        room_data["Number"] = room.LookupParameter("Number").AsValueString()
        room_data["Level"] = room.LookupParameter("Level").AsValueString()        
        try:
            room_data["Text"] = room.LookupParameter("Text").AsValueString() if room.LookupParameter("Text").AsValueString() != None else ""
        except:
            room_data["Text"] = ""
        boundary_segments = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
        for segment in boundary_segments[0]:
            line = segment.GetCurve()
            s_point_x = line.GetEndPoint(0).Multiply(304.8).X
            s_point_y = line.GetEndPoint(0).Multiply(304.8).Y
            e_point_x = line.GetEndPoint(1).Multiply(304.8).X
            e_point_y = line.GetEndPoint(1).Multiply(304.8).Y
            # if [s_point_x, s_point_y] not in boundary_locations:
            #     boundary_locations.append([s_point_x, s_point_y])
            # if [e_point_x, e_point_y] not in boundary_locations:
            #     boundary_locations.append([e_point_x, e_point_y])
            boundary_locations.append([s_point_x, s_point_y])
            boundary_locations.append([e_point_x, e_point_y])
        boundary_locations.append(boundary_locations[0])
        room_data["geometry"] = boundary_locations
        output[str(room.Id.IntegerValue)] = room_data
    return output