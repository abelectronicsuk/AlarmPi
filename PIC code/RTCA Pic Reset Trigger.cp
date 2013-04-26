#line 1 "//And/e/AB Electronics/RTC Alarm Pi/pic code/RTCA Pic Reset Trigger.c"


void main() {

 IRCF0_bit = 1;
 IRCF1_bit = 0;
 IRCF2_bit = 0;
 IRCF3_bit = 0;


 ANSELA = 0x00;
 TRISA = 0b00000100;

 PORTA.B4 = 0;
 PORTA.B5 = 1;

 INTCON = 0b10010000;
 OPTION_REG.INTEDG = 0;
}

void interrupt() {
 if(INTCON.INTF == 1 ){

 PORTA.B4 = 1;
 PORTA.B5 = 0;
 Delay_ms(500);
 PORTA.B4 = 0;
 PORTA.B5 = 1;

 INTCON.INTF = 0;
 }
}
