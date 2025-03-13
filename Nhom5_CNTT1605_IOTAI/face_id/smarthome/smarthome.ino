#include <Servo.h>

// Khai báo các chân
const int gasSensorPin = A0;    // Cảm biến khí gas
const int lightSensorPin1 = A1; // Cảm biến ánh sáng 1
const int lightSensorPin2 = A2; // Cảm biến ánh sáng 2
const int lightSensorPin3 = A3; // Cảm biến ánh sáng 3
const int buzzerPin = 8;        // Còi
const int ledGasPin = 7;        // LED cảnh báo khí gas
const int ledLightPin1 = 6;     // LED chiếu sáng 1
const int ledLightPin2 = 5;     // LED chiếu sáng 2
const int ledLightPin3 = 4;     // LED chiếu sáng 3
const int servoGasPin = 9;      // Servo khí gas
const int servoFacePin = 10;    // Servo nhận diện khuôn mặt

// Ngưỡng khí gas và ánh sáng
const int gasThreshold = 300;
const int lightThreshold1 = 500;
const int lightThreshold2 = 500;
const int lightThreshold3 = 500;

Servo gasServo;
Servo faceServo;
bool faceRecognized = false;

void setup() {
  pinMode(buzzerPin, OUTPUT);
  pinMode(ledGasPin, OUTPUT);
  pinMode(ledLightPin1, OUTPUT);
  pinMode(ledLightPin2, OUTPUT);
  pinMode(ledLightPin3, OUTPUT);
  pinMode(gasSensorPin, INPUT);
  pinMode(lightSensorPin1, INPUT);
  pinMode(lightSensorPin2, INPUT);
  pinMode(lightSensorPin3, INPUT);

  gasServo.attach(servoGasPin);
  gasServo.write(0);
  faceServo.attach(servoFacePin);
  faceServo.write(0);

  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == '1') {
      faceRecognized = true;
      Serial.println("Face recognized: door opened.");
    } else if (command == '0') {
      faceRecognized = false;
      Serial.println("Face reset: door closed.");
    }
  }

  int gasValue = analogRead(gasSensorPin);
  int lightValue1 = analogRead(lightSensorPin1);
  int lightValue2 = analogRead(lightSensorPin2);
  int lightValue3 = analogRead(lightSensorPin3);

  Serial.print("Gas: ");
  Serial.print(gasValue);
  Serial.print(" | Light 1: ");
  Serial.print(lightValue1);
  Serial.print(" | Light 2: ");
  Serial.print(lightValue2);
  Serial.print(" | Light 3: ");
  Serial.println(lightValue3);

  if (gasValue > gasThreshold) {
    digitalWrite(buzzerPin, HIGH);
    digitalWrite(ledGasPin, HIGH);
    gasServo.write(90);
    Serial.println("GAS_DETECTED");
  } else {
    digitalWrite(buzzerPin, LOW);
    digitalWrite(ledGasPin, LOW);
    gasServo.write(0);
    Serial.println("GAS_CLEARED");
  }

  digitalWrite(ledLightPin1, lightValue1 < lightThreshold1 ? HIGH : LOW);
  digitalWrite(ledLightPin2, lightValue2 < lightThreshold2 ? HIGH : LOW);
  digitalWrite(ledLightPin3, lightValue3 < lightThreshold3 ? HIGH : LOW);

  if (faceRecognized) {
    faceServo.write(90);
  } else {
    faceServo.write(0);
  }

  delay(100);
}