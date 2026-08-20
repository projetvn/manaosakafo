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
  pinMode(pin, OUTPUT);
  digitalWrite(pin, HIGH);
}

void Pompe::verser(unsigned long temps)
{
  digitalWrite(pin, LOW);
  delay(temps);
  digitalWrite(pin, HIGH);
}