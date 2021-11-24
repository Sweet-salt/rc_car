from flask import Flask
from flask import render_template, request 
import RPi.GPIO as GPIO
import time
 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
 
print("waiting")


app = Flask(__name__)
 
STOP  = 0
FORWARD  = 1
BACKWARD = 2
 
CH1 = 0
CH2 = 1
 
ENL = 22
DIRL = 23
 
ENR = 26 
DIRR = 20

CW1 = 1     # Clockwise Rotation
CCW1 = 0    # Counterclockwise Rotation
#SPR = 200   # Steps per Revolution (360 / 1.8) <-- source code has 7.5 degree steps for SPR of 48.

Num = 0  

SingleCoilR = [[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]]
SingleCoilL = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]

V_StepPins = [7,11,13,15]
H_StepPins = [2,3,4,17]

for pin in H_StepPins:
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin,False)

for pin in V_StepPins:
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin,False)

GPIO.setup(ENL, GPIO.OUT)
GPIO.setup(DIRL, GPIO.OUT)
GPIO.setup(ENR, GPIO.OUT)
GPIO.setup(DIRR, GPIO.OUT)

pwmL = GPIO.PWM(ENL, 100)
pwmR = GPIO.PWM(ENR, 100)

def allStop():
    GPIO.output(ENL, GPIO.LOW)
    GPIO.output(DIRL, GPIO.LOW)
    GPIO.output(ENR, GPIO.LOW)
    GPIO.output(DIRR, GPIO.LOW)

def forWard(speed):
    pwmL.start(speed)
    GPIO.output(DIRL, GPIO.LOW)
    pwmR.start(speed)
    GPIO.output(DIRR, GPIO.LOW)

def backWard(speed):
    pwmL.start(speed)
    GPIO.output(DIRL, GPIO.HIGH)
    pwmR.start(speed)
    GPIO.output(DIRR, GPIO.HIGH)

def leftTurn(speed):
    pwmR.start(speed)
    GPIO.output(DIRR, GPIO.LOW)
    GPIO.output(ENL, GPIO.LOW)
    GPIO.output(DIRR, GPIO.LOW)
    
def rightTurn(speed):
    GPIO.output(ENR, GPIO.LOW)
    GPIO.output(DIRR, GPIO.LOW)
    pwmL.start(speed)
    GPIO.output(DIRL, GPIO.LOW)
    
@app.route("/CAM/<FUNC>/<int:dist>/<float:stepspeed>")
def stepMotor(FUNC, dist, stepspeed):
 t_num = int(2048*dist/360)
 print(t_num)
 degree = str(dist)
 delay = float(stepspeed)
 StepCounter = 0 
 StepCount1 = 4

 if FUNC == "CCW":
  msg = "Turn Counter ClockWise " + degree + "DEG."
  for Num in range(0,t_num): #360/11.25(=stride angle)*63.684(=Gear Ratio)=2037
                              # rotate right with single coil excitation(full step)
        for pin in range(0, 4):
            xpin = H_StepPins[pin]
            
            if SingleCoilR[StepCounter][pin]!=0: 
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)
        StepCounter += 1 
        if (StepCounter==StepCount1):
            StepCounter = 0
        if (StepCounter<0):
            StepCounter = StepCount1
        time.sleep(delay)                
        Num += 1
 elif FUNC == "CW":
  msg = "Turn ClockWise " + degree + "DEG."
  for Num in range(0,t_num): #360/11.25(=stride angle)*63.684(=Gear Ratio)=2037
                             # rotate right with single coil excitation(full step)
        for pin in range(0, 4):
            xpin = H_StepPins[pin]
            if SingleCoilL[StepCounter][pin]!=0: 
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)
        StepCounter += 1 
        if (StepCounter==StepCount1):
            StepCounter = 0
        if (StepCounter<0):
            StepCounter = StepCount1
        time.sleep(delay)
        Num += 1
 elif FUNC == "DOWN":
  msg = "Put the Camera Down " + degree + "DEG."
  for Num in range(0,t_num): #360/11.25(=stride angle)*63.684(=Gear Ratio)=2037
                              # rotate right with single coil excitation(full step)
        for pin in range(0, 4):
            xpin = V_StepPins[pin]
            if SingleCoilL[StepCounter][pin]!=0: 
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)
        StepCounter += 1 
        if (StepCounter==StepCount1):
            StepCounter = 0
        if (StepCounter<0):
            StepCounter = StepCount1
        time.sleep(delay)                
        Num += 1
 elif FUNC == "UP":
  msg = "Put the Camera Up " + degree + "DEG."
  for Num in range(0,t_num): #360/11.25(=stride angle)*63.684(=Gear Ratio)=2037
                             # rotate right with single coil excitation(full step)
        for pin in range(0, 4):
            xpin = V_StepPins[pin]
            if SingleCoilR[StepCounter][pin]!=0: 
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)
        StepCounter += 1 
        if (StepCounter==StepCount1):
            StepCounter = 0
        if (StepCounter<0):
            StepCounter = StepCount1
        time.sleep(delay)
        Num += 1
 else :
  msg = "Undefined action!!!"   
 position = {
   'msg' : msg }
 return render_template('stepMotor.html', **position)

@app.route("/CAR/<direction>/<int:speed>/<float:distance>")
def carMove(direction, speed, distance):
    distance = float(distance)
    speed = int(speed)

    if direction == "STOP":
        msg = "CAR is stopped"
        print("Stop")
        allStop()
 
    elif direction =="FORWARD":
        msg = "CAR is Forwarding"        
        print("Forward")
        forWard(speed)
        time.sleep(distance)
        pwmL.stop()
        pwmR.stop()
        allStop()
        
    elif direction =="BACKWARD":
        msg = "CAR is Backwarding"        
        print("Backward")
        backWard(speed)
        time.sleep(distance)
        pwmL.stop()
        pwmR.stop()
        allStop()

    elif direction =="LEFT":
        msg = "CAR is turning LEFT"         
        print("Turn to the left")
        leftTurn(speed)
        time.sleep(distance)
        pwmL.stop()
        pwmR.stop()
        allStop()

    elif direction =="RIGHT":
        msg = "CAR is turning RIGHT"        
        print("Turn to the right")
        rightTurn(speed)
        time.sleep(distance)
        pwmL.stop()
        pwmR.stop()
        allStop()
        
        
    else:
        msg = "Undefined action!!!"   
    position = {
       'msg' : msg }
    return render_template('carMotor.html', **position)

    
if __name__ == "__main__":
 app.run(host='223.194.165.234', port=8000, debug=True)    






