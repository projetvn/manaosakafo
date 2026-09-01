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

// --- NOUVELLES VARIABLES POUR LES 3 ÉTAPES ---
int etapeProcessus; // 1: Catégories, 2: Liste Plats, 3: Recette Finale
String categorieChoisie;
String platChoisi;
JSONArray categories;
JSONArray platsDisponibles;

void setup() {
  size(1300, 700);
  
  retour=new Bouton();
  section=0; // 0: Etat initial, 1: Afficher categories, 2: Afficher liste plats, 3: Preparation manuelle, 4: Preparation robot
  
  port=new Serial(this, "/dev/ttyACM0", 9600);
  port.bufferUntil('\n');

  page=0;
  analyseEnCours=false;
  resultatPret=false;
  alerte=false;
  count=0;
  robot=false;
  
  etapeProcessus=1;
  categorieChoisie="";
  platChoisi="";

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
      etapeProcessus=1;
      declencherAnalyse(); // <--- DÉCOMMENTÉ ICI
      // chargerResultat();  <--- COMMENTÉ ICI
    }
  }

  if(page==0){
    if(analyseEnCours){
      afficherAnalyse();
    }
    else if(resultatPret){
      if(etapeProcessus==1){
        afficherCategories();
      }
      else if(etapeProcessus==2){
        afficherChoixPlats();
      }
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
    // Étape 1 : Choix du type de cuisine
    if(etapeProcessus==1){
      for(i=0; i<nbchoix; i++){
        if(choix[i].clicked()){
          categorieChoisie = categories.getString(i);
          etapeProcessus = 2;
          resultatPret = false;
          declencherAnalyse(); // Lance Gemini pour l'étape 2 avec la catégorie choisie
          break;
        }
      }
    }
    // Étape 2 : Choix du plat dans la liste
    else if(etapeProcessus==2){
      for(i=0; i<nbchoix; i++){
        if(choix[i].clicked()){
          platChoisi = platsDisponibles.getString(i);
          etapeProcessus = 3;
          resultatPret = false;
          declencherAnalyse(); // Lance Gemini pour l'étape 3 pour générer les étapes de cuisson
          break;
        }
      }
    }
  }
  
  if(retour.clicked()){
    if(section==1){
      resultatPret=false;
      etapeProcessus=1;
    }
    else if(section==2){
      page=0;
      resultatPret=true;
      etapeProcessus=1;
    }
    else if(section==3){
      page=0;
      resultatPret=true;
      etapeProcessus=2;
    }
    else{
      page=0;
      resultatPret=false;
      robot=false;
      etapeProcessus=1;
    }
  }
}
