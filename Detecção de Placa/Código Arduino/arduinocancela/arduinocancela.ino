#include <Servo.h> 

int redPin =  11;
int greenPin =  12;
int bluePin =  13;
int sensorPin = 10;

const int pinoServo = 9; //Pino do Servo
Servo s; //Objeto do tipo servo
int pos; //posicao do servo
byte anguloCancelaFechada = 54; //Valor do angulo para a cancela fechada
byte anguloCancelaAberta = 154; //Valor do angulo para a cancela aberta
 

void setup()
{
  Serial.begin(9600);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(sensorPin, INPUT);
  digitalWrite(redPin, LOW); //Led inicia desligado
  digitalWrite(greenPin, LOW); //Led inicia desligado
  digitalWrite(bluePin, LOW); //Led inicia desligado
  s.attach(pinoServo); //ASSOCIAÇÃO DO PINO DIGITAL AO OBJETO DO TIPO SERVO
  s.write(anguloCancelaFechada); //inicia o motor na posição da cancela fechada
  
}
 
void loop()
{
  leituraPlaca();
  abrirManualmente();
}
void leituraPlaca()
{
  int valor_recebido;
  valor_recebido = Serial.read(); 
 
  if(valor_recebido == 76 ) // Sinal recebido do script de detecção de placa, sinal de placa liberada
  { 
      digitalWrite(greenPin, HIGH);
      digitalWrite(redPin, LOW);   
      digitalWrite(bluePin, LOW);
      abrirCancela(); //Chama a função para abrir a cancela
      delay(6000); //Intervalo de 6 segundos
      fecharCancela(); //Chama a função para fechar a cancela
      digitalWrite(greenPin, LOW); //Desliga o led verde
      digitalWrite(redPin, LOW); //Desliga o led vermelho   
      digitalWrite(bluePin, LOW); //Desliga o led azul
      
  }
  
  if(valor_recebido == 68) // Sinal recebido do script de detecção de placa, sinal de que algo foi detectado mas não foi feita a leitura da placa corretamente
  {
      digitalWrite(bluePin, HIGH); //Liga o led Azul
      digitalWrite(redPin, LOW); //Desliga o led vermelho
      digitalWrite(greenPin, LOW); //Desliga o led verde
  }

 
  if(valor_recebido == 78) // Sinal recebido do script de detecção de placa, sinal de que a placa foi detectada mas não está cadastrada no sistema
  {
     digitalWrite(redPin, HIGH); // Liga o led vermelho
     digitalWrite(bluePin, LOW); //Desliga o led azul
     digitalWrite(greenPin, LOW); //Desliga o led verde    
  }  
}

//Função para abrir a cancela
void abrirCancela(){
  for(pos = anguloCancelaFechada; pos < anguloCancelaAberta; pos++){ // PARA "pos" IGUAL A "anguloCancelaFechada",
    //ENQUANTO "pos" MENOR QUE "anguloCancelaAberta", INCREMENTA "pos"
    s.write(pos); //Escreve o valor da posição que o servo vai girar
    delay(15); //Intervalo de 15 milisegundos       
  }
}
 
//Função para fechar a cancela
void fecharCancela(){ //
  for(pos = anguloCancelaAberta; pos >= anguloCancelaFechada; pos--){ //PARA "pos" IGUAL A "anguloCancelaAberta",
    //ENQUANTO "pos" MAIOR OU IGUAL "anguloCancelaFechada", DECREMENTA "pos"
    s.write(pos); //Escreve o valor da posição que o servo vai girar
    delay(15); //Intervalo de 15 milisegundos
  }
}

//Função para abrir a cancela manualmento
void abrirManualmente(){
  if (digitalRead(sensorPin) == HIGH)
  {    
    Serial.println("Cancela aberta");
    digitalWrite(greenPin, HIGH);
    digitalWrite(greenPin, LOW);
    digitalWrite(redPin, LOW);   
    digitalWrite(bluePin, LOW);
    abrirCancela();
    digitalWrite(greenPin, LOW);
    digitalWrite(redPin, LOW);   
    digitalWrite(bluePin, LOW);
    delay(6000);
    fecharCancela();
  }
}
 
