void afficherEtatInitial(){
  fill(TEXTE);
  textAlign(CENTER);

  textSize(30);
  text("CUISTOT AUTOMATIQUE", width/2, 50);

  fill(CARTE);
  stroke(BORDURE);
  strokeWeight(1);
  rect(50,100,width-100,500,18);

  if(alerte){
    String messageAlerte;
    messageAlerte=json.getString("message_alerte");

    fill(TEXTE);
    textSize(25);
    text(messageAlerte,width/2,height/2);
  }

  else{
    fill(TEXTE);
    textSize(25);
    text("Le recipient n'est pas encore charge",width/2,330);

    fill(TEXTE2);
    textSize(17);
    text("Chargez le recipient pour commencer",width/2,370);
  }
}

void afficherAnalyse() {
  fill(TEXTE);
  textAlign(CENTER);
  textSize(30);
  text("CUISTOT AUTOMATIQUE",width/2,50);

  fill(CARTE);
  stroke(BORDURE);
  rect(50,100,width-100,500,18);

  fill(TEXTE);
  textSize(25);
  text("Analyse en cours, patiente...",width/2,315);
}

void afficherPlats(){
  section=1;
  
  textAlign(CENTER);
  retour.display();
  
  nbchoix = plats.size();
  choix=new Bouton[nbchoix];

  fill(TEXTE);
  textAlign(CENTER);
  textSize(30);
  text("CUISTOT AUTOMATIQUE",width/2,50);

  fill(CARTE);
  stroke(BORDURE);
  rect(50,100,width-100,500,18);

  fill(TEXTE);
  textSize(25);
  text("Choisissez votre plat",width/2,145);

  fill(TEXTE2);
  textSize(16);
  text("Les recettes disponibles sont basees sur les ingredients detectes",width/2,180);

  float hauteur;
  float espace;
  float total;
  float debutY;

  espace=12;
  hauteur=65;
  total=nbchoix * hauteur + (nbchoix - 1) * espace;
  debutY=220;

  for(i=0;i<nbchoix;i++){
    JSONObject plat;
    plat=plats.getJSONObject(i);
    nom=plat.getString("nom");

    float yy;
    yy=debutY + i * (hauteur + espace);

    fill(255);
    stroke(BORDURE);
    rect(130,yy,width-260,hauteur,10);

    fill(BRUN_CLAIR);
    textAlign(CENTER);
    textSize(20);

    text(nf(i+1, 2),180,yy + hauteur/2);

    stroke(BORDURE);
    line(230,yy,230,yy + hauteur);

    fill(TEXTE);
    textAlign(LEFT, CENTER);
    textSize(18);
    text(nom,260,yy + hauteur/2);

    fill(BRUN);
    textAlign(CENTER);
    textSize(27);
    text("›",width - 170,yy + hauteur/2);

    choix[i] = new Bouton();
    choix[i].setPosition(130,yy,width - 260,hauteur);
    choix[i].setText("");
    choix[i].setColor(255);
  }
}

