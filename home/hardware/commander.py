#!/usr/bin/env python
# -*- coding: utf-8 -*-
__tittle__ = "Commander SCT for Pickering"
__version__ = "v0.0.1.0"
__status__ = "Desarrollo"
__description___ = "si una función miembro empieza con _ no se agrega al ICD"
__author__ = 'Federico Martiniau'
__mail__ = 'fmartiniau@invap.com.ar'
__copyright__ = "Copyright 2022, INVAP S.E."
__credits__ = ["", ""]
__date__ = "2024/08/02"
__NOTICE__ = """
PROPRIETARY NOTICE: 
  This document contains information which is proprietary to INVAP and 
  shall not be published, reproduced, copied, disclosed, or used for 
  other than its intended purpose without the express written consent 
  of a duly authorized representative of INVAP.

AVISO DE PROPIEDAD: 
  Este documento contiene información propiedad de INVAP y no podrá publicarse, 
  reproducirse, copiarse, divulgarse ni utilizarse para fines distintos a 
  los previstos sin el consentimiento expreso por escrito de un representante 
  debidamente autorizado de INVAP
"""  
__destails__ = """

 """

# ---- IMPORTS
import logging as logger
# from typing import Optional
# from typing import Union
import traceback as tb
import time
from builtins import int
# from typing import List
# from typing import Tuple

from jsonrpcclient.exceptions import ReceivedErrorResponseError
from zmq.error import ZMQError


# ---- IMPORTS PROPIOS
# from .version import get_library_version
from invap.egse.jsonrpcclient import AgainError
from invap.egse.jsonrpcclient import ZeroMQClient

#import invap.tei.puspacketgenerator.bytes
#from invap.tei.sctutils.decorators import convert
#from invap.tei.sctutils.decorators import Converters
# ---- IMPORTS PROPIOS
# from .version import get_library_version
# from invap.tei.jsonrpcclient import AgainError
# from invap.tei.jsonrpcclient import ZeroMQClient

# ---- PARAMETROS
# ---- VARIABLES GLOBALES


# ---- Funciones  de inicio
# __version__ = get_library_version()

# ---- VARIABLES ESTATICAS
TITULOP = '    ##    ' + __tittle__ + ' ' + __version__ + '    ##    '

# Manejo de respustas
RESULT_ERROR = 0
RESULT_DATA = 1
OPERATION_OK = True
OPERATION_NOT_OK = False

# ---- ERRORES
# Todos los mensajes de error y los alertas deben estar identificados con un numero (codigo) unico para el script

