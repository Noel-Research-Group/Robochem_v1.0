int io[14] = {0,1,2,3,4,5,6,7,8,9,0,1,2,3};
int d = 0;


void setup() {
  // Open serial connection
  Serial.begin(19200);
  Serial.flush();
  // Set up pins 1-13 as OUTPUT and initialize to 0 (LOW)
  for (int i = 2; i <= 13; i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, 1);  //initiate pins off
  }
}


void loop() {
  if (Serial.available() > 0) {
    io[d] = int(char(Serial.read()) - '0');  // store input in the array
    for (int j = 0; j <=13; j++) {
      Serial.print(io[j]);
    }
    Serial.println();
    d++;  // move to next position
    if (d == 14) {  // when all values are registered (pin 0-13), apply settings
      d = 0;  // reset index
      Serial.flush();
      // Serial.flush();  // get rid of end-of-line characters causing extra loops
      for (int i = 2; i <= 13; i++) {
        if (io[i] == 0){
          digitalWrite(i, LOW);
        }
        if (io[i] == 1){
          digitalWrite(i, HIGH);
        }
      }
    }
  }
  delay(10);
}
