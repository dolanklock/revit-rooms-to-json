#! python3
# run in Cpython script

from geojson import Feature, Polygon, FeatureCollection, dump
from pytopojson import topology
from pyproj import Transformer
import os

from modules import data_frame_to_excel
import pandas as pd

def rvt_rooms_shapes(rooms_data, parameters,output_path_root,output = "topo") : #accepts dictionary for rooms_data, array of strings for parameters, output options can be specifified, defaults to topojson

    ouptut_options = ["topo", "geo", "all", "xls"]
    if output not in ouptut_options:
        raise ValueError("Invalid output type. Expected one of: %s" % ouptut_options)  

    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True) 
    def xy_to_decdeg(point): # converts cartesian points to decimal degrees, returns array [long,lat] 
        return list(transformer.transform(point[0], point[1]))

    #group rooms per level
    rooms_per_level = {} #dict grouping rooms per level {level :[room, room], level :[room ,room]}
    for key, value in rooms_data.items():
        rooms_per_level.setdefault(value["Level"], []).append(key)
    # print(rooms_per_level)

    rooms_props_dict = {}
    #for each level, go through each room, extract parameters and create a feature_collection item (geojson item https://datatracker.ietf.org/doc/html/rfc7946)
    for level in rooms_per_level:
        # print("\n")
        # print(level)
        feature_collection = [] #array of features (geojson items)

        for room in rooms_per_level[level]:
            # print(rooms_data[room]["Number"])

            room_polygon = [] #polygon item per room(geojson)
            
            for polygon in rooms_data[room]['geometry']:
                room_polygon.append([xy_to_decdeg(coord) for coord in polygon])

            feature_collection.append(Feature(geometry=Polygon(room_polygon), #append polygon to feature collection of geojson
                properties={param : rooms_data[room][param] for param in parameters}                
                ))
            
            rooms_props_dict[rooms_data[room]["Number"]] = {param : rooms_data[room][param] for param in parameters}

        feature_collection_all = FeatureCollection(feature_collection)  # create geojson object of floor plan
        
        #SAVE FILES       
        try:
            os.mkdir(output_path_root)
        except FileExistsError:
            pass
        
        if output == "geo" or output == "all": #output geojson
            output_path = output_path_root+"\\geo"          
            try:
                os.mkdir(output_path)
            except FileExistsError:
                pass
            
            with open(output_path+'\\geo-{}.geojson'.format(level.replace(" ", "").upper()), 'w') as f:
                dump(feature_collection_all, f)

        if output == "topo" or output == "all": #output topojson
            output_path = output_path_root+"\\topo"
            try:
                os.mkdir(output_path)
            except FileExistsError:
                pass
            
            topology_ = topology.Topology()
            topojson = topology_({"object_name": feature_collection_all})
            with open(output_path+'\\topo-{}.json'.format(level.replace(" ", "").upper()), 'w') as f:
                dump(topojson, f)
        
    if output == "xls" or output == "all": #output excel
        excel_name = os.path.basename(os.path.normpath(output_path_root))
        output_path = output_path_root
        try:
            os.mkdir(output_path)
        except FileExistsError:
            pass
        
        df = pd.DataFrame.from_dict(rooms_props_dict, orient="index")
        df = df.apply(pd.to_numeric, errors="ignore")
        df = df.sort_values("Number")

        conversion_dict = {
            "Area" : {
                "unit" : "m²",
                "multiplier" : 0.092903 
            },
            "Perimeter" : {
                "unit" : "m",
                "multiplier" : 0.3048
            },
        }

        for key in conversion_dict: 
            try:
                df[key] = df[key] * conversion_dict[key]["multiplier"]
                df.rename(columns={key: "{} ({})".format(key,conversion_dict[key]["unit"])}, inplace=True)
            except:
                pass

        data_frame_to_excel.data_frame_to_excel(df,excel_name = output_path+'\\{}-ROOM_DATA.xlsx'.format(excel_name),sheet_name = "Room_data", table_name = "Rm_data")
        with open(output_path+'\\{}-ROOM_DATA.json'.format(excel_name), 'w') as f:
            dump(rooms_props_dict, f)


