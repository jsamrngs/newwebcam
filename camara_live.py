from flask import Flask, Response
import cv2

app = Flask(__name__)

# Cámara USB (0) o URL RTSP
CAMERA_SOURCE = 0
# CAMERA_SOURCE = "rtsp://usuario:clave@IP:554/Streaming/Channels/101"

cap = cv2.VideoCapture(CAMERA_SOURCE)

def generar_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Codificar frame como JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Enviar como stream MJPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/live')
def live():
    return Response(generar_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "<h1>Cámara Live</h1><img src='/live'>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
