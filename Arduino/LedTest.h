#ifndef DEF_LEDTEST
#define DEF_LEDTEST

class LedTest 
{
  public:
    LedTest();
    ~LedTest();
    void setPin(int p);
    int getPin();
    void allumer();
    void eteindre();

  private:
    int pin;
};

#endif