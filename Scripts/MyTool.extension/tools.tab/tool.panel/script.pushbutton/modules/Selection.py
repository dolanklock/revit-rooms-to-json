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

import sys
sys.path.append("M:\\600 VWCC\\ARCHITECTURAL\\BIM\\pykTools\\pyKTools\\MyTool.extension\\lib")

from pyrevit import forms
import math
from GetSetParameters import *
from System.Collections.Generic import List
from pyrevit import *
import pyrevit
import Schedules

# CODE BELOW HERE #

__author__ = "Dolan Klock"

# Tooltip
__doc__ = "Used as container file of classes and functions"


def get_category_by_name(cat_name):
    """Gets the category from the doc by the given string of that category

    Args:
        cat_name (string): name of category to return

    Returns:
        DB.Category: _description_
    """
    all_categories = doc.Settings.Categories
    return [cat for cat in all_categories if cat.Name == cat_name][0]


class ElementToCopy(forms.TemplateListItem):
    @property
    def name(self):
        return GetParameter.get_type_name(self)


class GetElementsFromDoc(object):
    
    @staticmethod
    def get_element_by_id(element_id):
        return doc.GetElement(DB.ElementId(element_id))
    
    @staticmethod
    def all_sheets(document):
        """

        :param document (Document) revit document to retrieve elements from
        :param elements_only (bool) if false, the method will get and return all view types. If True, method
        will get and return all views in document
        :returns
        """
        all_elements = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType()
        return all_elements
       

    @staticmethod
    def all_views(document, elements_only=False):
        """
        :param document (Document) revit document to retrieve elements from
        :param elements_only (bool) if false, the method will get and return all view types. If True, method
        will get and return all views in document
        :returns (FilteredElementCollector)
        """
        all_types = DB.FilteredElementCollector(document).OfClass(DB.ViewFamilyType)
        if elements_only:
            all_elements = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Views). \
                WhereElementIsNotElementType()
            return all_elements
        return all_types
    
    @staticmethod
    def all_doors(document, elements_only=False):
        """

        :param document (Document) revit document to retrieve elements from
        :param elements_only (bool) if false, the method will get and return all view types. If True, method
        will get and return all views in document
        :returns (FilteredElementCollector)
        """
        if elements_only:
            all_elements = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Doors). \
                WhereElementIsNotElementType()
            return all_elements
        all_elements = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Doors). \
                WhereElementIsElementType()
        return all_elements
    
    @staticmethod
    def all_rooms(document, is_placed_only=True):
        """
        """
        all_rooms = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
        if is_placed_only:
            all_rooms = [room for room in all_rooms if room.Area != 0]
        return all_rooms
        
    @staticmethod
    def all_floors(document, elements_only=False):
        """

        :param document (Document) revit document to retrieve elements from
        :param elements_only (bool) if false, the method will get and return all view types. If True, method
        will get and return all views in document
        :returns
        """
        all_types = all_elements = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Floors). \
                WhereElementIsElementType()
        if elements_only:
            all_elements = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Floors). \
                WhereElementIsNotElementType()
            return all_elements
        return all_types

    @staticmethod
    def all_walls(document, elements_only=False):
        """

        :param document (Document) revit document to retrieve elements from
        :param elements_only (bool) if false, the method will get and return all view types. If True, method
        will get and return all views in document
        :returns
        """
        all_types = DB.FilteredElementCollector(document).OfClass(DB.Walls)
        if elements_only:
            all_elements = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Walls). \
                WhereElementIsNotElementType()
            return all_elements
        return all_types


    @staticmethod
    def all_dimensions(document, elements_only=False):
        all_types = DB.FilteredElementCollector(document).OfClass(DB.DimensionType)
        # if elements_only:
        #     all_elements = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Dimensions).\
        #         WhereElementIsNotElementType()
        #     return all_elements
        return all_types

    @staticmethod
    def all_text(document, elements_only=False):
        """
        :param document (Document) revit document to retrieve elements from
        :param elements_only (bool) if false, the method will get and return all view types. If True, method
        will get and return all views in document
        :returns
        """
        all_types = DB.FilteredElementCollector(document).OfClass(DB.TextNoteType)
        if elements_only:
            all_elements = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_TextNotes). \
                WhereElementIsNotElementType()
            return all_elements
        return all_types

    @staticmethod
    def all_rooms_placed(document):
        all_rooms_collector = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
        all_rooms_placed = [room for room in all_rooms_collector if room.LookupParameter("Area").AsDouble() > 0]
        return all_rooms_placed


