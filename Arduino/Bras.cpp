#include "Arduino.h"
#include "Bras.h"

Bras::Bras()
{

}

Bras::~Bras()
{

}

void Bras::fixer(int c, int m)
{
  coud.attach(c);
  melangeur.attach(m);
  coud.write(0);
}

void Bras::descendre()
{
  coud.write(90);
  delay(500);
  melangeur.write(70);
}

void Bras::monter()
{
  melangeur.write(0);
  delay(500);
  coud.write(0);
}
