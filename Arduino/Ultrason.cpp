#include "Arduino.h"
#include "Ultrason.h"

Ultrason::Ultrason()
{

}

Ultrason::~Ultrason()
{

}

void Ultrason::setPinEcho(int p)
{
  pinEcho = p;
}

void Ultrason::setPinTrig(int p)
{
  pinTrig = p;
}

float Ultrason::calculDistance()
{
  float t, v;
  t=0;
  v=0.034;
  distance=0;

  digitalWrite(pinTrig, LOW);
  delayMicroseconds(2);
  digitalWrite(pinTrig, HIGH);
  delayMicroseconds(10);
  digitalWrite(pinTrig, LOW);
  
  t = pulseIn(pinEcho, HIGH);
  distance = v*t/2;

  return distance;

}