import cv2
import threading
import time
from datetime import datetime
from PIL import Image, ImageTk
from matplotlib.pylab import indices
from detector import DetectorPersonas
import os
import requests

import cv2

def detectar_camaras():
    camaras = []
    for i in range(10):  # prueba hasta 10 cámaras
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camaras.append(i)
            cap.release()
    return camaras


class CamaraUI:

    def seleccionar_camara(self):
        indices = detectar_camaras()

        if not indices:
            raise Exception("No se detectaron cámaras en este equipo.")

        # Si hay más de una, asumimos que la USB es la última
        if len(indices) > 1:
            print(f"Cámaras detectadas: {indices} → usando la última (USB)")
            return indices[-1]

        print(f"Solo una cámara detectada: {indices[0]}")
        return indices[0]


    
    def __init__(self, preview_label):
        self.preview_label = preview_label
        self.captura = None
        self.grabando = False
        self.thread_video = None
        self.thread_grabacion = None

        # Detector
        self.detector = DetectorPersonas(cooldown=10)

        # Crear carpetas en el Escritorio
        self.preparar_carpetas()

        # Selección automática de cámara USB
        self.indice_camara = self.seleccionar_camara()


    def iniciar_camara(self):
        if self.captura is None:
            self.captura = cv2.VideoCapture(self.indice_camara)
        self.mostrar_preview()

    def mostrar_preview(self):
        if self.captura is None:
            return

        ret, frame = self.captura.read()
        if ret:

            # --- DETECCIÓN DE PERSONAS ---
            person_detected, boxes, frame = self.detector.detectar(frame)

            # Si detecta persona y cooldown permite → tomar foto
            if person_detected and self.detector.puede_tomar_foto():
                self.tomar_foto(frame)

            # Convertir a RGB para tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
            self.preview_label.configure(image=img)
            self.preview_label.image = img

        self.preview_label.after(10, self.mostrar_preview)

    def obtener_ruta_escritorio():
        return os.path.join(os.environ["USERPROFILE"], "Desktop")

    def preparar_carpetas(self):
        escritorio = os.path.join(os.environ["USERPROFILE"], "Desktop")
        self.base_path = os.path.join(escritorio, "webmedia")

        # Si existe un archivo con ese nombre → error
        if os.path.exists(self.base_path) and not os.path.isdir(self.base_path):
            raise Exception("Existe un archivo llamado 'webmedia' en el Escritorio. No se puede crear la carpeta.")

        # Crear carpeta principal
        os.makedirs(self.base_path, exist_ok=True)

        # Subcarpetas
        self.fotos_path = os.path.join(self.base_path, "fotos")
        self.videos_path = os.path.join(self.base_path, "videos")

        os.makedirs(self.fotos_path, exist_ok=True)
        os.makedirs(self.videos_path, exist_ok=True)

        print(f"[RUTAS] Carpeta base: {self.base_path}")
        print(f"[RUTAS] Fotos: {self.fotos_path}")
        print(f"[RUTAS] Videos: {self.videos_path}")


    def iniciar_grabacion(self):
        if self.grabando:
            return

        self.grabando = True
        self.thread_grabacion = threading.Thread(target=self._ciclo_grabacion)
        self.thread_grabacion.daemon = True
        self.thread_grabacion.start()

    def _ciclo_grabacion(self):
        while self.grabando:
            nombre_archivo = datetime.now().strftime("video_%Y%m%d_%H%M%S.avi")
            ruta_video = os.path.join(self.videos_path, nombre_archivo)

            print(f"[VIDEO] Grabando: {ruta_video}")

            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            out = cv2.VideoWriter(ruta_video, fourcc, 20.0, (640, 480))

            inicio = time.time()

            while self.grabando and (time.time() - inicio < 20 * 60):
                ret, frame = self.captura.read()
                if ret:
                    out.write(frame)
                else:
                    break

            out.release()
            print("[VIDEO] Archivo guardado, iniciando nuevo ciclo...")


    def detener_grabacion(self):
        self.grabando = False
        print("Grabación detenida.")

    def liberar(self):
        self.grabando = False
        if self.captura:
            self.captura.release()

    
    def tomar_foto(self, frame):
        fecha = datetime.now().strftime("%Y-%m-%d")
        carpeta_fecha = os.path.join(self.fotos_path, fecha)
        os.makedirs(carpeta_fecha, exist_ok=True)

        nombre = datetime.now().strftime("foto_%H-%M-%S.jpg")
        ruta = os.path.join(carpeta_fecha, nombre)

        cv2.imwrite(ruta, frame)
        print(f"[FOTO] Persona detectada → guardada en {ruta}")

        # Enviar a Telegram
        self.enviar_telegram(ruta)



    def enviar_telegram(self, ruta_foto):
        TOKEN = "8747525842:AAFilTKQkr-gysnsK8OsCbksO_t_P_8zbK0"
        CHAT_ID = "1601321503"

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        with open(ruta_foto, "rb") as foto:
            requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": foto})

        print(f"[TELEGRAM] Foto enviada a Telegram: {ruta_foto}")
