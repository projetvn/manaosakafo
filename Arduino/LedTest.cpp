#include "Arduino.h"
#include <avr/interrupt.h>
#include "pins_arduino.h"
#include "LedTest.h"

LedTest::LedTest()
{
  
}

LedTest::~LedTest()
{

}

void LedTest::setPin(int p)
{
  pin = p;
  pinMode(pin, OUTPUT);
}

int LedTest::getPin()
{
  return pin;
}

void LedTest::allumer()
{
  digitalWrite(pin, HIGH);
}

void LedTest::eteindre()
{
  digitalWrite(pin, LOW);
}