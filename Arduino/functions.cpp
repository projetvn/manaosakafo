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
  for(i=0; i<nb; i++)
  {
    sel.verser(180);
    delay(500);
    sel.remettreEnPlace(0);
  }
}

void verserHuile(int poids)
{
  int temps;
  temps = 0;
  /*
    1ml->1000ms
    poids->temps
    temps=poids*1000;
  */
  temps = poids*1000;
  huile.verser(180);
  delay(temps);
  huile.remettreEnPlace(0);
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
  Serial.println(temps);
  eau.verser(temps);
}

void melanger(int duree)
{
  cuilliere.descendre();
  delay(duree);
  cuilliere.monter();
}

void travails()
{
  char buffer[50];
  char temp2[6][10];
  int tempNombre, bufferLen, tempLen, temp2Len, i;
  unsigned long debut, duree;
  char c;
  bufferLen=0;
  tempLen=0;
  temp2Len=0;
  if(Serial.available())
  {
    c=Serial.read();
    while(c!='\n')
    {
      buffer[bufferLen++]=c;
      while(!Serial.available());
      c=Serial.read();
    }
    
    buffer[bufferLen]='\0';
    //strcpy(buffer,"sel=2,activer=0,duree=1000");
    if(strcmp(buffer, "stop")==0)
    {
      plaque.eteindre();
    }
    
    else
    {
      char *token = strtok(buffer, ",");
      while (token!=NULL && temp2Len<5)
      {
        strcpy(temp2[temp2Len], token);
        temp2Len++;
        token = strtok(NULL, ",");
      }
      for(i=0; i<temp2Len; i++)
      {
        debut = millis();
        char *temp = strtok(temp2[i], "=");
        Serial.println(temp);
        int valeur = atoi(strtok(NULL, "="));
        if(strcmp(temp, "sel")==0)
        {
          ajoutSel(valeur);
        }
        else if(strcmp(temp, "huile")==0)
        {
          verserHuile(valeur);
        }
        else if(strcmp(temp, "eau")==0)
        {
          verserEau(valeur);
        }
        else if(strcmp(temp, "melanger")==0)
        {
          melanger(valeur);
        }
        else if(strcmp(temp, "activer")==0)
        {
          if(valeur==1)
            plaque.activer();
          else if(valeur==0)
            plaque.eteindre();
        }

        else if(strcmp(temp, "duree")==0)
        {
          if(millis()-debut<valeur)
          {
            delay(valeur-millis()-debut);
          }
          Serial.println("3");
        }
      } 
    }
  }

  charge=false;
  C=false;
  L=false;
}