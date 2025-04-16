# -*- coding: utf-8 -*-
__title__ = "Multimetro"
__library__ = " "
__status__ = "Desarrollo"
__description___ = "Libreria para manejo de instrumentos"
__author__ = "Alexis Sandoval | Lautaro Martinez"
__copyright__ = "Copyright 2024, INVAP S.E."
__version__ = "2.0.0"


TITULO = (
    "    ##    "
    + __title__
    + " - "
    + __version__
    + "    ##    "
)

###########################################
#             IMPORTS PROPIOS             #
###########################################
import time
from typing import Optional
from instrumentos.manejo import Instrument
import general.mensajes_usuario as MU
# from manejo import Instrument
# import mensajes_usuario as MU

# MUL_FLUKE8840A = "GPIB0::1::INSTR"
# MUL_U1251A = "ASRL13::INSTR"
# Variable para comparacion de OL de resistencia
RES_OL = 9.9e+38
class Multimetro(Instrument):
    def __new__(cls, log, address):
        """Se involucra en la creación de una instancia
        y devuelve una subclase específica por modelo de fuente
        """
        temp_instance = super().__new__(cls)
        temp_instance.__init__(log, address)
        if "GPIB" in address:
            IDN = temp_instance.query('G3')
        else:    
            IDN = temp_instance.query('*IDN?')
        time.sleep(0.01)
        IDN = IDN.strip()

        if "FLUKE8840A" in IDN:
            return super().__new__(Fluke)
        elif "U1251A" in IDN:
            return super().__new__(Agilent)
        else:
            raise ValueError(f"Modelo de multimetro no soportado: {IDN}")

    def __init__(self, log, address):
        super().__init__(log, address)

    def query(self, command: str) -> str:
        return super().query(command)

    def send_command(self, command: str) -> None:
        super().send_command(command)

class Fluke(Multimetro):
    ################################################
    #          Consultas sobre el equipo           #
    ################################################
    def get_value_res(self, conf = None):
        """
        ...

        """
        try:
            # configurar modo resistencia
            self.send_command('F3')
            # rango AUTO
            self.send_command('R0')
            value = self.query('?')
            if float(value) > 100000:
                # configura rango 20M
                self.send_command('R6')
            return value
        except:
            MU.mensajes_usuario(
                "Error","Error al obtener valor del multímetro"
            )
            return None
        
    def get_value_vol(self, conf = None):
        """
        ...
        
        """
        try:
            # configura modo voltaje
            self.send_command('F1')
            # configura rango 200V
            self.send_command('R4')
            value = self.query('?')
            return value
        except:
            MU.mensajes_usuario(
                "Error", "Error al obtener valor del multimetro")
            return None
        
class Agilent(Multimetro):
    def __init__(self,log,address):
        super().__init__(log,address)
        self.mensaje_mostrado_res = False
        self.mensaje_mostrado_vol = False
    ################################################
    #          Consultas sobre el equipo           #
    ################################################
    def get_value_res(self, conf = None):
        """
        ...
        
        """
        if not self.mensaje_mostrado_res:
            MU.mensajes_usuario(
                'instruccion',
                'Gire el selector para configurar el multimetro en modo resistencia.\n'
                'Pulse "Siguiente" cuando esté listo.'
            )
            self.mensaje_mostrado_res = True
        try:
            if conf is not None:
                self.send_command(conf)
            value = self.query('READ?')
            while value == '*B\r\n':
                value = self.query('READ?')
            return value
        except:
            MU.mensajes_usuario(
                "Error", "Error al obtener valor del multimetro")
            return None        
    
    def get_value_vol(self, conf = None):
        """
        ...
        
        """
        if not self.mensaje_mostrado_vol:
            MU.mensajes_usuario(
                'instruccion',
                'Gire el selector para configurar el multimetro en modo voltaje.\n'
                'Pulse "Siguiente" cuando esté listo.'
            )
            self.mensaje_mostrado_vol = True
        try:
            if conf is not None:
                self.send_command(conf)
            value = self.query('READ?')
            while value == '*B\r\n':
                value = self.query('READ?')
            return value
        except:
            MU.mensajes_usuario(
                "Error", "Error al obtener valor del multimetro")
            return None
        
if __name__ == "__main__":
    import test.log_config as Lg
    log = Lg.Logger(__title__,"MUL")
    log.loguear(TITULO)
