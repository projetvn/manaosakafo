#ifndef DEF_ULTRASON
#define DEF_ULTRASON

class Ultrason
{
  public:
    Ultrason();
    ~Ultrason();
    void setPinEcho(int p);
    void setPinTrig(int p);
    float calculDistance();
  
  private:
    int pinEcho, pinTrig;
    float distance;
};

#endif