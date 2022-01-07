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
import PySimpleGUI as sg
import time
#_________________________________________

# 1. Construction of directory checkpoint

retval = os.getcwd() # main script directoy : python script

path_data =retval+"/data" # frame directoy : data

path_binary=path_data+"/binary" # frame directoy : binary
#_________________________________________

# 2. Get back video name
global name_video
with open ('data/binary/name_video.txt', 'rb') as f:
    name_video= pickle.load(f)
f.close()
# 2.1 video properties
cap = cv2.VideoCapture(name_video)
numberframe=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) #get number of frame
fps=cap.get(cv2.CAP_PROP_FPS)#get fps of the video
# time_of_record
time_of_record = (numberframe-1)/fps
#video size
original_im_w=cap.get(3)
original_im_h=cap.get(4)

#_________________________________________

# 2.2 Get back tracking variable
os.chdir(path_binary) # directory change for binary


# get back data range of color wanted to track in HSV
with open ('Settings/color_to_track.txt', 'rb') as f:
    color_to_track= pickle.load(f)
f.close

# light
with open ('Settings/value.txt', 'rb') as f:
    light= pickle.load(f)
f.close

# saturation
with open ('Settings/saturation.txt', 'rb') as f:
    saturation= pickle.load(f)
f.close
# minimal_size
with open ('Settings/minimal_size.txt', 'rb') as f:
    minimal_size= pickle.load(f)
f.close
#contour_algo
with open ('Settings/contour_algo.txt', 'rb') as f:
    contour_algo= pickle.load(f)
f.close()

# calibration [m/pixel] ratio
with open ('Settings/cal_len.txt', 'rb') as f:
    cal_len= pickle.load(f)
f.close
#every color we want to track settings
for color in color_to_track:
    with open ('Settings/'+color+'_lvl_up.txt', 'rb') as f:
        globals()[color+'_lvl_up']= pickle.load(f)
    f.close()
    with open ('Settings/'+color+'_lvl_down.txt', 'rb') as f:
        globals()[color+'_lvl_down']= pickle.load(f)
    f.close()
    with open ('Settings/code_'+color+'.txt', 'rb') as f:
        globals()['code_'+color]= pickle.load(f)
    f.close()

# define array to stock data from each frame for each color
for color in color_to_track:
    globals()['size_'+color]=[]
    globals()['pos_'+color]=[]
    globals()['angle_'+color]=[]
    globals()['number_'+color]=[]
   
#_________________________________________
    
# 3 Tracking
os.chdir(path_data) # directory change for data

# variable to stock the frame when the tracking fail
for color in color_to_track:
    globals()['fail_to_track_'+color]=[]

frame_liste=[]
# 
for number in range(int(numberframe)):
    frame_liste.append(number)
    
# 3.1 Image from video

#Load image in data frame and loop them
for number, item in enumerate(frame_liste):# get frame by frame
    # Capture frame-by-frame
    ret, im = cap.read()
    name = 'frame'+str(number)+'.jpg'
    cv2.imwrite(name, im) #write each frame
    #progression bar 
    sg.one_line_progress_meter('Importing image from video', number+1, len(frame_liste), '-key-')

# 3.2 Track object in each frame
for number, item in enumerate(frame_liste):# get frame by frame 

    name = 'frame'+str(number)+'.jpg'
    im =cv2.imread(name)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get the colors that are in specific range
    for color in color_to_track:
        globals()['mask_'+color] = cv2.inRange(hsv,\
        (globals()[color+'_lvl_down'],saturation,light),\
        (globals()[color+'_lvl_up'],255,255))

    #contouring in the image for different colors
    for color in color_to_track:
        globals()['contours_'+color],globals()['hierarchy_'+color] =\
        cv2.findContours(globals()['mask_'+color],contour_algo,\
        cv2.CHAIN_APPROX_SIMPLE)

    #for every color contours, find the biggest rectangle
    for color in color_to_track:
        object_found_image=0
        for cnt in globals()['contours_'+color]: #for every contour found for one color
            ((center_x,center_y),size_rect,angle) = cv2.minAreaRect(cnt)

            if size_rect[0] >minimal_size and size_rect[1] >minimal_size:#filter to eliminate noise that forme small rectangle
                object_found_image+=1
                globals()['size_'+color].append(size_rect)
                globals()['pos_'+color].append((center_x,center_y))
                globals()['angle_'+color].append(angle)
            
                #draw principle contour and save this image to check futur ploted data
                
                '''
                box = cv2.boxPoints(((center_x,center_y),size_rect,angle))
                box = np.int0(box)
                rectcont=cv2.drawContours(im,[box],0,globals()['code_'+color],5)
                name_contour = 'binary/tracked' + str(number) +'_'+color+'_'+str(object_found_image) +'.jpg'
                cv2.imwrite(name_contour, rectcont)
                '''
                
        #if no object, the data of the frame is not exploitable and
        #we must not use it
        if object_found_image == 0:
          
            globals()['fail_to_track_'+color].append(number)
            globals()['size_'+color].append((-1,-1))
            globals()['pos_'+color].append((-1,-1))
            globals()['angle_'+color].append(0)
            globals()['number_'+color].append(-1)
        else:
            globals()['number_'+color].append(object_found_image) #-1 is the signe of not found
    #progression bar
    sg.one_line_progress_meter('Computing contours', number+1, len(frame_liste), '-key-')

