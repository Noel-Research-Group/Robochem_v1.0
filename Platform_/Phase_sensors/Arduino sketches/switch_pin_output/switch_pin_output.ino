int int_array[18] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
String pin_str = "";


void setup() {
  // Open serial connection
  Serial.begin(19200);
  Serial.flush();
  // Set up pins 1-13 as OUTPUT and initialize to 0 (LOW)
  for (int i = 2; i <= sizeof(int_array) / sizeof(int_array[0]); i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, 0);
  }
}


void loop() {
  while (Serial.available()){
    // read pin number (input)
    char in_char = Serial.read();
    if (int(in_char)!=-1){
      pin_str+=in_char;
    }
    // switch output at the pin received via Serial
    if (in_char=='\n'){
      int pin_num = pin_str.toInt();
      int_array[pin_num] = !int_array[pin_num];  // switching value
      digitalWrite(pin_num,int_array[pin_num]);  // writing value
      // sending feedback on pin status
      //Serial.write("\n");
      if(int_array[pin_num]==1){
        Serial.write("HIGH\n");
      }
      if(int_array[pin_num]==0){
        Serial.write("LOW\n");
      }
      pin_str = "";
    }
  }
  delay(100);
}
