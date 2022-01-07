# Python image tracking and analysis 2021
# Code developer :
# Tony Govoni
#_________________________________________

# Settings_configuration : The goal of this script is to let the user tune the tracking parameters and display
# the live result on his video.
#_________________________________________

# Importing package
import numpy as np
import cv2
import tkinter as tk
import pickle
import PIL
from PIL import Image
from PIL import ImageTk
import math
#_________________________________________

# 1. Get back video name
global name_video
with open ('data/binary/name_video.txt', 'rb') as f:
    name_video= pickle.load(f)
f.close()

#_________________________________________

# 2. Tracking settings

# 2.1 Outside loop variable declaration

global color_choice #the color that the user want to tune
color_choice=''

# 2.2 Tkinter GUI
global cap
cap = cv2.VideoCapture(name_video)
im_w=cap .get(3)
im_h=cap .get(4)
im_w_original=im_w
im_h_original=im_h

window = tk.Tk()  #Makes main window
my_screen_width = window.winfo_screenwidth() #get the user screen size
my_screen_height = window.winfo_screenheight()

global screenreduction
screenreduction=0

#if the video is too big for user screen then resize it
while(im_w +300> my_screen_width):
    im_w=im_w-im_w_original*0.1 #reduce by 10%
    im_h=im_h-im_h_original*0.1

while(im_h+380> my_screen_height):
    im_w=im_w-im_w_original*0.1
    im_h=im_h-im_h_original*0.1


window.wm_title("Tracking settings")
window.config(background="#FFFFFF")
window.geometry(str(int(im_w+266))+'x'+str(int(im_h)+380)) #geometry in function of the video size

color_button_w=10 #General width used for the color button

#Graphics window
imageFrame = tk.Frame(window, width=im_w, height=im_h)
imageFrame.pack()
imageFrame.place(x=135,y=0)

#Capture video frames
lmain = tk.Label(imageFrame)
lmain.pack()
lmain.place(x=0,y=0)


# 2.3.1 V for value  [0,255]

global value
value= 60 # set low to accepte dark object to be tracked

# 2.3.2 S for saturation [0,255]

global saturation
saturation= 100 # set low to accepte poor color

# 2.3.3 H for hue (is a parameter that define a color) [0,180]

# this is the sample of color that we want to track
all_color=     ['g',   'r',   'b',   'o',     'y',     'v',     'p',   'c']
all_color_name=['green','red','blue','orange','yellow','purple','pink','cyan']

#green #[50,80]
global g_lvl_up # for example the green color boundary for the hue are set to
g_lvl_up =80    #[50,80]
global g_lvl_down
g_lvl_down =64

global code_g
code_g=(0,180,0) #this is a BGR code used to represent the color in plot 

#blue #[100,130]
global b_lvl_up
b_lvl_up = 130
global b_lvl_down
b_lvl_down =100

global code_b
code_b=(180,0,0)

#red #[170,180] # be carfull, red is defined in two interval in HSV
global r_lvl_up
r_lvl_up = 180
global r_lvl_down
r_lvl_down =170

global code_r
code_r=(0,0,255)

#orange #[10,23]
global o_lvl_up
o_lvl_up = 23
global o_lvl_down
o_lvl_down =10

global code_o
code_o=(14,201,255)

#yellow #[28,32]
global y_lvl_up
y_lvl_up = 32
global y_lvl_down
y_lvl_down =28

global code_y
code_y=(0,242,255)

#purple (use letter 'v' because 'p' is used for pink) #[135,145]
global v_lvl_up
v_lvl_up = 145
global v_lvl_down
v_lvl_down =135

global code_v
code_v=(234,4,136)

#pink #[146,160]
global p_lvl_up
p_lvl_up = 160
global p_lvl_down
p_lvl_down =146

global code_p
code_p=(236,2,236)

#cyan #[87,93]
global c_lvl_up
c_lvl_up = 93
global c_lvl_down
c_lvl_down =87

global code_c
code_c=(255,255,0)

# 2.4 Tracking and main show_frame loop

# Minimal size for an object to be track
global minimal_size
minimal_size = 20 #this size is in pixels

color_to_track=[] # the list in which the user add the color he want to track

