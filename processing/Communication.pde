void declencherAnalyse(){
  analyseEnCours=true;
  resultatPret=false;

  thread("lancerScriptPython");
}

void lancerScriptPython() {
  try {
    ProcessBuilder pb;
    String lignePython;
    int codeRetour;

    if(etapeProcessus == 1){
      pb=new ProcessBuilder("/home/vatosoa/ProjetL2/gemini-env/bin/python3", "/home/vatosoa/sketchbook/test/data/test_gemini_json.py", "1");
    }
    else if(etapeProcessus == 2){
      pb=new ProcessBuilder("/home/vatosoa/ProjetL2/gemini-env/bin/python3", "/home/vatosoa/sketchbook/test/data/test_gemini_json.py", "2", categorieChoisie);
    }
    else {
      pb=new ProcessBuilder("/home/vatosoa/ProjetL2/gemini-env/bin/python3", "/home/vatosoa/sketchbook/test/data/test_gemini_json.py", "3", platChoisi);
    }

    pb.redirectErrorStream(true);

    Process process;
    process=pb.start();

    java.io.BufferedReader reader;
    reader=new java.io.BufferedReader(
      new java.io.InputStreamReader(process.getInputStream())
    );

    while((lignePython=reader.readLine()) != null){
      println("[python] " + lignePython);
    }

    codeRetour=process.waitFor();

    if(codeRetour==0){
      chargerResultat();
    }
    else{
      println("Le script Python a echoue, code retour : " + codeRetour);
    }
  }

  catch(Exception e){
    println("Erreur lors du lancement du script : " + e.getMessage());
  }

  finally{
    analyseEnCours=false;
  }
}

void chargerResultat(){
  File f;

  f=new File(sketchPath("/home/vatosoa/sketchbook/test/data/recettes_robot.json"));

  if(!f.exists()){
    println("Fichier resultat introuvable : " + f.getAbsolutePath());
    return;
  }

  json=loadJSONObject("/home/vatosoa/sketchbook/test/data/recettes_robot.json");

  if(json.hasKey("contient_non_comestible") && json.getBoolean("contient_non_comestible")){
    resultatPret=false;
    alerte=true;
    return;
  }

  alerte=false;

  if(etapeProcessus == 1){
    categories = json.getJSONArray("categories");
  } 
  else if(etapeProcessus == 2){
    platsDisponibles = json.getJSONArray("plats_disponibles");
  } 
  else if(etapeProcessus == 3){
    plats = json.getJSONArray("plats");
    page = 1; // Passe directement à l'affichage du plat sélectionné
  }

  resultatPret=true;
}

void envoyerEtapeRobot(){
  JSONObject plat;
  
  plat=plats.getJSONObject(indexPlat);
  preparation_robot=plat.getJSONArray("etapes_robot");
  
  if(preparation_robot==null){
    return;
  }

  if(count<preparation_robot.size()){
    JSONObject etape;
    etape=preparation_robot.getJSONObject(count);

    etapesRobot="";
    etapesRobot=etapesRobot+"activer="+etape.getString("activer")+",";

    if(etape.getInt("eau_ml")>0){
      etapesRobot=etapesRobot+"eau="+Integer.toString(etape.getInt("eau_ml"))+",";
    }

    if(etape.getInt("sel_g")>0){
      etapesRobot=etapesRobot+"sel="+Integer.toString(etape.getInt("sel_g"))+",";
    }

    if(etape.getInt("huile_ml")>0){
      etapesRobot=etapesRobot+"huile="+Integer.toString(etape.getInt("huile_ml"))+",";
    }

    if(etape.getBoolean("melanger")){
      etapesRobot=etapesRobot+"melanger="+Integer.toString(etape.getInt("duree_secondes"))+",";
    }

    if(etape.getInt("duree_secondes")>0){
      etapesRobot=etapesRobot+"duree="+Integer.toString(etape.getInt("duree_secondes"))+",";
    }

    etapesRobot=etapesRobot+"\n";
    port.write(etapesRobot);
    println("Processing -> Arduino : " + etapesRobot);
    count++;
  }

  else{
    port.write("stop\n");
    println("Processing -> Arduino : stop");
    count=0;
    resultatPret=false;
  }
}