MSG_ERROR_GENERAL = 'ERROR 000:[' + __tittle__ + '] Error trying to initialize class msiclient:{}'
MSG_ERROR_PARAMATRO_FUERA_DE_RANGO = 'ERROR 001:[' + __tittle__ + '] Error in the command {} the parameter {} with value {} is outside the expected values {} - {}'
MSG_ERROR_PARAMATRO_STRING_INVALIDO = 'ERROR 002:[' + __tittle__ + '] Error in the command {} the parameter {} with value {} is outside the expected values {}'
MSG_ERROR_AL_ENVIAR_COMANDO = 'ERROR 003: [' + __tittle__ + '] EError sending command {}'
MSG_ERROR_AL_EJECUTAR_TEST = 'ERROR 004: [' + __tittle__ + '] Error executing test'
MSG_ERROR_AL_CONECTAR = 'ERROR 005:[' + __tittle__ + '] Error attempting to connect:{}, error: {}'
MSG_ERROR_AL_CONECTAR = 'ERROR 005:[' + __tittle__ + '] Error attempting to connect:{}, error: {}'
MSG_ERROR_NOT_IMPLEMENTED = 'ERROR 006:[' + __tittle__ + '] Not implemented: {}'

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ---- Definicion de claese
class Commander:
    """Class that defines the complete interface to be able to interact with the EGSE
     from SAS-EGSE via the INVAP Service-Bus using the standard protocol
     JSONRPC.

     Both requests and responses are sent in JSON format.
     The data transport layer uses the ZMQ protocol.

     **Example of JSON-RPC format:**

     ..code-block::JSON

         {
             "method" : "config_board",
             "params" : {
                 "file_id": 1,
             },
             "jsonrpc":"2.0",
             "id": 0
         }
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = __version__

    # ------------------------------------------------------------------------
    def __init__(
        self, hostname: str = "tcp://localhost:6003", timeout: int = 2000
    ):
        """Initializes the Client class of the library and which it instantiates
         a JSON-RPC client which is used to connect with the
         INVAP-SEVICE-BUS. It uses as parameters the IP/DNS of a server, the
         Port on which it listens and a default timeout is established.
         (default timeout: 1000ms)

         :param hostname: Connection String in format:
            tcp://"IPaddress:IPport".

         :param timeout: an integer representing milliseconds,
                         default = 1000ms
        """
        print_msg(TITULOP)
        try:
            self.client = ZeroMQClient(endpoint=hostname, timeout_ms=timeout)
            logger.info(print_msg("Connected to service {}: {}".format(__tittle__, hostname)))
        except ZMQError as error:
            logger.error(MSG_ERROR_AL_CONECTAR.format(hostname, error))

    # ------------------------------------------------------------------------
    def __send_request(self, function_name, *args, **kwargs):
        try:
            result = self.client.request(function_name, *args, **kwargs)
        except (AgainError, ReceivedErrorResponseError) as error:
            lines = [
                f"Error trying to send request: {function_name}",
                f"With the following arguments: {args}",
                f"And the following Keywords: {kwargs}",
                str(error),
            ]
            logger.error("\n".join(lines))
        else:
            if result.data.ok:
                payload = result.data.result
            else:
                payload = result.error
            return payload

    # ------------------------------------------------------------------------
    def __gen_command(self, command, *args) -> tuple:
        """ 
        * general command function
        """

        try:
            result = self.__send_request(command, *args)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))


    # ------------------------------------------------------------------------
    # ----              Comandos Propios del EGS
    # ------------------------------------------------------------------------

    #  --------------------------------------------
    def get_commands_list(self) -> tuple:
        """
          * Action: Requests the list of valid commands.
          * Response: list of solar panels

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        
        command = 'get_command_list'
        commands = {}
        commands["get_commands_list"] = "Returns the list of commands"
        commands['get_version'] = 'Returns the version of the script'

        # zmq suscriptor
        commands['zmq_start_suscription'] = 'Suscrive to zmq publisher' 

        # Funciones de log
        commands["log_get_last_events"] = "Returns the last N logged elements"
        commands["log_get_statistics"] = "Returns log statistics"

        # Funciones de guardado en CSV
        commands["csv_start_record_in_file"] = "Start saving commands and tlmy in CSV file"
        commands["csv_stop_record_in_file"] = "Stop saving commands and tlmy in CSV file"
        commands["csv_set_file_name"] = "Set neme for CSV file"

        # funciones de configuracon y ambiente
        commands['get_config'] = 'Returns the configuration'
        commands['get_md5_config'] = 'Returns the MD5 of the configuration'
        commands['get_system_info'] = 'Returns the system information'
        commands['get_cpu_info'] = 'Returns the CPU information'
        commands['get_ram_info'] = 'Returns the RAM information'
        commands['get_disk_info'] = 'Returns Disk information'
        commands['get_network_info'] = 'Returns the network information'
        commands['get_pip_info'] = 'Returns the list of libraries installed in pip'
        commands['get_conda_info'] = 'Returns the list of libraries installed in conda'
        commands['get_timestamp'] = 'Returns the servisce timestmp'
        """
        command = 'get_commands_list'
        try:
            result = self.__send_request(command)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
            
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))


    #  --------------------------------------------
    def pik_open(self,card, bus,dev) -> tuple:
        """        
        Open board.

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'pik_open'
        try:
            result = self.__send_request(command,card,bus,dev)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))




    def pik_close(self,card) -> tuple:
        """        
        close board.

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'pik_close'
        try:
            result = self.__send_request(command,card)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))


    def pik_clear_card(self,card) -> tuple:
        """        
        Clear board.

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'pik_clear_card'
        try:
            result = self.__send_request(command,card)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))



    def pik_clear_sub(self,card, sub) -> tuple:
        """        
        Clear Sub board.

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'pik_clear_sub'
        try:
            result = self.__send_request(command,card,sub)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))


    def pik_view_sub(self,card,sub) -> tuple:
        """        
        Board viewsub.

        Parameters
        ----------
        card , sub

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'pik_view_sub'
        try:
            result = self.__send_request(command,card, sub)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))



    def pik_subinfo(self,card,sub) -> tuple:
        """        
        Board get subinfo data.

        Parameters
        ----------
        card , sub

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'pik_subinfo'
        try:
            result = self.__send_request(command,card, sub)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))






    def pik_op_bit(self,card,sub,ch,bit) -> tuple:
        """        
        Board OpBit.

        Parameters
        ----------
        card , sub, ch, bit

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'pik_op_bit'
        try:
            result = self.__send_request(command,card, sub, ch, bit)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))



    #  --------------------------------------------
    def get_version(self) -> tuple:
        """        
        Returns the version of the software components.

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'get_version'
        try:
            result = self.__send_request(command)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------
    # ---- Funciones/comandos de ZMQ
    # -----------------------------------

    # ----------------------------------- 
    def zmq_start_suscription(self) -> tuple:
        """
        * zmq_start_suscription()
          * Action: .
          * Response: Si se conecto

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'zmq_start_suscription'

        try:
            result = self.__send_request(command)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------
    # ---- Funciones/comandos de Log
    # -----------------------------------

    def log_get_last_events(self) -> tuple:
        """
        * log_get_last_events()
          * Action: Solicita los ultimos eventos registrados en el log.
          * Response: Ultimos eventos de log.

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'log_get_last_events'

        try:
            result = self.__send_request(command)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def log_get_statistics(self) -> tuple:
        """
        * log_get_statistics()
          * Action: Solicita estadisticas de logueo.
          * Response: Estadisticas del logueo.

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """

        command = 'log_get_statistics'
        try:
            result = self.__send_request(command)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------
    # ---- Funciones/comandos de CSV
    # -----------------------------------

    def csv_start_record_in_file(file_name: str = None) -> tuple:
        """
        * csv_start_record_in_file()
          * Action: Start record commands and telemetry in CSV file
          * Response: Confirmation of sending the command

        Parameters
        ----------
        str: 
            file_name: name of file

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'csv_start_record_in_file'

        try:
            result = self.__send_request(command, file_name)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def csv_stop_record_in_file(self) -> tuple:
        """
        * csv_stop_record_in_file()
          * Action: Stops record commands and telemetry in CSV file
          * Response: Confirmation of sending the command

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'csv_stop_record_in_file'

        try:
            result = self.__send_request(command)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def csv_set_file_name(self, file_name: str = 'tlmy') -> tuple:
        """
        * csv_set_file_name()
          * Action: Stops record commands and telemetry in CSV file
          * Response: Confirmation of sending the command

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        """
        command = 'csv_set_file_name'

        try:
            result = self.__send_request(command, file_name)

            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------
    # ---- Funciones de configuracon y ambiente
    # -----------------------------------
   
    def get_config(self):
        """
        * get_config()
          * Action: Requests the actual configuration of the service
          * Response: Configuration of the service

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.
        """

        command = 'get_config'
        try:
            result = self.__send_request(command)
            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def get_md5_config(self):
        """
        * get_md5_config()
          * Action: Requests the MD5 of config files
          * Response: List of MD5 and name files

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.
        """

        command = 'get_md5_config'
        try:
            result = self.__send_request(command)
            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def get_system_info(self):
        """
        * get_system_info()
          * Action: Requests the actual operativsystem information
          * Response: operativsystem info

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.
        """

        command = 'get_system_info'
        try:
            result = self.__send_request(command)
            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def get_cpu_info(self):
        """
        * get_cpu_info()
          * Action: Requests the actual CPU information
          * Response: CPU info

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.
        """

        command = 'get_cpu_info'
        try:
            result = self.__send_request(command)
            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def get_ram_info(self):
        """
        * get_ram_info()
          * Action: Requests the actual memory RAM information
          * Response: memory RAM info

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.
        """

        command = 'get_ram_info'
        try:
            result = self.__send_request(command)
            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def get_disk_info(self):
        """
        * get_disk_info()
          * Action: Requests the actual hard disck information
          * Response: Hard disck info

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.
        """

        command = 'get_disk_info'
        try:
            result = self.__send_request(command)
            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def get_network_info(self):
        """
        * get_network_info()
          * Action:  Requests the actual network configuration
          * Response: network configuration info

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.
        """

        command = 'get_network_info'
        try:
            result = self.__send_request(command)
            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def get_pip_info(self):
        """
        * get_pip_info()
          * Action:  Requests the actual pip libraries list installed
          * Response: pip list

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.
        """

        command = 'get_pip_info'
        try:
            result = self.__send_request(command)
            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def get_conda_info(self):
        """
        * get_conda_info()
          * Action:  Requests the actual conda libraries list installed
          * Response: conda list

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.
        """

        command = 'get_conda_info'
        try:
            result = self.__send_request(command)
            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))

    # -----------------------------------------------------
    def get_timestamp(self):
        """
        * get_timestamp()
          * Action:  Requests the actual timestmp
          * Response: Timestmp

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.
        """

        command = 'get_conda_info'
        try:
            result = self.__send_request(command)
            if result is not None:
                return result
            else:
                return (OPERATION_NOT_OK, result)
        except Exception:
            logger.error(print_msg((tb.format_exc())))
            logger.error(print_msg((MSG_ERROR_AL_ENVIAR_COMANDO.format(command))))
            return (OPERATION_NOT_OK, MSG_ERROR_AL_ENVIAR_COMANDO.format(command))



# ----------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---- FUNCIONES SECUNDARIAS
def test():
    try:
        cmder = Commander("tcp://localhost:9194", 5000)  #DN 9094  y 50000 ori
         
        print('pik_open')
        print(cmder.pik_open("1","25","8"))
        time.sleep(0.1)
        
        print('pik_op_bit')
        print(cmder.pik_op_bit("1","2","1","1"))
        time.sleep(0.1)
        
        print('pik_op_bit')
        print(cmder.pik_op_bit("1","2","74","1"))
        time.sleep(0.1)
        print('pik_view_sub')
        print(cmder.pik_view_sub("1","2"))      
        
        
        
        time.sleep(12)
        
        print('pik_op_bit')
        print(cmder.pik_op_bit("1","2","74","0"))
        time.sleep(0.1)        
 
        print('pik_op_bit')
        print(cmder.pik_op_bit("1","7","1","1"))
        time.sleep(0.1) 
        print('pik_view_sub')
        print(cmder.pik_view_sub("1","7"))      
        time.sleep(0.1)         
       
        
        print('pik_clear_card')
        print(cmder.pik_clear_card("1"))
        time.sleep(0.1)  
        
        print('pik_clear_sub')
        print(cmder.pik_clear_sub("1", "7"))
        time.sleep(0.1)  
        
        print('pik_subinfo')
        print(cmder.pik_subinfo("1","5"))      
        time.sleep(0.1)                                     
        print('pik_subinfo')
        print(cmder.pik_subinfo("1","1"))      
        time.sleep(0.1)           
        print('pik_close')
        print(cmder.pik_close("1"))
        time.sleep(0.1)
 
        """
        print('get_commands_list')
        print(cmder.get_commands_list())
        time.sleep(0.1)

        print('get_version')
        print(cmder.get_version())
        time.sleep(0.1)
        
       

        print('get_config')
        print(cmder.get_config())
        time.sleep(0.1)

        print('get_md5_config')
        print(cmder.get_md5_config())
        time.sleep(0.1)

        print('get_system_info')
        print(cmder.get_system_info())
        time.sleep(0.1)

        print('get_cpu_info')
        print(cmder.get_cpu_info())
        time.sleep(0.1)

        print('get_ram_info')
        print(cmder.get_ram_info())
        time.sleep(0.1)

        print('get_disk_info')
        print(cmder.get_disk_info())
        time.sleep(0.1)

        print('get_network_info')
        print(cmder.get_network_info())
        time.sleep(0.1)

        print('get_network_info')
        print(cmder.get_network_info())
        time.sleep(0.1)

        print('get_pip_info')
        print(cmder.get_pip_info())
        time.sleep(0.1)

        print('get_conda_info')
        print(cmder.get_conda_info())
        time.sleep(0.1)
        """


        return 'Ok'
    except Exception:
        logger.error(print_msg((tb.format_exc())))
        logger.error(print_msg((MSG_ERROR_AL_EJECUTAR_TEST.format())))
        return (OPERATION_NOT_OK, MSG_ERROR_AL_EJECUTAR_TEST.format())

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---- FUNCION PRINCIPAL


def run(arg):

    # Titulo que se muestra por pantalla
    header()
    # Fin titulo que se muestra en pantalla
    result = test()
    print(result)
    return True

# --------------------------------------------------------------------------


def get_version() -> tuple:
    """
    Devuelve la version del script

    Returns
    -------
    tuple
        Exito: Si la operación se ejecutó correctamente (True o False)
        Result: Version o lista de versiones de las liberias importadas.

    """
    version = '{}:{}\n'.format(__tittle__, __version__)
    return (OPERATION_OK, version)

# -------------------------------
def print_msg(msg: str) -> tuple:
    """
    se encarga de imprimir en forma correcta todo lo que se debe mostrar por pantalla
    """
    try:
        for linea in msg.split("\n"):
            print("\r" + linea.strip("\n"))
        return (OPERATION_OK, msg)
    except Exception:
        print(msg)
        return (OPERATION_OK, msg)

# -------------------------------


def header():
    # Titulo que se muestra por pantalla
    print(r"""
