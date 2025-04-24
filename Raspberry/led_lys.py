import time
import pigpio
import smbus2
import schedule
import datetime

#initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    print("couldnt connect to pigpio")
    exit()

#I2C setup (oh yeah)
bus = smbus2.SMBus(1)
i2c_address = 0x4b

#pwm setup
pwm_pin = 18 #gpio 18 = pin 12
frequency = 800 #Hz
running = False

def dags_lys():
    global running
    running = True
    print("Godmorgen min lille Grønne Barn!")

def dags_lys_stop():
    global running
    running = False
    print("Sov godt min skat...zzzzzz")
    pi.hardware_PWM(pwm_pin, 0, 0)

def show_time():
    current_time = datetime.datetime.now().time()
    print(current_time)

#schedule from 9 - 20
schedule.every().day.at("10:32").do(dags_lys)
schedule.every().day.at("20:00").do(dags_lys_stop)
schedule.every(10).seconds.do(show_time)

try:
    while True:
        schedule.run_pending()
        if running:
            # Reading 16-bit valye from i2c sensor
            rd = bus.read_word_data(i2c_address, 0)
            #swap byte order
            data = ((rd & 0xFF) << 8 )| ((rd & 0xFF00)>> 8)
            #shift to 14 bit range
            data = data >> 2

            print("LDR Data:", data)

            duty_cycle = int((data/700)*600000)
            duty_cycle = max(0, min(duty_cycle,600000))
            pi.hardware_PWM(pwm_pin,frequency,duty_cycle)

            if duty_cycle < 150000:
                pi.hardware_PWM(pwm_pin, 0, 0)


            print("dutycycle: ",duty_cycle)

        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting program...")

finally:
    #stop pwm and cleanup
    pi.hardware_PWM(pwm_pin, 0, 0)
    pi.stop()