// Original code from Cathal?, modified at some point. Currently installed in the FNAL, Lab6, darkroom LAPPD test 
efine ENCODER_USE_INTERRUPTS

#include <Encoder.h>

// ---- All the parameters a user might want to change are in this block ----
bool move_leftright;// = true; // if false we will move up/down
double setpoint = -56000; // Desired position. (+ve) = towards wall / up, (-ve) = towards us / down
int wait_time_base = 1; // Wait time in ms before we try update the motor
int wait_time_flip = 100; // Wait time in ms before we try update the motor after overshooting
int wait_time_print = 1000; // Wait time in ms before printing again
int wait_time_home = 1000; // Once we reach our destination, how long do we wait before resetting and moving again
double base_speed = 30.; // default motor speed
double floor_speed = 2.; // minimum speed of motor
int home_limit = 500; // if we have been at the destination for this many checks, we are done
bool debug = false; // should be false for normal operation, otherwise operation will be degraded
// --------------------------------------------------------------------------

int wait_time = wait_time_base;
double speed = base_speed; // FYI technically this gets cast to an int when we write to a pwm pin
double currentPosition = 0;  // Encoder position
double last_pos = 0; // What was the encoder position last time we checked
bool forward = true; // motor direction. true = forward, false = backward
bool flip = false; // if the motor has just overshot, this will be true for 100ms

int nHome = 0; // number of consecutive times we have checked and the motor is at the destination
int nSame = 0; // number of consecutive times we have checked and the motor is at the same location (not destination)
int nRun = 0; // how many times have we reset and started again
int counter = 0; // number of times loop() has executed. just for debugging

// Which pin you use for what matters, don't change without doing some research.
// Intialise with pins for left/right movement

int motorPin1;
int motorPin2;
int pwmPin;
int encoderPinA;
int encoderPinB;

// Initialise all these times to current time as placeholder
unsigned long last_time = millis(); // timestamp of time we most recently checked on the motor
unsigned long last_time_home = millis(); // timestamp when we reached our destination ("home")
unsigned long last_time_print = millis(); // timestamp when we last printed out values. Warning - printing degrades encoder performance, only do it for debugging

Encoder myEncoder; // This guy will keep track of the motor position

// Flag to track if the motor should start moving
bool motorReady = false;  // New flag to indicate if motor movement should start

void setup() {
  Serial.begin(9600);  // for printouts
  delay(1000); // wait 1s so the serial is set up before we print
  Serial.println("not done");

  if(debug){
    Serial.println("********************************");
    Serial.println("******    WARNING!!!!    *******");
    Serial.println("********************************");
    Serial.println("Debug mode will severely degrade encoder performance");
  }
}

