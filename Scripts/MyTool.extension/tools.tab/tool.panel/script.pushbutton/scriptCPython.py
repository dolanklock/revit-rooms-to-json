#! python3

import sys
import json
from geojson import Feature, Polygon, FeatureCollection, dump
from pytopojson import topology
from pyproj import Transformer
from datetime import datetime
import os

from modules import rvt_room_shapes



# CODE BELOW HERE #
json_received = json.loads(sys.argv[1])
# json_received = {"data": {"test": 'testing'}}

#change to directory of current script
cur_dir=sys.path[0]

#test dump json
with open(os.path.join(cur_dir, 'data.json'), 'w') as f:
    json.dump(json_received, f)


parameters_received = ["param1", "param2"]
parameters = parameters_received

output = "both"
# rvt_room_shapes.rvt_rooms_shapes(geometries,parameters,output)
    
 #TODO
    #parse received json into parameters and geometries 
    #run rvt_room_shapes.py script with received data
