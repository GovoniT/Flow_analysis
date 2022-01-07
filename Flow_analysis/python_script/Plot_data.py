# Python image tracking and analysis 2021
# code developer :
# Tony Govoni
#_________________________________________

# Tracking_machine : The goal of this script is to find all contour of colored object in a image and
# store all data in multiple text files in the folder binary
#_________________________________________

#importing module

import cv2
import numpy as np
import os
import pickle
import math
import time
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib import cbook
from matplotlib.patches import Rectangle
#_________________________________________

# 1. Importing data from Tracking machine

# Name of the video
with open ('data/binary/name_video.txt', 'rb') as f:
    name_video= pickle.load(f)
f.close()

#Getting all the data stocked in the txt files
with open ('data/binary/Settings/cal_len.txt', 'rb') as f:
    cal_len= pickle.load(f)
f.close()
with open ('data/binary/Settings/flow_orientation.txt', 'rb') as f:
    flow_orientation= pickle.load(f)
f.close()

#first getting the list of the color we have tracked :
with open ('data/binary/Settings/color_to_track.txt', 'rb') as f:
    color_to_track= pickle.load(f)
f.close()
#and the corresponding BGR color code
for color in color_to_track:
    with open ('data/binary/Settings/code_'+color+'.txt', 'rb') as f:
        globals()['code_'+color]= pickle.load(f)
    f.close()
#then we get back all the data relative to the colored object
for color in color_to_track:
    with open ('data/binary/pos_'+color+'.txt', 'rb') as f:
        globals()['pos_'+color]= pickle.load(f)
    f.close()
    with open ('data/binary/angle_'+color+'.txt', 'rb') as f:
        globals()['angle_'+color]= pickle.load(f)
    f.close()
    with open ('data/binary/size_'+color+'.txt', 'rb') as f:
        globals()['size_'+color]= pickle.load(f)
    f.close()
    with open ('data/binary/number_'+color+'.txt', 'rb') as f:
        globals()['number_'+color]= pickle.load(f)
    f.close()
    with open('data/binary/angular_veloc_'+color+'.txt','rb') as f:
        globals()['angular_veloc_'+color]= pickle.load(f)
    f.close()
    with open('data/binary/veloc_'+color+'.txt','rb') as f:
        globals()['veloc_'+color]= pickle.load(f)
    f.close()
    with open('data/binary/angular_acc_'+color+'.txt','rb') as f:
        globals()['angular_acc_'+color]= pickle.load(f)
    f.close()
    with open('data/binary/acc_'+color+'.txt','rb') as f:
        globals()['acc_'+color]= pickle.load(f)
    f.close()

#the number of image is the lenght of the list number_color (all same lenght for each color)
number_frame = len(globals()['number_'+color_to_track[0]])

#the tracking time
with open ('data/binary/time_of_record.txt', 'rb') as f:
    time_of_record= pickle.load(f)
f.close()

#finally we get back the indices of failed frame to track
for color in color_to_track:
    with open ('data/binary/fail_to_track_'+color+'.txt', 'rb') as f:
        globals()['fail_to_track_'+color] = pickle.load(f)
    f.close()
#_________________________________________

# 2. Computing value for the plot

#Getting value for the plot
#average size of rectangle: 
size_mean_x=[]
size_mean_y=[]

#swap size if not well define:
#done only on one color
for size in globals()['size_'+color_to_track[0]]:
    if size[0]>=0 and size[1]>=0:
        if size[0]>size[1]:
                size_mean_x.append(size[0])
                size_mean_y.append(size[1])
        else:
            
            size_mean_x.append(size[1])
            size_mean_y.append(size[0])
size_mean_x.sort()
size_mean_y.sort()

#use middle value
size_mean_x=size_mean_x[math.ceil(len(size_mean_x)/2)]/2
size_mean_y=size_mean_y[math.ceil(len(size_mean_y)/2)]/2
#Image dimension:
image_0=cv2.imread('data/frame0.jpg') # take the first frame
dimensions = image_0.shape

