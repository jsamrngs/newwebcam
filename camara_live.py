from flask import Flask, Response, render_template_string
import cv2

app = Flask(__name__)

# ---------------------------------------------------------
# DETECCIÓN AUTOMÁTICA DE CÁMARAS (PRIORIDAD USB)
# ---------------------------------------------------------
def detectar_camaras():
    camaras = []
    for i in range(10):  # prueba hasta 10 cámaras
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camaras.append(i)
            cap.release()
    return camaras

def seleccionar_camara_usb():
    indices = detectar_camaras()

    if not indices:
        raise Exception("No se detectaron cámaras en este equipo.")

    # Si hay más de una, la última suele ser la USB
    if len(indices) > 1:
        print(f"[INFO] Cámaras detectadas: {indices} → usando la última (USB)")
        return indices[-1]

    print(f"[INFO] Solo una cámara detectada: {indices[0]}")
    return indices[0]

# Selección automática
CAMERA_SOURCE = seleccionar_camara_usb()
cap = cv2.VideoCapture(CAMERA_SOURCE)

# ---------------------------------------------------------
# STREAMING MJPEG
# ---------------------------------------------------------
def generar_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# ---------------------------------------------------------
# PÁGINA RESPONSIVA
# ---------------------------------------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cámara Live</title>

<style>
    body {
        margin: 0;
        background-color: #000;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }

    img {
        width: 100%;
        height: auto;
        max-height: 100vh;
        object-fit: contain;
    }

    @media (max-width: 600px) {
        img {
            width: 100vw;
            height: auto;
        }
    }
</style>
</head>

<body>
    <img src="/live" alt="Cámara en vivo">
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/live')
def live():
    return Response(generar_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
