#ifndef DEF_PLAQUE
#define DEF_PLAQUE  

class Plaque
{
  public:
    Plaque();
    ~Plaque();
    void setPin(int p);
    void getPin(int p);
    void activer();
    void eteindre();

  private:
    int pin;
};

#endif