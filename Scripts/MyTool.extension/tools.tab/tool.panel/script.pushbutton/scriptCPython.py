#! python3

import sys
import pickle
from modules import rvt_room_shapes


# CODE BELOW HERE #
#Receive temp file path from sent dict
temp_file_path = sys.argv[1]

#open temp file
with open(temp_file_path, 'rb') as temp_file:
    dict_received = pickle.load(temp_file)


#test dump json (since cannot print in console) -- REMOVE WHEN TESTING IS NOT NEEDED !!!
# change to directory of current script
# cur_dir=sys.path[0]
    
# with open(os.path.join(cur_dir, 'data.json'), 'w') as f:
#     json.dump(dict_received, f)

#Parse received data
parameters = dict_received["parameters"]
room_data = dict_received["room_data"]
export_path = dict_received["export_dir"]
output = dict_received["export_format"]

rvt_room_shapes.rvt_rooms_shapes(room_data,parameters,export_path,output)
    