#_________________________________________

# 3. Ploting the general data
root = tk.Tk()
root.destroy()

root = tk.Tk() # start Tk loop

#time line of the record
time_line=np.linspace(0.,time_of_record,number_frame)

def BGR_to_matplotlibRGB(BGR): #used for matplotlib color plot
    return tuple([BGR[2]/255,BGR[1]/255,BGR[0]/255])

#trace of the center of each panel
fig1,axis1 =  plt.subplots(1,1)
for color in color_to_track:
    globals()['pos_x_'+color]=[]
    globals()['pos_y_'+color]=[]
    for position_xy in globals()['pos_'+color]:
        globals()['pos_x_'+color].append(position_xy[0])
        globals()['pos_y_'+color].append(position_xy[1])
    plot_data_x=[]
    plot_data_y=[]
    for frame in range(0,number_frame):
        if frame not in globals()['fail_to_track_'+color]: #do not plot image not found
            if ((flow_orientation  == "right")and(globals()['pos_x_'+color][frame]>globals()['pos_x_'+color][frame-1]))\
               or((flow_orientation  == "left")and(globals()['pos_x_'+color][frame]<globals()['pos_x_'+color][frame-1])):
                plot_data_x.append(globals()['pos_x_'+color][frame])
                plot_data_y.append(globals()['pos_y_'+color][frame])
        else:
            plot_data_x.append(np.nan)
            plot_data_y.append(np.nan)
            
    #plot position
    plt.plot(plot_data_x,plot_data_y,color=\
    BGR_to_matplotlibRGB(globals()['code_'+color]),linestyle='-')
    
plt.title('General path : '+str(name_video))
plt.axis([0,dimensions[1],dimensions[0],0])
x_axis_value=[]
x_axis_point=[]
y_axis_value=[]
y_axis_point=[]
for i in range(0,6):
    x_axis_value.append(round(dimensions[1]/5*i*cal_len,2))
    y_axis_value.append(round(dimensions[0]/5*i*cal_len,2))
    x_axis_point.append(dimensions[1]/5*i)
    y_axis_point.append(dimensions[0]/5*i)
    
plt.xticks(x_axis_point, x_axis_value)
plt.yticks(y_axis_point, y_axis_value)
axis1.set_xlabel('distance [m]')
axis1.set_ylabel('distance [m]')
plt.gca().set_aspect('equal', adjustable='box')

#plot velocity and acceleration data
fig2,a2 =  plt.subplots(1,1,figsize=(6,3))
fig2.tight_layout(pad=3.0)
for color in color_to_track:
    globals()['acc_magn_'+color]=[]
    globals()['vel_magn_'+color]=[]
    for vector_xy in globals()['veloc_'+color]:
        globals()['vel_magn_'+color].append(\
        math.sqrt(vector_xy[0]**2+vector_xy[1]**2))
        
    for vector_xy in globals()['acc_'+color]:
        globals()['acc_magn_'+color].append(\
        math.sqrt(vector_xy[0]**2+vector_xy[1]**2))
        
    plot_data_acc=[]
    plot_data_vel=[]
    plot_data_ang_acc=[]
    plot_data_ang_vel=[]
    for frame in range(0,number_frame):
        if frame not in globals()['fail_to_track_'+color]: #do not plot image not found
##            plot_data_acc.append(\
##            globals()['acc_magn_'+color][frame])
            if frame == 0:
                plot_data_vel.append(globals()['vel_magn_'+color][frame])
            else:
##
                if ((flow_orientation  == "right")and(globals()['pos_x_'+color][frame]>globals()['pos_x_'+color][frame-1]))\
                   or((flow_orientation  == "left")and(globals()['pos_x_'+color][frame]<globals()['pos_x_'+color][frame-1])):
                    plot_data_vel.append(globals()['vel_magn_'+color][frame])
                else:
                    plot_data_vel.append(np.nan)
            
