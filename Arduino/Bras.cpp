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
  int i;
  for(i=10; i<=85; i+=5)
  {
    coud.write(i);
    delay(250);
  }
  delay(500);
  melangeur.write(70);
}

void Bras::monter()
{
  int i;
  melangeur.write(90);
  delay(500);
  for(i=80; i>=0; i-=5)
  {
    coud.write(i);
    delay(250); 
  }
}
