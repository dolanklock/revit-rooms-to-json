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
from rpw.ui.forms import FlexForm, select_folder, Label, ComboBox, TextBox, TextBox,Separator, Button, CheckBox
from rpw.ui.forms.resources import *


import json
import sys
import datetime
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

    #Default export folder name
    date = datetime.date.today()
    folder_name = '{}_{}'.format(doc.Title,date)

    #Default parameters selected
    parameters_selected=["Number","Level"]
    def_params = parameters_selected[::]

    #Button class for buttons used in flex form
    class ButtonClass(Window):
        @staticmethod
        def params_clicked(sender, e):
            global parameters_selected 
            parameters_selected = pick_parameters.pick_parameters(def_params)

    #Select script options window        
    room_selection_options = ["All","By Level","By Selection"] #created to facilitate combo box name and value consistency
    components = [
              Label('Room Selection Method:'),
              ComboBox('user_room_selection', {opt:opt for opt in room_selection_options}, default=room_selection_options[0]),
              Label('Type of Export:'),
              ComboBox('user_file_export', {"geojson & topojson" : "both", 'topojson': "topo", "geojson" : "geo" }, default="geojson & topojson" ),
              CheckBox('user_inner_boundary', 'Ignore inner boundaries', default = False),
              Label('Customize parameters (default: {}):'.format(", ".join(def_params))),
              Button('Add Other Parameters', on_click= ButtonClass.params_clicked),
              Separator(),
              Label('Default Folder Name:' ),
              TextBox('user_file_name', Text=folder_name),
              Button('Export')
              ]
    
    form = FlexForm('Set options', components) 
    form.show()

    #Get user input
    user_input = form.values
    user_input["parameters"] = parameters_selected

    ##Select rooms from revit instance
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
    all_rooms_placed = [room for room in all_rooms if room.Area != 0]

    room_selection = user_input['user_room_selection']
    if room_selection == 'All':
        rooms = Selection.GetElementsFromDoc.all_rooms(doc, is_placed_only=True)
    elif room_selection == 'By Level':
        all_levels = [l for l in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType()]
        all_level_names = [l.get_Parameter(DB.BuiltInParameter.DATUM_TEXT).AsValueString() for l in all_levels]
        chosen_levels = GUI.user_prompt_get_object_from_names(all_levels, all_level_names, title="Choose level to get views at", multiselect=True)
        rooms = [room for room in all_rooms_placed if room.LookupParameter('Level').AsValueString() in [l.Name for l in chosen_levels]]
        # chosen_views = Selection.get_views_by_level(chosen_levels.get_Parameter(DB.BuiltInParameter.DATUM_TEXT).AsValueString(), plan_views=True)
    elif room_selection == 'By Selection':
        # selectionFilter = SelectionFilters.
        # selectionFilter = SelectionFilters.CustomISelectionFilter("Rooms").AllowElement()
        # rooms = Autodesk.Revit.UI.Selection.Selection.PickObjects(Autodesk.Revit.UI.Selection.ObjectType.Element,
        #                                                            SelectionFilters.ISelectionFilter('Rooms'))
        # rooms = uidoc.Selection.PickElementsByRectangle(selectionFilter, "Select Rooms")
        rooms = [doc.GetElement(ref_id.ElementId) for ref_id in uidoc.Selection.PickObjects(Autodesk.Revit.UI.Selection.ObjectType.Element, "Select Rooms")]
    else:
        sys.exit()
   
    #Select output location
    user_dir = forms.pick_folder(title=None, owner=None)
    if user_dir == None: #cancel script on cancel
        sys.exit()
    root_dir = user_dir +"\\"
    

    print("loading...")

    #Get Room data from revit
    output_rooms = get_room_shapes.get_room_shapes(rooms,parameters_selected,user_input['user_inner_boundary'])
    
    #Send data to C python file
    output_dict = {"room_data": output_rooms, 'parameters': parameters_selected, "export_dir" : root_dir+folder_name+"\\" ,"export_format" : user_input['user_file_export']}
    send_dict.send_dict(output_dict, pathToScript)
    print("EXPORT FOLDER LOCATION: "+ root_dir+folder_name+"\\")
    


#TODO: dialogue front back options

#TODO: getting windows error when getting all rooms at level, figure out work around. Try
    #  putting code in try except block and if fails then shop list in half and save the other half and send the other half again to cpython
