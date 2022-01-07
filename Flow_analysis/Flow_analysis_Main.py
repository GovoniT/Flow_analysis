
# Python image tracking and analysis 2021
# Code developer :
# Tony Govoni
#_________________________________________

# Flow_analysis_Main : The goal of this script is to control all other scripts and loop to restart when asked
#_________________________________________

# 1. Importing package
import os
import pickle
#_________________________________________

# 2. Path and directory manipulation

retval = os.getcwd() #main directroy : Flow_analysis

pathofscript =retval+"/python_script"  #path to all scripts

os.chdir(pathofscript) #go to python_script folder

# 2.1 Creating the data directory to store the frame
try: #try to create the directory
    if not os.path.exists('data'):
        os.makedirs('data')
except OSError: #report if some error occures
    print ('Error: Creating directory of data')

path_data =pathofscript+"/data" # frame directoy : data

os.chdir(path_data) # directory change for data

# 2.2 Creating the binary directory to store the data relative to the color tracked
try:
    if not os.path.exists('binary'):
        os.makedirs('binary')
        
except OSError:
    print ('Error: Creating directory of binary')

path_binary =path_data+"/binary" # frame directoy : My_data

os.chdir(path_binary) # directory change for binary

# 2.3 Creating the My_data directory to store the whole data analysed of a record
try:
    if not os.path.exists('My_data'):
        os.makedirs('My_data')
        
except OSError:
    print ('Error: Creating directory of My_data')
# 2.4 Creating the Settings directory to store the settings for tracking
try:
    if not os.path.exists('Settings'):
        os.makedirs('Settings')
        
except OSError:
    print ('Error: Creating directory of Settings')

os.chdir(pathofscript) #turing back in the script directory

#_________________________________________

# 3. Variable

# set of variable used to decide if a restart of the program is asked by the user
restart=True
restart_setting=True

# 4. Scripts loop
while (restart): #while the restart is asked by the user
    
    # 4.1 Start with clear all past data
    exec(open('Clear_data.py'.encode('utf-8')).read())

    # 4.2 : Chose a video to analyse
    exec(open('Video_selection.py'.encode('utf-8')).read())

    if restart_setting==True:
        # 4.3 : Start Settings_configuration
        exec(open('Settings_configuration.py'.encode("utf-8")).read())
        
    # 4.4 : Manipulate all the data from the record
    exec(open('Tracking_machine.py'.encode('utf-8')).read())
    
    os.chdir(pathofscript) #Tracking_machine.py change the working directoy, a reset is needed
    # 4.5 : Plot the data
    exec(open('Plot_data.py'.encode('utf-8')).read())

    # 4,6 : Restart ?
    os.chdir(pathofscript) #Plot_data.py change the working directoy, a reset is needed

    with open ('data/binary/restart.txt', 'rb') as f: # read if the user asked for a restart
        restart=pickle.load(f)
    f.close()
    try:
        with open ('data/binary/restart_half.txt', 'rb') as f:  # read if the user asked for changing the settings
            restart_setting=pickle.load(f)
        f.close()
    except:
        None
        


print('end Image_analysis.py')

# end
# --------------------------------------------------------------------------------------
