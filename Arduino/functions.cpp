#include <math.h>
#include "HardwareSerial.h"
#include "headers.h"

void detectionPresence()
{
  float d;
  d = 19;
  Ultrason U;
  U.setPinEcho(8);
  U.setPinTrig(7);
  if(U.calculDistance()<d)
  {
    Serial.println(U.calculDistance());
  }
}
unsigned long tempsD_Inclinaison(float poids)
{
  
}