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

from pyrevit import forms
import json
import sys
from modules import Selection
from modules import GUI
from modules import get_room_shapes
from modules import pick_parameters
from modules import send_dict
from modules import GetSetParameters


__author__ = "Anna Milczarek, Dolan Klock"


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
        chosen_levels = GUI.user_prompt_get_object_from_names(all_levels, all_level_names, title="Choose level to get views at", multiselect=True)
        rooms = [room for room in all_rooms_placed if room.LookupParameter('Level').AsValueString() in [l.Name for l in chosen_levels]]
        # chosen_views = Selection.get_views_by_level(chosen_levels.get_Parameter(DB.BuiltInParameter.DATUM_TEXT).AsValueString(), plan_views=True)
    elif room_selection == '3':
        # selectionFilter = SelectionFilters.
        # selectionFilter = SelectionFilters.CustomISelectionFilter("Rooms").AllowElement()
        # rooms = Autodesk.Revit.UI.Selection.Selection.PickObjects(Autodesk.Revit.UI.Selection.ObjectType.Element,
        #                                                            SelectionFilters.ISelectionFilter('Rooms'))
        # rooms = uidoc.Selection.PickElementsByRectangle(selectionFilter, "Select Rooms")
        rooms = [doc.GetElement(ref_id.ElementId) for ref_id in uidoc.Selection.PickObjects(Autodesk.Revit.UI.Selection.ObjectType.Element, "Select Rooms")]
    else:
        sys.exit()

    
    room_boundary_opt = GUI.UI_two_options(title="Room Boundary Options", 
                                           main_instruction="Export outer boundaries only?", 
                                           commandlink1="Yes, outer boundaries only", 
                                           commandlink2="No, include inner boundaries")
    properties = pick_parameters.pick_parameters()

    output_rooms = get_room_shapes.get_room_shapes(rooms,properties,room_boundary_opt)
    
    root_dir = forms.pick_folder(title=None, owner=None) +"\\"
    
    print("loading...")

    output_dict = {"room_data": output_rooms, 'parameters': properties, "export_dir" : root_dir}
    send_dict.send_dict(output_dict, pathToScript)
    print("EXPORT AT: "+ root_dir)
    


#TODO: test

#TODO: getting windows error when getting all rooms at level, figure out work around. Try
    #  putting code in try except block and if fails then shop list in half and save the other half and send the other half again to cpython

#TODO: get name of revit file and include it in export name