class UITaskDialog:

    @staticmethod
    def task_dialog_two_options(title="", option_one_name="", option_two_name=""):
        td = Autodesk.Revit.UI.TaskDialog(title)
        td.CommonButtons = Autodesk.Revit.UI.TaskDialogCommonButtons.Ok
        td.AddCommandLink(Autodesk.Revit.UI.TaskDialogCommandLinkId.CommandLink1, option_one_name)
        td.AddCommandLink(Autodesk.Revit.UI.TaskDialogCommandLinkId.CommandLink2, option_two_name)
        result = td.Show()
        return result


def get_link_doc():
    """
    This function generates a UI of all of the linked models in the host model and returns selected linked model
    """
    revit_links = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_RvtLinks).ToElements()
    if len(revit_links) == 0:
        forms.alert("There are no linked Revit models inside this model")
        sys.exit()
    rvt_link_instances = [rvt_link for rvt_link in revit_links if isinstance(rvt_link, DB.RevitLinkInstance)]
    input_rvt_link_instance = forms.SelectFromList.show(rvt_link_instances, multiselect=False, name_attr="Name")
    link_doc = input_rvt_link_instance.GetLinkDocument()
    return link_doc


def pick_category(doc):
    """
    Lists all categories from document and prompts for user to select one from list
    :param doc: (Document) the document you want to get categories from
    :return (Category) returns the chosen category
    """
    all_categories = doc.Settings.Categories
    input_category = forms.SelectFromList.show(all_categories, multiselect=False, name_attr="Name")
    return input_category


def pick_element_type(doc, category):
    """

    """
    built_in_category = category.BuiltInCategory
    filter_element_collector = DB.FilteredElementCollector(doc).OfCategory(built_in_category).WhereElementIsElementType()
    # all_types = [e for e in filter_element_collector]
    all_types_names = [ElementToCopy(e_type) for e_type in filter_element_collector]
    input_element_type = forms.SelectFromList.show(all_types_names, multiselect=True)
    return input_element_type


def pick_element_type_of_class(types):
    """

    """
    all_types_names = [ElementToCopy(e_type) for e_type in types]
    input_element_type = forms.SelectFromList.show(all_types_names, multiselect=True)
    return input_element_type


def copy_from_doc(items_to_copy, from_doc, to_doc):
    """

    """
    types_copy_collection = List[DB.ElementId]()
    for type in items_to_copy:
        types_copy_collection.Add(type.Id)
    with pyrevit.revit.Transaction("Copy elements from document"):
        return DB.ElementTransformUtils.CopyElements(from_doc,
                                              types_copy_collection,
                                              to_doc,
                                              None,
                                              DB.CopyPasteOptions()
                                              )
        
def copy_items_view_to_view(source_view, dest_view, elements_copy):
    from rpw import db
    # create ICollection
    elements_collection = List[DB.ElementId]()
    for i in elements_copy:
        elements_collection.Add(i.Id)
    with db.Transaction("Copy elements"):
        DB.ElementTransformUtils.CopyElements(sourceView=source_view,
                                               elementsToCopy=elements_collection,
                                                 destinationView=dest_view,
                                                   additionalTransform=DB.Transform.Identity,
                                                     options=DB.CopyPasteOptions())

def get_titleblocks_from_sheet(sheet, doc):
    "Thanks to Erik Frits for this function ! https://www.learnrevitapi.com/blog/get-titleblock-from-sheet-views/"
    # type:(ViewSheet, Document) -> list
    """Function to get TitleBlocks from the given ViewSheet.
    :param sheet: ViewSheet that has TitleBlock
    :param doc:   Document instance of the Project
    :return:      list of TitleBlocks that are placed on the given Sheet."""

    # RULE ARGUMENTS
    rule_value         = sheet.SheetNumber
    param_sheet_number = DB.ElementId(DB.BuiltInParameter.SHEET_NUMBER)
    f_pvp              = DB.ParameterValueProvider(param_sheet_number)
    evaluator          = DB.FilterStringEquals()
    # CREATE A RULE (Method has changed in Revit API in 2022)
    f_rule = DB.FilterStringRule(f_pvp, evaluator, rule_value)
    # CREATE A FILTER
    tb_filter = DB.ElementParameterFilter(f_rule)
    # GET TITLEBLOCKS
    tb = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks) \
        .WhereElementIsNotElementType().WherePasses(tb_filter).ToElements()
    return list(tb)


