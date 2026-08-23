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

    pb=new ProcessBuilder("python3","/home/nyonitiana/manaosakafo/processing/data/capturer_et_analyser.py");
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

  f=new File(sketchPath("/home/nyonitiana/manaosakafo/processing/data/recettes_robot.json"));

  if(!f.exists()){
    println("Fichier resultat introuvable : " + f.getAbsolutePath());
    return;
  }

  json=loadJSONObject("/home/nyonitiana/manaosakafo/processing/data/recettes_robot.json");

  if(json.getBoolean("contient_non_comestible")){
    resultatPret=false;
    alerte=true;
    return;
  }

  alerte=false;
  plats=json.getJSONArray("plats");
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
