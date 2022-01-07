# Python image tracking and analysis 2021
# Code developer :
# Tony Govoni
#_________________________________________

#Video_selection : The goal of this script is to let the user select a video to analyse
#_________________________________________

#importing module
import cv2
import numpy as np
import os
import time
import pickle
import math
import tkinter as tk
from tkinter import ttk
import PIL
from PIL import Image
from PIL import ImageTk

#_________________________________________


# 1. Creating video selection
#Getting all video name
path_to_dir  = 'My_video'  # path to directory
global files_in_dir 
files_in_dir = os.listdir(path_to_dir)# get list of files in the directory

# 2. Set up GUI Tkinter while loop

videochoice = tk.Tk()  #Makes main window

my_screen_width = videochoice.winfo_screenwidth() #get the user screen size
my_screen_height = videochoice.winfo_screenheight()

videochoice.wm_title("Video selection")
videochoice.config(background="#FFFFFF")
tk.Label(videochoice, text="Choose your video :",font=("Helvetica", 16),width=60,).grid(row=0)

# 2. Function for the Tk loop
def Change_video(): # change video : simply destroy show video window
    screenim.destroy()

def Ok_video(): # if this video selected : save the name of the video
    global files_in_dir
    global video_number
    with open('data/binary/name_video.txt','wb') as f:
       pickle.dump(path_to_dir+'/'+files_in_dir[video_number],f) #name writted in binary file
    f.close()
    screenim.destroy() #destroy all Tk window
    videochoice.destroy()
    
    
def Show_frame(): #display the video to the user, so that he is sure of what video he choose
    global files_in_dir
    global cap
    global im_w
    global im_h
    global lmain
    global screenim
    global video_number
    
    
    flag, frame = cap.read() #frame from video
    if flag == False: #if flag is false, it mean that the video is over
        cap = cv2.VideoCapture(path_to_dir+'/'+files_in_dir[video_number]) #so we restart it to make it loop
        flag, frame = cap.read()
    
    
    
    frame = cv2.resize(frame, tuple([int(im_w),int(im_h)]), interpolation = cv2.INTER_AREA)
    #classic convertion opencv2Tk
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(master =screenim, image=img) #display this in screenim window
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    
    lmain.after(10, Show_frame) #loop after 10 [ms] to next frame
    
def Show_video(video_indice): #launch video indicated by user
    global files_in_dir
    global cap
    global im_w
    global im_h
    global lmain
    global screenim
    global video_number
    video_number=video_indice
    #creat a new Tk window to display the video
    screenim = tk.Tk()
    screenim.wm_title("Video display")
    screenim.config(background="#FFFFFF")
    #video
    cap = cv2.VideoCapture(path_to_dir+'/'+files_in_dir[video_indice])
    im_w=cap.get(3) #video width
    im_w_original=im_w
    im_h=cap.get(4) #video height
    im_h_original=im_h
    #if the video is too big for user screen, resize it
    while(im_w +50> my_screen_width):
        im_w=im_w-im_w_original*0.1 #reduce by 10%
        im_h=im_h-im_h_original*0.1

    while(im_h+100> my_screen_height):
        im_w=im_w-im_w_original*0.1
        im_h=im_h-im_h_original*0.1
        
    #Graphics window
    imageFrame = tk.Frame(screenim, width=im_w , height=im_h)
    imageFrame.grid(row=0, column=0, padx=10, pady=2)

    #Capture video frames
    lmain = tk.Label(imageFrame)
    lmain.grid(row=0, column=0)
      
    screenim.wm_title("Video display")
    screenim.config(background="#FFFFFF")
    #button for confirm or change video
    tk.Button(screenim,text='Confirm video selection',font=("Helvetica", 16),width=40,command=Ok_video).grid(row=1)
    tk.Button(screenim,text='Change video',font=("Helvetica", 16),width=40,command=Change_video).grid(row=2)
    Show_frame()
    screenim.mainloop()
    

#creating buttons for each video name
video_indice=0
for video_name in files_in_dir:
    globals()['button_'+str(video_indice)] = tk.Button(videochoice,text=video_name,font=("Helvetica", 16),width=40, command=lambda video_indice=video_indice : Show_video(video_indice)).grid(row=video_indice+1)
    video_indice +=1

videochoice.mainloop()  #Starts Main GUi Loop
#____________________________________
#while loop finish destroy all windows and release webcam
cap.release()
#end
# --------------------------------------------------------------------------------------
