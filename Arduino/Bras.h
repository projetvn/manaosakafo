#ifndef DEF_BRAS
#define DEF_BRAS

#include <Servo.h>

class Bras
{
  public:
    Bras();
    ~Bras();
    void fixer(int c, int m);
    void melanger();
    void descendre();
    void monter();

  private:
    Servo coud, melangeur;
};

#endif