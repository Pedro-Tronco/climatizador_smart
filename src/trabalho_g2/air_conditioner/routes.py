from fastapi import FastAPI

from .services import AirConditionerService

from .schemas import Temperatures


class AirConditionerController():
    def __init__(self, ac_service: AirConditionerService) -> None:
        self._ac_service = ac_service
        
        
    def register_endpoints(self, app: FastAPI) -> None:
        
        @app.get('/temps', response_model=Temperatures)
        def get_temperatures_celcius():
            return self._ac_service.get_current_temperatures()
        
        @app.post('/temps', response_model=Temperatures)
        def set_temperatures_celcius(temps: Temperatures):
            return self._ac_service.adjust_temperatures(temps)