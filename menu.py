import tkinter as tk
from tkinter import ttk
from camara import CamaraUI  # lo crearemos luego
#from galeria import abrir_galeria  # lo crearemos luego
from tkinter import messagebox

from detector import DetectorPersonas



class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Cámara - usb")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Marco principal
        self.frame = tk.Frame(self.root, bg="#1e1e1e")
        self.frame.pack(fill="both", expand=True)

        # Área de previsualización
        self.preview = tk.Label(self.frame, bg="black")
        self.preview.pack(fill="both", expand=True, padx=10, pady=10)

        # Barra inferior de botones
        botones_frame = tk.Frame(self.frame, bg="#1e1e1e")
        botones_frame.pack(fill="x", pady=10)

        # Botones
        self.btn_grabar = ttk.Button(botones_frame, text="Grabar", command=self.iniciar_grabacion)
        self.btn_grabar.pack(side="left", expand=True, padx=10)

        self.btn_detener = ttk.Button(botones_frame, text="Detener", command=self.detener_grabacion)
        self.btn_detener.pack(side="left", expand=True, padx=10)

        #self.btn_galeria = ttk.Button(botones_frame, text="Galería", command=abrir_galeria)
        #self.btn_galeria.pack(side="left", expand=True, padx=10)

        self.btn_salir = ttk.Button(botones_frame, text="Salir", command=self.root.destroy)
        self.btn_salir.pack(side="left", expand=True, padx=10)

        

        # Inicializar cámara (solo interfaz, sin lógica aún)
        self.camara = CamaraUI(self.preview)
        self.camara.iniciar_camara()

        self.detector = DetectorPersonas(cooldown=10)  # 10 segundos entre fotos

        

    def iniciar_grabacion(self):
        self.camara.iniciar_grabacion()
        messagebox.showinfo("Grabación", "Grabación iniciada")

    def detener_grabacion(self):
        self.camara.detener_grabacion()
        messagebox.showinfo("Grabación", "Grabación detenida")



if __name__ == "__main__":
    root = tk.Tk()
    app = MenuPrincipal(root)
    root.mainloop()
    
