import cv2
import time
from datetime import datetime
import os
import requests
from detector import DetectorPersonas

class CamaraUSBLite:
    def __init__(self):
        self.detector = DetectorPersonas(cooldown=10)
        self.captura = cv2.VideoCapture(0)

        if not self.captura.isOpened():
            raise Exception("No se pudo abrir la cámara USB.")

        self.preparar_carpetas()

    def preparar_carpetas(self):
        escritorio = os.path.join(os.environ["USERPROFILE"], "Desktop")
        self.base_path = os.path.join(escritorio, "webmedia")

        os.makedirs(self.base_path, exist_ok=True)

        self.fotos_path = os.path.join(self.base_path, "fotos")
        os.makedirs(self.fotos_path, exist_ok=True)

    def tomar_foto(self, frame):
        fecha = datetime.now().strftime("%Y-%m-%d")
        carpeta_fecha = os.path.join(self.fotos_path, fecha)
        os.makedirs(carpeta_fecha, exist_ok=True)

        nombre = datetime.now().strftime("foto_%H-%M-%S.jpg")
        ruta = os.path.join(carpeta_fecha, nombre)

        cv2.imwrite(ruta, frame)
        print(f"[FOTO] Persona detectada → guardada en {ruta}")

        self.enviar_telegram(ruta)

    def enviar_telegram(self, ruta_foto):
        TOKEN = "xxxxxx"
        CHAT_ID = "xxxx"

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        with open(ruta_foto, "rb") as foto:
            requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": foto})

        print(f"[TELEGRAM] Foto enviada a Telegram: {ruta_foto}")

    def iniciar(self):
        print("[INFO] Sistema de vigilancia USB Lite iniciado.")
        print("[INFO] Sin previsualización. Sin grabación. Solo detección y fotos.")

        while True:
            ret, frame = self.captura.read()

            if not ret:
                print("[ERROR] No se pudo leer frame de la cámara.")
                time.sleep(1)
                continue

            person_detected, boxes, frame = self.detector.detectar(frame)

            if person_detected and self.detector.puede_tomar_foto():
                self.tomar_foto(frame)

            time.sleep(0.05) 

if __name__ == "__main__":
    cam = CamaraUSBLite()
    cam.iniciar()