+------------------------------------------------------------------------------+
|   |
|                     ██╗███╗   ██╗██╗   ██╗ █████╗ ██████╗                    |
|                     ██║████╗  ██║██║   ██║██╔══██╗██╔══██╗                   |
|                     ██║██╔██╗ ██║██║   ██║███████║██████╔╝                   |
|                     ██║██║╚██╗██║╚██╗ ██╔╝██╔══██║██╔═══╝                    |
|                     ██║██║ ╚████║ ╚████╔╝ ██║  ██║██║                        |
|                     ╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  S.E.                  |
|   |""")

    print_msg('|' + ' ' * 78 + '|')
    renglon = TITULOP
    largo = len(renglon)
    espacio = int((80 - largo) / 2)

    print_msg('|' + ' ' * espacio + renglon + ' ' * (78 - (espacio + largo)) + '|')
    print_msg('|' + ' ' * 78 + '|')

    print_msg('|' + ' ' * 78 + '|')
    renglon = __copyright__
    largo = len(renglon)
    print_msg('|' + ' ' * 2 + renglon + ' ' * (78 - (2 + largo)) + '|')

    renglon = 'Author: ' + __author__
    largo = len(renglon)
    print_msg('|' + ' ' * 2 + renglon + ' ' * (78 - (2 + largo)) + '|')

    renglon = 'Mail: ' + __mail__
    largo = len(renglon)
    print_msg('|' + ' ' * 2 + renglon + ' ' * (78 - (2 + largo)) + '|')
    print_msg('+' + '-' * 77 + '*/')
    print_msg('\n' * 4)
    return None


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ---- FUNCION DEBUG
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        arg = sys.argv[RESULT_DATA]
    else:
        arg = '0'
    if arg != '0':
        print('Parametros ingresados: ' + arg)

    run(arg)