##            plot_data_ang_acc.append(\
##            globals()['angular_acc_'+color][frame])
##            
##            plot_data_ang_vel.append(\
##            globals()['angular_veloc_'+color][frame])
            
        if frame in globals()['fail_to_track_'+color]:
##            plot_data_acc.append(np.nan)
            plot_data_vel.append(np.nan)
##            plot_data_ang_acc.append(np.nan)
##            plot_data_ang_vel.append(np.nan)
    #plot
    #velocity
    a2.plot(time_line,plot_data_vel,color=\
    BGR_to_matplotlibRGB(globals()['code_'+color]),linestyle='-')
    a2.set_title('Velocity magnitude')
    a2.set_xlim([0,time_of_record])
    a2.set_ylim([0,max(globals()['vel_magn_'+color])])
    a2.set_ylabel('V [m/s]')


            
##    a2[0].plot(time_line,plot_data_vel,color=\
##    BGR_to_matplotlibRGB(globals()['code_'+color]),linestyle='-')
##    a2[0].set_title('Velocity magnitude')
##    a2[0].set_xlim([0,time_of_record])
##    a2[0].set_ylim([0,max(globals()['vel_magn_'+color])])
##    a2[0].set_ylabel('V [m/s]')
##    #accelration
##    a2[1].plot(time_line,plot_data_acc,color=\
##    BGR_to_matplotlibRGB(globals()['code_'+color]),linestyle='-')
##    a2[1].set_title('Acceleration magnitude')
##    a2[1].set_xlim([0,time_of_record])
##    a2[1].set_ylim([0,max(globals()['acc_magn_'+color])])
##    a2[1].set_ylabel('A [m/s^2]')
##    #angl_veloc
##    a2[2].plot(time_line,plot_data_ang_vel,color=\
##    BGR_to_matplotlibRGB(globals()['code_'+color]),linestyle='-')
##    a2[2].set_title('Angular velocity')
##    a2[2].set_xlim([0,time_of_record])
##    a2[2].set_ylim([min(globals()['angular_veloc_'+color]),\
##    max(globals()['angular_veloc_'+color])])
##    a2[2].set_ylabel('phi [rad/s]')
##    #angl_acc
##    a2[3].plot(time_line,plot_data_ang_acc,color=\
##    BGR_to_matplotlibRGB(globals()['code_'+color]),linestyle='-')
##    a2[3].set_title('Angular acceleration')
##    a2[3].set_xlim([0,time_of_record])
##    a2[3].set_xlabel('time [s]')
##    a2[3].set_ylim([min(globals()['angular_acc_'+color]),\
##    max(globals()['angular_acc_'+color])])
##    a2[3].set_ylabel('phi_dot [rad/s^2]')


plt.show(block=False)
#_________________________________________

# 3.1 Interactive Plot : give data for each frame

root.geometry("400x600")
root.wm_title("option")
#plt.sca(axis1)
#screen dimension
my_screen_width = root.winfo_screenwidth() #get the user screen size
my_screen_height = root.winfo_screenheight()
im_w=dimensions[1]
im_h=dimensions[0]
#if the image is too big for user screen then resize it
while(im_w+100> my_screen_width):
    im_w=im_w/2
    im_h=im_h/2
while(im_h +100> my_screen_height):
    im_w=im_w/2
    im_h=im_h/2


global counter
counter = -1
global increment
increment =tk.IntVar()
increment.set(1)
global check_frame
check_frame = False
global data_name
data_name=''