void afficherPreparationManuelle(int index) {
  section=2;
  
  textAlign(CENTER);
  retour.display();
  
  textAlign(CENTER);
  retour.display();
  JSONObject plat;
  String etape;
  float yy;

  plat=plats.getJSONObject(index);
  preparation_manuelle=plat.getJSONArray("preparation_manuelle");

  fill(TEXTE);
  textAlign(CENTER);
  textSize(30);
  text("CUISTOT AUTOMATIQUE",width/2,50);

  fill(CARTE);
  stroke(BORDURE);
  rect(50,100,width-100,500,18);

  fill(TEXTE);
  textSize(23);
  text("Preparation des ingredients",width/2,145);

  fill(TEXTE2);
  textSize(16);
  text("Preparez les ingredients avant de les mettre dans la casserole",width/2,180);

  float hauteur;
  float espace;
  float debutY;

  hauteur=55;
  espace=10;
  debutY=220;

  for(j=0;j<preparation_manuelle.size();j++){
    etape=preparation_manuelle.getString(j);
    yy=debutY + j * (hauteur + espace);

    fill(255);
    stroke(BORDURE);
    rect(130,yy,width-260,hauteur,8);

    fill(BRUN_CLAIR);
    textAlign(CENTER);
    textSize(18);
    text(j+1,170,yy + hauteur/2);

    stroke(BORDURE);
    line(210,yy,210,yy + hauteur);

    fill(TEXTE);
    textAlign(LEFT, CENTER);
    textSize(16);
    text(etape,240,yy + hauteur/2);
  }
  
  yy=debutY + j * (hauteur + espace);

  fill(INFO);
  stroke(BORDURE);
  rect(80,yy,width-160,55,10);

  fill(TEXTE);
  textAlign(CENTER);
  textSize(15);
  text("Suivez les etapes avant de lancer la preparation du robot.",width/2,yy + 55/2);
}

void afficherPreparationRobot(){
  fill(TEXTE);
  textAlign(CENTER);
  textSize(30);
  text("CUISTOT AUTOMATIQUE",width/2,50);

  fill(CARTE);
  stroke(BORDURE);
  rect(50,100,width-100,500,18);

  fill(INFO);
  stroke(BORDURE);
  rect(80,125,width-160,115,12);

  fill(TEXTE);
  textAlign(LEFT, CENTER);
  textSize(21);
  text("Le robot est en phase de preparation",115,160);

  textSize(15);
  text("Etape " + min(count, preparation_robot.size()) +" / " +preparation_robot.size(),115,195);

  fill(BARRE_FOND);
  noStroke();
  rect(115,215,width-230,9,5);

  if(preparation_robot.size()>0){
    float progression;

    progression=(float)count / preparation_robot.size();
    progression=constrain(progression, 0, 1);

    fill(BRUN);
    rect(115,215,(width - 230) * progression,9,5);
  }

  if(count-1<preparation_robot.size() && count-1!=0){
    JSONObject etape;

    etape=preparation_robot.getJSONObject(count-1);

    fill(255);
    stroke(BORDURE);
    rect(80,270,width - 160,270,12);

    float yy;
    yy=315;

    if(etape.getString("activer").equals("1")){
      afficherParametre("Chauffer","ON" + "",yy);
      yy += 43;
    }

    if(etape.getInt("eau_ml")>0){
      afficherParametre("Eau",etape.getInt("eau_ml") + " ml",yy);
      yy += 43;
    }

    if(etape.getInt("sel_g")>0){
      afficherParametre("Sel",etape.getInt("sel_g") + " g",yy);
      yy += 43;
    }

    if(etape.getInt("huile_ml")>0){
      afficherParametre("Huile",etape.getInt("huile_ml") + " ml",yy);
      yy += 43;
    }

    if(etape.getBoolean("melanger")){
      afficherParametre("Melanger","ON",yy);
      yy += 43;
    }

    if(etape.getInt("duree_secondes")>0){
      afficherParametre("Duree",etape.getInt("duree_secondes") + " sec",yy);
    }
  }

  fill(INFO);
  stroke(BORDURE);
  rect(80,560,width - 160,55,10);

  fill(TEXTE);
  textAlign(CENTER);
  textSize(15);

  if(count-1<preparation_robot.size() &&  count-1!=0){
    text("Votre repas est en cours de preparation.",width/2,587);
  }

  else{
    text("Votre repas est pret.",width/2,587);
    section=3;
    textAlign(CENTER);
    retour.display();
  }
}

void afficherParametre(String nomParametre,String valeur,float yy){
  fill(TEXTE);
  textAlign(LEFT, CENTER);
  textSize(16);
  text(nomParametre,120,yy);

  fill(TEXTE2);
  text(valeur,500,yy);

  stroke(BORDURE);
  line(120,yy + 20,width - 120,yy + 20);
}
