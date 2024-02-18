#IronPython

import subprocess
import json

def send_dict(sent_dict, pathToScript):
    """_summary_

    Args:
        sent_dict (_type_): _description_
        pathToScript (_type_): _description_
    """
    # print("*"*80)
    # print(sent_dict)
    # print("*"*80)
    message = json.dumps(sent_dict)
    cmd = ['python', pathToScript, message]

    # Create the subprocess startup info object This prevents the black terminal window from popping up when running hte subprocess
    startup_info = subprocess.STARTUPINFO()
    startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # Run the command and capture the output
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startup_info)

