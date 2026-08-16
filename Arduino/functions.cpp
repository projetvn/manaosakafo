#include "HardwareSerial.h"
#include "headers.h"

void detectionPresence()
{
  float d;
  d = 19.60;
  Ultrason U;
  U.setPinEcho(8);
  U.setPinTrig(7);
  if(U.calculDistance()<d || U.calculDistance()>20)
  {
    Serial.println("P");
  }
}