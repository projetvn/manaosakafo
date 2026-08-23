#ifndef DEF_PLAQUE
#define DEF_PLAQUE  

class Plaque
{
  public:
    Plaque();
    ~Plaque();
    void setPin(int p);
    int getPin();
    int getEtat();
    void activer();
    void eteindre();

  private:
    int pin, etat;
};

#endif