def show_frame(): # #show_frame is used to display the image and show the tracked object
    global cap 
    #color to track check :
    for color in all_color: # fo all colors if user check the box to track the color
        if color not in color_to_track: #add it to the track list
            if globals()[color+'_check'].get() ==True :
                color_to_track.append(color)
        else : #remove it 
            if color in color_to_track:
                if globals()[color+'_check'].get() ==False :
                    color_to_track.remove(color)


    flag, frame = cap.read() #frame from video
    if flag == False: # if flag is false it mean that no more frame is available in the video
        cap = cv2.VideoCapture(name_video) #so restart the capture to make the video loop
        flag, frame = cap.read()
    
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #convert to HSV

    # Threshold the HSV image to get the colors that are in specific range [H down, S,V] to [H up,255,255]
    for color in color_to_track:                                                
        globals()['mask_'+color] = cv2.inRange(cv2image,\
        (globals()[color+'_lvl_down'],saturation,value),\
        (globals()[color+'_lvl_up'],255,255))

    #contouring in the image for different colors
    for color in color_to_track:
        globals()['contours_'+color],globals()['hierarchy_'+color] =\
        cv2.findContours(globals()['mask_'+color],var_algo_choice.get(),\
        cv2.CHAIN_APPROX_SIMPLE)

    #even if no object tracked, display rectcont (the image)
    rectcont=frame

    #for every color contours find in the image draw a rectangle
    for color in color_to_track:
        for cnt in globals()['contours_'+color]:
            ((center_x,center_y),size_rect,angle) = cv2.minAreaRect(cnt)
            if size_rect[0] >minimal_size and size_rect[1] >minimal_size :
            #filter to eliminate noise that make small rectangle
            
                rect = ((center_x,center_y),size_rect,angle) #each rectangle contour has a give center,size and angle
                box = cv2.boxPoints(rect) #create the rectangle found
                box = np.int0(box)
                rectcont=cv2.drawContours(frame,[box],0,\
                globals()['code_'+color],8) #draw it on the drame in the right color code

    #resize the image so that it can be desplayed one the user screen
    rectcont = cv2.resize(rectcont, tuple([int(im_w),int(im_h)]), interpolation = cv2.INTER_AREA)
    #classic opencv to Tk image conversion
    rectcont = cv2.cvtColor(rectcont, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(rectcont)
    
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(50, show_frame) #show next frame in 10 [ms]


# 2.5 Tk button and variable for tune the tracking

#color selection
tk.Label(window, text = 'Color to track : ',font=("Helvetica", 14)).place(x=1,y=0)
#bool variable
for color in all_color:
    globals()[color+'_check'] = tk.IntVar()

#check button variable (many can be choose)
greenC = tk.Checkbutton(window, text = "green",fg= "green", variable = g_check, onvalue = 1, offvalue = 0,width = color_button_w,font=("Helvetica", 12),height=2)
redC = tk.Checkbutton(window, text = "red",fg= "red", variable = r_check, onvalue = 1, offvalue = 0,width = color_button_w,font=("Helvetica", 12),height=2)
blueC = tk.Checkbutton(window, text = "blue",fg= "blue", variable = b_check, onvalue = 1, offvalue = 0,width = color_button_w,font=("Helvetica", 12),height=2)
orangeC = tk.Checkbutton(window, text = "orange",fg= "orange", variable = o_check, onvalue = 1, offvalue = 0,width = color_button_w,font=("Helvetica", 12),height=2)
yellowC = tk.Checkbutton(window, text = "yellow",fg= "yellow", variable = y_check, onvalue = 1, offvalue = 0,width = color_button_w,font=("Helvetica", 12),height=2)
purpleC = tk.Checkbutton(window, text = "purple",fg= "purple", variable = v_check, onvalue = 1, offvalue = 0,width = color_button_w,font=("Helvetica", 12),height=2)
pinkC = tk.Checkbutton(window, text = "pink",fg= "pink", variable = p_check, onvalue = 1, offvalue = 0,width = color_button_w,font=("Helvetica", 12),height=2)
cyanC = tk.Checkbutton(window, text = "cyan",fg= "cyan", variable = c_check, onvalue = 1, offvalue = 0,width = color_button_w,font=("Helvetica", 12),height=2)

#check button placing each time  + 27 pixel in the y direction for the next button
greenC.pack()
greenC.place(x=8,y=30)

redC.pack()
redC.place(x=8,y=30 +48*1)

blueC.pack()
blueC.place(x=8,y=30 +48*2)

orangeC.pack()
orangeC.place(x=8,y=30 +48*3)

yellowC.pack()
yellowC.place(x=8,y=30 +48*4)

purpleC.pack()
purpleC.place(x=8,y=30 +48*5)

pinkC.pack()
pinkC.place(x=8,y=30 +48*6)

cyanC.pack()
cyanC.place(x=8,y=30 +48*7)

#Variable button to chose wich color upper and lower bound the user want to tune

#color selection
tk.Label(window, text = 'Color to tune : ',font=("Helvetica", 14)).place(x=im_w+138,y=0)

def selection(): #selection is used to select a color H parameter that the user want to tune
    color_choice=var_color_choice.get()
    global index_color
    index_color=all_color.index(color_choice)
    tk.Label(window, text = '['+str(globals()[color_choice+'_lvl_down'])+\
    ','+str(globals()[color_choice+'_lvl_up'])+']',font=("Helvetica", 14),\
    fg=all_color_name[index_color],width=20,height=2).place(\
        x=135+im_w/2-118,y=im_h+120)

#radio variable ( only one can be choose)
var_color_choice = tk.StringVar()

greenR = tk.Radiobutton(window, text="green",fg="green", variable=var_color_choice, value='g',command=selection,width = color_button_w,font=("Helvetica", 12),height=2)
redR = tk.Radiobutton(window, text="red",fg="red", variable=var_color_choice, value='r',command=selection,width = color_button_w,font=("Helvetica", 12),height=2)
blueR = tk.Radiobutton(window, text="blue",fg="blue", variable=var_color_choice, value='b',command=selection,width = color_button_w,font=("Helvetica", 12),height=2)
orangeR = tk.Radiobutton(window, text="orange",fg="orange", variable=var_color_choice, value='o',command=selection,width = color_button_w,font=("Helvetica", 12),height=2)
yellowR = tk.Radiobutton(window, text="yellow",fg="yellow", variable=var_color_choice, value='y',command=selection,width = color_button_w,font=("Helvetica", 12),height=2)
purpleR = tk.Radiobutton(window, text="purple",fg="purple", variable=var_color_choice, value='v',command=selection,width = color_button_w,font=("Helvetica", 12),height=2)
pinkR = tk.Radiobutton(window, text="pink",fg="pink", variable=var_color_choice, value='p',command=selection,width = color_button_w,font=("Helvetica", 12),height=2)
cyanR = tk.Radiobutton(window, text="cyan",fg="cyan", variable=var_color_choice, value='c',command=selection,width = color_button_w,font=("Helvetica", 12),height=2)



#radio button placing

greenR.pack()
greenR.place(x=im_w+140,y=30)

redR.pack()
redR.place(x=im_w+140,y=30+48)

blueR.pack()
blueR.place(x=im_w+140,y=30+48*2)

orangeR.pack()
orangeR.place(x=im_w+140,y=30+48*3)

yellowR.pack()
yellowR.place(x=im_w+140,y=30+48*4)

purpleR.pack()
purpleR.place(x=im_w+140,y=30+48*5)

pinkR.pack()
pinkR.place(x=im_w+140,y=30+48*6)

cyanR.pack()
cyanR.place(x=im_w+140,y=30+48*7)



# value saturation and color threshold tunning

tk.Label(window, text = 'Color Threshold tunning : ',font=("Helvetica", 14),width=20).place(x=135+im_w/2-115,y=im_h+85)
tk.Label(window, text = '-',font=("Helvetica", 14),width=20,height=2).place(x=135+im_w/2-118,y=im_h+120)

#color H control
# each function here simply increase or decrease a variable on the press of buttons and display the change
def color_up_plus():
    color_choice=var_color_choice.get()
    globals()[color_choice+'_lvl_up']+=2
    if globals()[color_choice+'_lvl_up']>180: #upper bound limit
        globals()[color_choice+'_lvl_up']=180
    tk.Label(window, text = '['+str(globals()[color_choice+'_lvl_down'])\
    +','+str(globals()[color_choice+'_lvl_up'])+']',font=("Helvetica",\
    14),fg=all_color_name[index_color],width=20,height=2).place(\
    x=135+im_w/2-118,y=im_h+120)
    
def color_up_minus():
    color_choice=var_color_choice.get()
    globals()[color_choice+'_lvl_up']-=2
    #dont allow lvl up to be lower than lvl down
    if globals()[color_choice+'_lvl_up'] <= globals()[color_choice+'_lvl_down']:
        globals()[color_choice+'_lvl_up']=globals()[color_choice+'_lvl_down']+1
    tk.Label(window, text = '['+str(globals()[color_choice+'_lvl_down'])\
    +','+str(globals()[color_choice+'_lvl_up'])+']',font=("Helvetica",\
    14),fg=all_color_name[index_color],width=20,height=2).place(\
    x=135+im_w/2-118,y=im_h+120)
def color_down_plus():
    color_choice=var_color_choice.get()
    globals()[color_choice+'_lvl_down']+=2
    #dont allow lvl down to be upper than lvl up
    if globals()[color_choice+'_lvl_down'] >= globals()[color_choice+'_lvl_up']:
        globals()[color_choice+'_lvl_down']=globals()[color_choice+'_lvl_up']-1

    tk.Label(window, text = '['+str(globals()[color_choice+'_lvl_down'])\
    +','+str(globals()[color_choice+'_lvl_up'])+']',font=("Helvetica",\
    14),fg=all_color_name[index_color],width=20,height=2).place(
    x=135+im_w/2-118,y=im_h+120)
def color_down_minus():
    color_choice=var_color_choice.get()
    globals()[color_choice+'_lvl_down']-=2
    if globals()[color_choice+'_lvl_down']<0: #lower bound limit
        globals()[color_choice+'_lvl_down']=0
    tk.Label(window, text = '['+str(globals()[color_choice+'_lvl_down'])\
    +','+str(globals()[color_choice+'_lvl_up'])+']',font=("Helvetica",\
    14),fg=all_color_name[index_color],width=20,height=2).place(\
    x=135+im_w/2-118,y=im_h+120)

#color H button placing

color_up_plusB=tk.Button(text = u"\u25B2",command=color_up_plus)
color_up_minusB=tk.Button(text = u"\u25BC",command=color_up_minus)

color_down_plusB=tk.Button(text = u"\u25B2",command=color_down_plus)
color_down_minusB=tk.Button(text = u"\u25BC",command=color_down_minus)

color_up_plusB.pack()
color_up_plusB.place(x=135+im_w/2+109,y=im_h+119)
color_up_minusB.pack()
color_up_minusB.place(x=135+im_w/2+109,y=im_h+144)

color_down_plusB.pack()
color_down_plusB.place(x=135+im_w/2-141,y=im_h+119)
color_down_minusB.pack()
color_down_minusB.place(x=135+im_w/2-141,y=im_h+144)

#value and saturation

tk.Label(window, text = 'Value and saturation (Lower bound): ',font=("Helvetica", 14),width=29).place(x=135+im_w/2-162,y=im_h)


#value label
tk.Label(window, text = 'value : '+str(value),font=("Helvetica", 14),width=9,height=2).place(x=135+im_w/2-130,y=im_h+30)

#value
def value_up():# each function here simply increase or decrease a variable on the press of buttons and display the change
    global value
    value=value+5
    if value >255:
        value=255
    value_label =tk.Label(window, text = 'value : '+str(value),font=("Helvetica", 14),width=9,height=2).place(x=135+im_w/2-130,y=im_h+30) 
    

def value_down():
    global value
    value=value-5
    if value <0:
        value=0
    value_label =tk.Label(window, text = 'value : '+str(value),font=("Helvetica", 14),width=9,height=2).place(x=135+im_w/2-130,y=im_h+30)
#value button
valueupB = tk.Button(text = u"\u25B2", command=value_up)
valuedownB = tk.Button(text = u"\u25BC", command=value_down)



#saturation label
tk.Label(window, text = 'sat. : '+str(saturation),font=("Helvetica", 14),width=9,height=2).place(x=135+im_w/2+10,y=im_h+30)

#saturation
def sat_up():# each function here simply increase or decrease a variable on the press of buttons and display the change
    global saturation
    saturation=saturation+5
    if saturation >255:
        saturation=255
    saturation_label =tk.Label(window, text = 'sat. : '+str(saturation),font=("Helvetica", 14),width=9,height=2).place(x=135+im_w/2+10,y=im_h+30)
    

def sat_down():
    global saturation
    saturation=saturation-5
    if saturation <0:
        saturation=0
    saturation_label =tk.Label(window, text = 'sat. : '+str(saturation),font=("Helvetica", 14),width=9,height=2).place(x=135+im_w/2+10,y=im_h+30)


#saturation button
satupB = tk.Button(text = u"\u25B2", command=sat_up)
satdownB = tk.Button(text = u"\u25BC", command=sat_down)


#value and saturation button placing
valueupB.pack()
valueupB.place(x=135+im_w/2-25,y=im_h+29)
valuedownB.pack()
valuedownB.place(x=135+im_w/2-25,y=im_h+54)

satupB.pack()
satupB.place(x=135+im_w/2+115,y=im_h+29)
satdownB.pack()
satdownB.place(x=135+im_w/2+115,y=im_h+54)

#Size label
tk.Label(window, text = 'Suppress tracking for object smaller than : '+str(minimal_size)+' pixles',font=("Helvetica", 14),width=40,height=2).place(x=155+im_w/2-255,y=im_h+180)

def size_up():# each function here simply increase or decrease a variable on the press of buttons and display the change
    global minimal_size
    minimal_size=minimal_size+1
    minimal_size_label =tk.Label(window, text = 'Supress tracking for object smaller than : '+str(minimal_size)+' pixles',font=("Helvetica", 14),width=40,height=2).place(x=155+im_w/2-255,y=im_h+180)
    
def size_down():
    global minimal_size
    minimal_size=minimal_size-1
    if minimal_size<0:
        minimal_size=0
    minimal_size_label =tk.Label(window, text = 'Supress tracking for object smaller than : '+str(minimal_size)+' pixles',font=("Helvetica", 14),width=40,height=2).place(x=155+im_w/2-255,y=im_h+180)

# size button
sizeupB = tk.Button(text = u"\u25B2", command=size_up)
sizedownB = tk.Button(text = u"\u25BC", command=size_down)
# size button placing
sizeupB.pack()
sizeupB.place(x=137+im_w/2+205,y=im_h+179)
sizedownB.pack()
sizedownB.place(x=137+im_w/2+205,y=im_h+204)

#Flow direction
global flow_orientation
flow_orientation = "right"
flow_label = tk.Label(window, text = 'Flow direction : '+str(flow_orientation),font=("Helvetica", 14),width=20).place(x=435+im_w/2-115,y=im_h+50)
def flow_orientation_r():
    global flow_orientation
    flow_orientation = "right"
    flow_label = tk.Label(window, text = 'Flow direction : '+str(flow_orientation),font=("Helvetica", 14),width=20).place(x=435+im_w/2-115,y=im_h+50)
def flow_orientation_l():
    global flow_orientation
    flow_orientation = "left"
    flow_label = tk.Label(window, text = 'Flow direction : '+str(flow_orientation),font=("Helvetica", 14),width=20).place(x=435+im_w/2-115,y=im_h+50)

flow_right = tk.Button(text = "right", command=flow_orientation_r)
flow_left = tk.Button(text = "left", command=flow_orientation_l)
# flow button placing
flow_right.pack()
flow_right.place(x=435+im_w/2-0,y=im_h+78)
flow_left.pack()
flow_left.place(x=435+im_w/2-30,y=im_h+78)
# 2.6 Contour algorithm choice

#radio variable ( only one can be choose)
var_algo_choice = tk.IntVar()
#radio button
ExternalR = tk.Radiobutton(window, text="Ext.", variable=var_algo_choice, value=0,width = color_button_w,font=("Helvetica", 13),height=2)
ListR = tk.Radiobutton(window, text="List", variable=var_algo_choice, value=1,width = color_button_w,font=("Helvetica", 13),height=2)
#radio button placing and label

tk.Label(window, text = 'Contour algo : ',font=("Helvetica", 14),width=12,height=2).place(x=137+im_w/2-200,y=im_h+240)
ExternalR.pack()
ExternalR.place(x=137+im_w/2-50,y=im_h+240)
ListR.pack()
ListR.place(x=137+im_w/2+75,y=im_h+240)
# 2.7 Tk setting exit and save

def Quit_prog():    #if the user confirm to quit setting
    
    #save all the settings into the binary directory

    #value
    with open ('data/binary/Settings/value.txt', 'wb') as f:
        pickle.dump(value,f)
    f.close()
    #saturation
    with open ('data/binary/Settings/saturation.txt', 'wb') as f:
        pickle.dump(saturation,f)
    f.close()
    #minimalsize
    with open ('data/binary/Settings/minimal_size.txt', 'wb') as f:
        pickle.dump(minimal_size,f)
    f.close()
   #contour_algo
    with open ('data/binary/Settings/contour_algo.txt', 'wb') as f:
        pickle.dump(var_algo_choice.get(),f)
    f.close()
    #flow orientation
    with open ('data/binary/Settings/flow_orientation.txt', 'wb') as f:
        pickle.dump(flow_orientation,f)
    f.close()
    
    
    #color we want to track + upper and lower bound + the BGR corresponding code
    with open ('data/binary/Settings/color_to_track.txt', 'wb') as f:
        pickle.dump(color_to_track,f)
    f.close()    
    #+upper and lower bound + the BGR corresponding code
    for color in color_to_track:
        with open ('data/binary/Settings/'+color+'_lvl_up.txt', 'wb') as f:
            pickle.dump(globals()[color+'_lvl_up'],f)
        f.close()
        with open ('data/binary/Settings/'+color+'_lvl_down.txt', 'wb') as f:
            pickle.dump(globals()[color+'_lvl_down'],f)
        f.close()
        with open ('data/binary/Settings/code_'+color+'.txt', 'wb') as f:
            pickle.dump(globals()['code_'+color],f)
        f.close()

    #then destroy the tk windows
    exitwindow.destroy()
    window.destroy()

def Exit(): #open a window to confirm the color you want to track and confirm you want to stop tunning trakcing parameters
    global exitwindow
    global end_program_bool
    #start tk window loop for exit menu
    exitwindow = tk.Tk()
    exitwindow.wm_title("Settings confirmation")
    tk.Label(exitwindow, text="Save settings and track the folowing colors : ?",font=("Helvetica", 14),width=50,height=1).grid(row=0)
    color_texte_selection='' 
    for color in color_to_track: #get all color the user choose
        color_texte_selection += (all_color_name[all_color.index(color)] +', ')
    #display the choice
    tk.Label(exitwindow, text=color_texte_selection,font=("Helvetica", 14),width=50,height=1).grid(row=1)
    tk.Button(exitwindow,text='OK',font=("Helvetica", 14),width=50,height=1, command=Quit_prog).grid(row=2, sticky=tk.W, pady=4)
#button for exit
exitB= tk.Button(text = 'Save settings',font=("Helvetica", 16),width=20, command=Exit)
exitB.pack()
exitB.place(x=137+im_w/2-134,y=im_h+300)

show_frame()  #Display the frame
window.mainloop()  #Starts tkinter loop
#____________________________________

# 3. Calibration


# 3.1 Screen shot of the video

#start a new tk (very similar but simplier to the setting one)
screenim = tk.Tk()  
screenim.wm_title("Length calibration")
screenim.config(background="#FFFFFF")

#Graphics window
imageFrame = tk.Frame(screenim, width=im_w , height=im_h)
imageFrame.grid(row=0, column=0, padx=10, pady=2)

#Capture video frames
lmain = tk.Label(imageFrame)
lmain.grid(row=0, column=0)

def show_frame(): #same show frame but without the tracking
    global name_video
    global cap
    flag, frame = cap.read() #frame from video
    if flag == False:
        cap = cv2.VideoCapture(name_video)
        flag, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    cv2image = cv2.resize(cv2image, tuple([int(im_w),int(im_h)]), interpolation = cv2.INTER_AREA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame) 
def Screen_shot(): #let the user take a screen shoot for the calibration
    _, frame = cap.read()
    im_w=cap .get(3)
    im_h=cap .get(4)

    #give the user the biggest frame possible
    global screenreduction
    while(im_w > my_screen_width):
        im_w=im_w-im_w_original*0.1
        im_h=im_h-im_h_original*0.1
        screenreduction+=0.1
        
    while(im_h+100> my_screen_height):
        im_w=im_w-im_w_original*0.1
        im_h=im_h-im_h_original*0.1

    frame=cv2.resize(frame, tuple([int(im_w),int(im_h)]), interpolation = cv2.INTER_AREA)
    cv2.imwrite('data/binary/Settings/Cal_im.jpg', frame) #save this image
    screenim.destroy() 
    
exitB= tk.Button(text = 'Screen shot for length calibration',font=("Helvetica", 16),width=25, command=Screen_shot)
exitB.grid(row=1)
show_frame()
screenim.mainloop()

# 3.2 Draw line

#let the user draw a line on the screen shot to calibrate the length in the image

def vp_start_gui(): #start a tk loop
    global artist_loop
    artist_loop= tk.Tk()
    artist_loop.wm_title("Length draw")
 
    def Enter_L(): #let the user enter a length in a box
        global enterL
        enterL=tk.Tk()
        enterL.wm_title("Enter Length")
        tk.Label(enterL, text="Enter length in [m] :",font=("Helvetica", 14),width=20,height=1).grid(row=0)
        global L
        L = tk.Entry(enterL)
        L.grid(row=0, column=1)
        tk.Button(enterL,text='Save', command=Quit_prog).grid(row=2, column=1, sticky=tk.W, pady=4)
        
        enterL.mainloop()
        
    def Quit_prog(): #quit script and save the calibration

        #save the length of the segment in pixel
        global x1,x2,y1,y2
        global L
        global screenreduction

        #remember that we resize the image, so if we apply a screen reduction take it in account for the calibration
        if screenreduction==0:
            calibration_length= (float(L.get())/math.sqrt(((x2-x1)**2 + (y2-y1)**2))) #[m/pixel]
        else:
            calibration_length= (float(L.get())*(1-screenreduction)/((math.sqrt(((x2-x1)**2 + (y2-y1)**2))))) #[m/pixel]

        # save the calibration in a binary file
        with open ('data/binary/Settings/cal_len.txt', 'wb') as f:
            pickle.dump(calibration_length,f)
        f.close()
        global enterL
        global exitwindow
        #destroy all tk loop
        enterL.destroy()
        exitwindow.destroy()
        artist_loop.destroy()


    def check_draw(): #if the user is ok with his draw
        global exitwindow
        exitwindow = tk.Tk()
        exitwindow.wm_title("Length draw")
        tk.Label(exitwindow, text="Calibration ok ?",font=("Helvetica", 14),width=20,height=1).grid(row=0)
        tk.Button(exitwindow,text='Reset',font=("Helvetica", 14),width=20,height=1, command=refresh).grid(row=2, sticky=tk.W, pady=4)
        tk.Button(exitwindow,text='OK',font=("Helvetica", 14),width=20,height=1, command=Enter_L).grid(row=3, sticky=tk.W, pady=4)

    def draw_line(event): #when the user click on the tk window, draw something
        global click_number
        global x1,y1,x2,y2
        if click_number==0:
            x1=event.x
            y1=event.y
            click_number=1
            my_art.create_oval(x1-3,y1-3,x1+3,y1+3,fill='blue') #draw the first point
        else:
            x2=event.x
            y2=event.y
            my_art.create_oval(x2-3,y2-3,x2+3,y2+3,fill='blue') #draw the second point
            my_art.create_line(x1,y1,x2,y2,fill='blue',width=3) #draw the line between the two point
            click_number=0
            check_draw()
            
    #general tk window configuration
    my_art = tk.Canvas(artist_loop, width=im_w_original*(1-screenreduction),height=im_h_original*(1-screenreduction))
    image = ImageTk.PhotoImage(file = "data/binary/Settings/Cal_im.jpg")
    my_art.create_image(im_w_original*(1-screenreduction)/2, im_h_original*(1-screenreduction)/2, image = image)
    tk.Label(artist_loop, text="Draw a line of known length",font=("Helvetica", 14),width=20,height=1).grid(row=0)
    my_art.grid(row=1)
    my_art.bind('<Button-1>',draw_line)

    global click_number
    click_number=0
    artist_loop.mainloop()

if __name__ == '__main__':
    def refresh(): # refresh / restart the whole tk loop if user is not satisfy with is drawing
        global exitwindow
        exitwindow.destroy()
        global artist_loop
        artist_loop.destroy()
        vp_start_gui()
    

    vp_start_gui()

#____________________________________
#release capture
cap.release()
#end
# --------------------------------------------------------------------------------------
