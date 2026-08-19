#include "headers.h"
#include "Pompe.h"
Contenant sel, huile;
Bras cuilliere;
Bouton charger, lancer;
Pompe eau;
Plaque plaque;
bool charge, C, L;
void setup() 
{
  Serial.begin(9600);

  charge = false;
  C=false;
  L=false;
  sel.miseEnPlace(9);
  huile.miseEnPlace(10);

  cuilliere.fixer(5, 6);

  charger.setPin(7);
  lancer.setPin(8);

  charger.setEtatprecedent(digitalRead(charger.getPin()));
  lancer.setEtatprecedent(digitalRead(lancer.getPin()));
}

void loop() 
{
  detectionPresence();
  recipientCharge();
  lancerCuistot();
  travails();
}
