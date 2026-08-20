import processing.serial.*;
import java.io.File;
import java.lang.*;

Serial port;
int page,i,j;
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
boolean alerte;
String etapesRobot;
int count;

void setup() {
  size(1800,1000);
  port=new Serial(this, "/dev/ttyACM0", 9600);
  page=0;
  
  analyseEnCours=false;
  resultatPret=false;
  alerte=false;
  count=0;
}

void draw(){
  background(245);
  
  ligne=port.readStringUntil('\n');
    
  if(ligne!=null)
  {
    ligne=trim(ligne);
    
    if(ligne.equals("2") && !analyseEnCours)
    {
      declencherAnalyse();
    }
  }
      
  if(page!=0)
  {
    for(i=1;i<=nbchoix;i++)
    {
      if(page==i)
      {
        etapesRobot="";
        if(ligne.equals("3")){
          fill(0);
          textSize(17);
          textAlign(CENTER);
          text("Le robot est en phase de preparation", 900, 60);
          preparation_robot=plats.getJSONObject(i-1).getJSONArray("etapes_robot");
          if(count < preparation_robot.size()){
            etapesRobot=etapesRobot+"activer="+Integer.toString(preparation_robot.getJSONObject(count).getInt("activer"))+",";     
             
            if (preparation_robot.getJSONObject(count).getInt("eau_ml") > 0){
              etapesRobot=etapesRobot+"eau="+Integer.toString(preparation_robot.getJSONObject(count).getInt("eau_ml"))+",";     
            }
                  
            if (preparation_robot.getJSONObject(count).getInt("sel_g") > 0){
              etapesRobot=etapesRobot+"sel="+Integer.toString(preparation_robot.getJSONObject(count).getInt("sel_g"))+",";     
            }
            
            if (preparation_robot.getJSONObject(count).getInt("huile_ml") > 0){
              etapesRobot=etapesRobot+"huile="+Integer.toString(preparation_robot.getJSONObject(count).getInt("huile_ml"))+",";     
            }
            
            if (preparation_robot.getJSONObject(count).getBoolean("melanger")){
              etapesRobot=etapesRobot+"melanger"+",";     
            }
            
            if(preparation_robot.getJSONObject(count).getInt("duree_secondes") > 0){
              etapesRobot=etapesRobot+"duree="+Integer.toString(preparation_robot.getJSONObject(count).getInt("duree_secondes"))+",";     
            }
            
            etapesRobot=etapesRobot+"\n";
            port.write(etapesRobot);
            count++;
          }
          else{
            port.write("stop\n");
            fill(0);
            textSize(17);
            textAlign(CENTER);
            text("Votre repas est pret", 900, 60);
            count=0;
            page=0;
          }
        }
        
        else{
          etapesManuelle="Veuillez preparer les ingredients avant de les mettre dans la casserole en suivant ces etapes:\n" ;
          preparation_manuelle=plats.getJSONObject(i-1).getJSONArray("preparation_manuelle");
          for(j=0;j<preparation_manuelle.size();j++)
          {
            etapesManuelle=etapesManuelle+"- "+preparation_manuelle.getString(j)+"\n";
          }
          fill(0);
          textSize(25);
          textAlign(CENTER);
          text(etapesManuelle, 900, 500);
        }
      }
    }
  }
  
  if(page==0)
  {
    if(analyseEnCours)
    {
      fill(0);
      textSize(17);
      textAlign(CENTER);
      text("Analyse en cours, patiente...", 900, 60);
    }
  
    else if(resultatPret)
    {
      afficherPlats();
    }  
    
    else
    {
      if(alerte){
        String messageAlerte;
        
        messageAlerte=json.getString("message_alerte");
        fill(0);
        textSize(25);
        textAlign(CENTER);
        text(messageAlerte, 900, 500); 
      }
      
      else{
        fill(0);
        textSize(17);
        textAlign(CENTER);
        text("Le recipient n'est pas encore charge", 900, 60);
      }
    }
  }
}

void mousePressed(){
  for(i=0;i<nbchoix;i++){
    if(choix[i].clicked()){
      page=i+1;
    }
  }
}

void afficherPlats(){
  JSONObject plat;
  nbchoix=plats.size();
  choix=new Bouton[nbchoix];
  y=500-110*3/2;
  
  for(i=0;i<nbchoix;i++)
  {
    choix[i]=new Bouton();
    plat=plats.getJSONObject(i);
    nom=plat.getString("nom");
    choix[i].setPosition(650,y+i*110,500,100);
    choix[i].setText(nom);
    choix[i].setColor(255);
    choix[i].setTextxPosition(900);
    textAlign(CENTER);
    choix[i].setColorh(200,200,200);
    choix[i].setTextColor(0);
    choix[i].display();
  }
}

void declencherAnalyse(){
  analyseEnCours=true;
  resultatPret=false;
  
  thread("lancerScriptPython");
}

void lancerScriptPython() {
  try {
    ProcessBuilder pb;
    String ligne;
    int codeRetour;
    pb=new ProcessBuilder("python3", "data/capturer_et_analyser.py");
    pb.redirectErrorStream(true); //fusionne stdout/stderr, utile pour debug
    Process process;
    process=pb.start();

    // Optionnel : afficher la sortie du script dans la console Processing
    java.io.BufferedReader reader;
    reader=new java.io.BufferedReader(
      new java.io.InputStreamReader(process.getInputStream())
    );
    
    while((ligne=reader.readLine()) != null)
    {
      println("[python] " + ligne);
    }

    codeRetour=process.waitFor(); //bloque CE thread, pas draw()

    if(codeRetour==0) 
    {
      chargerResultat();
    } 
    else 
    {
      println("Le script Python a echoue, code retour : " + codeRetour);
    }
  }
  catch (Exception e) {
    println("Erreur lors du lancement du script : " + e.getMessage());
  }
  finally {
    analyseEnCours=false;
  }
}

void chargerResultat() {
  File f;
  f=new File(sketchPath("data/recettes_robot.json"));
  if(!f.exists()){
    println("Fichier resultat introuvable : " + f.getAbsolutePath());
    return;
  }

  json = loadJSONObject("data/recettes_robot.json");

  if(json.getBoolean("contient_non_comestible"))
  {
    resultatPret = false;
    alerte = true;
    return;
  }

  alerte = false;
  plats = json.getJSONArray("plats");
  resultatPret = true;
}
