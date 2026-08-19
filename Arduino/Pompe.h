#ifndef DEF_POMPE
#define DEF_POMPE

class Pompe 
{
  public:
    Pompe();
    ~Pompe();
    void mettreEnPlace(int p);
    void verser(int temps);
  
  private:
    int pin;
};

#endif