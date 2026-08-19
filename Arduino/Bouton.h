#ifndef DEF_BOUTON
#define DEF_BOUTON

class Bouton
{
  public:
    Bouton();
    ~Bouton();
    void setPin(int p);
    void setEtatprecedent(int ep);
    void setEtatActuel(int ea);
    int getPin();
    int getEtatPrecedent();
    int getEtatActuel();

  private:
    int pin, etatActuel, etatPrecedent;
};

#endif