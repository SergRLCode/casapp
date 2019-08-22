int pinOne = 2;
int pinTwo = 3;
int pinThree = 4;
int pinFour = 5;

String focus_state = "";

void setup() {
  Serial.begin(9600);
  pinMode(pinOne, OUTPUT);
  pinMode(pinTwo, OUTPUT);
  pinMode(pinThree, OUTPUT);
  pinMode(pinFour, OUTPUT);
}

void loop() {
  while (Serial.available()){
    focus_state = Serial.readString();
    Serial.println(focus_state);
    if (focus_state == "one_on"){  
      digitalWrite(pinOne, HIGH);
    } else if (focus_state == "one_off"){
      digitalWrite(pinOne, LOW);
    } else if (focus_state == "two_on"){
      digitalWrite(pinTwo, HIGH);
    } else if (focus_state == "two_off"){
      digitalWrite(pinTwo, LOW);
    } else if (focus_state == "three_on"){
      digitalWrite(pinThree, HIGH);
    } else if (focus_state == "three_off"){
      digitalWrite(pinThree, LOW);
    } else if (focus_state == "four_on"){
      digitalWrite(pinFour, HIGH);
    } else if (focus_state == "four_off"){
      digitalWrite(pinFour, LOW);
    }
    focus_state="";
  }
}
