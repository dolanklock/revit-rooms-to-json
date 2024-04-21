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
from pyrevit.forms import ProgressBar
from rpw.ui.forms import Alert, FlexForm, Label, ComboBox, TextBox,Separator, Button, CheckBox
from rpw.ui.forms.resources import *

import sys
import datetime
from modules import get_room_shapes
from modules import pick_parameters
from modules import send_dict
from modules import GUI
from modules.room_selection import room_selection

__author__ = "Anna Milczarek, Dolan Klock"


if __name__ == "__main__":
    #Directory to C python script
    cur_dir = sys.path[0]
    pathToScript = cur_dir+"\\scriptCPython.py"

    #Default export folder name
    date = datetime.date.today()
    folder_name = '{}_{}'.format(doc.Title,date)

    #Default parameters selected
    parameters_selected = ["Number","Level"]
    def_params = parameters_selected[::]

    #Button class for buttons used in flex form
    class ButtonClass(Window):
        @staticmethod
        def params_clicked(sender, e):
            form.Hide()
            global parameters_selected 
            parameters_selected = pick_parameters.pick_parameters(def_params)
            form.show()

    #Select script options window        
    room_selection_options = ["All","By Level","By Selection"] #created to facilitate combo box name and value consistency
    components = [
              Label('Room Selection Method:'),
              ComboBox('user_room_selection', {opt:opt for opt in room_selection_options}, default=room_selection_options[0]),
              Label('Type of Export:'),
              ComboBox('user_file_export', {"geojson & topojson" : "both", 'topojson': "topo", "geojson" : "geo" }, default="geojson & topojson" ),
              CheckBox('user_inner_boundary', 'Ignore inner boundaries', default = False),
              Label('Customize parameters (default: {}):'.format(", ".join(def_params))),
              Button('Add Additional Parameters', on_click= ButtonClass.params_clicked),
              Separator(),
              Label('Default Folder Name:' ),
              TextBox('user_file_name', Text=folder_name),
              Button('Next')
              ]
    
    form = FlexForm('Settings', components) 
    form.show()


    #Get user input
    user_input = form.values
    
    if user_input == {}:
        GUI.task_terminated()
    user_input["parameters"] = parameters_selected

    ##Select rooms from revit instance
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
    all_rooms_placed = [room for room in all_rooms if room.Area != 0]

    room_select_by = user_input['user_room_selection']
    rooms = room_selection(doc, uidoc, room_select_by, all_rooms_placed)

    if rooms == []:
        Alert("Nothing exported. Close to exit.",header="Empty Selection",title="Task Terminated", exit = True)     

    #Select output location
    user_dir = forms.pick_folder(title=None, owner=None)
    if user_dir == None: #cancel script on cancel
        GUI.task_terminated()

    root_dir = user_dir +"\\"
    
    with forms.ProgressBar(title='Loading...', indeterminate=True): #show progress bar
        #Get Room data from revit
        output_rooms = get_room_shapes.get_room_shapes(rooms, parameters_selected,user_input['user_inner_boundary'])
        
        #Send data to C python file
        output_dict = {"room_data": output_rooms, 'parameters': parameters_selected, "export_dir" : root_dir+folder_name+"\\" ,"export_format" : user_input['user_file_export']}
        send_dict.send_dict(output_dict, pathToScript)

    GUI.task_complete("EXPORT FOLDER LOCATION: \n{}".format(GUI.text_wrap(root_dir+folder_name+"\\")),header="DATA EXPORTED :)") 
    


