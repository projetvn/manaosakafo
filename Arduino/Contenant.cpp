#include "Contenant.h"

Contenant::Contenant()
{

}

Contenant::~Contenant()
{

}

void Contenant::setPin(int p)
{
  pin=p;
  servoContenant.attach(pin);
}

void Contenant::verser(float angle)
{
  servoContenant.write(angle);
}

void Contenant::remettreEnPlace(float angle)
{
  servoContenant.write(0);
}