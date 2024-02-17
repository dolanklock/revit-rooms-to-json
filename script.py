import clr
clr.AddReferenceByPartialName('PresentationCore')
clr.AddReferenceByPartialName('AdWindows')
clr.AddReferenceByPartialName("PresentationFramework")
clr.AddReferenceByPartialName('System')
clr.AddReferenceByPartialName('System.Windows.Forms')

from Autodesk.Revit import DB
from Autodesk.Revit import UI
import Autodesk
import Autodesk.Windows as aw

uiapp = __revit__
uidoc = uiapp.ActiveUIDocument
doc = uiapp.ActiveUIDocument.Document

from pyrevit import forms
from System.Collections.Generic import List

import subprocess
import json
import sys
# sys.path.append('M:\\600 VWCC\\ARCHITECTURAL\\BIM\\pykTools\\pyKTools\\MyTool.extension\\lib')
sys.path.append('Y:\\pyKTools\\2024-02-17\\pyKTools\\MyTool.extension\\lib')
import Selection
import GUI
import SelectionFilters


__author__ = "Anna Milczarek, Dolan Klock"


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


def send_dict(sent_dict, pathToScript):
    """_summary_

    Args:
        sent_dict (_type_): _description_
        pathToScript (_type_): _description_
    """
    message = json.dumps(sent_dict)
    cmd = ['python', pathToScript, message]

    # Create the subprocess startup info object This prevents the black terminal window from popping up when running hte subprocess
    startup_info = subprocess.STARTUPINFO()
    startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # Run the command and capture the output
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startup_info)


def pick_parameters(picked_params=["Number","Level"]):
    """pick parameters function - accepts array of default parameters 

    Args:
        picked_params (list, optional): _description_. Defaults to ["Number","Level"].
    """
    Label = DB.LabelUtils
    #Get rooms
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()

    #Take first room from list of rooms as an example room
    example_room = [room for room in all_rooms][0]

    #Create dictionary of parameters, grouped by their group (e,g Group1:[par1,par20], Group2:[par3])
    parameters = {Label.GetLabelForGroup(param.Definition.GetGroupTypeId()):
                [
                p.Definition.Name for p in example_room.Parameters
                if Label.GetLabelForGroup(p.Definition.GetGroupTypeId()) == Label.GetLabelForGroup(param.Definition.GetGroupTypeId())
                and p.Definition.Name not in picked_params]
                for param in example_room.Parameters}

    #Sort param dictionary, param arrays and remove duplicate params
    for group in sorted(parameters):
            parameters[group].sort()
            temp = set(parameters[group])
            parameters[group] = temp

    # for g in parameters:
    #     print(g)
    #     for p in parameters[g]:
    #         print("---->"+p)
    #     print("___")

    #Create and add an ALL group of parameters that is formated as ALL: ["group: paramter1", "group: paramter2",etc],
    all_parameters_group = [key+": "+value for key, array in parameters.items() for value in array]
    all_parameters_group.sort()
    parameters["ALL"]=all_parameters_group

    #Pick parameters form
    result = forms.SelectFromList.show(parameters,
        "Pick Additional Parameters",
        width = 300,
        height = 400,
        button_name='Next', 
        multiselect = True,
        group_selector_title='Parameter Groups',
        )

    if result != None:
        #remove the group (remove everything before ": ") from each result picked from ALL category
        result = [res.split(": ",1)[1] if ": " in res else res for res in result]
        picked_params.extend(result)
    
    return(picked_params)


if __name__ == "__main__":
    #Change directory to script folder
    cur_dir = sys.path[0]
    pathToScript = cur_dir+"\\scriptCPython.py"
    
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
    all_rooms_placed = [room for room in all_rooms if room.Area != 0]
    room_selection = GUI.UI_three_options(title="Room Selection",
                                                main_instruction="Choose how you want to select rooms by",
                                                commandlink1="All",
                                                commandlink2="By Level",
                                                commandlink3="By Selection")
    if room_selection == '1':
        rooms = Selection.GetElementsFromDoc.all_rooms(doc, is_placed_only=True)
    elif room_selection == '2':
        all_levels = [l for l in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType()]
        all_level_names = [l.get_Parameter(DB.BuiltInParameter.DATUM_TEXT).AsValueString() for l in all_levels]
        chosen_level = GUI.user_prompt_get_object_from_names(all_levels, all_level_names, title="Choose level to get views at", multiselect=False)
        rooms = [room for room in all_rooms_placed if room.LookupParameter('Level').AsValueString() == chosen_level.Name]
        # chosen_views = Selection.get_views_by_level(chosen_level.get_Parameter(DB.BuiltInParameter.DATUM_TEXT).AsValueString(), plan_views=True)
    elif room_selection == '3':
        # selectionFilter = SelectionFilters.
        # selectionFilter = SelectionFilters.CustomISelectionFilter("Rooms").AllowElement()
        # rooms = Autodesk.Revit.UI.Selection.Selection.PickObjects(Autodesk.Revit.UI.Selection.ObjectType.Element,
        #                                                            SelectionFilters.ISelectionFilter('Rooms'))
        # rooms = uidoc.Selection.PickElementsByRectangle(selectionFilter, "Select Rooms")
        rooms = [doc.GetElement(ref_id.ElementId) for ref_id in uidoc.Selection.PickObjects(Autodesk.Revit.UI.Selection.ObjectType.Element, "Select Rooms")]
    else:
        sys.exit()

    output_rooms = get_room_shapes(rooms, outside_boundary_only=True)
    print(output_rooms)
    
    # output_dict = {"data": {"test": 'testing'}}
    output_dict = {"data": output_rooms, 'properties': pick_parameters()}
    send_dict(output_dict, pathToScript)



#TODO: test
#TODO: pick parameters function pass in object to cpython

#TODO: getting windows error when getting all rooms at level, figure out work around. Try
    #  putting code in try except block and if fails then shop list in half and save the other half and send the other half again to
    # cpython

#TODO: allow selection of multiple levles
    
#TODO: prompt user to choose rooms with columns cut out or ignore columns (need
    #  to figure out "get_room_shapes" above function. currently it ignores int column outline and
    #  only gets the outside room boundary. I had it where it got both, need to tweak code to achieve that)

# outside boundary counter clockwise and inner clockwise