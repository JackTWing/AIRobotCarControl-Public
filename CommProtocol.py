import serial
import time

# establish serial connection
ser = serial.Serial('COM4', 9600)  # update COMport for current robot
time.sleep(2)

def send_motor_command(motor_id, speed):
    command = f"MOT:{motor_id},{speed};"
    ser.write(command.encode())

def send_turn_command(angle, speed):
    command = f"TRN:{angle},{speed};"
    ser.write(command.encode())

def send_servo_command(angle):
    command = f"MOT:{angle};"
    ser.write(command.encode())

def send_message(message):
    command = f"COM:{message};"
    ser.write(command.encode())

def send_uls_command(timeBetweenReadings, numReadings):
    command = f"ULS:{timeBetweenReadings},{numReadings};"
    ser.write(command.encode())

def recieve():
    for i in range(0, 10):
        recieveSerial()

def recieveSerial():
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        return line
    
def recieveULSFeedback():
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        if line.split(':')[0].strip() == "ULS_RET":
            print(line.split(':')[1].strip()) + " cm"
            return line.split(':')[1].strip() + " cm"
        return "No ULS_RET received"