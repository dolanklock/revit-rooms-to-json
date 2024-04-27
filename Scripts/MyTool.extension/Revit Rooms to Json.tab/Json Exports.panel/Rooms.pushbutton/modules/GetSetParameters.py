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


class OptionsLineStyle(forms.TemplateListItem):
    @property
    def name(self):
        return self.Name


def get_parameter_type(element_parameter):
    element_parameter_type = element_parameter.StorageType
    return str(element_parameter_type)


def set_parameter(element_parameter, parameter_value):
    t = Autodesk.Revit.DB.Transaction(doc, "Setting elements parameter value")
    t.Start()
    element_parameter.Set(parameter_value)
    t.Commit()


class SetParameter:

    @staticmethod
    def set_instance_parameter_value(element, parameter_name=None, parameter_value=None):
        """
        Sets any instance parameter value on any element
        :param element: The element you want to change parameter for
        :param parameter_name: (String) The name of the parameter that you want to change
        :param parameter_value: (String, Integer, Float) The new value for the parameter
        :return: N/A
        """
        element_parameter = element.LookupParameter(parameter_name)
        element_parameter_type = get_parameter_type(element_parameter)
        if element_parameter_type == 'String':
            if not isinstance(parameter_value, str):
                raise ValueError("Value must be of type string")
            else:
                set_parameter(element_parameter, parameter_value)
        elif element_parameter_type == 'Double':
            if not isinstance(parameter_value, float):
                raise ValueError("Value must be of type float")
            else:
                set_parameter(element_parameter, parameter_value)
        elif element_parameter_type == 'Integer':
            if not isinstance(parameter_value, int):
                raise ValueError("Value must be of type Integer")
            else:
                set_parameter(element_parameter, parameter_value)

    @staticmethod
    def set_type(element, new_types_id):
        type_to_set_to = DB.ElementId(new_types_id)
        t = Autodesk.Revit.DB.Transaction(doc, "Change element type")
        t.Start()
        element.ChangeTypeId(type_to_set_to)
        t.Commit()

    @staticmethod
    def set_type_mark(element, value):
        """
        Sets the elements type mark parameter value
        :param element: The element you want to add type mark value for
        :param value: (String)
        :return: N/A
        """
        element_type_id = element.GetTypeId()
        element_type = doc.GetElement(element_type_id)
        element_parameter = element_type.get_Parameter(DB.BuiltInParameter.WINDOW_TYPE_ID)
        if not isinstance(value, str):
            raise ValueError("Value must be of type string")
        else:
            t = Autodesk.Revit.DB.Transaction(doc, "Set elements type mark")
            t.Start()
            element_parameter.Set(value)
            t.Commit()

    @staticmethod
    def set_element_workset(element, workset):
        """
        Sets the elements workset to a different user created one
        :param element: The element that you want to change workset for
        :param workset: (DB.Workset Object) The workset that you want to change element to
        :return: N/A
        """
        workset_param = element.get_Parameter(DB.BuiltInParameter.ELEM_PARTITION_PARAM)
        t = Autodesk.Revit.DB.Transaction(doc, "Setting elements parameter value")
        t.Start()
        workset_param.Set(workset.Id.IntegerValue)
        t.Commit()


class GetParameter:

    @staticmethod
    def get_type_name(element):
        """
        This method will take in an element object and get the elements type and then the types name
        If an element type is passed in as an argument the try block will fail and the except block will
        be executed and retrieve the types name and return it
        :param element: (element object) element whose type name to get
        :return: (String) elements type name
        """
        try:
            element_type_id = element.GetTypeId()
            element_type = doc.GetElement(element_type_id)
            element_parameter_value = element_type.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
            return element_parameter_value
        except:
            element_parameter_value = element.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
            return element_parameter_value

    @staticmethod
    def get_instance_parameter_by_name(element, parameter_name=None):
        """
        Gets any instance parameter value by name for any element passed in to the argument
        :param element: The element for the parameter you want to get
        :param parameter_name: (String) The name of the parameter that you want the value for
        :return: N/A
        """
        element_parameter = element.LookupParameter(parameter_name)
        element_parameter_type = get_parameter_type(element_parameter)
        if element_parameter_type == 'String':
            return element_parameter.AsValueString()
        elif element_parameter_type == 'Double':
            return element_parameter.AsDouble()
        elif element_parameter_type == 'Integer':
            return element_parameter.AsInteger()


