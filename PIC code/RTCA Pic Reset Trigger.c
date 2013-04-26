

void main() {
    // set oscillator to 32KHz
    IRCF0_bit = 1;
    IRCF1_bit = 0;
    IRCF2_bit = 0;
    IRCF3_bit = 0;

     // disable analogue inputs and set RA2 to input, all other pins are outputs
     ANSELA = 0x00;
     TRISA = 0b00000100;
     
     PORTA.B4 = 0;
     PORTA.B5 = 1;
     // enable interups
     INTCON = 0b10010000;
     OPTION_REG.INTEDG = 0; // trigger INT on rising edge
}

void interrupt() {
     if(INTCON.INTF == 1 ){
     //if (PORTA.B2 == 0){
        PORTA.B4 = 1;
        PORTA.B5 = 0;
        Delay_ms(500);
        PORTA.B4 = 0;
        PORTA.B5 = 1;
      //}
      INTCON.INTF = 0;       // Clear Interrupt Flag
  }
}