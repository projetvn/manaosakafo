#include "Arduino.h"
#include "Pompe.h"

Pompe::Pompe()
{

}

Pompe::~Pompe()
{

}

void Pompe::mettreEnPlace(int p)
{
  pin = p;
}

void Pompe::verser(int temps)
{
  digitalWrite(pin, HIGH);
  delay(temps);
  digitalWrite(pin, LOW);
}