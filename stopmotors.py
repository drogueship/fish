# Script that controls 2 DC motors on a Billy Bass Fish
# Based on the Adafruit DCTest.py script 
# Author: Mari DeGrazia
# arizona4n6@gmail.com

import time
import atexit
from multiprocessing import Process
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

MOTOR_HEAD = 1
MOTOR_MOUTH = 2
MOTOR_TAIL = 3
#function to tilt head up when the fish talks
def turnOffMotors():
	mh.getMotor(MOTOR_HEAD).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(MOTOR_MOUTH).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(MOTOR_TAIL).run(Adafruit_MotorHAT.RELEASE)


#set up motors
mh = Adafruit_MotorHAT(addr=0x60)

myMotorMouth = mh.getMotor(MOTOR_MOUTH)
myMotorMouth.setSpeed(255)
myMotorMouth.run(Adafruit_MotorHAT.RELEASE)

myMotorHead =  mh.getMotor(MOTOR_HEAD)
myMotorHead.setSpeed(255)
myMotorHead.run(Adafruit_MotorHAT.RELEASE)

myMotorTail = mh.getMotor(MOTOR_TAIL)
myMotorTail.setSpeed(255)
myMotorTail.run(Adafruit_MotorHAT.RELEASE)

if __name__ == '__main__':
		print "we can't stop, we have to slow down first"
		turnOffMotors()
		print "smoke em if you got em"
		


