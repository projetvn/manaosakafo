#include <string.h>
#include "Arduino.h"
#include <math.h>
#include "HardwareSerial.h"
#include "headers.h"

void detectionPresence()
{
  float d;
  d = 19;
  if(U.calculDistance()<d)
  {
    if(charge==false)
    {
      charge = true;
      Serial.println("1");
    }
  }
}

void recipientCharge()
{
  charger.setEtatActuel(digitalRead(charger.getPin()));
  if(charger.getEtatPrecedent()==HIGH && charger.getEtatActuel()==LOW)
  {
    if(C==false)
    {
      Serial.println("2");
      C=true;
    }
  }
  charger.setEtatprecedent(charger.getEtatActuel());
}

void lancerCuistot()
{
  lancer.setEtatActuel(digitalRead(lancer.getPin()));
  if(lancer.getEtatPrecedent()==HIGH && lancer.getEtatActuel()==LOW)
  {
    if(L==false)
    {
      Serial.println("3");
      L=true;
    }
  }
  lancer.setEtatprecedent(lancer.getEtatActuel());
}


void ajoutSel(int poids)
{
  int i, nb;
  /*
    1g -> une fois
    poids-> nb fois
    nb = poids;
  */
  nb = poids;

  for(i=0; i<nb-1; i++)
  {
    sel.verser(165);
    //ledSel.allumer();
    delay(250);
    //ledSel.eteindre();
    sel.verser(180);
    delay(250); 
  }
  sel.verser(90);
  delay(250);
  sel.remettreEnPlace(0);
}

void verserHuile(int poids)
{
  int i;
  unsigned long temps;
  temps = 0;
  /*
    1ml->1000ms
    poids->temps
    temps=poids*1000;
  */
  temps = poids*1000UL;
  for(i=170; i>30; i-=5)
  {
    huile.verser(i);
    delay(500);
  }
  delay(temps);
  for(i=30; i<=180; i+=10)
  {
    huile.remettreEnPlace(i);
    delay(500);
  }
}

void verserEau(int poids)
{
  unsigned long temps;
  /*
    250ml->9440ms
    poids->temps;
    donc temps=(poids*9440)/250
  */
  temps = ((unsigned long)poids * 9440UL) / 250;
  eau.verser(temps);

}

void melanger(unsigned long duree)
{
  duree = duree*1000UL;
  cuilliere.descendre();
  delay(duree);
  cuilliere.monter();
}

bool travails()
{
  char buffer[50];
  char temp2[6][16];
  int bufferLen, temp2Len, i;
  unsigned long debut;
  char c;
  bufferLen = 0;
  temp2Len = 0;
  if (Serial.available())
  {
    c = Serial.read();
    while (c != '\n')
    {
      if (bufferLen < 49)  // protection contre débordement
      {
        buffer[bufferLen++] = c;
      }
      while (!Serial.available());
      c = Serial.read();
    }
    buffer[bufferLen] = '\0';
    if (strcmp(buffer, "stop") == 0)
    {
      plaque.eteindre();
      return true;
    }
    else
    {
      char *token = strtok(buffer, ",");
      while (token != NULL && temp2Len < 6)
      {
        strcpy(temp2[temp2Len], token);
        temp2Len++;
        token = strtok(NULL, ",");
      }

      debut = millis();
      for (i = 0; i < temp2Len; i++)
      {
        char *temp = strtok(temp2[i], "=");
        char *valStr = strtok(NULL, "=");

        // ignore les tokens malformes
        if (temp == NULL || valStr == NULL)
          continue;

        // ignore un token qui n'est compose que d'espaces
        while (*temp == ' ') temp++;
        if (*temp == '\0')
          continue;

        int valeur = atoi(valStr);

        if (strcmp(temp, "sel") == 0)
        {
          ajoutSel(valeur);
        }
        else if (strcmp(temp, "huile") == 0)
        {
          verserHuile(valeur);
        }
        else if (strcmp(temp, "eau") == 0)
        {
          verserEau(valeur);
        }
        else if (strcmp(temp, "melanger") == 0)
        {
          melanger(valeur);
        }
        else if (strcmp(temp, "activer") == 0)
        {
          if(plaque.getEtat()==valeur)
          {
            continue;
          }
          else 
          {
            if(valeur==1)
              plaque.activer();
            else
             plaque.eteindre();
          }
        }
        else if (strcmp(temp, "duree") == 0)
        {
          unsigned long val;
          val = valeur*1000UL;
          unsigned long ecoule = millis() - debut;
          if(ecoule < (unsigned long)val)
          {
            delay(val - ecoule);
          }
        }
      }
    }

    // Accuse de reception TOUJOURS envoye, quel que soit le contenu de la ligne
    Serial.println("3");
  }

  return false;
}