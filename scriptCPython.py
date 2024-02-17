#! python3

import sys
import json
from geojson import Feature, Polygon, FeatureCollection, dump
from pytopojson import topology
from pyproj import Transformer
from datetime import datetime
import os


def rvt_rooms_shapes(rooms_data, output = "topo") : #accepts dictionary for rooms_data, output options can be specifified, defaults to topojson
    output_path_root = "M:\\Project Library\\Python\\Drop Box\\" 

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
            
            for coord in rooms_data[room]['geometry']:
                room_polygon.append(xy_to_decdeg(coord))
                
                #to simplify shape 
                # if xy_to_decdeg(coord) not in room_polygon:
                #     room_polygon.append(xy_to_decdeg(coord))
            
            #if shape is simplified, add first coordinate to the end
            # room_polygon.append(room_polygon[0])                 
            room_polygon_r = room_polygon[::-1] #reverse coordinates to clockwise
            feature_collection.append(Feature(geometry=Polygon([room_polygon_r]), #append polygon to feature collection of geojson
                properties={
                    "Number": rooms_data[room]["Number"],
                    "DDRmNum": rooms_data[room]["Text"],
                    "Level": rooms_data[room]["Level"],}))
            
        feature_collection_all = FeatureCollection(feature_collection)  # create geojson object of floor plan
        folder_name = '{}_{}'.format(datetime.date.today(), "test")

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


# rvt_rooms_shapes(output,"both")

# CODE BELOW HERE #
json_received = json.loads(sys.argv[1])
# json_received = {"data": {"test": 'testing'}}

#change to directory of current script
cur_dir=sys.path[0]

#test dump json
with open(os.path.join(cur_dir, 'data.json'), 'w') as f:
    json.dump(json_received, f)

# rvt_rooms_shapes(json_received, output = "both")