import processing.serial.*;
import java.io.File;
import java.lang.*;

Serial port;
int page, i, j;
String nom;
JSONArray plats;
JSONObject json;
float y;
Bouton[] choix;
int nbchoix;
volatile boolean analyseEnCours;
volatile boolean resultatPret;
String ligne;
JSONArray preparation_manuelle;
JSONArray preparation_robot;
String etapesManuelle;
String etapesRobot;
boolean alerte;
int count;
color FOND;
color CARTE;
color BORDURE;
color TEXTE;
color TEXTE2;
color BRUN;
color BRUN_CLAIR;
color INFO;
color BARRE_FOND;
color BARRE;
int indexPlat;
boolean robot;
Bouton retour;
int section;

void setup() {
  size(1300, 700);
  
  retour=new Bouton();
  section=0;//1 si afficherplat 2 si afficherprepman 3 si afficheretaperobot
  
  port=new Serial(this, "/dev/ttyACM0", 9600);
  port.bufferUntil('\n');

  page=0;
  analyseEnCours=false;
  resultatPret=false;
  alerte=false;
  count=0;
  robot=false;

  FOND=color(250, 247, 243);
  CARTE=color(255, 253, 250);
  BORDURE=color(225, 215, 205);
  TEXTE=color(55, 38, 29);
  TEXTE2=color(100, 72, 55);
  BRUN=color(75, 48, 35);
  BRUN_CLAIR=color(145, 92, 60);
  INFO=color(246, 237, 228);
  BARRE_FOND=color(228, 220, 213);
  
  retour.setPosition(20,20,100,30);
  retour.setColor(TEXTE);
  retour.setColorh(100, 72, 55);
  retour.setText("retour");
  retour.setTextxPosition(70);
  retour.setTextColor(250);
}

void draw() {
  background(FOND);

 
    ligne=port.readStringUntil('\n');
    if(ligne!=null){
      ligne=trim(ligne);

      println("Arduino : " + ligne);

      if(ligne.equals("2") && !analyseEnCours){
        //declencherAnalyse();
        chargerResultat();
      }
  }

  if(page==0){
    if(analyseEnCours){
      afficherAnalyse();
    }

    else if(resultatPret){
      afficherPlats();
    }

    else{
      afficherEtatInitial();
    }
  }

  else{
    if(plats != null && page >= 1 && page <= plats.size()){
      indexPlat=page-1;

      if(ligne!=null && ligne.equals("3")){
        robot=true;
      }
      
      if(robot){
        if(ligne!=null && ligne.equals("3")){
           envoyerEtapeRobot();
         }
         afficherPreparationRobot();
      }

      else{
        afficherPreparationManuelle(indexPlat);
      }
    }
  }
}

void mousePressed() {
  if(page==0 && resultatPret){
    for(i=0;i<nbchoix;i++){
      if(choix[i].clicked()){
        page=i+1;
        count=0;
        break;
      }
    }
  }
  
  if(retour.clicked()){
    if(section==1){
      resultatPret=false;
    }
    
    else if(section==2){
      page=0;
    }
    
    else{
      page=0;
      resultatPret=false;
      robot=false;
    }
  }
}
