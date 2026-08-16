#include "Contenant.h"

Contenant::Contenant()
{

}

Contenant::~Contenant()
{

}

void Contenant::miseEnPlace(int p)
{
  servoContenant.attach(p);
}

void Contenant::verser(float angle)
{
  servoContenant.write(angle);
}

void Contenant::remettreEnPlace(float angle)
{
  servoContenant.write(0);
}