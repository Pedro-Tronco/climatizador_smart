# from RPLCD.gpio import CharLCD
# import RPi.GPIO as GPIO
# import time

# def main() -> None:
#     lcd = CharLCD(
#         numbering_mode=GPIO.BCM,
#         cols=16,
#         rows=2,
#         pin_rs=26,
#         pin_e=19,
#         pins_data=[13, 6, 5, 11]
#     )

#     try:
#         # Limpa a tela antes de escrever
#         lcd.clear()
        
#         # Escreve na primeira linha
#         lcd.write_string('Raspberry Pi')
        
#         # Pula para a segunda linha (linha 1, coluna 0)
#         lcd.cursor_pos = (1, 0)
#         lcd.write_string('Teste LCD 1602A!')
        
#         print("Texto enviado! Gire o potenciometro se nao aparecer nada.")
        
#         # Mantem o texto na tela por 15 segundos
#         time.sleep(15)

#     finally:
#         # Limpa a tela e libera os pinos ao finalizar
#         lcd.clear()
#         lcd.close(clear=True)
#         print("Teste finalizado.")
        
from .arduino.controller import ArduinoController
from .arduino.schemas import LedColors
import time

class DetectionStatus:

    def __init__(self, arduino: ArduinoController):
        self.active = False
        self._arduino = arduino

    def toggle(self, blocked: bool):
        self.active = blocked
        
        if self.active:
            self._arduino.set_led_color(LedColors.GREEN)
        
        else:
            self._arduino.set_led_color(LedColors.RED)
            

def main() -> None:
    arduino = ArduinoController(port='COM8')
    status = DetectionStatus(arduino=arduino)
    
    try:

        # Start monitoring sensors
        arduino.start(
            toggle_callback=status.toggle
        )

        # Set initial LED color
        arduino.set_led_color(LedColors.BLUE)

        # Main application loop
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping application...")

    finally:
        arduino.set_led_color(LedColors.OFF)
        arduino.close()