#kick double


#for some frame multiple big rectangle have been found, because sometimes
#the big object is divided in half(or more) by something in the fied of view
#we make an interpolation to found the real center position of the object
#using vector and size of each subrectangle

# vector norm
def norm_vec(vector):
    return math.sqrt((vector[0]**2 + vector[1]**2))
#find which size is the longer
def find_big_len(size):
    if size[0]>size[1]:
        return size[0]
    else:
        return size[1]
def find_small_len(size):
    if size[0]>size[1]:
        return size[1]
    else:
        return size[0]
# angle between two vectors in degree
def angle_of_vectors(a,b):
    
     dotProduct = a[0]*b[0] + a[1]*b[1]
     
     modOfVector1 = math.sqrt(a[0]**2 +a[1]**2)*math.sqrt(b[0]**2 + b[1]**2 )

     cos_theta = dotProduct/modOfVector1
     angleInDegree = math.degrees(math.acos(cos_theta))

     return angleInDegree
# cos of the angle between two vectors
def angle_of_vectors_cos(a,b):
    
     dotProduct = a[0]*b[0] + a[1]*b[1]
     
     modOfVector1 = math.sqrt(a[0]**2 +a[1]**2)*math.sqrt(b[0]**2 + b[1]**2 )

     cos_theta = dotProduct/modOfVector1

     return cos_theta

def New_rectangle(rec_1_center,rec_2_center,rec_1_sz,rec_2_sz,angle2):
    #first construction of the vector between center 1 and 2
    vec =[rec_2_center[0]-rec_1_center[0],rec_2_center[1]-rec_1_center[1]]
    # unit vector between center 1 and 2
    vec_n = [vec[0]/norm_vec(vec),vec[1]/norm_vec(vec)]
    #determine whiche lenght is the bigger:
    rec_1_L=find_big_len(rec_1_sz)
    rec_2_L=find_big_len(rec_2_sz)
    #determine whiche lenght is the smaller:
    rec_1_l=find_small_len(rec_1_sz)
    rec_2_l=find_small_len(rec_2_sz)
    #determine the angle with respect to the origin
    angle_respect_x_axis=angle_of_vectors([1,0],vec_n)
    cos_respect_y_axis=angle_of_vectors_cos([0,-1],vec_n)
    if cos_respect_y_axis <0:
        angle_origin= angle_respect_x_axis
    else:
        angle_origin= -angle_respect_x_axis
        
    #edge of the mean rectangle construction
    edge1=[rec_1_center[0]-(vec_n[0]*rec_1_L/2),\
    rec_1_center[1]-(vec_n[1]*rec_1_L/2)]
    edge2=[rec_2_center[0]+(vec_n[0]*rec_2_L/2),\
    rec_2_center[1]+(vec_n[1]*rec_2_L/2)]
    #mean rectangle computed properties
    new_size_x=norm_vec([edge2[0]-edge1[0],edge2[1]-edge1[1]])
    new_center=[edge1[0]+(vec_n[0]*new_size_x/2) ,\
    edge1[1]+(vec_n[1]*new_size_x/2)]
    new_size_y=(rec_1_l+rec_2_l)/2
    return [new_center, [new_size_x,new_size_y],angle_origin]

#angle defined from [-0,-90], detect angle jump
def angle_correction(angle2,angle1):
    if (angle2 < -67.5) and (angle1 >-22.5) : #jump from -0 to -90
        return 90 #so +90
        
    if (angle2 > -22.5) and (angle1 <-67.5) : #from -90 to -0
        return -90 #so -90
    else:
        return 0 #no change