def Click_Next(check_frame_in): #plot the next frame data
    global counter
    global increment
    global check_frame
    stay_counter=counter #if just check frame, stay at the same frame
    counter += int(increment.get())
    if counter>=number_frame: #reset to first frame
        counter-=number_frame
    
    if check_frame_in==True: # if just check the frame, counter dont change
        counter=stay_counter
        
    plt.clf()
    for color in color_to_track:
        if counter not in globals()['fail_to_track_'+color]: #plot only if data available
            #define 4 small rectangle to generate one big rectangle from the center
            rect1=Rectangle([globals()['pos_x_'+color][counter],\
            globals()['pos_y_'+color][counter]],size_mean_x,
            size_mean_y,globals()['angle_'+color][counter],\
            facecolor=BGR_to_matplotlibRGB(\
            globals()['code_'+color]),edgecolor='black')
            
            rect2=Rectangle([globals()['pos_x_'+color][counter],\
            globals()['pos_y_'+color][counter]],-size_mean_x,\
            size_mean_y,globals()['angle_'+color][counter],
            facecolor=BGR_to_matplotlibRGB(\
            globals()['code_'+color]), edgecolor='black')
            
            rect3=Rectangle([globals()['pos_x_'+color][counter],\
            globals()['pos_y_'+color][counter]],size_mean_x,\
            -size_mean_y,globals()['angle_'+color][counter],\
            facecolor=BGR_to_matplotlibRGB(\
            globals()['code_'+color]), edgecolor='black')
            
            rect4=Rectangle([globals()['pos_x_'+color][counter],\
            globals()['pos_y_'+color][counter]],-size_mean_x,\
            -size_mean_y,globals()['angle_'+color][counter],\
            facecolor=BGR_to_matplotlibRGB(\
            globals()['code_'+color]), edgecolor='black')
            
            plt.title('Frame : '+str(counter)+\
            '     Time : '+str(round(time_line[counter],4)))

            #add rectangle
            currentAxis = fig1.gca()
            if check_frame==True:
                nameframe='frame'+str(counter)
                image = plt.imread('data/'+nameframe+'.jpg')
                plt.imshow(image)
            
            plt.xticks(x_axis_point, x_axis_value)
            plt.yticks(y_axis_point, y_axis_value)
            axis1.set_xlabel('distance [m]')
            axis1.set_ylabel('distance [m]')
            currentAxis.add_patch(rect1)
            currentAxis.add_patch(rect2)
            currentAxis.add_patch(rect3)
            currentAxis.add_patch(rect4)

    count_fail=0
    for color in color_to_track:
        if counter in globals()['fail_to_track_'+color]:
            count_fail +=1
    if count_fail == len(color_to_track):
        plt.title('Frame : '+str(counter)+'     Time : '+str(round(time_line[counter],4)))
        plt.text(0.5*dimensions[1],0.5*dimensions[0],'Objects not found in this frame',ha='center',size=20)
    plt.draw()
    plt.axis([0,dimensions[1],dimensions[0],0])
    plt.gca().set_aspect('equal', adjustable='box')

