#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;
int teamRood = 16;
int teamBlauw = 17;
int vibrator = 21;
long timeStart;
String bericht;

const int SHORT_PRESS_TIME = 1000; // 1000 milliseconds
const int LONG_PRESS_TIME  = 1000; // 1000 milliseconds

int switchpower = 2;
bool slep = 0;

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
  pinMode(GPIO_NUM_2, INPUT_PULLUP);
}

void vibrate(){
     digitalWrite(vibrator, HIGH);
     delay(100);
     digitalWrite(vibrator, LOW);
  }
void setup_sleep() {
  /*
      First we configure the wake up source
      We set our ESP32 to wake up every 5 seconds
  */

  // Hieronder optie om vanzelf elke zoveel tijd wakker te laten worden, nu niet nodig
  //esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR * S_TO_H_FACTOR);

  // hier om wakeup via btn te doen
  esp_sleep_enable_ext0_wakeup(GPIO_NUM_2, 0);
  
  delay(10);

  // en rest van example  

  /*
    Next we decide what all peripherals to shut down/keep on
    By default, ESP32 will automatically power down the peripherals
    not needed by the wakeup source, but if you want to be a poweruser
    this is for you. Read in detail at the API docs
    http://esp-idf.readthedocs.io/en/latest/api-reference/system/deep_sleep.html
    Left the line commented as an example of how to configure peripherals.
    The line below turns off all RTC peripherals in deep sleep.
  */
  //esp_deep_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);
  //Serial.println("Configured all RTC Peripherals to be powered down in sleep");

  /*
    Now that we have setup a wake cause and if needed setup the
    peripherals state in deep sleep, we can now start going to
    deep sleep.
    In the case that no wake up sources were provided but deep
    sleep was started, it will sleep forever unless hardware
    reset occurs.
  */
  //LoRa.end(); // LORA antenne hangt er bij jullie niet aan
  //LoRa.sleep();
  delay(100);


  pinMode(5, INPUT);

  pinMode(14, INPUT);
  pinMode(15, INPUT);
  pinMode(16, INPUT);
  pinMode(17, INPUT);
  pinMode(18, INPUT);
  pinMode(19, INPUT);

  pinMode(26, INPUT);
  pinMode(27, INPUT);


  delay(100);
  Serial.println("Going to sleep now");
  delay(2);
  esp_deep_sleep_start();
  Serial.println("This will never be printed");
}

void loop() {
  //switch on/off
 if(digitalRead(switchpower) == HIGH && slep == 0){
    Serial.println("sleep");
    setup_sleep();
    slep = 1;
    delay(100);
  }
  
  if(digitalRead(switchpower) == LOW && slep == 1){
    slep = 0;
    Serial.println("no sleep");
    vibrate();
    delay(100);
  }

  if (Serial.available()) {
    SerialBT.write(Serial.read());
  }
  if (SerialBT.available()) {
    int connection = SerialBT.read();
    String connectionString = String(connection);
    if (connectionString = "10991111101101019911610110010") {
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
  } 
  else if(lastStateRood == LOW && currentStateRood == HIGH) { // button is released
    if (isPressingRood == true) {
      bericht = "teamRoodUp";
      vibrate();
      SerialBT.print(bericht);
      Serial.println(bericht);
    }
    isPressingRood = false;      
  }

  else if(isPressingRood == true && isLongDetectedRood == false) {
    long pressDurationRood = millis() - pressedTimeRood;

    if( pressDurationRood > LONG_PRESS_TIME ) {
      bericht = "teamRoodDown";
      vibrate();
      SerialBT.print(bericht);
      Serial.println(bericht);
      isLongDetectedRood = true;
      isPressingRood = false;
    }
  }

  if(lastStateBlauw == HIGH && currentStateBlauw == LOW) {        // button is pressed
    pressedTimeBlauw = millis();
    isPressingBlauw = true;
    isLongDetectedBlauw = false;
  } 
  else if(lastStateBlauw == LOW && currentStateBlauw == HIGH) { // button is released
    if (isPressingBlauw == true) {
      bericht = "teamBlauwUp";
      vibrate();
      SerialBT.print(bericht);
      Serial.println(bericht);
    }
    isPressingBlauw = false;
  }
  else if(isPressingBlauw == true && isLongDetectedBlauw == false) {
    long pressDurationBlauw = millis() - pressedTimeBlauw;

    if( pressDurationBlauw > LONG_PRESS_TIME ) {
      bericht = "teamBlauwDown";
      vibrate();
      SerialBT.print(bericht);
      Serial.println(bericht);
      isLongDetectedBlauw = true;
      isPressingBlauw = false;
    }
  }

  // save the the last state
  lastStateRood = currentStateRood;
  lastStateBlauw = currentStateBlauw;
}