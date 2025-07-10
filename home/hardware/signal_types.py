# -*- coding: utf-8 -*-
__title__ = "Dicc Señales"
__date__ = "2021-08-03 18:15:46"
__version__ = "v2.0.0"
__status__ = "Desarrollo"
__description__ = ""
__author__ = "Lautaro Martinez"
__mail__ = "lmartinez@invap.com.ar"
__details__ = """
    En esta seccion se generan los diccionarios y listas necesarias para
    poder completar las tablas de los procedimientos con los valores maximos 
    y minimos esperados para cada medicion. Tambien contiene los diccionarios
    de configuracion por cada instrumento y los tipos de instrumentos 
            """


class Señales():
    """
    Objeto que se encarga de nuclear los diferentes tipos de señales que 
    maneja el grupo de Integracion Electrica, y los distintos diccionarios
    que contienen la informacion de valores maximos y minimos esperados por
    cada tipo de señal y tipo de medicion a realizar.

    Parameters
    ----------
    None

    Returns
    -------
    None

    """

    TIPO_SEÑALES = (
        "PWRHP",
        "PWRLP",
        "PWR",
        "RS422",
        "RS422-R", 
        "RS422-RC",     
        "HPC-HV",
        "HPC-LV",
        "HPCDIODE-HV",
        "HPCDIODE-LV",
        "PT200",
        "PT2000",
        "G10K",       
        "RCTN0805",
        "LVDS",
        "BDM-DC",        
        "GPI_LVCMOS",      
        "GPI_CMOS_LS_XT",
        "AIN5",
        "AIN5-",
        "AOUT10-",
        "CAN", 
        "SpW",  
        "1553", 
        "TAM", 
        "MTC", 
        "CSS", 
        "TAMBTE",  
        "TS-MON", 
        "ARM-CON", 
        "Chasis")

    SEÑALES_PASIVAS = {
        "pwr_max": "OL",
        "pwr_min": "10K",
        "422_max": "OL",
        "422_min": "4K",
        "422-r_max": 135,
        "422-r_min": 95,
        "hpchv_max": "1,5K",
        "hpchv_min": 180, 
        "hpclv_max": "1,5K",
        "hpclv_min": 180,
        "hpcdhv_max": "100K",
        "hpcdhv_min": "1K",
        "hpcdlv_max": "100K",
        "hpcdlv_min": "1K",
        "pt200_max": 220,
        "pt200_min": 210,
        "pt2000_max": 2200,
        "pt2000_min": 2100,
        "g10k_max": "14K",
        "g10k_min": "10K",
        "rctn_max": "TBD",
        "rctn_min": "TBD",
        "lvds_max": 132,
        "lvds_min": 90,
        "bdm_max": "OL", 
        "bdm_min": "1M",
        "lvcmos_max": "OL",
        "lvcmos_min": "10K",
        "cmosxt_max": "OL",
        "cmosxt_min": "10K",
        "ain5_max": "OL",
        "ain5_min": "10K",
        "ain5-_max": "OL",
        "ain5-_min": "10K",
        "aout10-_max": "OL", 
        "aout10-_min": "50K",
        "can_max": 132, 
        "can_min": 108, 
        "spw_max": 132, 
        "spw_min": 90, 
        "1553_max": 5, 
        "1553_min": 2, 
        "tam_max": 100, 
        "tam_min": 40,
        "mtc_max": 100,
        "mtc_min": 40,
        "tambte_max": "OL",
        "tambte_min": "10K",
        "ts_max": "11K",
        "ts_min": "4K",
        "armcon_max": "OL",
        "armcon_min": "10K",
        "armcon_cont_max": 2,
        "armcon_cont_min": 0,
        "chasis_max": 2,
        "chasis_min": 0    
    }

    AMP_POL_VACIO = {
        "pwr_sabia_max": 33, 
        "pwr_sabia_min": 24,
        "pwr_a14_max": 103, 
        "pwr_a14_min": 97,
        "pwr_a24_max": 103, 
        "pwr_a24_min": 97,
        "hpchv_max": 31, 
        "hpchv_min": 22, 
        "hpclv_max": 17, 
        "hpclv_min": 12,
        "hpcdhv_max": 30, 
        "hpcdhv_min": 22, 
        "hpcdlv_max": 16, 
        "hpcdlv_min": 12,        
        "lvds_max": "TBD",
        "lvds_min": "TBD",         
        "lvcmos_max": "0= 0,5 | 1= 5,5", 
        "lvcmos_min": "0= 0 | 1= 2,4",
        "cmosxt_max": "0= 0,5 | 1= 5,5",
        "cmosxt_min": "0= 0 | 1= 3,5",        
        "spw_max": "TBD", 
        "spw_min": "TBD"
    }

    AMP_VACIO = {
        "422_max": "0= -1,8V | 1= 6V", 
        "422_min": "0= -6V | 1= +1,8V",
        "ain5_max": 5, 
        "ain5_min": 0,
        "ain5-_max": 5, 
        "ain5-_min": -5,
        "aout10-_max": 10,
        "aout10-_min": -10,
        "can_max": 7, 
        "can_min": -2,         
        "1553_max": "28Vpp", 
        "1553_min": "1,1Vpp",
        "tam_max": 7, 
        "tam_min": -7,
        "mtc_max": "-8,5V | 10V", 
        "mtc_min": "-10V | 8,5V",
        "tambte_max": "5,1", 
        "tambte_min": "-5,1"
    }

    POLARIDAD = {
        "422_max": "TBD", 
        "422_min": "TBD",
        "422_dato": "stable with + edge of clock",
        "422_clk": "stable data in + edge",
        "422_pps": "active on low \n16µs ±1µs",
        "422_nom": "positive pulse",
        "can_max": "TBD", 
        "can_min": "TBD",
        "1553_max": "first positive edge", 
        "1553_min": ""
    }

    PINES_CERRADOS = {
        "pwr_sabia_max": 33, 
        "pwr_sabia_min": 24,
        "pwr_a14_max": 103, 
        "pwr_a14_min": 97,
        "pwr_a24_max": 103, 
        "pwr_a24_min": 97,
        "hpchv_max": 31, 
        "hpchv_min": 22, 
        "hpclv_max": 17, 
        "hpclv_min": 12,
        "hpcdhv_max": 30, 
        "hpcdhv_min": 22, 
        "hpcdlv_max": 16, 
        "hpcdlv_min": 12,
        "pt200_max": 2, 
        "pt200_min": 1.6,
        "pt2000_max": 2.22, 
        "pt2000_min": 1.8,
        "g10k_max": 2.9, 
        "g10k_min": 2.35,
        "rctn_max": 3, 
        "rctn_min": 1.8,        
        "422_max": "0= -0,6V | 1= 6V", 
        "422_min": "0= -6V | 1= 0,6V",
        "lvcmos_max": "0= 0,5 | 1= 5,5",
        "lvcmos_min": "0= 0 | 1= 2,4",
        "cmosxt_max": "0= 0,5 | 1= 5,5",
        "cmosxt_min": "0= 0 | 1= 3,5",       
        "ain5_max": "5V (difference less than 5% than in vacuum)", 
        "ain5_min": "0V (difference less than 5% than in vacuum)",
        "ain5-_max": "5V (difference less than 5% than in vacuum)", 
        "ain5-_min": "-5V (difference less than 5% than in vacuum)",
        "aout10-_max": "10V (difference less than 5% than in vacuum)", 
        "aout10-_min": "-10V (difference less than 5% than in vacuum)",                
        "can_max": "dom= 3V | rec= 0,05V", 
        "can_min": "dom= 1,5 | rec= -0,5",        
        "1553_max": "22Vpp", 
        "1553_min": "1,1Vpp",
        "tam_max": "7V", 
        "tam_min": "-7V",
        "mtc_max": "-8,5V | 10V", 
        "mtc_min": "-10V | 8,5V",
        "tambte_max": "5,1V", 
        "tambte_min": "-5,1V",     
        "css_max": "200mV", 
        "css_min": "0"
    }

    TIEMPO_PULSO = {
        "hpc_max": "53ms", 
        "hpc_min": "47ms",
        "tam_max": "3,6ms", 
        "tam_min": "3ms",
        "tambte_max": "N/A", 
        "tambte_min": "N/A"  
    }

    CONSUMO = {
        "pwr_sabia_max": "TBD", 
        "pwr_sabia_min": "TBD",
        "pwr_a14_max": "TBD", 
        "pwr_a14_min": "TBD",
        "pwr_a24_max": "TBD", 
        "pwr_a24_min": "TBD",
        "mtc_max": "0x000 - 165mA | 0xFFF - 240mA", 
        "mtc_min": "0x000 - 240mA | 0xFFF - 165mA",
        "css_max": "20mA", 
        "css_min": "0",
        "ain5-_max": "NA", 
        "ain5-_min": "NA",
        "aout10-_max": "NA", 
        "aout10-_min": "NA"
    }

    RISE_TIME = {
        "hpc_max": "2ms", 
        "hpc_min": "0ms", 
        "422_max": "10% Pulse width", 
        "422_min": "0", 
        "lvcmos_max": "TBD", 
        "lvcmos_min": "TBD",
        "cmosxt_max": "TBD",
        "cmosxt_min": "TBD",
        "can_max": "no reflections", 
        "can_min": "no reflections",
        "1553_max": "110ns", 
        "1553_min": "90ns"
    }

    FALL_TIME = {
        "hpc_max": "2ms", 
        "hpc_min": "0ms", 
        "422_max": "10% Pulse width", 
        "422_min": "0", 
        "lvcmos_max": "TBD", 
        "lvcmos_min": "TBD",
        "cmosxt_max": "TBD",
        "cmosxt_min": "TBD",
        "can_max": "no reflections", 
        "can_min": "no reflections",
        "1553_max": "110ns", 
        "1553_min": "90ns" 
    }

    INRUSH = {
        "pwr_sabia_max": "TBD", 
        "pwr_sabia_min": "TBD",
        "pwr_a14_max": "TBD", 
        "pwr_a14_min": "TBD",
        "pwr_a24_max": "TBD", 
        "pwr_a24_min": "TBD",
    }

    TLMY = {
        "pwr_sabia_max": "TBD", 
        "pwr_sabia_min": "TBD",
        "pwr_a14_max": "TBD", 
        "pwr_a14_min": "TBD",
        "pwr_a24_max": "TBD", 
        "pwr_a24_min": "TBD",
        "422_max": "TBD", 
        "422_min": "TBD", 
        "hpchv_max": "TBD", 
        "hpchv_min": "TBD", 
        "hpclv_max": "TBD", 
        "hpclv_min": "TBD",
        "hpcdhv_max": "TBD", 
        "hpcdhv_min": "TBD", 
        "hpcdlv_max": "TBD", 
        "hpcdlv_min": "TBD",
        "pt200_max": "TBD", 
        "pt200_min": "TBD",
        "pt2000_max": "TBD", 
        "pt2000_min": "TBD", 
        "g10k_max": "TBD", 
        "g10k_min": "TBD",
        "rctn_max": "TBD", 
        "rctn_min": "TBD",        
        "lvds_max": "TBD", 
        "lvds_min": "TBD", 
        "bdm_max": "TBD", 
        "bdm_min": "TBD",        
        "lvcmos_max": "TBD",
        "lvcmos_min": "TBD",
        "cmosxt_max": "TBD",
        "cmosxt_min": "TBD",
        "ain5_max": "TBD", 
        "ain5_min": "TBD", 
        "ain5-_max": "TBD", 
        "ain5-_min": "TBD",
        "aout10-_max": "TBD", 
        "aout10-_min": "TBD",
        "can_max": "TBD",
        "can_min": "TBD", 
        "spw_max": "TBD", 
        "spw_min": "TBD", 
        "1553_max": "TBD", 
        "1553_min": "TBD", 
        "tam_max": "TBD", 
        "tam_min": "TBD",
        "mtc_max": "TBD", 
        "mtc_min": "TBD",
        "css_max": "TBD",
        "css_min": "TBD",
        "tambte_max": "TBD", 
        "tambte_min": "TBD"    
    }

    VER_FUNC = {
        "lvds_max": "TBD",
        "lvds_min": "TBD",
        "spw_max": "TBD", 
        "spw_min": "TBD"
    }