def Click_Previous(): #same function but decrease
    global counter
    global check_frame
    counter -= int(increment.get())
    if counter<=-1: #go to last frame
        counter+= (number_frame)
    plt.clf()
    for color in color_to_track:
        if counter not in globals()['fail_to_track_'+color]:
            #define 4 small rectangle to generate one big rectangle from the center
            #define 4 small rectangle to generate one big rectangle from the center
            rect1=Rectangle([globals()['pos_x_'+color][counter],\
            globals()['pos_y_'+color][counter]],size_mean_x,
            size_mean_y,globals()['angle_'+color][counter],\
            facecolor=BGR_to_matplotlibRGB(\
            globals()['code_'+color]),edgecolor='black')
            
            rect2=Rectangle([globals()['pos_x_'+color][counter],\
            globals()['pos_y_'+color][counter]],-size_mean_x,\
            size_mean_y,globals()['angle_'+color][counter],
            facecolor=BGR_to_matplotlibRGB(\
            globals()['code_'+color]), edgecolor='black')
            
            rect3=Rectangle([globals()['pos_x_'+color][counter],\
            globals()['pos_y_'+color][counter]],size_mean_x,\
            -size_mean_y,globals()['angle_'+color][counter],\
            facecolor=BGR_to_matplotlibRGB(\
            globals()['code_'+color]), edgecolor='black')
            
            rect4=Rectangle([globals()['pos_x_'+color][counter],\
            globals()['pos_y_'+color][counter]],-size_mean_x,\
            -size_mean_y,globals()['angle_'+color][counter],\
            facecolor=BGR_to_matplotlibRGB(\
            globals()['code_'+color]), edgecolor='black')
            
            plt.title('Frame : '+str(counter)+\
            '     Time : '+str(round(time_line[counter],4)))
            #add rectangle
            currentAxis = fig1.gca()
            if check_frame==True:
                nameframe='frame'+str(counter)
                image = plt.imread('data/'+nameframe+'.jpg')
                plt.imshow(image)
            plt.xticks(x_axis_point, x_axis_value)
            plt.yticks(y_axis_point, y_axis_value)
            axis1.set_xlabel('distance [m]')
            axis1.set_ylabel('distance [m]')
            currentAxis.add_patch(rect1)
            currentAxis.add_patch(rect2)
            currentAxis.add_patch(rect3)
            currentAxis.add_patch(rect4)
    count_fail=0
    for color in color_to_track:
        if counter in globals()['fail_to_track_'+color]:
            count_fail +=1
    if count_fail == len(color_to_track):
        plt.title('Frame : '+str(counter)+'     Time : '+str(round(time_line[counter],4)))
        plt.text(0.5*dimensions[1],0.5*dimensions[0],'Objects not found in this frame',ha='center',size=20)
    plt.draw()
    plt.axis([0,dimensions[1],dimensions[0],0])
    plt.gca().set_aspect('equal', adjustable='box')

def Check_frame(): #display the current frame, so that the user can check the data
    global check_frame
    if check_frame==False:
        check_frame=True
        
    else:
        check_frame=False
    #display result
        global counter
    Click_Next(True)
      
#Save data compile all the data in a .txt file
#this .txt file is arrange with a space bewteen data
#so that it can be reuse with pandas, excel, matlab, etc...
def Save_data():
    global entry_1
    texte_file =open ('data/binary/My_data/'+entry_1.get()+'.txt', 'w')
    #writing first line with information
    line ='time'
    for color in color_to_track:
        line=line+' position_'+color+'_x '+'position_'+color+'_y '+'angle_'+color+' vel_x_'+color+' vel_y_'+color+' ang_vel_'+color+' acc_x_'+color+' acc_y_'+color+' ang_acc_'+color
    texte_file.write(line)
    #then writing all the data:
    for k in range(0,number_frame):
        line=str(time_line[k])+'    '
        for color in color_to_track:
            line=line+str(globals()['pos_x_'+color][k])+' '+str(globals()['pos_y_'+color][k])+' '+str(globals()['angle_'+color][k])+' '+str(globals()['veloc_'+color][k][0])+' '+str(globals()['veloc_'+color][k][1])+' '+str(globals()['angular_veloc_'+color][k])+' '+str(globals()['acc_'+color][k][0])+' '+str(globals()['acc_'+color][k][1])+' '+str(globals()['angular_acc_'+color][k])+' '
        texte_file.write('\n%s' % line)
    texte_file.close()
    print('data : '+entry_1.get()+'.txt get saved in the folder : My_data') # confirmation line
    global saveroot
    saveroot.destroy()   
    
def Save_display(): #launch the save root
    global saveroot
    saveroot = tk.Tk()
    saveroot.wm_title("Save")
    tk.Label(saveroot, text="Data_name").grid(row=0)
    global entry_1

    entry_1 = tk.Entry(saveroot)
    
    entry_1.grid(row=0, column=1)
    
    tk.Button(saveroot,text='Save', command=Save_data).grid(row=2, column=1, sticky=tk.W, pady=4)

