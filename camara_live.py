from flask import Flask, Response, render_template_string
import cv2

app = Flask(__name__)

CAMERA_SOURCE = 0
cap = cv2.VideoCapture(CAMERA_SOURCE)

def generar_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# Página responsiva
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

    /* Para pantallas muy pequeñas */
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
