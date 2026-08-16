#include "headers.h"
Contenant sel, huile, sucre;
Bras cuilliere;
void setup() 
{
  Serial.begin(9600);

  sel.miseEnPlace(9);
  huile.miseEnPlace(10);
  sucre.miseEnPlace(11);

  cuilliere.fixer(5, 6);
  
}

void loop() 
{
  detectionPresence();
}
