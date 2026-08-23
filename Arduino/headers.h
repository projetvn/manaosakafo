#include "Ultrason.h"
#include "Contenant.h"
#include "Bras.h"
#include "Pompe.h"
#include "Bouton.h"
#include "Plaque.h"
#include "LedTest.h"

extern Ultrason U;
extern Contenant sel, huile;
extern Bras cuilliere;
extern bool charge, C, L;
extern Bouton charger, lancer;
extern Pompe eau;
extern Plaque plaque;
extern LedTest ledBras, ledSel, ledHuile;
void detectionPresence();
void ajoutSel(int poids);
void verserHuile(int poids);
void verserEau(int poids);
void melanger(unsigned long duree);
unsigned long calibreVersementHuile(int poids);
void recipientCharge();
void lancerCuistot();
bool travails();