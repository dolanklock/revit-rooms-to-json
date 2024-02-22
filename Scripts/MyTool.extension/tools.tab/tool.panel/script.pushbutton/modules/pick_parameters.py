#IronPython

import Autodesk
from Autodesk.Revit import DB
from pyrevit import forms
from System.Collections.Generic import List
uiapp = __revit__
uidoc = uiapp.ActiveUIDocument
doc = uiapp.ActiveUIDocument.Document

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