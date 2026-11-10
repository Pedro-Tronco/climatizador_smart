from RPLCD.gpio import CharLCD
import RPi.GPIO as GPIO
import time

def main() -> None:
    lcd = CharLCD(
        numbering_mode=GPIO.BCM,
        cols=16,
        rows=2,
        pin_rs=26,
        pin_e=19,
        pins_data=[13, 6, 5, 11]
    )

    try:
        # Limpa a tela antes de escrever
        lcd.clear()
        
        # Escreve na primeira linha
        lcd.write_string('Raspberry Pi')
        
        # Pula para a segunda linha (linha 1, coluna 0)
        lcd.cursor_pos = (1, 0)
        lcd.write_string('Teste LCD 1602A!')
        
        print("Texto enviado! Gire o potenciometro se nao aparecer nada.")
        
        # Mantem o texto na tela por 15 segundos
        time.sleep(15)

    finally:
        # Limpa a tela e libera os pinos ao finalizar
        lcd.clear()
        lcd.close(clear=True)
        print("Teste finalizado.")
        
