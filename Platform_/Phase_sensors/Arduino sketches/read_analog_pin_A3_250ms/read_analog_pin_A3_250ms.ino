int sensorPin = A1;
int sensorValue = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  sensorValue = analogRead(sensorPin);  // read analog pin 3
  Serial.println(sensorValue);  // send value via serial connection
  delay(125);  // 125 ms delay between cycles
}
