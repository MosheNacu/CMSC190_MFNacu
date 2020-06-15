#   Nacu, Moshe F.
#   2016-00913
#   Pathfinder: Device for Obstacle Detection and Avoidance to Help the Mobility of Visually Impaired People
#   CMSC190 2nd Sem A.Y. 2019-2020
#===========================================================================================================

import cv2
import numpy as np
import os
import time
import math
import RPi.GPIO as GPIO

print("Waiting for Button...")

#==========button==========
buttonStatus = 0
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)#Button to GPIO23

#===== counts time for button hold =====
def buttonHold(channel):
    global buttonStatus
    start_time = time.time()

    while GPIO.input(18) == GPIO.LOW: # Wait for the button up
        pass
    
    buttonTime = time.time() - start_time
    if .1 <= buttonTime < 2:        # Ignore noise
        buttonStatus = 2        # 1= brief push
    elif 2 <= buttonTime < 4:
        buttonStatus = 2        # 2= Long push
    elif buttonTime >= 4:
        buttonStatus = 2        # 3= really long push
    
def outputBlink():              #makes the output "blink"   Used as an indicator
    time.sleep(.4)
    GPIO.output(26,GPIO.HIGH)
    GPIO.output(12,GPIO.HIGH)
    time.sleep(.4)
    GPIO.output(26,GPIO.LOW)
    GPIO.output(12,GPIO.LOW)

GPIO.add_event_detect(18, GPIO.BOTH, callback=buttonHold, bouncetime=200)

status = False  #button status

#========================================================================
deci= "Decision: "
GPIO.setwarnings(False)
GPIO.setup(26,GPIO.OUT) #left buzzer
GPIO.setup(12,GPIO.OUT) #right buzzer
outputBlink()
try:
    while True:
        
        button_state = GPIO.input(18)
        if button_state == False and buttonStatus == 2: #if button is held for 2-4 seconds and released
            print(buttonStatus)
            buttonStatus = 0
            status = False if status else True
            if status:
                #==================================================================
                print("Starting up... ")
                outputBlink()
                outputBlink()
                
                cap = cv2.VideoCapture(0)
                startTime = time.time()
                while True:
                    _, frame = cap.read()
                    blur = cv2.GaussianBlur(frame,(5,5),cv2.BORDER_DEFAULT)     #Applies Gaussian Blur to minimize noise
                    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
                
                    sec = time.time() - startTime                               #time duration
                    
                    #================drawing================
                    height = frame.shape[0]                 #gets height of img
                    width = frame.shape[1]                  #gets width of img
                    
                    p1 = int(height*.25)
                    p2 = int(width/3)                       #divides left and center
                    p3 = (p2*2)                             #divides center and right
                    
                    #=====draw the lines=====
                    cv2.line(frame,(0,int(height/2)),(width,int(height/2)),(255,255,255),1)                             #2 meter mark
                    cv2.line(frame,(0,p1),(width,p1),(255,255,255),1)                                                   #1 meter mark
                    cv2.line(frame,(p2,0),(p2,height),(255,255,255),1)                                                  #left line
                    cv2.line(frame,(p3,0),(p3,height),(255,255,255),1)                                                  #right line
                    cv2.putText(frame, str(math.trunc(round(sec))), (20,20), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255))  #shows time duration
                    
                    #==============Region of Interest====================
                    myROIL = [(0, int(height/2)), (p2, int(height/2)), (0, int(height)), (p2, int(height))]  # (x, y)
                    myROIC = [(p2, int(height/2)), (p3, int(height/2)),  (p2, int(height)), (p3, int(height))]  # (x, y)
                    myROIR = [(p3, int(height/2)), (int(width), int(height/2)), (p3, int(height)), (width, int(height))]  # (x, y)
                
                    x1,y1,w,h = cv2.boundingRect(np.array(myROIL))
                    cv2.rectangle(frame,(x1,y1),(x1+w,y1+h),(255,0,0),2)
                    x2,y2,w,h = cv2.boundingRect(np.array(myROIC))
                    cv2.rectangle(frame,(x2,y2),(x2+w,y2+h),(0,255,0),2)
                    x3,y3,w,h = cv2.boundingRect(np.array(myROIR))
                    cv2.rectangle(frame,(x3,y3),(x3+w,y3+h),(0,0,255),2)
                    
                    #========== Shi-Tomasi ==========
                    
                    corners = cv2.goodFeaturesToTrack(gray, 100, 0.01, 10)
                    corners = np.int0(corners)
                    
                    #==========counts good features per ROI==========
                    countL=0
                    countC=0
                    countR=0
                    
                    for corner in corners:
                        x,y = corner.ravel()
                        if x > x1 and x <= x1 + w and y > y1 and y <= y1 + h:
                            cv2.circle(frame,(x,y),3,(255,0,0),-1)                  #blue
                            countL+=1                                               #Left Counter
                        elif x > x2 and x <= x2 + w and y > y2 and y <= y2 + h:
                            cv2.circle(frame,(x,y),3,(0,255,0),-1)                  #green
                            countC+=1                                               #Center Counter
                        elif x > x3 and x <= x3 + w and y > y3 and y <= y3 + h:
                            cv2.circle(frame,(x,y),3,(0,0,255),-1)                  #red
                            countR+=1                                               #Right Counter
                        else:
                            cv2.circle(frame,(x,y),3,(255,255,255),-1)
                    print("Left: " + str(countL))
                    print("Center: " + str(countC))
                    print("Right: " + str(countR) +"\n")
                    
                    #==========decision maker==========
                    cv2.putText(frame, str(countL), ((x1+w)-30,y1+20), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,0,0)) #displays countL
                    cv2.putText(frame, str(countC), ((x2+w)-30,y1+20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,255,0)) #displays countC
                    cv2.putText(frame, str(countR), ((x3+w)-30,y1+20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,255)) #displays countR
                    cv2.putText(frame, deci, ((x1+w)+30,y1-10), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255)) #displays decision
                    
                    
                    if(math.trunc(sec) % 2 == 0 and (str(math.trunc(round(sec,2)*10))[-1:] == '0' or str(math.trunc(round(sec,2)*10))[-1:] == '1')):  #play audio every 2.0 or 2.1 sec
                        print(sec)
                        if min(countL,countC,countR) == countL:
                            print(">>> Decision: Step Left" +"\n")
                            deci= "Decision: Step Left"
                            GPIO.output(26,GPIO.HIGH)
                        elif min(countL,countC,countR) == countC:
                            print(">>> Decision: Move Forward" +"\n")
                            deci= "Decision: Move Forward"
                            GPIO.output(26,GPIO.HIGH)
                            GPIO.output(12,GPIO.HIGH)
                        elif min(countL,countC,countR) == countR:
                            print(">>> Decision: Step Right" +"\n")
                            deci= "Decision: Step Right"
                            GPIO.output(12,GPIO.HIGH)
                        time.sleep(.2)
                        GPIO.output(26,GPIO.LOW)
                        GPIO.output(12,GPIO.LOW)
                    
                    #reset per frame
                    countL=0
                    countC=0
                    countR=0
                    
                    cv2.imshow('Corner',frame)      #shows the output       Comment out for headless mode
                
                    #=================================
                    
                    k = cv2.waitKey(5) & 0xFF
                    if k == 27 or (button_state == False and buttonStatus == 2): #waits until esc key or button is pressed
                        print('Shutting Down...')
                        outputBlink()
                        outputBlink()
                        outputBlink()
                        exit()
                
                cv2.destroyAllWindows()
                cap.release()
            #==================================================================
        else:
            continue
except:
    GPIO.cleanup()

print("done")