#________________________

# 4. Data correction

# 4.1 Angle correction

#we try to find if in an image a rectangle is split in multiple section
#so that we can compute an absolute reference angle 
for color in color_to_track:
    globals()['angle_ref_'+color]=[False] #angle of reference for each color
    for number in globals()['number_'+color]:
        if number >1:
            globals()['angle_ref_'+color]=[True] #signal that an absolute angle can be compute
            globals()['angle_ref_'+color].append(\
            globals()['number_'+color].index(number)) #get the index
            break
    #then apply general angle correction
    angle_corr=90
    indice=0 #correction start for the second frame
    notfoundjump=0
    for number in globals()['number_'+color]:
        if indice==0:
            if number>0:
                indice+=number #do no correction for the first frame
            else: indice+=1
            
        elif number >1 :
            if notfoundjump==0: #dont compute if no object found in this frame
                #compute angle of correction between frame and last frame
                angle_corr =angle_corr+ angle_correction(\
                globals()['angle_'+color][indice],\
                globals()['angle_'+color][indice-1])
                
                globals()['angle_ref_'+color].append(angle_corr) #store the correction
                indice += number # indice go to next frame and not to next object
            else: #object not found in last frame
                #compute angle of correction between frame and last frame with an object
                angle_corr =angle_corr+ angle_correction(\
                globals()['angle_'+color][indice],\
                globals()['angle_'+color][indice-1-notfoundjump])
                
                globals()['angle_ref_'+color].append(angle_corr) #store the correction
                indice += number # indice go to next frame and not to next object
                #jump done so reset
                notfoundjump=0
                
                
        elif number ==1:
            if notfoundjump==0: #dont compute if no object found in this frame
                #compute angle of correction between frame and last frame
                angle_corr =angle_corr+ angle_correction(\
                globals()['angle_'+color][indice],\
                globals()['angle_'+color][indice-1])
                
                globals()['angle_ref_'+color].append(angle_corr) #store the correction
                indice += 1
            else: #object not found in last frame
                #compute angle of correction between frame and last frame with an object
                angle_corr =angle_corr+\
                angle_correction(globals()['angle_'+color][indice],\
                globals()['angle_'+color][indice-1-notfoundjump])
                
                globals()['angle_ref_'+color].append(angle_corr) #store the correction
                indice += 1
                #jump done so reset
                notfoundjump=0
            
        elif number ==-1: #not found , so dont use this angle for this computation and the next one
            notfoundjump+=1 #jump one indice
            indice += 1
 
#correction apply
for color in color_to_track:
    indice=0
    if globals()['angle_ref_'+color][0]==True:
        indicecorr=2
    if globals()['angle_ref_'+color][0]==False:
        indicecorr=1
    for number in globals()['number_'+color]:
        if number>0 :#frame correction that need one
            if indice>0:
                globals()['angle_'+color][indice] +=\
                globals()['angle_ref_'+color][indicecorr]
                indicecorr+=1
                indice +=number
        if indice==0 :#frame 0 correction if needed
            if number ==1:
                globals()['angle_'+color][0] += 0
                indice+=1
        if number==-1:
            indice+=1

#now we have corrected angle that dont make any jump at every 90°
#if there is an angle of reference, we want to know its value before it will be computed more precisly
for color in color_to_track:
    if globals()['angle_ref_'+color][0]==True:
        globals()['angle_offset_'+color]=\
        globals()['angle_'+color][globals()['angle_ref_'+color][1]]