#restart is called when the user want to restart
def Restart():
    global restart_prog
    global restartroot
    restartroot = tk.Tk()
    restartroot.wm_title("Restart")
    tk.Label(restartroot, text="Restart an analysis ?",width=30).pack()
    tk.Label(restartroot, text="All results will be deleted !",width=30).pack()

    tk.Button(restartroot,text='Restart an analysis with the same settings', command=Restart_half,width=30).pack()
    tk.Button(restartroot,text='Full Restart', command=Restart_full,width=30).pack()

def Restart_full(): #restart completly the program
    global restartroot
    #save to tell the main script to restart
    with open ('data/binary/restart.txt', 'wb') as f:
        pickle.dump(1,f)
    f.close()
    #save to tell the main script to restart settings configuration
    with open ('data/binary/restart_half.txt', 'wb') as f:
        pickle.dump(1,f)
    f.close()
    
    #desrtoy all windows
    plt.close(fig1)
    plt.close(fig2)
    restartroot.destroy()
    root.destroy()

def Restart_half(): #restart the program with same settings
    global restartroot
    #save to tell the main script to restart
    with open ('data/binary/restart.txt', 'wb') as f:
        pickle.dump(1,f)
    f.close()
    #save to tell the main script to not restart settings configuration
    with open ('data/binary/restart_half.txt', 'wb') as f:
        pickle.dump(0,f)
    f.close()
    
    #desrtoy all windows
    plt.close(fig1)
    plt.close(fig2)
    restartroot.destroy()
    root.destroy()
    
def Exit_prog(): #exit the program 
    global restartroot
    global end_program_bool
    restartroot = tk.Tk()
    restartroot.wm_title("Quit")
    tk.Label(restartroot, text="Exit the program ?").grid(row=0)
    tk.Label(restartroot, text="All results not saved will be lost !").grid(row=1)
    tk.Button(restartroot,text='Quit', command=Quit_prog).grid(row=2, column=1, sticky=tk.W, pady=4)

def Quit_prog(): #when the user want to quit programm
    global restartroot
    #save to tell the main script to not restart
    with open ('data/binary/restart.txt', 'wb') as f:
        pickle.dump(0,f)
    f.close()
    plt.close(fig1)
    plt.close(fig2)
    restartroot.destroy()
    root.destroy()


# Button for the Tk interface
mButton1 = tk.Button(text = 'Next',width=10, command = lambda :Click_Next(False), fg = "black", bg = "white")
mButton1.pack()
mButton2 = tk.Button(text = 'Previous',width=10,command = Click_Previous, fg = "black", bg = "white")
mButton2.pack()
mButton2 = tk.Button(text = 'Check frame',width=10,command = Check_frame, fg = "black", bg = "white")
mButton2.pack()
mButton3 = tk.Radiobutton(text="1", variable=increment, value=1,width = 8, fg = "black", bg = "white")
mButton3.pack()
mButton4 = tk.Radiobutton(text="5", variable=increment, value=5,width = 8, fg = "black", bg = "white")
mButton4.pack()
mButton5 = tk.Radiobutton(text="10", variable=increment, value=10,width = 8, fg = "black", bg = "white")
mButton5.pack()
mButton6 = tk.Radiobutton(text="20", variable=increment, value=20,width = 8, fg = "black", bg = "white")
mButton6.pack()
mButton7 = tk.Radiobutton(text="100", variable=increment, value=100,width = 8, fg = "black", bg = "white")
mButton7.pack()

mButton8 = tk.Button(text = 'Save Data (.txt import wizard Excel)',width=30, command= Save_display, fg = "black", bg = "white")
mButton8.pack()
mButton9 = tk.Button(text = 'Restart vith another video ',width=20, command= Restart, fg = "black", bg = "white")
mButton9.pack()
mButton10 = tk.Button(text = 'Quit program ',width=20, command= Exit_prog, fg = "black", bg = "white")
mButton10.pack()

root.mainloop() #Tk loop

#end
#-------------------------------------------------------------------------------------
