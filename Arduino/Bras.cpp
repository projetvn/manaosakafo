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
}

void Bras::monter()
{
  coud.write(0);
}