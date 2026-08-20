#include "headers.h"
#include "Pompe.h"
Ultrason U;
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

  U.setPinEcho(11);
  U.setPinTrig(12);

  plaque.setPin(2);
  eau.mettreEnPlace(4);
  
  sel.miseEnPlace(5);
  huile.miseEnPlace(6);

  cuilliere.fixer(9, 10);

  charger.setPin(8);
  lancer.setPin(7);

  charger.setEtatprecedent(digitalRead(charger.getPin()));
  lancer.setEtatprecedent(digitalRead(lancer.getPin()));

  plaque.eteindre();

  verserEau(250);

}

void loop() 
{
  /*while(charge==false)
    detectionPresence();
  while(C==false)
    recipientCharge();
  while(L==false)
    lancerCuistot();
  travails();*/
}
