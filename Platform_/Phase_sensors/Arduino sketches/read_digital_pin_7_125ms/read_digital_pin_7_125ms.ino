/*
Connections:

OPB350 phase sensor | Arduino UNO
        white wire --> analog pin A1
        green wire --> floating in empty breadboard line (connect to GND for calibration**)
         blue wire --> digital pin 4
       orange wire --> digital pin 7
          red wire --> 5V
        black wire --> GND

[!] IMPORTANT NOTE: [!]
Do NOT short the analog wire with GND, as it will lead to constant 0 logical output.

** = during calibration the sensor should be removed from the capillary

*/

int orangePin = 7;
int orangeValue = 0;
int bluePin = 4;
int blueValue = 0;
int delayTime = 125;

void setup() {
  // Open serial connection
  Serial.begin(19200);
  // Set the pins to input
  pinMode(orangePin, INPUT);
  pinMode(bluePin, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  orangeValue = digitalRead(orangePin);  // read digital pin 7
  Serial.println(orangeValue);  // send value via serial connection
  delay(delayTime);  // 250 ms delay between cycles
//  blueValue = digitalRead(bluePin);  // read digital pin 4
//  Serial.println(blueValue);  // send value via serial connection
//  delay(delayTime);  // 250 ms delay between cycles
  
}
