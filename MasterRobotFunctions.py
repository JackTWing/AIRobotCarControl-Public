import time
import CommProtocol as cp

def driveDistance(distance, speed):
    # Wheel Circumference == 21 cm
    # Wheel rotation time (@100) = 0.7 s

    # added factor for acurate distance measurement
    factor = 3.0

    timeToTravel = (distance / 21 * 0.7) * (100 / speed) * factor

    if distance < 0: 
       speed = -100

    cp.send_motor_command(1, speed)
    cp.send_motor_command(2, speed)

    # wait for time passed in transit
    time.sleep(abs(timeToTravel))

    cp.send_motor_command(1, 0)
    cp.send_motor_command(2, 0)

    # wait 0.1s to make sure command is completed
    time.sleep(0.1)

def turn(angle, speed):
    cp.send_turn_command(angle, speed)

def getUlsReading(angle, numReadings):
    cp.send_servo_command(angle)
    time.sleep(0.5)
    cp.send_uls_command(0.1, numReadings)
    time.sleep(0.1)
    message = "Feedback from ultrasonic sensor (no reply needed from you): " + cp.recieveULSFeedback()
    return message

def ghostFunction(arg1, arg2):
    print("ghost function used")

class RobotControl:
    def init(self):
        print("\n==== Initialized! ====\n")
    def instruction(self):
        return 0

    def sendToGPT(self, message):
        # sends a message or data / instructions to GPT for processing
        self.recieveFromGPT()
        