from time import sleep
import RPi.GPIO as GPIO
from bottle import route, run, template, request   #zona biblioteci (similar cu include)
import pigpio
import time
import numpy as np
import matplotlib.pyplot as plt

GPIO.setmode(GPIO.BOARD)
motor1=7
motor2=8
DIRmotor1fata=10
DIRmotor1spate=22
DIRmotor2fata= 35                          #zona declarari : acestea sunt valorile pinilor din gpio
DIRmotor2spate=37
GPIO.setwarnings(False)

pi = pigpio.pi()
buzzer=18                                 #valoarea pinului din pigpio
pi.set_mode(buzzer, pigpio.OUTPUT)

trig=23
echo=24
pi.set_mode(trig, pigpio.OUTPUT)
pi.set_mode(echo, pigpio.INPUT)

GPIO.setup(motor1,GPIO.OUT)
GPIO.setup(motor2,GPIO.OUT)
GPIO.setup(DIRmotor1fata,GPIO.OUT)
GPIO.setup(DIRmotor1spate,GPIO.OUT)          #declarare tip pini (output/input)
GPIO.setup(DIRmotor2fata,GPIO.OUT)
GPIO.setup(DIRmotor2spate,GPIO.OUT)
pwmPIN1=GPIO.PWM(motor1, 100)
pwmPIN1.start(0)                              #incepe de pe loc
pwmPIN2=GPIO.PWM(motor2, 100)
pwmPIN2.start(0)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(11,GPIO.OUT)
servofata = GPIO.PWM(11,50)

servofata.start(0)
servofata.ChangeDutyCycle(7)

ledrosu=13
ledverde=15
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
GPIO.output(ledrosu, GPIO.LOW)
GPIO.output(ledverde, GPIO.HIGH)
global valori
valori = []

def calculDistanta():      
    
    pi.write(trig, 1)
    time.sleep(0.00001)
    pi.write(trig, 0)
    start = time.time()
    stop = time.time()
    while pi.read(echo) == 0:                         #codul pentru senzorul de distanta
        start = time.time()                           #se bazeaza pe emiterea si receptionarea unei undei
    while pi.read(echo) == 1:                         #cu o viteza prestabilita; codul calculeaza diferenta de timp
        stop = time.time()                            #dintre emisie-receptie, si calculeaza distanta pe baza lui
    duration = stop - start
    distance = 34300/2 * duration
    if distance < 3400:
        print("Distance = %.2f" %distance)
        valori.append(distance)
    if distance < 50:
        GPIO.output(ledverde, GPIO.LOW)            #emisie semnal urgenta (se aprinde rosu, se stinge verdele
        GPIO.output(ledrosu, GPIO.HIGH)
        pi.hardware_PWM(buzzer, 500, 500000)       #se porneste buzzerul
    else:
        GPIO.output(ledverde, GPIO.HIGH)
        GPIO.output(ledrosu, GPIO.LOW)             #altfel se porneste ledul verde, se stinge rosu si buzzerul
        pi.hardware_PWM(buzzer, 0, 0)              #ramane tacut
        

