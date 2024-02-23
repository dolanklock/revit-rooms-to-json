import Autodesk
from Autodesk.Revit import DB
import sys
import GUI
import Selection
import SelectionFilter

def room_selection(doc, uidoc, select_by, all_rooms_placed):  
    if select_by == 'All':
        rooms = Selection.GetElementsFromDoc.all_rooms(doc, is_placed_only=True)
    elif select_by == 'By Level':
        all_levels = [l for l in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType()]
        all_level_names = [l.get_Parameter(DB.BuiltInParameter.DATUM_TEXT).AsValueString() for l in all_levels]
        chosen_levels = GUI.user_prompt_get_object_from_names(all_levels, all_level_names, title="Choose level to get views at", multiselect=True)
        rooms = [room for room in all_rooms_placed if room.LookupParameter('Level').AsValueString() in [l.Name for l in chosen_levels]]
    elif select_by == 'By Selection':
        # Prompt the user to select room elements
        rooms = [doc.GetElement(ref.ElementId) for ref in uidoc.Selection.PickObjects(Autodesk.Revit.UI.Selection.ObjectType.Element,
                                                                                       SelectionFilter.SelectionFilterRooms(), "Select rooms")]
        # rooms = [doc.GetElement(ref_id.ElementId) for ref_id in uidoc.Selection.PickObjects(Autodesk.Revit.UI.Selection.ObjectType.Element, "Select Rooms")]
    else:
        sys.exit()
    return rooms

# selectionFilter = SelectionFilters.
# selectionFilter = SelectionFilters.CustomISelectionFilter("Rooms").AllowElement()
# rooms = Autodesk.Revit.UI.Selection.Selection.PickObjects(Autodesk.Revit.UI.Selection.ObjectType.Element,
#                                                            SelectionFilters.ISelectionFilter('Rooms'))
# rooms = uidoc.Selection.PickElementsByRectangle(selectionFilter, "Select Rooms")