#include "Servo.h"
#include "Contenant.h"

Contenant::Contenant()
{

}

Contenant::~Contenant()
{

}

void Contenant::miseEnPlace(int p)
{
  if(p==6)
  {
    servoContenant.write(180);
    servoContenant.attach(p);
    servoContenant.write(180);
  }
  else
  {
    servoContenant.write(0);
    servoContenant.attach(p);
  }
}

void Contenant::verser(float angle)
{
  servoContenant.write(angle);
}

void Contenant::remettreEnPlace(float angle)
{
  servoContenant.write(angle);
}