# 4.2 Mean rectangle correction
for color in color_to_track:
    globals()['new_pos_'+color]=[]
    globals()['new_size_'+color]=[]
    globals()['new_angle_'+color]=[]
    indice=0
    indice_2=-1
    for number in globals()['number_'+color]:
        indice_2 +=1
        if number >1 :

            interp_iter=number-1 #number of interpolation
            while interp_iter !=0: #we interpolate the next (number-1) rectangle and form 2by2 a new rectangle
                                                  #(rec_1_center,                               rec_2_center,                               rec_1_sz,                                         rec_2_sz,                                 angle2)
                mean_rect=\
                New_rectangle(globals()['pos_'+color][indice+interp_iter-1],\
                globals()['pos_'+color][indice+interp_iter],\
                globals()['size_'+color][indice+interp_iter-1],\
                globals()['size_'+color][indice+interp_iter],\
                globals()['angle_'+color][indice+interp_iter])

                interp_iter-=1
                # for the next interpolation, the mean rectangle, will be rectangle_2
                #new_center
                globals()['pos_'+color][indice+interp_iter]=mean_rect[0]
                #new_size
                globals()['size_'+color][indice+interp_iter]=mean_rect[1]
                #new_angle
                globals()['angle_'+color][indice+interp_iter]=mean_rect[2]

                #point of control for the New rectangle function
                
                          
                '''
                #show on image whats going on
                im = cv2.imread('frame'+str(indice_2)+'.jpg')
                #draw principle contour and save this image to check
                box = cv2.boxPoints(tuple(mean_rect))
                box = np.int0(box)
                rectcont=cv2.drawContours(im,[box],0,globals()['code_'+color],2)
                name_contour_mean = 'binary/tracked_mean_'+str(indice_2)+'_'+color+'_'+str(number-interp_iter+1) + '.jpg'
                cv2.imwrite(name_contour_mean, rectcont)
                '''
                

            if indice == globals()['angle_ref_'+color][1]:
                globals()['angle_offset_'+color] =  mean_rect[2]- globals()['angle_offset_'+color]

            #when while loop finish store the mean rectangle
            globals()['new_pos_'+color].append(mean_rect[0])
            globals()['new_size_'+color].append(mean_rect[1])
            globals()['new_angle_'+color].append(mean_rect[2])
        else:
            globals()['new_size_'+color].append(\
            globals()['size_'+color][indice])
            globals()['new_pos_'+color].append(\
            globals()['pos_'+color][indice])
            globals()['new_angle_'+color].append(\
            globals()['angle_'+color][indice])
        if number>0:
            indice += number
        else: #if number <0 not found image
            indice +=1 #so +1 to next frame



#variable corrected 
for color in color_to_track:
    globals()['angle_'+color]=globals()['new_angle_'+color]
    globals()['size_'+color]=globals()['new_size_'+color]
    globals()['pos_'+color]=globals()['new_pos_'+color]

# and if an angle of referrence is found
for color in color_to_track:
    if globals()['angle_ref_'+color][0]==True:
        indice=0
        #then rescale all angle 
        for number in globals()['number_'+color]:
            if number==1:
                globals()['angle_'+color][indice]+=\
                globals()['angle_offset_'+color]
            indice+=1


# 5 Discret derivative

def Deriv(pos_t,pos_t_plus_dt,dt):
    return tuple([(pos_t_plus_dt[0]-pos_t[0])/dt,(pos_t_plus_dt[1]-pos_t[1])/dt])

def Deriv_angle(a_t,a_t_plus_dt,dt):
    #angle define from -180 to 0
    #jump from -180 to 180 -> -360
    if a_t<-135 and a_t_plus_dt>-45:
        return (a_t_plus_dt-a_t -180)/dt
    #jump from +180 to -180 -> +360
    if a_t>-45 and a_t_plus_dt<-135:
        return (a_t_plus_dt-a_t +180)/dt
    #if normal
    return (a_t_plus_dt-a_t)/dt

delta_time= 1/fps
#construction of the time line
timeline=[]
for i in range (0,numberframe):
    timeline.append(i*delta_time)

for color in color_to_track:
    globals()['angular_veloc_'+color]=[]
    globals()['veloc_'+color]=[]
    globals()['time_v_'+color]=[]
    indice=0
    indice2=2
    notfoundjump=0
    for number in globals()['number_'+color]:
        if indice==0:
            if number>0:
                indice+=1 #do nothing for the first frame
            else: indice+=1

        elif number >0 :
            if notfoundjump==0: #dont compute if no object found in this frame
                #compute diff between frame and last frame
                #angle
                globals()['angular_veloc_'+color].append(\
                Deriv_angle(globals()['angle_'+color][indice-1],\
                globals()['angle_'+color][indice],delta_time))
                #pos
                globals()['veloc_'+color].append(\
                Deriv(globals()['pos_'+color][indice-1],\
                globals()['pos_'+color][indice],delta_time))
                globals()['time_v_'+color].append(delta_time*indice)
                indice += 1 # indice go to next frame
            else: #object not found in last frame
                #compute diff between frame and last frame with an object
                #angle
                globals()['angular_veloc_'+color].append(\
                Deriv_angle(globals()['angle_'+color][indice-1-notfoundjump],\
                globals()['angle_'+color][indice],\
                delta_time*(1+notfoundjump)))
                #pos
                globals()['veloc_'+color].append(\
                Deriv(globals()['pos_'+color][indice-1-notfoundjump],\
                globals()['pos_'+color][indice],\
                delta_time*(1+notfoundjump)))
                
                globals()['time_v_'+color].append(delta_time*indice)
                indice += 1 # indice go to next frame
                #jump done so reset
                notfoundjump=0

        elif number ==-1: #not found , so dont use this frame for computation and the go to next one
            notfoundjump+=1 #jump one indice
            indice += 1
