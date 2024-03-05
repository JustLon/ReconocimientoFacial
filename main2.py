import cv2
import face_recognition
import tkinter as tk
from PIL import Image, ImageTk

class FaceRecognitionApp:
    def __init__(self, root, video_source=0, resolution=(640, 480), fps=30):
        self.root = root
        self.root.title("Face Recognition")

        self.video_source = video_source
        self.cap = cv2.VideoCapture(self.video_source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

        self.stop_script = False

        self.video_label = tk.Label(self.root)
        self.video_label.pack(padx=10, pady=10)

        self.reference_image = cv2.imread("reference.jpg")
        self.reference_encoding = face_recognition.face_encodings(self.reference_image)[0]

        self.fps = fps

        self.show_frame()

    def show_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = self.adjust_color_balance(frame)

        face_locations = face_recognition.face_locations(frame)

        if face_locations:
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            for face_location, face_encoding in zip(face_locations, face_encodings):
                results = face_recognition.compare_faces([self.reference_encoding], face_encoding)
                label = "Gaby" if results[0] else "Desconocido"
                color = (0, 255, 0) if results[0] else (0, 0, 255)

                cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), color, 2)
                cv2.putText(frame, label, (face_location[3], face_location[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        pil_img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=pil_img)

        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        if not self.stop_script:
            self.video_label.after(int(1000 / self.fps), self.show_frame)

    def adjust_color_balance(self, frame):
        # Adjust color balance if necessary
        # For example, reducing blue component
        # frame[:, :, 0] = frame[:, :, 0] * 0.8
        return frame

    def stop(self):
        self.stop_script = True
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()
