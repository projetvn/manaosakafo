public class Bouton{
  private float x,y;
  private float w,h;
  private String text;
  private int R,G,B,Rh,Gh,Bh;
  private int textColor;
  private float xtext;
  
  public Bouton(){}
  
  public void setTextxPosition(float x){
    xtext=x;
  }
  
  public void setPosition(float x,float y,float w,float h){
    this.x=x;
    this.y=y;
    this.w=w;
    this.h=h;
  }
  
  public void setText(String text){
    this.text=text;
  }
  
  public void setColorh(int R,int G,int B){
    Rh=R;
    Gh=G;
    Bh=B;
  }
  
  public void setColor(int R){
    this.R=R;
    this.G=R;
    this.B=R;
  }
  
  public void setColor(int R,int G,int B){
    this.R=R;
    this.G=G;
    this.B=B;
  }
  
  private boolean hover(){ //souris en dessus
    if(mouseX>x && mouseX<x+w && mouseY>y && mouseY<y+h){
      return true;
    }
    return false;
  }
  
  public void display(){
    if(hover()){
     fill(Rh,Gh,Bh);
    }
    else{
      fill(R,G,B);
    }
    rect(x,y,w,h,5);
    if(text!=null){
      fill(textColor);
      textSize(17);
      text(text,xtext,y+h/2+4);
    }
  }
  
  public void setTextColor(int couleur){
    textColor=couleur;
  }
  
  public boolean clicked(){
    if(mousePressed && hover()){
      return true;
    }
    return false;
  }
}
