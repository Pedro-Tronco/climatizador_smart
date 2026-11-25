from ..raspi.controller import RaspiController

from ..telemetry.schemas import SensorState

from .schemas import (
    Temperatures,
)

class AirConditionerService:
    def __init__(self, raspi_controller: RaspiController) -> None:
        self._raspi_controller = raspi_controller
        
        self._normal_temperature_celcius: int = 22
        self._eco_temperature_celcius: int = 25
        
        self._state = SensorState.OK
        
        
    def _update_state(self):
        match self._state:
            case SensorState.OK:
                self._ac_is_on = True
                self._current_temperature = self._normal_temperature_celcius
            
            case SensorState.WARNING:
                self._ac_is_on = True
                self._current_temperature = self._eco_temperature_celcius
                
            case SensorState.DISABLED:
                self._ac_is_on = False
                
            case _:
                pass
        self._raspi_controller.write_lcd(
            f'Status: {"ON " if self._ac_is_on else "OFF"}'
            '     '
            f'Temp: {self._current_temperature} C'
        )
    
        
    def adjust_temperatures(self, temperatures: Temperatures) -> Temperatures:    
        self._normal_temperature_celcius = temperatures.normal_celcius
        self._eco_temperature_celcius = temperatures.eco_celcius
        
        self._update_state()
        return self.get_current_temperatures()
        
        
    def get_current_temperatures(self) -> Temperatures:
        return Temperatures(
            normal_celcius=self._normal_temperature_celcius,
            eco_celcius=self._eco_temperature_celcius,
        )
        
        
    def change_status(self, state: SensorState) -> None:
        self._state = state
            
        self._update_state()