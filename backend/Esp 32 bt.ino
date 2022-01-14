#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;
int teamRood = 22;
int teamBlauw = 23;
int vibrator = 21;
long timeStart;
String bericht;

const int SHORT_PRESS_TIME = 1000; // 1000 milliseconds
const int LONG_PRESS_TIME  = 1000; // 1000 milliseconds

// Variables will change:
int lastStateRood = LOW;
int lastStateBlauw = LOW;
int currentStateRood;
int currentStateBlauw;
unsigned long pressedTimeRood  = 0;
unsigned long pressedTimeBlauw  = 0;
unsigned long releasedTimeRood = 0;
unsigned long releasedTimeBlauw = 0;
bool isPressingRood = false;
bool isPressingBlauw = false;
bool isLongDetectedRood = false;
bool isLongDetectedBlauw = false;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32test"); //Bluetooth device name
  Serial.println("The device started, now you can pair it with bluetooth!");
  pinMode(teamRood, INPUT_PULLUP);
  pinMode(teamBlauw, INPUT_PULLUP);
  pinMode(vibrator, OUTPUT);
}

void vibrate(){
     digitalWrite(vibrator, HIGH);
     delay(100);
     digitalWrite(vibrator, LOW);
  }

void loop() {
  if (Serial.available()) {
    SerialBT.write(Serial.read());
  }
  if (SerialBT.available()) {
    int hallo = SerialBT.read();
    String halloString = String(hallo);
    if (halloString = "10991111101101019911610110010") {
      vibrate();
    }    
  }
  delay(20);
  
 currentStateRood = digitalRead(teamRood);
 currentStateBlauw = digitalRead(teamBlauw);

  if(lastStateRood == HIGH && currentStateRood == LOW) {        // button is pressed
    pressedTimeRood = millis();
    isPressingRood = true;
    isLongDetectedRood = false;
  } else if(lastStateRood == LOW && currentStateRood == HIGH) { // button is released
    isPressingRood = false;
    releasedTimeRood = millis();

    long pressDurationRood = releasedTimeRood - pressedTimeRood;

    if( pressDurationRood < SHORT_PRESS_TIME )
      bericht = "teamRoodUp";
      vibrate();
      SerialBT.print(bericht);
      Serial.println(bericht);
  }

  if(isPressingRood == true && isLongDetectedRood == false) {
    long pressDurationRood = millis() - pressedTimeRood;

    if( pressDurationRood > LONG_PRESS_TIME ) {
      bericht = "teamRoodDown";
      vibrate();
      SerialBT.print(bericht);
      Serial.println(bericht);
      isLongDetectedRood = true;
    }
  }

  if(lastStateBlauw == HIGH && currentStateBlauw == LOW) {        // button is pressed
    pressedTimeBlauw = millis();
    isPressingBlauw = true;
    isLongDetectedBlauw = false;
  } else if(lastStateBlauw == LOW && currentStateBlauw == HIGH) { // button is released
    isPressingBlauw = false;
    releasedTimeBlauw = millis();

    long pressDurationBlauw = releasedTimeBlauw - pressedTimeBlauw;

    if( pressDurationBlauw < SHORT_PRESS_TIME )
      bericht = "teamBlauwUp";
      vibrate();
      SerialBT.print(bericht);
      Serial.println(bericht);
  }

  if(isPressingBlauw == true && isLongDetectedBlauw == false) {
    long pressDurationBlauw = millis() - pressedTimeBlauw;

    if( pressDurationBlauw > LONG_PRESS_TIME ) {
      bericht = "teamBlauwDown";
      vibrate();
      SerialBT.print(bericht);
      Serial.println(bericht);
      isLongDetectedBlauw = true;
    }
  }

  // save the the last state
  lastStateRood = currentStateRood;
  lastStateBlauw = currentStateBlauw;
}
