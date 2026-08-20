#include <avr/interrupt.h>
#include "Arduino.h"
#include "Bouton.h"

Bouton::Bouton()
{
  etatPrecedent=HIGH;
}

Bouton::~Bouton()
{

}

void Bouton::setPin(int p)
{
  pin=p;
  pinMode(pin, INPUT_PULLUP);
}

void Bouton::setEtatprecedent(int ep)
{
  etatPrecedent=ep;
}

void Bouton::setEtatActuel(int ea)
{
  etatActuel=ea;
}

int Bouton::getPin()
{
  return pin;
}

int Bouton::getEtatPrecedent()
{
  return etatPrecedent;
}

int Bouton::getEtatActuel()
{
  return etatActuel;
}