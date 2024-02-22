#! python3
# run in Cpython script

from geojson import Feature, Polygon, FeatureCollection, dump
from pytopojson import topology
from pyproj import Transformer
import datetime
import os

def rvt_rooms_shapes(rooms_data, parameters,output_path_root, output = "topo") : #accepts dictionary for rooms_data, array of strings for parameters, output options can be specifified, defaults to topojson

    ouptut_options = ["topo", "geo", "both"]
    if output not in ouptut_options:
        raise ValueError("Invalid output type. Expected one of: %s" % ouptut_options)  

    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True) 
    def xy_to_decdeg(point): # converts cartesian points to decimal degrees, returns array [long,lat] 
        return list(transformer.transform(point[0], point[1]))

    #group rooms per level
    rooms_per_level = {} #dict grouping rooms per level {level :[room, room], level :[room ,room]}
    for key, value in rooms_data.items():
        if value["Level"] not in rooms_per_level:
            rooms_per_level[value["Level"]] = [key]
        else:
            rooms_per_level[value["Level"]].append(key)

    #for each level, go through each room, extract parameters and create a feature_collection item (geojson item https://datatracker.ietf.org/doc/html/rfc7946)
    for level in rooms_per_level:
        print("\n")
        print(level)
        feature_collection = [] #array of features (geojson items)

        for room in rooms_per_level[level]:
            print(rooms_data[room]["Number"])

            room_polygon = [] #polygon item per room(geojson)
            
            for polygon in rooms_data[room]['geometry']:
                polygon_coord=[]
                for coord in polygon:
                    polygon_coord.append(xy_to_decdeg(coord))
                room_polygon.append(polygon_coord)

            feature_collection.append(Feature(geometry=Polygon(room_polygon), #append polygon to feature collection of geojson
                properties={param : rooms_data[room][param] for param in parameters}                
                ))
            
        feature_collection_all = FeatureCollection(feature_collection)  # create geojson object of floor plan
        
        #SAVE FILES
        date = datetime.date.today()
        folder_name = '{}_{}'.format(date,"export")
        try:
            os.mkdir(output_path_root+"{}".format(folder_name))
        except FileExistsError:
            pass
        
        if output == "geo" or output == "both": #output geojson
            output_path = output_path_root+"{}\\geo".format(folder_name)            
            try:
                os.mkdir(output_path)
            except FileExistsError:
                pass
            
            with open(output_path+'\\geo-{}.geojson'.format(level.replace(" ", "").lower()), 'w') as f:
                dump(feature_collection_all, f)

        if output == "topo" or output == "both": #output topojson
            output_path = output_path_root+"{}\\topo".format(folder_name)
            try:
                os.mkdir(output_path)
            except FileExistsError:
                pass
            
            topology_ = topology.Topology()
            topojson = topology_({"object_name": feature_collection_all})
            with open(output_path+'\\topo-{}.json'.format(level.replace(" ", "").lower()), 'w') as f:
                dump(topojson, f)


