#!/usr/bin/python3
# El nombre de archivo es :  flights.py

# Que hace:
# ---------------------------------------------------------------
#
# 1) Lee el archivo en que se almacena la data recibida por nuestro radar adsb , el archivo es aircraft.json.
# 2) Comprueba si en el archivo aparece alguna coincidencia con lo especificado en el programa
# 3) De ser asi , envia una alerta al chat que se indique su id

import datetime
import json
import time
import syslog
import telegram
import re

################################################################
# Definimos el bot de telegram encargado de enviar el mensaje mediante su token
bot = telegram.Bot(token="")

# Lista especifica de aeronaves a vigilar
icaolist = {
        '34358d': 'Pegasus EC-LGC ABEJA31',
        '345358': 'Pegasus EC-MHV ABEJA35',
        '34348c': 'Pegasus EC-LAR ABEJA30',
        '3432c2': 'Pegasus EC-LDF ABEJA09/11',
        '34329a': 'Pegasus EC-LBD ABEJA10',
        '34358e': 'Pegasus EC-LGD ABEJA32',
        '3452c5': 'Pegasus EC-MMF ABEJA36',
        '343350': 'Pegasus EC-KXU ABEJA20',
        '3445d8': 'Pegasus EC-MDO ABEJA33',
        '345357': 'Pegasus EC-MHU ABEJA34',
#        '345294': 'PROBANDO', #Prueba
        '346105': 'Salvamento Maritimo Coruña' #Salvamento
}

flightlist = {
        'HBAL': 'HBAL Google balloons',
        'AIB': 'Airbus',
        'ABEJA': 'Helicptero DGT'
}

# Squawks a vigilar (mensajes)
squawklist = {
#        '6303':'JU-Air',
        '7500':'Secuestro (hombre con cuchillo)',
        '7600':'Fallo de radio',
        '7700':'EMERGENCIA (avion cayendo , en descenso)'
}

# ID del canal de telegram por el que se enviara el mensaje
def sendTelegram(msg_content):
   bot.sendMessage(chat_id=, text=msg_content)
   print(msg_content)
   return None

def processAircraftList( aircraftList, icaolist, flightlist, squawklist, processed):

        for aircraft in aircraftList:
             hexcode = aircraft["hex"]
             msg_content = ''
             additional_infos = ''
             squawk = ''
             flight = ''
             if 'squawk' in aircraft:
               squawk = aircraft["squawk"]
             #Mensaje que se enviara desde el bot , contiene : mapa y ruta , foto , informacion del vuelo , ademas del texto asociado arriba
             if "flight" in aircraft:
                flight = aircraft["flight"].strip()
             if hexcode in icaolist or any(code in flight for code in flightlist) or squawk in squawklist:
                syslog.syslog('Match ' + flight)
                if hexcode not in processed:
                    processed[hexcode] = datetime.datetime.now().replace(microsecond=0)
                    msg_content += 'http://tar1090.adsbexchange.com/?icao=' + hexcode + '   \n'
                    msg_content += 'https://www.planespotters.net/hex/' + hexcode.upper() + '   \n'
                    if hexcode in icaolist:
                        additional_infos += icaolist[hexcode] + '  \n'
                    if flight:
                      msg_content += 'https://www.radarbox.com/data/flights/' + flight + '   \n'
                      if any(code in flight for code in flightlist):
                        additional_infos += next((v for k, v in flightlist.items() if k in flight), None) + '  \n'
                    if squawk:
                      if squawk in squawklist:
                        msg_content += 'Squawk: ' + squawk + ' ' + squawklist[squawk]
                      else:
                        msg_content += 'Squawk: ' + squawk
                    msg_content += additional_infos
                    syslog.syslog(msg_content)
                    sendTelegram(msg_content)
                else:
                    # Estamos trackeando el avion y ya hemos enviado el mensaje a telegram , actualizamos
                    processed[hexcode] = datetime.datetime.now().replace(microsecond=0)
#                   dd print ('updated timestamp for ', hexcode )

# Tiempo que dejaremos pasar entre avisos , si no vuelve a salir , o ha aterrizado o se ha ido de la cobertura de nuestro receptor
# De no ser asi , se volvera a enviar un aviso al canal 
goneaway = 1200

syslog.syslog('Hi, flights.py starting up')
# Crea una lista de las aeronaves seguidas
processed = {'start':datetime.datetime.now() }
while True:
# Lee el archivo donde se almacenan los datos aircraft.json.
        with open('/run/readsb/aircraft.json') as data_file:
            data = json.load(data_file)
            processAircraftList(data["aircraft"], icaolist, flightlist, squawklist, processed)

# Borra la entrada del diccionario si no lo ha visto en los segundos de goneaway
            for hexcode in list(processed) :
                 if processed[hexcode]  < datetime.datetime.now() - datetime.timedelta(seconds= goneaway) :
#                    print ('removing ', hexcode)
                    del processed[hexcode]
            # tiempo de espera para volver a comprobar el archivo
            time.sleep(10)
#
###################################################################################################