#define DHT11_Pin 2

int Humidity = 0; 
int Temp = 0;
int TempComma = 0;
bool DHTError = false;

byte char2hex(char c){
  switch(c){
    case '0':return 0;
    case '1':return 1;
    case '2':return 2;
    case '3':return 3;
    case '4':return 4;
    case '5':return 5;
    case '6':return 6;
    case '7':return 7;
    case '8':return 8;
    case '9':return 9;
    case 'A':return 10;
    case 'B':return 11;
    case 'C':return 12;
    case 'D':return 13;
    case 'E':return 14;
    case 'F':return 15;
  }
  return 0;
}

void DelayTimer(long int DelayValue){
  long int DelayTime = micros();
  do {
    
  }while (micros()-DelayTime < DelayValue);
}
void DHT11(){

long int DataTime = 0;

byte Result[45];
byte DataArray = 0;
byte DataCounter = 0;
byte DHTData[4];

bool BlockDHT=false;
 
// Trigger Sensor (described in the Datasheet)

 pinMode(DHT11_Pin,OUTPUT); 
 digitalWrite(DHT11_Pin,HIGH);
 DelayTimer(250000); //Wait 250millisec
 digitalWrite(DHT11_Pin,LOW);
 DelayTimer(30000);   //Wait 30millisec
 digitalWrite(DHT11_Pin,HIGH);
 DelayTimer(50); //Wait 50microsec
 pinMode(DHT11_Pin,INPUT); 


// read the Bits and put them into a Result array (It will count 42 bits. The first two one are useless due my code)

do {
  if (digitalRead(DHT11_Pin) == 0 && BlockDHT == false) {BlockDHT = true;Result[DataArray]=(micros()-DataTime);DataArray++;DataTime=micros();} //If DHT pin is low, go to next Dataset
  if (digitalRead(DHT11_Pin) == 1) {BlockDHT = false;} // As long as DHT pin is Hight add time in Microseconds to Result
  

}while((micros()-DataTime) < 150); // if DTH Sensor high for more than 150 usec, leave loop

// Asign 1 or 0 to Result variable. If more than 80uS Data as "1"
// Starting at Data set 02. First two Datasets are ignored!

for (int  i=2; i< DataArray; i++) {
  if (Result[i] <= 90) Result[i]=0; else Result[i]=1;
  //Serial.print(Result[i]);Serial.print(" ");
                                  }
 //Serial.println();

for (int  j=0; j< 5; j++){     // redo it for the 5 Bytes (40 Databits /8 = 5)
for (int  i=0; i< 8; i++) {bitWrite(DHTData[j], 7-i, Result[i+2+(j*8)]);}  // Create 5 Databytes from the 40 Databits (Ignoring the 2 first Databits)

}
// check checksum                            }

if (DHTData[4] == (DHTData[0]+DHTData[1]+DHTData[2]+DHTData[3])){Humidity = DHTData[0];Temp = DHTData[2];TempComma = DHTData[3];DHTError=false;} else DHTError=true; //If Checksum is worng, Temp=99 (Dataset 0-3 in addition = Dataset 4 = Checksum OK)

}
void crPrintHEX(unsigned long DATA, unsigned char numChars) {
    unsigned long mask  = 0x0000000F;
    mask = mask << 4*(numChars-1);
    
    for (unsigned int i=numChars; i>0; --i) {
         Serial.print(((DATA & mask) >> (i-1)*4),HEX);
         mask = mask >> 4;
    }    
}


void setup() { 
  Serial.begin(500000);
}
static uint8_t hue = 0;
String txt = "";
byte line = 0;

int pulses = 0;
int lastPulses = 0;
long millisTimer0 = 0;

void loop() { 
  while(Serial.available()){
    char c = Serial.read();
    if(c == 'S'){
       DHT11();      
       crPrintHEX(Humidity,2);
       crPrintHEX(Temp,2);
       crPrintHEX(TempComma,2);
       Serial.println("");
    }else if(c == 'P'){
      Serial.println(lastPulses,HEX);
    }
  }
  bool pulse = analogRead(A0)>750;
  pulses+=pulse;
  if(millis()-millisTimer0>=100){
    millisTimer0 = millis();
    lastPulses = pulses;
    pulses = 0;
  }
}
