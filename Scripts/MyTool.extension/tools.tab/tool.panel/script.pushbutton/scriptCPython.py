#! python3

import sys
import json
import os
from modules import rvt_room_shapes

# CODE BELOW HERE #
json_received = json.loads(sys.argv[1])

#change to directory of current script
cur_dir=sys.path[0]

#test dump json -- REMOVE WHEN TESTING IS NOT NEEDED !!!
with open(os.path.join(cur_dir, 'data.json'), 'w') as f:
    json.dump(json_received, f)

#Parse received json
parameters = json_received["parameters"]
room_data = json_received["room_data"]
export_path = json_received["export_dir"]

output = "both"
rvt_room_shapes.rvt_rooms_shapes(room_data,parameters,export_path,output)
    
