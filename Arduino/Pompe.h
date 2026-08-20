#ifndef DEF_POMPE
#define DEF_POMPE

class Pompe 
{
  public:
    Pompe();
    ~Pompe();
    void mettreEnPlace(int p);
    void verser(unsigned long temps);
  
  private:
    int pin;
};

#endif