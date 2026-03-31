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
app = uiapp.Application
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

#TODO
#add mm or imperial toggle and add multiplier for that
#add include linked models or not check - but for linked models user cannot chose the levels for the rooms
#re-organize to handle if only linked rooms (chosing parameters if no rooms in model, and all rooms are from linked rooms)
#possibly move linked rooms as an external module?

def transform_coord(coord, transform_object):
    transformed_xyz = transform_object.OfPoint(DB.XYZ(coord[0],coord[1],0.0))
    return [transformed_xyz.X,transformed_xyz.Y]

def scale_transform_origin(transform, factor=304.8):
    """
    Adjusts the Transform by scaling only its Origin (translation component).
    The BasisX, BasisY, and BasisZ remain unchanged to preserve rotation.
    """
    scaled_origin = DB.XYZ(transform.Origin.X * factor, 
                            transform.Origin.Y * factor, 
                            transform.Origin.Z * factor)

    # Create a new transform with the same rotation but scaled translation
    scaled_transform = DB.Transform.Identity
    scaled_transform.BasisX = transform.BasisX  # Keep rotation as is
    scaled_transform.BasisY = transform.BasisY
    scaled_transform.BasisZ = transform.BasisZ
    scaled_transform.Origin = scaled_origin  # Only scale translation

    return scaled_transform

def get_element_id(app,element):
    if app.VersionNumber >= 2026:
        return element.Id
    return element.Id.IntegerValue

    
if __name__ == "__main__":
    #Directory to C python script
    cur_dir = sys.path[0]
    pathToScript = cur_dir+"\\scriptCPython.py"

    #Default export folder name
    date = datetime.date.today()
    folder_name = '{}_{}'.format(doc.Title,date)

    #Default parameters selected
    parameters_selected = ["Number","Name","Level","Area","Perimeter"]
    def_params = parameters_selected[::]
    room_doc_dict = {}

    #Button class for buttons used in flex form
    class ButtonClass(Window):
        @staticmethod
        def params_clicked(sender, e):
            form.Hide()
            global parameters_selected
            try:
                parameters_selected = pick_parameters.pick_parameters(doc,def_params)
            except:
                try:
                    first_link = list(DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance))[0].GetLinkDocument()
                    parameters_selected = pick_parameters.pick_parameters(first_link,def_params)
                except:
                    Alert("Nothing exported. Close to exit.",header="No rooms present in document",title="Task Terminated", exit=True)

            form.show()

    #Select script options window        
    room_selection_options = ["All","By Level","By Selection"] #created to facilitate combo box name and value consistency
    components = [
              Label('Room Selection Method:'),
              ComboBox('user_room_selection', {opt:opt for opt in room_selection_options}, default=room_selection_options[0]),
              Label('Type of Export:'),
              ComboBox('user_file_export', {"topojson, geojson, excel" : "all", 'topojson': "topo", "geojson" : "geo", "excel" :"xls" }, default="topojson, geojson, excel" ),
              CheckBox('user_inner_boundary', 'Ignore inner boundaries', default = False),
              CheckBox('user_revit_links', 'Include Revit link instances', default = True),
              CheckBox('include_doc_name', 'Include file name', default = False),
              Label('Customize parameters'),
              Label('(default: {}):'.format(", ".join(def_params))),
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
        
    folder_name = user_input["user_file_name"]
    doc_name_included = user_input["include_doc_name"]
    links_included = user_input["user_revit_links"]
    room_select_by = user_input['user_room_selection']

    ##Select rooms from revit instance
    all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
    all_rooms_placed = [room for room in all_rooms if room.Area != 0]

    
    rooms = room_selection(doc, uidoc, room_select_by, all_rooms_placed)
    if doc_name_included: #add room with room doc name to dictionary for rooms in doc
        parameters_selected.append("Revit Model")
        for room in rooms:
            room_doc_dict[room] = doc.Title


    all_linked_rooms = {}
    if links_included:
        for link in DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance):
            link_doc = link.GetLinkDocument()
            if link_doc:  # Ensure the linked document is loaded
                transform = scale_transform_origin(link.GetTotalTransform())

                linked_rooms = list(DB.FilteredElementCollector(link_doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType())
                for room in linked_rooms:
                    if room.Area != 0:                       
                        all_linked_rooms[str(get_element_id(app,room))] = transform
                        rooms.append(room)
                        if doc_name_included:
                            room_doc_dict[room] = link_doc.Title #add room with room doc name to dictionary for rooms in linked doc

    if rooms == []:
        Alert("Nothing exported. Close to exit.",header="Empty Selection",title="Task Terminated", exit = True)     


    #Select output location
    user_dir = forms.pick_folder(title=None, owner=None)
    if user_dir == None: #cancel script on cancel
        GUI.task_terminated()
    
    root_dir = user_dir +"\\"
    
    with forms.ProgressBar(title='Loading...', indeterminate=True): #show progress bar
        #Get Room data from revit
        if doc_name_included:
            output_rooms = get_room_shapes.get_room_shapes(rooms, parameters_selected,user_input['user_inner_boundary'],room_doc_dict)
        else:
            output_rooms = get_room_shapes.get_room_shapes(rooms, parameters_selected,user_input['user_inner_boundary'])

        #need to transform the geometries of the linked rooms to correspond to the host orientation vs the link orientation
        for room in output_rooms:
            if room in all_linked_rooms:
                geometry = output_rooms[room]['geometry']
                transform = all_linked_rooms[room]

                # Iterate over the outer list (each polygon)
                for i in range(len(geometry)):
                    # Iterate over each coordinate pair inside the polygon
                    for j in range(len(geometry[i])):
                        # Update coordinate in place
                        geometry[i][j] = transform_coord(geometry[i][j], transform)


        #Send data to C python file
        output_dict = {"room_data": output_rooms, 'parameters': parameters_selected, "export_dir" : root_dir+folder_name+"\\" ,"export_format" : user_input['user_file_export']}
        send_dict.send_dict(output_dict, pathToScript)

    GUI.task_complete("EXPORT FOLDER LOCATION: \n{}".format(GUI.text_wrap(root_dir+folder_name+"\\")),header="DATA EXPORTED :)") 
    