try:
    while True:
        
        @route('/')
        def index():
            return template('motoare.html')
    
        @route('/inainte')
        def inainte ():
            pwmPIN1.ChangeDutyCycle(100)
            GPIO.output(DIRmotor1fata, GPIO.HIGH)   #se seteaza comutatoarele pentru directia inainte
            GPIO.output(DIRmotor1spate, GPIO.LOW)
            pwmPIN2.ChangeDutyCycle(100)
            GPIO.output(DIRmotor2fata, GPIO.HIGH)  #ambele motoare sunt sincronizate
            GPIO.output(DIRmotor2spate, GPIO.LOW)
    
            return 'ok'

        @route('/stop')
        def stop():
            pwmPIN1.ChangeDutyCycle(0)
            GPIO.output(DIRmotor1fata, GPIO.HIGH)
            GPIO.output(DIRmotor1spate, GPIO.LOW)
            pwmPIN2.ChangeDutyCycle(0)
            GPIO.output(DIRmotor2fata, GPIO.HIGH)
            GPIO.output(DIRmotor2spate, GPIO.LOW)
    
            return 'ok'
        
        @route('/inapoi')
        def inapoi():
            pwmPIN1.ChangeDutyCycle(100)
            GPIO.output(DIRmotor1spate, GPIO.HIGH)
            GPIO.output(DIRmotor1fata, GPIO.LOW)
            pwmPIN2.ChangeDutyCycle(100)
            GPIO.output(DIRmotor2spate, GPIO.HIGH)
            GPIO.output(DIRmotor2fata, GPIO.LOW)
            
            return 'ok'
        
        @route('/dreapta_total')
        def dreapta_total():
            pwmPIN1.ChangeDutyCycle(100)
            GPIO.output(DIRmotor1spate, GPIO.HIGH)
            GPIO.output(DIRmotor1fata, GPIO.LOW)
            pwmPIN2.ChangeDutyCycle(100)
            GPIO.output(DIRmotor2fata, GPIO.HIGH)
            GPIO.output(DIRmotor2spate, GPIO.LOW)
            
            return 'ok'
        
        @route('/stanga_total')
        def stanga_total():
            pwmPIN1.ChangeDutyCycle(100)
            GPIO.output(DIRmotor1fata, GPIO.HIGH)
            GPIO.output(DIRmotor1spate, GPIO.LOW)
            pwmPIN2.ChangeDutyCycle(100)
            GPIO.output(DIRmotor2spate, GPIO.HIGH)
            GPIO.output(DIRmotor2fata, GPIO.LOW)
            
            return 'ok'
        
        @route('/claxon')
        def claxon():
            pi.hardware_PWM(buzzer, 400, 500000)

            return 'ok'
        
        
        @route('/stopclaxon')
        def stopclaxon():
            pi.hardware_PWM(buzzer, 0, 0)
            
            return 'ok'
        
        @route('/sondare')
        def sondare():
            stegulet=0
            duty=2
            while duty <= 12:
                servofata.ChangeDutyCycle(duty)
                calculDistanta()
                duty = duty + 10/36
                time.sleep(0.25)
            plt.subplot(1,1,1)
            grade=np.linspace(0,180,len(valori))
            linie=np.linspace(49.9,50.1,len(valori))
            plt.title('Distanta ca functie de unghiul de rotire') #cod grafic -- similar matlab
            plt.plot(grade,valori,grade,linie,'r')
            plt.ylabel('Distanta')
            plt.xlabel('Grade')
            
            plt.rc('font', size=15)
            fig=plt.gcf()
            fig.set_size_inches(16, 9)
            fig.savefig('Graficdreptunghi.png', dpi=100)
            time.sleep(2)
            return 'ok'
            
        @route('/stopsondare')
        def stopsondare():
            duty=7
            servofata.ChangeDutyCycle(duty)
            time.sleep(1)
            pi.hardware_PWM(buzzer, 0, 0)
            GPIO.output(ledverde, GPIO.HIGH)
            GPIO.output(ledrosu, GPIO.LOW)
        
            return 'ok'
        
        @route('/intoarceremanuala', method = 'POST')
        def manual():
            parametru_procentual = int(request.POST.get('state'))
            parametru_servo = parametru_procentual/10*(-1) + 12
            parametru_servo_ideal=parametru_servo
            servofata.ChangeDutyCycle(parametru_servo)
            return 'ok'
        
        @route('/cercetare', method = 'POST')
        def calculDistantascurta():
            cercetare = request.POST.get('state')
            if cercetare == 'On':
                pi.write(trig, 1)
                time.sleep(0.00001)
                pi.write(trig, 0)
                start = time.time()
                stop = time.time()
                while pi.read(echo) == 0:
                    start = time.time()
                while pi.read(echo) == 1:
                    stop = time.time()
                duration = stop - start
                distance = 34300/2 * duration
                if distance < 3400:
                    print("Distance = %.2f" %distance)
                if distance < 50:
                    GPIO.output(ledverde, GPIO.LOW)
                    GPIO.output(ledrosu, GPIO.HIGH)
                    pi.hardware_PWM(buzzer, 500, 500000)
                else:
                    GPIO.output(ledverde, GPIO.HIGH)
                    GPIO.output(ledrosu, GPIO.LOW)
                    pi.hardware_PWM(buzzer, 0, 0)
            else:
                GPIO.output(ledverde, GPIO.HIGH)
                GPIO.output(ledrosu, GPIO.LOW)
                pi.hardware_PWM(buzzer, 0, 0)
            return 'ok'
        
        run(host = '0.0.0.0', port = '5000')  #apelarea in pagina web

except KeyboardInterrupt:
    pass
GPIO.output(ledrosu, GPIO.LOW)             #parte iesire din program
GPIO.output(ledverde, GPIO.LOW)
servofata.stop()
GPIO.cleanup()
