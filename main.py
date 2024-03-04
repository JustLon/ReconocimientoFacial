import threading
import os
import cv2
from deepface import DeepFace
import tkinter as tk

os.system("pip install --upgrade opencv-python deepface")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0

reference_img = cv2.imread("reference.jpg")  # use your own image here
face_match = False
running = True  # Variable para controlar si el proceso de verificación está en ejecución

def check_face(frame):
    global face_match
    try:
        if DeepFace.verify(frame, reference_img.copy())['verified']:
            face_match = True
        else:
            face_match = False
    except ValueError:
        face_match = False

def start_verification():
    global running
    running = True
    while running:
        ret, frame = cap.read()
        if ret:
            if counter % 30 == 0:
                try:
                    threading.Thread(target=check_face, args=(frame.copy(),)).start()
                except ValueError:
                    pass
            counter += 1
            if face_match:
                cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            else:
                cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

            cv2.imshow('video', frame)

            key = cv2.waitKey(1)
            if key == ord('q'):
                running = False
                break

    cv2.destroyAllWindows()
    cap.release()

def stop_verification():
    global running
    running = False

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Verificación Facial")

# Crear botones
boton_iniciar = tk.Button(ventana, text="Iniciar Verificación", command=start_verification)
boton_iniciar.pack(pady=10)

boton_detener = tk.Button(ventana, text="Detener Verificación", command=stop_verification)
boton_detener.pack(pady=10)

# Ejecutar el bucle principal de la ventana
ventana.mainloop()
