#IronPython

import subprocess
import tempfile
import pickle

def send_dict(sent_dict, pathToScript):
    """_summary_

    Args:
        sent_dict (_type_): _description_
        pathToScript (_type_): _description_
    """

    #create temp file containing dict data
    with tempfile.TemporaryFile(delete=False) as temp_file:
        pickle.dump(sent_dict, temp_file)
        temp_file.close()
    
    #send path with name of file to Cpython
    message = temp_file.name
    cmd = ['python', pathToScript, message]

    # Create the subprocess startup info object This prevents the black terminal window from popping up when running hte subprocess
    startup_info = subprocess.STARTUPINFO()
    startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # Run the command and capture the output
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startup_info)