class GetTypes:

    @staticmethod
    def get_filled_region_types():
        """
        Gets all of the filled regions types in model
        :return: (list) All filled regions types in a list
        """
        return DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).ToElements()


class GetElements:

    @staticmethod
    def get_views():
        """
        Gets all of the views inside the current model
        :return: (View Object) Returns all views in the current model
        """
        return DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Views).WhereElementIsNotElementType()
    
    @staticmethod
    def get_view_templates():
        """
        Gets all of the views inside the current model
        :return: (View Object) Returns all views in the current model
        """
        view_fec = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Views).WhereElementIsNotElementType()
        return [v for v in view_fec if v.IsTemplate]

    @staticmethod
    def get_view_templates_from_doc(doc):
        """
        Gets all of the views inside the current model
        :return: (View Object) Returns all views in the current model
        """
        view_fec = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Views).WhereElementIsNotElementType()
        return [v for v in view_fec if v.IsTemplate]
    
    @staticmethod
    def get_worksets(kind="UserWorkset"):
        """
        Gets all worksets of whatever workset kind is passed in to the argument
        :param kind: (String) Pass in one of the members from the enumeration "WorksetKind" as a string for whichever
                     workset type you want to get:
                     (OtherWorkset, FamilyWorkset, ViewWorkset, StandardWorkset, UserWorkset)
        :return: (FilteredElementCollector) Returns filtered element collector of all worksets
        """
        if not isinstance(kind, str):
            raise TypeError('"kind" argument must be of type string.')
        try:
            workset_kind = getattr(DB.WorksetKind, kind)
            all_worksets = DB.FilteredWorksetCollector(doc).OfKind(workset_kind)
        except AttributeError:
            raise AttributeError('"{}" member does not exists for WorksetKind enumeration'.format(kind))
        else:
            return all_worksets

    @staticmethod
    def get_elements_built_in_category(doc, category_name="OST_Walls", element_types_only=None):
        """
        This function gets all elements of the specified category. You can use the "element_types_only" parameter
        in order to get types only if set to "True" or all elements placed in model if set to "False" or leave set to "None"
        to get all types and elements.
        Args:
            doc: (Document) document to retrieve elements from
            category_name: (String) Name of category of BuiltInCategory Enumeration member
            element_types_only:

        Returns: (FilteredElementCollector) returns FilteredElementCollector of all elements of category specified

        """
        if not isinstance(doc, DB.Document):
            raise ValueError("doc parameter must be of type Document")
        if not isinstance(category_name, str):
            raise ValueError("built_in_category_name parameter must be of type string")

        try:
            built_in_category = getattr(DB.BuiltInCategory, category_name)
        except AttributeError as ex:
            raise AttributeError('BuiltInCategory Enumeration does not have the member "{} - {}"'
                                 .format(category_name, ex))
        if element_types_only:
            elements = DB.FilteredElementCollector(doc).OfCategory(built_in_category) \
                .WhereElementIsElementType()
        elif not element_types_only:
            elements = DB.FilteredElementCollector(doc).OfCategory(built_in_category) \
                .WhereElementIsNotElementType()
        else:
            elements = DB.FilteredElementCollector(doc).OfCategory(built_in_category) \
                .ToElements()
        return elements

    @staticmethod
    def get_wall_types():
        pass

    @staticmethod
    def get_sheets():
        pass


class LineStyle:

    @staticmethod
    def choose_line_style():
        line_styles = DB.FilteredElementCollector(doc).OfClass(DB.GraphicsStyle)
        line_style_names = [OptionsLineStyle(l) for l in line_styles]
        input = forms.SelectFromList.show(line_style_names, title="Select A Line Style", multiselect=False)
        input = input.Id
        return input