def get_plan_regions_in_view(doc, view):
    """gets all plan regions in view

    Args:
        doc (_type_): _description_
        view (_type_): _description_

    Returns:
        _type_: _description_
    """
    all_plan_regions_in_view_fec = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_PlanRegion).WhereElementIsNotElementType()
    all_plan_rergions_in_view = [pl for pl in all_plan_regions_in_view_fec]
    return all_plan_rergions_in_view


def select_workset(doc, kind):
    """This function generates a UI of all of the linked models in the host model and returns selected linked model

    Args:
        doc (DB.Document): N/A
        kind (DB.WorksetKind): this is an enumeration member from WorksetKind Enumeration

    Returns:
        DB.Workset: returns the DB.Workset object
    """
    worksets = [w for w in DB.FilteredWorksetCollector(doc).OfKind(kind)]
    worksets_name = [w.Name for w in worksets]
    worksets_name_sorted = sorted([w.Name for w in worksets], key=lambda x: x[0])
    input_workset_name = forms.SelectFromList.show(worksets_name_sorted, multiselect=False)
    input_workset = worksets[worksets_name.index(input_workset_name)]
    return input_workset


def Select_floor_type(doc, multi_select=False):
    """prompts user for selection of floor type from all floor types in model and
    returns the floor types

    Args:
        doc (DB.Document): N/A

    Returns:
        DB.FloorType: N/A
    """
    all_floor_types = [t for t in GetElementsFromDoc.all_floors(doc, elements_only=False)]
    all_floor_types_name = [GetParameter.get_type_name(t) for t in all_floor_types]
    all_floor_types_name_sorted = sorted(all_floor_types_name, key=lambda x: x[0])
    input_floor_type = forms.SelectFromList.show(all_floor_types_name_sorted, multiselect=multi_select)
    return all_floor_types[all_floor_types_name.index(input_floor_type)]


def get_views_by_level(level_name, plan_views=True):
    all_views = GetElementsFromDoc.all_views(doc, elements_only=True)
    all_view_plans = list(filter(lambda x: x.ViewType == DB.ViewType.FloorPlan or x.ViewType == DB.ViewType.AreaPlan, all_views))
    all_views_ceilplans = list(filter(lambda x: x.ViewType == DB.ViewType.CeilingPlan, all_views))
    if plan_views:
        return [view for view in all_view_plans if view.get_Parameter(DB.BuiltInParameter.PLAN_VIEW_LEVEL).AsValueString() == level_name]
    return [view for view in all_views_ceilplans if view.get_Parameter(DB.BuiltInParameter.PLAN_VIEW_LEVEL).AsValueString() == level_name]


def get_floors_openings(doc, floor):
    """gets all of the openings associated to a floor

    Args:
        doc (DB.Document): can specify link doc or host doc to get floor openings from
        floor (DB.Floor): the floor element to get openings from

    Returns:
        [DB.ElementId]: list of all of the openings (element ids) associated to floor
    """
    all_openings = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_FloorOpening).WhereElementIsNotElementType()
    return [opening for opening in openings if opening.Host.Id == floor.Id]


def copy_floor_with_openings(doc_from, doc_to, floor):
    """_summary_

    Args:
        doc_from (_type_): _description_
        doc_to (_type_): _description_
        floor (_type_): _description_

    Returns:
        tuple[DB.Floor, DB.Opening]: returns a tuple with nested lists, first list is all floors coped and second list is all openings copied
    """
    floors_openings = get_floors_openings(doc_from, floor)
    floor_and_openings_to_copy = [opening.Id for opening in floors_openings]
    floor_and_openings_copy.append(floor.Id)
    floor_and_openings_copy_list = List[DB.ElementId](floor_and_openings_copy)
    copied_elements_openings_floors = DB.ElementTransformUtils.CopyElements(doc_from, floor_and_openings_copy_list, doc_to, None ,DB.CopyPasteOptions())
    copied_floors = filter(lambda e: doc.GetElement(e).Category.Name == "Floors", copied_elements_openings_floors)
    copied_openings = filter(lambda e: doc.GetElement(e).Category.Name == "Opening", copied_elements_openings_floors)
    return (copied_floors, copied_openings)