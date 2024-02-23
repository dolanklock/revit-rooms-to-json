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

# CODE BELOW HERE #

"""
Example of selection filters in use:

selection_filter_grid = SelectionFilters.SelectionFilterGrids()
grid_selected = uidoc.Selection.PickObject(Autodesk.Revit.UI.Selection.ObjectType.Element, selection_filter_grid).ElementId

"""

class SelectionFilterGrids(Autodesk.Revit.UI.Selection.ISelectionFilter):
    def AllowElement(self, element):
        if element.Category.Name == "Grids":
            return True
        return False

class SelectionFilterRooms(Autodesk.Revit.UI.Selection.ISelectionFilter):
    def AllowElement(self, element):
        return element.Category.Name == "Rooms"
    
    def AllowReference(self, reference, point):
        return True

class ISelectionFilter(Autodesk.Revit.UI.Selection.ISelectionFilter):
    def __init__(self, category_name):
        self.category_name = category_name
    def AllowElement(self, e):
        if e.Category.Name == self.category_name:
            return True
        else:
            return False
    def AllowReference(self, ref, point):
        return True
