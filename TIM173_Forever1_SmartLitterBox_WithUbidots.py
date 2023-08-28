import time
import requests
import math
import random
import RPi.GPIO as GPIO

TOKEN = "BBFF-mPzQWh9K7fbaKlvnFmnGWYvSNPQ2wX"  # Put your TOKEN here
DEVICE_LABEL = "smarth_litter_box"  # Put your device label here 
VARIABLE_LABEL_1 = "Distance1"  # Put your first variable label here
VARIABLE_LABEL_2 = "Distance2"  # Put your second variable label here
VARIABLE_LABEL_3 = "Distance3"  # Put your third variable label here

GPIO.setwarnings(False)
print ("TIM173_FOREVER1 - SMART LITTER BOX")
print ("SMK NEGERI 1 KAYUAGUNG")
print("")
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#Set GPIO Pins Servo
servoPIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
servo1 = GPIO.PWM(servoPIN,30)
servo1.start(2.7)
time.sleep(1)
servo1.start(0)

#set GPIO Pins Ultrasonic & Led
GPIO_TRIGGER1 = 18
GPIO_ECHO1 = 24
GPIO_TRIGGER2 = 19
GPIO_ECHO2 = 23
LED_MERAH = 16
LED_HIJAU = 17

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER1, GPIO.OUT)
GPIO.setup(GPIO_ECHO1, GPIO.IN)
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
GPIO.setup(GPIO_ECHO2, GPIO.IN)
GPIO.setup(LED_MERAH, GPIO.OUT)
GPIO.setup(LED_HIJAU, GPIO.OUT)


def distance1():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER1, True)
    
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER1, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO1) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO1) == 1:
        StopTime = time.time()
         
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance1 = (TimeElapsed * 34300) / 2
 
    return distance1

def distance2():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER2, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER2, False)
 
    StartTime2 = time.time()
    StopTime2 = time.time()
 
    # save StartTime       
    while GPIO.input(GPIO_ECHO2) == 0:
        StartTime2 = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO2) == 1:
        StopTime2 = time.time()
 
    # time difference between start and arrival
    TimeElapsed2 = StopTime2 - StartTime2
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance2 = (TimeElapsed2 * 34300) / 2
 
    return distance2

def build_payload(variable_1, variable_2, variable_3):
#### distance1###############
    lat = -6.4124
    long = 102.412412
    jarak1 = distance1()
    jarak2 = distance2()
    # Creates two random values for sending data
    value_1 = jarak1
    value_2 = jarak2

    # Creates a random gps coordinates
    payload = {variable_1: value_1,
               variable_2: value_2,
               variable_3: {"value": 1, "context": {"lat": lat, "lng": long}}}

    return payload


def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True


def main():
    payload = build_payload(
        VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3)

    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")

if __name__ == '__main__':
    try:
        while True:
            latitude = -6.4124
            longitude = 102.412412
            volume = distance1()
            jarak = distance2()
            print ("Volume Sampah = %.1f cm" % volume)
            print ("Jarak Terukur = %.1f cm" % jarak)
            time.sleep(1)
            
            #Pengkuran Jarak untuk Membuang Sampah
            if (jarak < 30 and jarak > 1):
		if volume > 5:
		    servo1.ChangeDutyCycle(7)
                    time.sleep(2)
                    servo1.ChangeDutyCycle(2.7)
                    time.sleep(1)
            	elif volume > 5 and volume > 1:
                    servo1.ChangeDutyCycle(0)
            else :
                servo1.ChangeDutyCycle(0)
                
            #Pengukuran Jarak Volume Sampah Sudah Penuh atau Belum
            if volume < 5 and volume > 1:
                GPIO.output(LED_MERAH, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(LED_HIJAU, GPIO.LOW)
                time.sleep(1)
            else:
                GPIO.output(LED_HIJAU, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(LED_MERAH, GPIO.LOW)
                time.sleep(1)
                
        # Menghentikan program dengan menekan CTRL + C
    except KeyboardInterrupt:
        print("")
        print("Pengukuran dihentikan oleh Pengguna")
        print(".............Good By...............")
        GPIO.cleanup()