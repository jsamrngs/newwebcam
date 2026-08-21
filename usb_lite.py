import cv2
import time
from datetime import datetime
import requests
from detector import DetectorPersonas

class CamaraUSBLite:
    def __init__(self):
        self.detector = DetectorPersonas(cooldown=10)
        self.captura = cv2.VideoCapture(0)

        if not self.captura.isOpened():
            raise Exception("No se pudo abrir la cámara USB.")

    def enviar_telegram_directo(self, frame):
        TOKEN = "8747525842:AAFilTKQkr-gysnsK8OsCbksO_t_P_8zbK0"
        CHAT_ID = "1601321503"

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        # Codificar imagen en memoria
        _, buffer = cv2.imencode(".jpg", frame)

        files = {
            "photo": ("foto.jpg", buffer.tobytes(), "image/jpeg")
        }

        requests.post(url, data={"chat_id": CHAT_ID}, files=files)

        print("[TELEGRAM] Foto enviada sin guardarla en disco.")

    def tomar_foto(self, frame):
        # Ahora solo enviamos a Telegram
        self.enviar_telegram_directo(frame)

    def iniciar(self):
        print("[INFO] Sistema de vigilancia USB Lite iniciado.")
        print("[INFO] Sin previsualización. Sin grabación. Solo detección y envío a Telegram.")

        while True:
            ret, frame = self.captura.read()

            if not ret:
                print("[ERROR] No se pudo leer frame de la cámara.")
                time.sleep(1)
                continue

            person_detected, boxes, frame = self.detector.detectar(frame)

            if person_detected and self.detector.puede_tomar_foto():
                self.tomar_foto(frame)

            time.sleep(0.05)  # reduce uso de CPU

if __name__ == "__main__":
    cam = CamaraUSBLite()
    cam.iniciar()
