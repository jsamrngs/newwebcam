# newwebcam – Sistema de vigilancia con detección de personas

Este proyecto utiliza OpenCV y MobileNetSSD para detectar personas, tomar fotos, grabar videos y enviar alertas por Telegram.

## Instalación

1. Instalar Python 3.10+
2. Clonar el repositorio:
   git clone https://github.com/usuario/newwebcam
3. Instalar dependencias:
   pip install -r requirements.txt
4. Ejecutar:
   python menu.py

## Estructura
- camara.py → manejo de cámara, fotos, videos
- detector.py → detección de personas
- menu.py → interfaz gráfica
- models/ → modelos MobileNetSSD
