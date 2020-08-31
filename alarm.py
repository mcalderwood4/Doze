import RPi.GPIO as GPIO
import time
import pygame
import threading


class Alarm:
    # called when alarm time equals current time
    def go(self):
        # starts sound if sound equals True
        if self.sound_on:
            t = threading.Thread(target=self.go_sound)
            t.daemon = True
            t.start()
        # starts light if light equals True
        if self.light:
            t2 = threading.Thread(target=self.go_light)
            t2.daemon = True
            t2.start()
        # starts scent if scent equals True
        if self.scent:
            t3 = threading.Thread(target=self.go_scent)
            t3.daemon = True
            t3.start()

    #creates new alarm
    def __init__(self, name, hour, minute, on, scent, light, sound_on, sound, ampm, idNum):
        self.hour = hour
        # if len(hour) == 1:
        #     self.hour = "0" + hour
        if ampm == "PM":
            #adds 12 if PM to adjust to 24hr clock
            hour = int(hour) + 12
        self.hour = str(hour)
        self.minute = str(minute)
        self.on = on
        self.sound_on = sound_on
        self.sound = sound
        self.light = light
        self.scent = scent
        self.name = name
        self.ampm = ampm
        self.timee = self.get_time()
        self.idNum = int(idNum)

    def get_time(self):
        # formats alarm time for display in the alarm list
        if self.ampm == "PM":
            return (str(int(self.hour) - 12) + ":" + str(self.minute)) + " " + self.ampm
        else:
            return (str(self.hour) + ":" + str(self.minute)) + " " + self.ampm

    def get_sound_name(self):
        return str(self.sound)

    #formats alarm time to check against computer time
    def alarm_time(self):
        return str(self.hour) + "" + str(self.minute)

    def turn_on(self):
        self.on = True

    def turn_off(self):
        self.on = False

    def scent_on(self):
        self.scent = True

    def scent_off(self):
        self.scent = False

    def get_name(self):
        return self.name

    def get_id(self):
        return self.idNum

    # runs when the alarm uses sound
    def go_sound(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.sound)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

    # runs when the alarm uses light
    def go_light(self):
        print("light")
        GPIO.setmode(GPIO.BCM)

        GPIO.setwarnings(False)

        # defining the pins
        green = 21
        green2 = 26
        red = 20
        red2 = 19
        blue = 16
        blue2 = 13

        # defining the pins as output
        GPIO.setup(red, GPIO.OUT)
        GPIO.setup(red2, GPIO.OUT)
        GPIO.setup(green, GPIO.OUT)
        GPIO.setup(green2, GPIO.OUT)
        GPIO.setup(blue, GPIO.OUT)
        GPIO.setup(blue2, GPIO.OUT)

        # choosing a frequency for pwm
        Freq = 100

        # defining the pins that are going to be used with PWM
        RED = GPIO.PWM(red, Freq)
        RED2 = GPIO.PWM(red2, Freq)
        GREEN = GPIO.PWM(green, Freq)
        GREEN2 = GPIO.PWM(green2, Freq)
        BLUE = GPIO.PWM(blue, Freq)
        BLUE2 = GPIO.PWM(blue2, Freq)


      # adjusts light to slowly change color, simulating sunrise
        RUNNING = True
        while RUNNING:
            RED.start(40)
            RED2.start(40)
            GREEN.start(1)
            GREEN2.start(1)
            BLUE.start(100)
            BLUE2.start(100)
            for x in range(1, 101):
                BLUE.ChangeDutyCycle(101 - x)
                BLUE2.ChangeDutyCycle(101 - x)
                time.sleep(1)
            RUNNING = False

        GPIO.cleanup()

    # called when the alarm uses scent
    # this section was not developed in the prototype due to time constraints
    def go_scent(self):
        print("scent")








