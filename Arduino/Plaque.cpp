#include "Arduino.h"
#include "Plaque.h"

Plaque::Plaque()
{

}

Plaque::~Plaque()
{

}

void Plaque::setPin(int p)
{
  pin = p;
  pinMode(pin, OUTPUT);
}

int Plaque::getPin()
{
  return pin;
}

int Plaque::getEtat()
{
  return etat;
}

void Plaque::activer()
{
  digitalWrite(pin, HIGH);
  etat=1;
}

void Plaque::eteindre()
{
  digitalWrite(pin, LOW);
  etat=0;
}