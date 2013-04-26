
_main:

;RTCA Pic Reset Trigger.c,3 :: 		void main() {
;RTCA Pic Reset Trigger.c,5 :: 		IRCF0_bit = 1;
	BSF        IRCF0_bit+0, BitPos(IRCF0_bit+0)
;RTCA Pic Reset Trigger.c,6 :: 		IRCF1_bit = 0;
	BCF        IRCF1_bit+0, BitPos(IRCF1_bit+0)
;RTCA Pic Reset Trigger.c,7 :: 		IRCF2_bit = 0;
	BCF        IRCF2_bit+0, BitPos(IRCF2_bit+0)
;RTCA Pic Reset Trigger.c,8 :: 		IRCF3_bit = 0;
	BCF        IRCF3_bit+0, BitPos(IRCF3_bit+0)
;RTCA Pic Reset Trigger.c,11 :: 		ANSELA = 0x00;
	CLRF       ANSELA+0
;RTCA Pic Reset Trigger.c,12 :: 		TRISA = 0b00000100;
	MOVLW      4
	MOVWF      TRISA+0
;RTCA Pic Reset Trigger.c,14 :: 		PORTA.B4 = 0;
	BCF        PORTA+0, 4
;RTCA Pic Reset Trigger.c,15 :: 		PORTA.B5 = 1;
	BSF        PORTA+0, 5
;RTCA Pic Reset Trigger.c,17 :: 		INTCON = 0b10010000;
	MOVLW      144
	MOVWF      INTCON+0
;RTCA Pic Reset Trigger.c,18 :: 		OPTION_REG.INTEDG = 0; // trigger INT on rising edge
	BCF        OPTION_REG+0, 6
;RTCA Pic Reset Trigger.c,19 :: 		}
L_end_main:
	GOTO       $+0
; end of _main

_interrupt:
	CLRF       PCLATH+0
	CLRF       STATUS+0

;RTCA Pic Reset Trigger.c,21 :: 		void interrupt() {
;RTCA Pic Reset Trigger.c,22 :: 		if(INTCON.INTF == 1 ){
	BTFSS      INTCON+0, 1
	GOTO       L_interrupt0
;RTCA Pic Reset Trigger.c,24 :: 		PORTA.B4 = 1;
	BSF        PORTA+0, 4
;RTCA Pic Reset Trigger.c,25 :: 		PORTA.B5 = 0;
	BCF        PORTA+0, 5
;RTCA Pic Reset Trigger.c,26 :: 		Delay_ms(500);
	MOVLW      6
	MOVWF      R12
	MOVLW      48
	MOVWF      R13
L_interrupt1:
	DECFSZ     R13, 1
	GOTO       L_interrupt1
	DECFSZ     R12, 1
	GOTO       L_interrupt1
	NOP
;RTCA Pic Reset Trigger.c,27 :: 		PORTA.B4 = 0;
	BCF        PORTA+0, 4
;RTCA Pic Reset Trigger.c,28 :: 		PORTA.B5 = 1;
	BSF        PORTA+0, 5
;RTCA Pic Reset Trigger.c,30 :: 		INTCON.INTF = 0;       // Clear Interrupt Flag
	BCF        INTCON+0, 1
;RTCA Pic Reset Trigger.c,31 :: 		}
L_interrupt0:
;RTCA Pic Reset Trigger.c,32 :: 		}
L_end_interrupt:
L__interrupt4:
	RETFIE     %s
; end of _interrupt
