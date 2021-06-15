#include <FastLED.h>

#define NUM_LEDS 300
#define DATA_PIN 7

CRGB leds[NUM_LEDS];

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

void setup() { 
  Serial.begin(500000);
  LEDS.addLeds<WS2812B,DATA_PIN,RGB>(leds,NUM_LEDS);
  LEDS.setBrightness(84);
  for(int i = 0;i<NUM_LEDS;i++){
    leds[i] = CHSV(0x00,0,0);  
  }
  FastLED.show();
}
static uint8_t hue = 0;
String txt = "";
byte line = 0;
void loop() { 
  while(Serial.available()){
    char c = Serial.read();
    if(c == '\r'){
      Serial.println(txt.length()/6);
      for(int i = 0;i<txt.length()/6;i++){
        byte msb = char2hex(txt[6*i]);
        byte lsb = char2hex(txt[6*i+1]);
        byte h = msb << 4 | lsb;
       
        msb = char2hex(txt[6*i+2]);
        lsb = char2hex(txt[6*i+3]);
        byte s = msb << 4 | lsb;
       
        msb = char2hex(txt[6*i+4]);
        lsb = char2hex(txt[6*i+5]);
        byte b = msb << 4 | lsb;
  
        leds[line*100+i] = CHSV((0x60+h)%255,s,b);
      }
      line+=1;
      txt = "";
    }else if(c == '\n'){
      FastLED.show();
      line = 0;
      txt = "";
    }else if(c == 'S' || c == 'P'){
      //GO AWAY S
    }else{
      txt+=c;
    }
  }
  
}
