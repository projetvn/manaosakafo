#include "HardwareSerial.h"
#include "headers.h"

void detectionPresence()
{
  float d;
  d = 21.5;
  Ultrason U;
  U.setPinEcho(8);
  U.setPinTrig(7);
  if(U.calculDistance()<d)
  {
    Serial.println("P");
  }
}