void loop() {
  // Read the current encoder position
  currentPosition = myEncoder.read();

  unsigned long time = millis();
  counter++;

  // Check if there is incoming serial data
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the incoming command
    command.trim();  // Remove any leading or trailing whitespace

    // Print out the received command for debugging
    Serial.print("Received command: ");
    Serial.println(command);

    // Split the command by spaces into parts
    String action = getCommandPart(command, 0);
    String direction = getCommandPart(command, 1);
    String distanceStr = getCommandPart(command, 2);
    int distance = distanceStr.toInt();  // Convert the distance argument to an integer

    // Process the command based on the action
    if (action == "move") {
      if (direction == "left" || direction == "right" || direction == "up" || direction == "down") {
        // Set the direction and setpoint based on the command
        if (direction == "left") {
          setpoint = distance;  // Move left (positive setpoint)
          forward = true;       // Set direction to forward
          motorReady = true;    // Enable motor movement
          move_leftright = true;  // Enable left/right mode
          Serial.print("Moving left by ");
          Serial.println(distance);

          // reasign the pins
          motorPin1 = 12;
          motorPin2 = 13;
          pwmPin = 11;
          encoderPinA = 6;
          encoderPinB = 7;
          myEncoder.begin(encoderPinA, encoderPinB);
          // Initialize motor pins
          pinMode(motorPin1, OUTPUT);
          pinMode(motorPin2, OUTPUT);
          pinMode(pwmPin, OUTPUT);
        }
        else if (direction == "right") {
          setpoint = -distance; // Move right (negative setpoint)
          forward = false;      // Set direction to backward
          motorReady = true;    // Enable motor movement
          move_leftright = true;  // Enable left/right mode
          Serial.print("Moving right by ");
          Serial.println(distance);

          // reasign the pins
          motorPin1 = 12;
          motorPin2 = 13;
          pwmPin = 11;
          encoderPinA = 6;
          encoderPinB = 7;

          myEncoder.begin(encoderPinA, encoderPinB);

          // Initialize motor pins
          pinMode(motorPin1, OUTPUT);
          pinMode(motorPin2, OUTPUT);
          pinMode(pwmPin, OUTPUT);
        }
        else if (direction == "up") {
          setpoint = distance;  // Move up (positive setpoint)
          forward = true;       // Set direction to forward
          motorReady = true;    // Enable motor movement
          move_leftright = false; // Switch to up/down mode
          Serial.print("Moving up by ");
          Serial.println(distance);

          //reasign the pins
          motorPin1 = 8;
          motorPin2 = 10;
          pwmPin = 9;
          encoderPinA = 3;
          encoderPinB = 4;
          myEncoder.begin(encoderPinA, encoderPinB);

          // Initialize motor pins
          pinMode(motorPin1, OUTPUT);
          pinMode(motorPin2, OUTPUT);
          pinMode(pwmPin, OUTPUT);
        }
        else if (direction == "down") {
          setpoint = -distance; // Move down (negative setpoint)
          forward = false;      // Set direction to backward
          motorReady = true;    // Enable motor movement
          move_leftright = false; // Switch to up/down mode
          Serial.print("Moving down by ");
          Serial.println(distance);
          // Optionally, you could update motor pins for up/down movement
          motorPin1 = 8;
          motorPin2 = 10;
          pwmPin = 9;
          encoderPinA = 3;
          encoderPinB = 4;
          myEncoder.begin(encoderPinA, encoderPinB);

          // Initialize motor pins
          pinMode(motorPin1, OUTPUT);
          pinMode(motorPin2, OUTPUT);
          pinMode(pwmPin, OUTPUT);
        }
      } else {
        Serial.println("Invalid direction. Use 'left', 'right', 'up', or 'down'.");
      }
    }
    else if (command == "reset") {
      resetState();  // Reset all variables to initial state
      Serial.println("System reset.");
    }
    else {
      Serial.println("Unknown command. Use 'move [direction] [distance]' or 'reset'.");
    }
  }

  // Only move the motor if the motorReady flag is true
  if (motorReady) {
    time = millis();
    counter++;

    // The rest of the motor movement logic remains the same
    if (nHome < home_limit) {
      if ((time - last_time > wait_time)) {
        last_time = time;

        if (flip) {
          wait_time = wait_time_base; // go back to default wait_time
        }

        if (currentPosition == last_pos) { // motor might be stuck
          nSame++;
        }
        else {
          nSame = 0;
        }
        last_pos = currentPosition;

        if (nSame > 1000) { // if we haven't moved in 1000 function calls, increase the speed
          speed *= 2.0;
          nSame = 0;
        }

        flip = false;
        if (currentPosition == setpoint) {
          nHome++;
        }
        else if (((currentPosition < setpoint) && !forward) || ((currentPosition > setpoint) && forward)) {
          forward = !forward;
          nHome = 0;
          flip = true;
          speed /= 1.03;
          wait_time = wait_time_flip; // temporarily increase wait time, so the motor can finish drifting
        }

        if (speed < floor_speed) {
          speed = floor_speed;
        }
        else if (speed > base_speed) {
          speed = base_speed;
        }

        if (flip) { // we have just overshot, let's stop moving temporarily
          digitalWrite(motorPin1, LOW);
          digitalWrite(motorPin2, LOW);
        }
        else if (nHome >= (home_limit - 1)) { // we are done, stop moving the motor
          digitalWrite(motorPin1, LOW);
          digitalWrite(motorPin2, LOW);
          last_time_home = time;
        }
        else if (!forward) {
          digitalWrite(motorPin1, HIGH);
          digitalWrite(motorPin2, LOW);
          analogWrite(pwmPin, speed);
        }
        else if (forward) {
          digitalWrite(motorPin1, LOW);
          digitalWrite(motorPin2, HIGH);
          analogWrite(pwmPin, speed);
        }
      }  // end if( (time - last_time > wait_time) )
    } //end if(nHome < 500)
    else if ((time - last_time_home) > wait_time_home) { // after some amount of time, execute reset function.
      resetState();
      Serial.println("Home limit reached. Resetting.");
    }
  } // End of motor movement block

}
// Helper function to extract parts of the command
String getCommandPart(String command, int partIndex) {
  int startIdx = 0;
  int endIdx = command.indexOf(' ', startIdx);
  int partCounter = 0;

  while (endIdx != -1 && partCounter < partIndex) {
    startIdx = endIdx + 1;
    endIdx = command.indexOf(' ', startIdx);
    partCounter++;
  }

  int partEndIdx = (endIdx == -1) ? command.length() : endIdx;
  return command.substring(startIdx, partEndIdx);
}

// This function resets system variables to their initial state
void resetState() {
  // Reset all relevant variables to initial values
  currentPosition = 0;
  last_pos = 0;
  forward = true;
  flip = false;
  nHome = 0;
  nSame = 0;
  nRun++;
  motorReady = false;
  speed = base_speed;
  setpoint = 0;
  wait_time = wait_time_base;
  last_time = millis();
  last_time_home = millis();
  last_time_print = millis();

  // Reset motor pins (turn off motor)
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  analogWrite(pwmPin, 0);  // Ensure motor is stopped

  Serial.println("State reset complete.");
}


void print() {
  Serial.println("********************************");
  Serial.print("Setpoint: ");
  Serial.println(setpoint);
  Serial.print(" Current Position: ");
  Serial.println(currentPosition);
  Serial.print(" Counter: ");
  Serial.println(counter);
  Serial.print(" nHome: ");
  Serial.println(nHome);
  Serial.print(" Speed: ");
  Serial.println(speed);
  Serial.print(" nSame: ");
  Serial.println(nSame);
  Serial.print(" Forward: ");
  Serial.println(forward);
  Serial.println("------------");
}
