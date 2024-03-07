import cv2
import face_recognition
import tkinter as tk
import os
from PIL import Image, ImageTk
from os import listdir, makedirs
from os.path import isfile, join, exists
import threading
import tkinter.filedialog as fd
from tkinter import messagebox
import json
import uuid
import shutil

class FaceRecognitionApp:
    def __init__(self, root, video_source=0, resolution=(320, 240), fps=15):
        self.root = root
        self.root.title("Agente R")

        self.video_source = video_source
        self.cap = cv2.VideoCapture(self.video_source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

        self.stop_script = False

        self.video_label = tk.Label(self.root)
        self.video_label.pack(padx=10, pady=10)

        # Se cargan las caras (La carpeta) para tener las referencias
        self.reference_encodings = self.load_reference_encodings("caras")

        #Se carga el Json con los datos de los usuarios
        self.user_data = self.load_user_data("datos/datos.json")

        self.fps = fps

        # Se usa un hilo separado para mostrar el marco (frame)
        self.thread = threading.Thread(target=self.show_frame)
        self.thread.daemon = True
        self.thread.start()

        # Botones de agregar y salir
        self.add_person_button = tk.Button(self.root, text="Agregar Persona", command=self.add_person)
        self.add_person_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.start_stop_script_button = tk.Button(self.root, text="Salir", command=self.stop)
        self.start_stop_script_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.file_path = None  # Variable para almacenar la ruta del archivo seleccionado

    def load_user_data(self, json_file):
        #json para los datos del usuario
        if exists(json_file):
            with open(json_file, "r") as file:
                return json.load(file)
        else:
            return []

    def load_reference_encodings(self, directory): #se cargan las referencias
        reference_encodings = []
        onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
        for filename in onlyfiles:
            image_path = join(directory, filename)
            reference_image = cv2.imread(image_path)
            face_encodings = face_recognition.face_encodings(reference_image)
            if face_encodings:
                reference_encoding = face_encodings[0]  # Tomar la primera codificación de rostro
                reference_encodings.append(reference_encoding)
            else:
                print(f"No se detectaron caras en la imagen {filename}.")
        return reference_encodings


    def show_frame(self):
        while not self.stop_script:
            ret, frame = self.cap.read()
            if not ret:
                continue

            # frame a baja res
            frame = cv2.resize(frame, (640, 480))  # Se ajusta el frame final

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = self.adjust_color_balance(frame)

            face_locations = face_recognition.face_locations(frame)

            if face_locations:
                face_encodings = face_recognition.face_encodings(frame, face_locations)

                for face_location, face_encoding in zip(face_locations, face_encodings):
                    label = "Desconocido"
                    color = (0, 0, 255)  # Rojo para persona que no se reconoce

                    # Se comparan las caras con las ref.
                    for i, reference_encoding in enumerate(self.reference_encodings):
                        results = face_recognition.compare_faces([reference_encoding], face_encoding)
                        if results[0]:
                            # Si coincide con una imagen de referencia, obtener el ID (nombre de la imagen)
                            user_id = os.path.splitext(os.path.basename(listdir("caras")[i]))[0]
                            # Buscar el ID en los datos de usuario
                            for user in self.user_data:
                                if user["id"] == user_id:
                                    label = f"{user['nombre']}, {user['edad']}"
                                    break
                            color = (0, 255, 0)  # Verde si se reconoce la cara
                            break  # Se reconoce entonces se sale del loop.

                    #Se ponen los datos en la pantalla, cuadro y datos.
                    cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), color, 2)
                    cv2.putText(frame, label, (face_location[3], face_location[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            pil_img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=pil_img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            self.video_label.update()

    def adjust_color_balance(self, frame):
        # Ajustes de color que se deban hacer.
        return frame

    def add_person(self):
        # Para Agregar a una persona nueva
        self.ventana_foto = tk.Toplevel(self.root)
        self.ventana_foto.title("Agregar persona")
        self.ventana_foto.geometry("400x200")
        self.ventana_foto.focus_force()

        # Titulo de la ventana
        title_label = tk.Label(self.ventana_foto, text="Agregar persona", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # Boton para ingresar la imagen
        upload_button = tk.Button(self.ventana_foto, text="Subir foto", command=self.upload_photo)
        upload_button.pack(pady=10)

        self.ventana_foto.focus_force() #Mantener el foco de la ventana secundaria!

    def upload_photo(self):
        # Con esta funcion operamos la accion del boton de subir la foto
        print("Uploading photo...")

        # Se abre un explorador de archivos
        self.file_path = fd.askopenfilename(title="Seleccione una imagen", filetypes=(("Image files", "*.jpg;*.jpeg;*.png;*.bmp"), ("all files", "*.*")))
        if self.file_path:
            print("File selected:", self.file_path)

            # Se abre y se redimenciona la imagen
            image = Image.open(self.file_path)
            image = image.resize((300, 300), Image.Resampling.LANCZOS)  # 300x300 para que quepa en la ventana

            # Se convierte a formato ImageTk.photoimage para que se pueda mostrar
            photo = ImageTk.PhotoImage(image)

            # Si ya hay una imagen entonces se elimina todo lo relacionado
            if hasattr(self, 'image_label'):
                self.image_label.destroy()
                self.name_label.destroy()
                self.name_entry.destroy()
                self.age_label.destroy()
                self.age_entry.destroy()

            # Se cre el display para la imagen
            self.image_label = tk.Label(self.ventana_foto, image=photo)
            self.image_label.image = photo  # Se deja la imagen para prevenir que se vaya al mas alla
            self.image_label.pack(side="top", pady=10)

            # Widgets para el nombre y coso
            self.name_label = tk.Label(self.ventana_foto, text="Nombre:")
            self.name_label.pack()
            self.name_entry = tk.Entry(self.ventana_foto)
            self.name_entry.pack()

            self.age_label = tk.Label(self.ventana_foto, text="Edad:")
            self.age_label.pack()
            self.age_entry = tk.Entry(self.ventana_foto)
            self.age_entry.pack()

            submit_button = tk.Button(self.ventana_foto, text="Aceptar", command=self.submit_photo)
            submit_button.pack()

            self.ventana_foto.geometry("400x600") #Redimensionamos la ventana para que todo quepa

            self.ventana_foto.focus_set()
        else:
            print("No file selected.")


    def submit_photo(self):
        name = self.name_entry.get()
        age = self.age_entry.get()

        if not name or not age:
            print('No se lleno el campo nombre o edad')#Advertencia de windows
            messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
            self.ventana_foto.focus_get()
            return

        if not age.isdigit():
            print('La edad debe ser un número')
            messagebox.showwarning("Edad inválida", "Por favor, introduce una edad válida.")
            self.age_entry.delete(0, tk.END)  # Limpiar el campo de edad
            self.ventana_foto.focus_get()
            return

        # Generar un ID unico para el usuario
        user_id = str(uuid.uuid4())

        # Se busca una cara en la imagen y se recorta
        self.recortar_caras(user_id)

        # Crear un nuevo diccionario de usuario
        user_data = {
            "id": user_id,
            "nombre": name,
            "edad": age
        }

        # Guardar los datos del usuario en el archivo json
        json_file = "datos/datos.json"
        if not exists(json_file):
            with open(json_file, "w") as file:
                json.dump([user_data], file, indent=4)
        else:
            with open(json_file, "r+") as file:
                data = json.load(file)
                data.append(user_data)
                file.seek(0)
                json.dump(data, file, indent=4)

        # Mover la imagen del usuario al directorio de caras con el ID como nombre de archivo
        image_filename = user_id + "ori.jpg"
        image_destination = join("carasori", image_filename)
        shutil.copy(self.file_path, image_destination)

        print("Imagen Subida")
        self.ventana_foto.destroy() # Salimos de la Imagen

        self.reference_encodings = self.load_reference_encodings("caras")
        self.user_data = self.load_user_data("datos/datos.json")

    def recortar_caras(self, user_id):
        # Cargar la imagen
        image = cv2.imread(self.file_path)

        # Convertir la imagen de BGR a RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detectar las ubicaciones de las caras en la imagen
        face_locations = face_recognition.face_locations(rgb_image)

        # Si se detecta al menos una cara
        if face_locations:
            # Iterar sobre todas las caras detectadas
            for i, face_location in enumerate(face_locations):
                # Obtener las coordenadas de la cara actual
                top, right, bottom, left = face_location

                # Recortar el area de la cara de la imagen
                cara_recortada = image[top:bottom, left:right]

                # Guardar la cara recortada en la carpeta caras con el ID como nombre de archivo
                if not exists("caras"):
                    os.makedirs("caras")
                
                image_filename = user_id + f".jpg"  # Usar el ID del usuario como nombre de archivo
                image_destination = join("caras", image_filename)
                cv2.imwrite(image_destination, cara_recortada)

                print(f"Cara {i+1} recortada guardada en la carpeta 'caras'")
        else:
            print("No se detectó ninguna cara en la imagen")

    def stop(self):
        self.stop_script = True
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()
