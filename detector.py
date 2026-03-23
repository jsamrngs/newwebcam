import cv2
import time

class DetectorPersonas:
    def __init__(self, cooldown=10):
        # Cooldown entre fotos
        self.cooldown = cooldown
        self.ultimo_disparo = 0

        # Cargar modelo MobileNet SSD
        self.net = cv2.dnn.readNetFromCaffe(
            "models/MobileNetSSD_deploy.prototxt",
            "models/MobileNetSSD_deploy.caffemodel"
        )


        # ID de la clase "person" en COCO
        self.PERSON_CLASS_ID = 15

    def detectar(self, frame):
        """
        Procesa un frame y detecta personas.
        Devuelve:
        - person_detected: bool
        - boxes: lista de coordenadas
        - frame_con_cajas: frame con recuadros dibujados
        """

        alto, ancho = frame.shape[:2]

        # Preparar blob
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            0.007843,
            (300, 300),
            127.5
        )

        self.net.setInput(blob)
        detecciones = self.net.forward()

        boxes = []
        person_detected = False

        # Recorrer detecciones
        for i in range(detecciones.shape[2]):
            confianza = detecciones[0, 0, i, 2]
            clase = int(detecciones[0, 0, i, 1])

            if confianza > 0.5 and clase == self.PERSON_CLASS_ID:
                person_detected = True

                box = detecciones[0, 0, i, 3:7] * [ancho, alto, ancho, alto]
                (x1, y1, x2, y2) = box.astype("int")
                boxes.append((x1, y1, x2, y2))

                # Dibujar recuadro
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        return person_detected, boxes, frame

    def puede_tomar_foto(self):
        """
        Controla el cooldown para evitar tomar fotos repetidas.
        """
        ahora = time.time()
        if ahora - self.ultimo_disparo >= self.cooldown:
            self.ultimo_disparo = ahora
            return True
        return False
