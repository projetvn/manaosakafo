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

void Plaque::activer()
{
  digitalWrite(pin, HIGH);
}

void Plaque::eteindre()
{
  digitalWrite(pin, LOW);
}