class RevitLinks:

    @staticmethod
    def get_all_rvt_links(doc, get_rvt_link_instances=True):
        """
        Gets all revit link instances or revit link types based on specified argument
        Args:
            doc: (Document)
            get_rvt_link_instances: (bool) True in order to get all revit link instances and false to get
            all revit link types

        Returns: (RevitLinkInstance, RevitLinkType)

        """
        revit_links = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_RvtLinks).ToElements()
        if get_rvt_link_instances:
            rvt_link_instances = [rvt_link for rvt_link in revit_links if isinstance(rvt_link, DB.RevitLinkInstance)]
            return rvt_link_instances
        else:
            rvt_link_types = [rvt_link for rvt_link in revit_links if isinstance(rvt_link, DB.RevitLinkType)]
            return rvt_link_types

class Views:

    @staticmethod
    def view_temp_override(arg, enable=True):
        from rpw import db
        if enable:
            with db.Transaction("enable temporary overrides"):
                arg.EnableTemporaryViewPropertiesMode(arg.ViewTemplateId)
        else:
            with db.Transaction("disable temporary overrides"):
                arg.DisableTemporaryViewMode(DB.TemporaryViewMode.TemporaryViewProperties)

    @staticmethod
    def view_crop_boundary_visible(view, visible=False):
        from rpw import db
        with db.Transaction("change views crop box visibile"):
            view.CropBoxVisible = visible

    @staticmethod
    def view_set_scope_box(view, scope_box_id):
        from rpw import db
        if scope_box_id is None:
            vsb_param = view.LookupParameter("Scope Box")
            with db.Transaction("Setting view scope box"):
                vsb_param.Set(DB.ElementId(-1))
        else:
            vsb_param = view.LookupParameter("Scope Box")
            with db.Transaction("Setting view scope box"):
                vsb_param.Set(scope_box_id)

    @staticmethod
    def view_crop_active(view, active=False):
        from rpw import db
        with db.Transaction("change view crop"):
            view.CropBoxActive = active

    @staticmethod
    def set_category_visibility(view, category_id, is_hidden):
        """Sets view or view templates category visibility
        Args:
            view_template (_type_): _description_
            category_id (_type_): _description_
            is_hidden (bool): _description_
        """
        with db.Transaction("Change view category visibility"):
            view.SetCategoryHidden(category_id, is_hidden)

    @staticmethod
    def get_category_visibility(view, category_id):
        """returns whether the category is hidden or not in the view

        Args:
            view (DB.View): view to check 
            category_id (_type_): refer to Selection module 
            it has a method for getting category by name (Selection.get_category_by_name)
            is_hidden (bool): _description_
        """
        return view.GetCategoryHidden(category_id)


class Revisions:
    
    @staticmethod
    def get_revision_by_name(revision_name):
        all_revisions = [r for r in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Revisions)]
        all_revision_names = [r.Name for r in all_revisions]
        return all_revisions[all_revision_names.index(revision_name)].Id

    @staticmethod
    def add_revision_sheet(sheet, revision_id):
        revisions = sheet.GetAdditionalRevisionIds()
        if revision_id not in revisions:
            revisions.append(revision_id)
            trans = DB.Transaction(doc, 'set sheet revision')
            trans.Start()
            sheet.SetAdditionalRevisionIds(List[DB.ElementId](revisions))
            trans.Commit()
        # return revisions

    @staticmethod
    def remove_revision_sheet(sheet, revision_id):
        revisions = sheet.GetAdditionalRevisionIds()
        if revision_id in revisions:
            revisions.remove(revision_id)
            trans = DB.Transaction(doc, 'set sheet revision')
            trans.Start()
            sheet.SetAdditionalRevisionIds(List[DB.ElementId](revisions))
            trans.Commit()



if __name__ == "__main__":
    e_id = DB.ElementId(5828568)
    e = doc.GetElement(e_id)

    type_name = GetParameter.get_type_name(e)

    print(type_name)

    SetParameter.set_instance_parameter_value(e, parameter_name='FILLED REGION LEVEL', parameter_value='testing12345')

    b_a = GetParameter.get_instance_parameter_by_name(e, parameter_name="Base Area")

    print(b_a)

    # SetParameter.set_instance_parameter_value(e, 'Isolate Filled Region', 1)

    SetParameter.set_type(e, new_types_id=2331973)

    SetParameter.set_type_mark(e, 'testing')

