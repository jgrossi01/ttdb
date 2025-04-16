__tittle__ = "Pickering"
__version__ = "v0.0.1.0"
# ---- IMPORTS
import logging as logger
import traceback as tb
import time
from builtins import int
from robot.api.deco import keyword


# ---- IMPORTS PROPIOS
from invap.egse.jsonrpcclient import AgainError
from invap.egse.jsonrpcclient import ZeroMQClient
from jsonrpcclient.exceptions import ReceivedErrorResponseError
from zmq.error import ZMQError
# ---- PARAMETROS
# ---- VARIABLES GLOBALES
# ---- Variables tipos de relays

ABRIR = "0"
CERRAR = "1"
MAINRELE = 2
FAULT_BUS_1 = 3
FAULT_BUS_2 = 4
F1_to_F4 = 5
F5_to_F8 = 6
MONITOR_RELE = 7
# ---- VARIABLES ESTATICAS
TITULOP = '    ##    ' + __tittle__ + ' ' + __version__ + '    ##    '

# Direccion IP del chasis pxi
direccion_ip = "tcp://10.245.1.103:9194"

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
class Placa:
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
          * Response: list of commands

        Parameters
        ----------
        none

        Returns
        -------
        tuple
            Bool: Whether the operation was successful or not
            Result: Values obtained as a result of the operation.

        
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

        command = 'get_timestamp'
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


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---- FUNCION PRINCIPAL

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




##############################################################################
########################## FUNCIONES PARA LA PLACA ###########################

# # def open_relay(tipo_relay,num_relay,ip_placa="tcp://10.98.67.41:5555"):
# def open_relay(tipo_relay,num_relay,ip_placa="tcp://10.245.1.103:5555"):
#     open_rele = str(f"open_one_rele;{tipo_relay};{num_relay}")
#     validate = __uso_placa__(open_rele,ip_placa)
#     return validate

# # def close_relay(tipo_relay,num_relay,ip_placa="tcp://10.98.67.41:5555"):
# def close_relay(tipo_relay,num_relay,ip_placa="tcp://10.245.1.103:5555"):
#     close_rele = str(f"close_one_rele;{tipo_relay};{num_relay}")
#     __uso_placa__(close_rele,ip_placa)


# def open_all():
#     for i in range(0,74):
#         open_relay(2,i)
#         time.sleep(0.1)
        

# def close_all():
#     for i in range(0,74):
#         close_relay(2,i)
#         time.sleep(0.1)


# def open_monitor_bus():
#     for i in range(0,74):
#         open_relay(3,i) # Bus 1
#         time.sleep(0.1)
#     for i in range(0,74):
#         open_relay(4,i) # Bus 2
#         time.sleep(0.1)
#     for i in range(0,4):
#         open_relay(5,i) # F1 - F4
#         time.sleep(0.1)
#     for i in range(0,4):
#         open_relay(6,i) # F5 - F8
#         time.sleep(0.1)
#     for i in range(0,2):
#         open_relay(7,i) # Monitor 1 - 2
#         time.sleep(0.1)

# ----------------------------------------
# ----- Funciones en desarrollo -- -------
# ----------------------------------------
        
# def iniciar_placa(card,bus,device):
#     cmder = Placa(direccion_ip, 5000)
#     cmder.pik_close(card)
#     cmder.pik_open(card,bus,device)
#     return cmder

# def uso_placa(cmder,card:str,tipo_relay:str,num_relay:str,estado:str):
#     cmder.pik_op_bit(card,tipo_relay,num_relay,estado)

def open_all(card,bus,dev):
    cmder = Placa(direccion_ip,5000)
    cmder.pik_open(card,bus,dev)
    cmder.pik_clear_card(card)
    time.sleep(0.5)
    cmder.pik_close(card)

# ------------------------------------------
# ------------- Para debug -----------------
# -------------------------------------------

if __name__ == "__main__":
    # uso_placa("1","25","14","3","1",CERRAR)
    # time.sleep(2)
    # uso_placa("1","25","14","7","1",CERRAR)
    None