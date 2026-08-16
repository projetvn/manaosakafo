#include <Servo.h>
#ifndef DEF_CONTENANT
#define DEF_CONTENANT

class Contenant
{
  public:
    Contenant();
    ~Contenant();
    void miseEnPlace(int p);
    void verser(float angle);
    void remettreEnPlace(float angle);
  
  private:
    Servo servoContenant;
};

#endif