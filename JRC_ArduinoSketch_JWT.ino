// Arduino Component of the AI Robot Car Control Project
// REMEMBER TO SWITCH MOTOR SHIELD TO UPLOAD...I WASTED 25 MIN ON THIS!
// Wheel Circumference == 21 cm
// Wheel rotation time (@100) = 0.7 s

#include <Servo.h>
#include <Arduino.h>

// Define Motor Pins:
#define motorStandby 3
#define ENA 5
#define ENB 6
#define IN1 7
#define IN2 8

//Servo Def:
#define PINServo 10
Servo myservo;

// Ultrasonic Pins:
#define trig 13
#define echo 12

void motTest() {
  digitalWrite(motorStandby, HIGH);
  digitalWrite(IN1, HIGH);
  analogWrite(ENA, 100);
  digitalWrite(IN2, HIGH);
  analogWrite(ENB, 100);
  delay(1000);

  digitalWrite(motorStandby, LOW);
  delay(1000);

  digitalWrite(motorStandby, HIGH);
  digitalWrite(IN1, LOW);
  analogWrite(ENA, 100);
  digitalWrite(IN2, LOW);
  analogWrite(ENB, 100);
  delay(1000);

  digitalWrite(motorStandby, LOW);
}

// I have removed the MPU code here as I did not use it in the project

void setup() {
  // Drive motor defs:
  pinMode(motorStandby, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  Serial.begin(9600);

  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);

  myservo.attach(PINServo, 500, 2400); //500: 0 degree  2400: 180 degree
  myservo.attach(PINServo);
  myservo.write(0); //sets the servo position according to the 90（middle）
  delay(500);
  myservo.write(100);

  delay(1000);
  motTest();
  mpuInit();
}

void loop() {

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil(';');
    send(command);
    if (command.startsWith("MOT:")) {
      int colonIndex = command.indexOf(':');
      int idIndex = command.indexOf(',') + 1;

      int motorSideID = command.substring(colonIndex + 1, idIndex - 1).toInt();
      int speed = command.substring(idIndex).toInt();
      String line1 = "ID: " + String(motorSideID);
      String line2 = "Speed: " + String(speed);
      Serial.println("Command Recieved: MOT");
      Serial.println(line1);
      Serial.println(line2);

      setMotorSpeed(motorSideID, speed);

    } else if (command.startsWith("SRV:")) {
      int colonIndex = command.indexOf(':');

      int angle = command.substring(colonIndex + 1).toInt();
      send("Command Recieved: SRV");

      setServo(angle);

    } else if (command.startsWith("TRN:")) {
      int colonIndex = command.indexOf(':');
      int idIndex = command.indexOf(',') + 1;
      int angle = command.substring(colonIndex + 1, idIndex - 1).toInt();
      int speed = command.substring(idIndex).toInt();
      send("Command Recieved: TRN");

      turnDegreesNoGyro(angle, speed);

    } else if (command.startsWith("VIS:")) {
      int colonIndex = command.indexOf(':');
      int idIndex = command.indexOf(',') + 1;
      int motorID = command.substring(colonIndex + 1, idIndex - 1).toInt();
      int speed = command.substring(idIndex).toInt();
      send("Command Recieved: VIS");
        // Needs some work...
      setMotorSpeed(motorID, speed);

    } else if (command.startsWith("ULS:")) {
      int colonIndex = command.indexOf(':');
      int idIndex = command.indexOf(',') + 1;
      int timeDelay = command.substring(colonIndex + 1, idIndex - 1).toInt();
      int numOfReadings = command.substring(idIndex).toInt();
      send("Command Recieved: ULS");

      getUlsReading(timeDelay, numOfReadings);

    } else if (command.startsWith("CAM:")) {
      int colonIndex = command.indexOf(':');
      int idIndex = command.indexOf(',') + 1;
      int setting1 = command.substring(colonIndex + 1, idIndex - 1).toInt();
      int setting2 = command.substring(idIndex).toInt();
      send("Command Recieved: CAM");

    } else if (command.startsWith("COM:")) {
      int colonIndex = command.indexOf(':');
      String message = command.substring(colonIndex + 1);

      send(message);

    } else {
      // send back - no function supported
      send("==== Function Not Recognized ====");
    }
  }

  // Anything else needing to run in loop should go here
}

void setMotorSpeed(int motorSideID, int speed) {
  uint8_t on;
  uint8_t sideOn;

  if(speed == 0) {on = LOW;}
  else {on = HIGH;}
  if(speed < 0) {sideOn = LOW;}
  else {sideOn = HIGH;}

  digitalWrite(motorStandby, on);
  switch(motorSideID) {
    case 1: {
      digitalWrite(IN1, sideOn);
      analogWrite(ENA, speed);
      send("case 1 executing");
      break;
    }
    case 2: {
      digitalWrite(IN2, sideOn);
      analogWrite(ENB, speed);
      send("case 2 executing");
      break;
    }
    default: {
      Serial.println("Motor ID Not Recognized");
    }
  }
  send("Executed");
}

void setServo(int positionAngle) {
  myservo.write(positionAngle + 100);
}

double ultrasonicMeasure() {
  // Send a pulse of 10 microseconds to the ultrasonics:

  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);

  // Find distance from pulse:

  long raw = pulseIn(echo, HIGH);
  double distance = raw * 0.034 / 2;


  Serial.print(distance);
  Serial.print("\n");
  return distance;
}

void getUlsReading(int timeDelay, int numReadings) {
  double sumDistance = 0;
  for(int i = 0; i < numReadings; i++) {
    sumDistance += ultrasonicMeasure();
    delay(timeDelay);
  }
  double distance = sumDistance / numReadings;
  Serial.print("ULS_RET: ");
  Serial.print(distance);
  Serial.print("\n");
}

void setPortDigital(int port, uint8_t state) {
  send("- " + port);
  send("- " + state);
  digitalWrite(port, state);
  send("Port Updated!");
}

void setPortAnalog(int port, int state) {
  send("- " + port);
  send("- " + state);
  analogWrite(port, state);
  send("Port Updated!");
}

void send(String message) {
  Serial.print(message);
  Serial.print("\n");
}

void updateGyro() {
  // Again, I have removed the gyro / MPU code
}

void turnDegrees(double degrees, int speed) {
  // Again, I have removed the gyro / MPU code
}

void turnDegreesNoGyro(double degrees, int speed) {
  speed = 50;
  double factor = 10;
  int timeToTurn = (degrees * factor) * (100 / speed);

  if(timeToTurn < 0) {timeToTurn *= -1;}

  if (degrees >= 0) {
    // turn right
    setMotorSpeed(1, -speed);
    setMotorSpeed(2, speed);
  } else {
    // turn left
    setMotorSpeed(1, speed);
    setMotorSpeed(2, -speed);
  }
  delay(timeToTurn);
  // stop motors
  setMotorSpeed(1, 0);
  setMotorSpeed(2, 0);
}