for color in color_to_track:
    globals()['angular_acc_'+color]=[]
    globals()['acc_'+color]=[]
    globals()['time_a_'+color]=[]
    for i in range(1,len(globals()['time_v_'+color])):
        globals()['angular_acc_'+color].append(\
        Deriv_angle(globals()['angular_veloc_'+color][i-1],\
        globals()['angular_veloc_'+color][i],\
        globals()['time_v_'+color][i]-globals()['time_v_'+color][i-1]))

        globals()['acc_'+color].append(\
        Deriv(globals()['veloc_'+color][i-1],\
        globals()['veloc_'+color][i],\
        globals()['time_v_'+color][i]-globals()['time_v_'+color][i-1]))

        globals()['time_a_'+color].append(\
        globals()['time_v_'+color][i])

#zero padding and add calibration ratio
for color in color_to_track:
    globals()['angular_acc_final_'+color]=[]
    globals()['acc_final_'+color]=[]
    globals()['angular_veloc_final_'+color]=[]
    globals()['veloc_final_'+color]=[]
    indicev=0
    indicea=0
    for t in timeline:
        time = timeline.index(t)
        if t in globals()['time_v_'+color]:
            globals()['veloc_final_'+color].append(\
            [globals()['veloc_'+color][indicev][0]*cal_len,\
            globals()['veloc_'+color][indicev][1]*cal_len])
            
            globals()['angular_veloc_final_'+color].append(\
            globals()['angular_veloc_'+color][indicev])
            indicev+=1
            
        if t in globals()['time_a_'+color]:
            globals()['acc_final_'+color].append(\
            [globals()['acc_'+color][indicea][0]*cal_len,\
            globals()['acc_'+color][indicea][1]*cal_len])
            
            globals()['angular_acc_final_'+color].append(\
            globals()['angular_acc_'+color][indicea])
            indicea+=1
        if t not in globals()['time_v_'+color]:
            globals()['veloc_final_'+color].append([0,0])
            globals()['angular_veloc_final_'+color].append(0)
        if t not in globals()['time_a_'+color]:
            globals()['acc_final_'+color].append([0,0])
            globals()['angular_acc_final_'+color].append(0)
            
#angle convertion in rad
for color in color_to_track:
   for i in range(0,numberframe):
      globals()['angular_veloc_final_'+color][i]=\
      globals()['angular_veloc_final_'+color][i]*2*math.pi/360
      globals()['angular_acc_final_'+color][i]=\
      globals()['angular_acc_final_'+color][i]*2*math.pi/360
      


# writting all data in binary
with open('binary/time_of_record.txt','wb') as f:
    pickle.dump(time_of_record,f)
f.close()


for color in color_to_track:
    with open('binary/fail_to_track_'+color+'.txt','wb') as f:
        pickle.dump(globals()['fail_to_track_'+color],f)
    f.close()
    with open('binary/angle_'+color+'.txt','wb') as f:
        pickle.dump(globals()['angle_'+color],f)
    f.close()
    with open('binary/pos_'+color+'.txt','wb') as f:
        pickle.dump(globals()['pos_'+color],f)
    f.close()
    with open('binary/size_'+color+'.txt','wb') as f:
        pickle.dump(globals()['size_'+color],f)
    f.close()
    with open('binary/number_'+color+'.txt','wb') as f:
        pickle.dump(globals()['number_'+color],f)
    f.close()
    with open('binary/angular_veloc_'+color+'.txt','wb') as f:
        pickle.dump(globals()['angular_veloc_final_'+color],f)
    f.close()
    with open('binary/veloc_'+color+'.txt','wb') as f:
        pickle.dump(globals()['veloc_final_'+color],f)
    f.close()
    with open('binary/angular_acc_'+color+'.txt','wb') as f:
        pickle.dump(globals()['angular_acc_final_'+color],f)
    f.close()
    with open('binary/acc_'+color+'.txt','wb') as f:
        pickle.dump(globals()['acc_final_'+color],f)
    f.close()
#end
#------------------------------------------------------
