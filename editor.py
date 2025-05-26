
"""
Group Name: CAS/DAN GROUP-15
Group Members:
- S388343 Princy Patel
- S390060 Lamia Sarwar 
- S389242 Mahesh Chandra Regmi
- S390909 Gallage Achintha Methsara Fernando
"""

from tkinter import *
from tkinter import filedialog, ttk, messagebox
import cv2
from PIL import ImageTk, Image
import numpy as np
from abc import ABC, abstractmethod

class ImageProcessor(ABC):
    @abstractmethod
    def process(self, image):
        pass

class GrayscaleProcessor(ImageProcessor):
    def process(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return cv2.cvtColor(gray_image, cv2.COLOR_GRAY2RGB)

class RotateProcessor(ImageProcessor):
    def process(self, image):
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

class CropProcessor(ImageProcessor):
    def __init__(self, x1, y1, x2, y2, ratio):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.ratio = ratio

    def process(self, image):
        x1_image = int(self.x1 * self.ratio)
        y1_image = int(self.y1 * self.ratio)
        x2_image = int(self.x2 * self.ratio)
        y2_image = int(self.y2 * self.ratio)
        return image[y1_image:y2_image, x1_image:x2_image]

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Image Editor - CAS/DAN Group = 15")
        self.root.geometry("1000x800")
        
        self._original_image = None
        self._modified_image = None
        self._filename = None
        self._undo_stack = []
        self._redo_stack = []
        self._crop_mode = False
        self._crop_start_x = None
        self._crop_start_y = None
        self._crop_id = None
        self._preview_dimensions = None
        self._ratio = 1.0

        self._create_gui()
        self._bind_shortcuts()

    def _create_gui(self):
        self._create_canvas_frame()
        self._create_button_frame()
        self._create_instructions_frame()

    def _create_canvas_frame(self):
        self.canvas_frame = Frame(self.root)
        self.canvas_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.canvas_original = Canvas(self.canvas_frame, width=350, height=350, bg="lightblue")
        self.canvas_original.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

        self.canvas_modified = Canvas(self.canvas_frame, width=350, height=350, bg="#CBC3E3")
        self.canvas_modified.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

    def _create_button_frame(self):
        self.button_frame = Frame(self.root, padx=20, pady=10, bg="white")
        self.button_frame.pack(fill=X)

        button_style = {'width': 10, 'height': 2}
        
        Button(self.button_frame, text="Select Image", command=self.select_image, **button_style).pack(side=LEFT, padx=5)
        Button(self.button_frame, text="Crop", command=self.crop, **button_style).pack(side=LEFT, padx=5)
        Button(self.button_frame, text="Grayscale", command=self.grayscale, **button_style).pack(side=LEFT, padx=5)
        Button(self.button_frame, text="Rotate", command=self.rotate, **button_style).pack(side=LEFT, padx=5)
        Button(self.button_frame, text="Undo", command=self.undo, **button_style).pack(side=LEFT, padx=5)
        Button(self.button_frame, text="Redo", command=self.redo, **button_style).pack(side=LEFT, padx=5)
        
        self.zoom_slider = Scale(self.button_frame, 
                               label="Zoom Image",
                               from_=25, 
                               to=125,
                               orient=HORIZONTAL,
                               length=300,
                               command=self.slider)
        self.zoom_slider.set(75)
        self.zoom_slider.pack(side=LEFT, padx=10)
        
        Button(self.button_frame, text="Save Image", command=self.save_image, **button_style).pack(side=LEFT, padx=5)

    def _create_instructions_frame(self):
        instructions_text = '''Instructions:                                                                                                                                Shortcuts:
        1. Select image to edit.                                                                                                            Select Image = Control + O      Undo = Control + Z
        2. View the original image on left and make changes to right image.                                 Crop = Control + C                    Redo = Control + Y
        3. Use functionality like Crop, Grayscale, or Rotate to edit image.                                     Grayscale = Control + G            Save Image = Control + S
        4. Use Undo/Redo, Zoom, and save your image.                                                                  Rotate = Control + R
        5. Use keyboard shortcuts for faster operations!'''
        
        instructions = Label(self.root, 
                           text=instructions_text,
                           justify=LEFT,
                           padx=10,
                           wraplength=900)
        instructions.pack(pady=10)

    def _bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda event: self.select_image())
        self.root.bind("<Control-c>", lambda event: self.crop())
        self.root.bind("<Control-g>", lambda event: self.grayscale())
        self.root.bind("<Control-r>", lambda event: self.rotate())
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Control-s>", lambda event: self.save_image())

    def select_image(self):
        try:
            self._filename = filedialog.askopenfilename(
                filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
            )
            if not self._filename:
                return

            self._original_image = cv2.imread(self._filename)
            if self._original_image is None:
                raise Exception("Failed to load image")

            self._original_image = cv2.cvtColor(self._original_image, cv2.COLOR_BGR2RGB)
            self._original_image = self._original_image.astype('uint8')

            self._modified_image = None
            self._undo_stack.clear()
            self._redo_stack.clear()

            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def display_image(self):
        if self._original_image is None:
            return

        try:
            factor = self.zoom_slider.get() / 100
            self._display_single_image(self._original_image, self.canvas_original, factor)
            image_to_show = self._modified_image if self._modified_image is not None else self._original_image
            self._display_single_image(image_to_show, self.canvas_modified, factor)
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying image: {str(e)}")

    def _display_single_image(self, image, canvas, factor):
        height, width = image.shape[:2]
        canvas_width = 350
        canvas_height = 350

        scale = min(canvas_width/width, canvas_height/height, 1)
        preview_scale = scale * factor

        preview_width = max(1, int(width * preview_scale))
        preview_height = max(1, int(height * preview_scale))

        preview_image = cv2.resize(image, (preview_width, preview_height), interpolation=cv2.INTER_AREA)
        preview_image = preview_image.astype('uint8')

        photo_image = ImageTk.PhotoImage(image=Image.fromarray(preview_image))

        canvas.config(width=preview_width, height=preview_height)
        canvas.delete("all")
        canvas.create_image(preview_width // 2, preview_height // 2, image=photo_image)

        if canvas == self.canvas_original:
            self.tk_original_image = photo_image
        else:
            self.tk_modified_image = photo_image

        if canvas == self.canvas_modified:
            self._preview_dimensions = (preview_width, preview_height)
            self._ratio = width / preview_width if preview_width != 0 else 1

    def _save_state(self):
        current_image = self._modified_image if self._modified_image is not None else self._original_image
        self._undo_stack.append(current_image.copy())
        self._redo_stack.clear()

    def grayscale(self):
        try:
            if self._modified_image is None and self._original_image is None:
                raise Exception("No image available")

            self._save_state()
            processor = GrayscaleProcessor()
            self._modified_image = processor.process(self._modified_image if self._modified_image is not None else self._original_image)
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Error applying grayscale: {str(e)}")

    def rotate(self):
        try:
            if self._modified_image is None and self._original_image is None:
                raise Exception("No image available")

            self._save_state()
            processor = RotateProcessor()
            self._modified_image = processor.process(self._modified_image if self._modified_image is not None else self._original_image)
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Error rotating image: {str(e)}")

    def crop(self):
        if self._original_image is None and self._modified_image is None:
            messagebox.showerror("Error", "No image available to crop!")
            return

        self._crop_mode = True
        self.canvas_modified.bind("<ButtonPress-1>", self._on_button_press)
        self.canvas_modified.bind("<B1-Motion>", self._on_mouse_move)
        self.canvas_modified.bind("<ButtonRelease-1>", self._on_button_release)

    def _on_button_press(self, event):
        self._crop_start_x = event.x
        self._crop_start_y = event.y
        if self._crop_id:
            self.canvas_modified.delete(self._crop_id)
            self._crop_id = None

    def _on_mouse_move(self, event):
        if not self._crop_mode:
            return

        if self._crop_id is None:
            self._crop_id = self.canvas_modified.create_rectangle(
                self._crop_start_x, self._crop_start_y,
                event.x, event.y,
                outline="red", width=2
            )
        else:
            self.canvas_modified.coords(
                self._crop_id,
                self._crop_start_x, self._crop_start_y,
                event.x, event.y
            )

    def _on_button_release(self, event):
        if not self._crop_mode:
            return

        try:
            self.canvas_modified.unbind("<ButtonPress-1>")
            self.canvas_modified.unbind("<B1-Motion>")
            self.canvas_modified.unbind("<ButtonRelease-1>")
            self._crop_mode = False

            x1, y1 = self._crop_start_x, self._crop_start_y
            x2, y2 = event.x, event.y

            if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
                raise Exception("Selected area is too small")

            self._save_state()
            processor = CropProcessor(x1, y1, x2, y2, self._ratio)
            self._modified_image = processor.process(
                self._modified_image if self._modified_image is not None else self._original_image
            )

            if self._crop_id:
                self.canvas_modified.delete(self._crop_id)
                self._crop_id = None

            self.display_image()

        except Exception as e:
            messagebox.showerror("Error", f"Error during crop: {str(e)}")

    def undo(self):
        try:
            if not self._undo_stack:
                raise Exception("Nothing to undo")

            if self._modified_image is not None:
                self._redo_stack.append(self._modified_image.copy())
            
            self._modified_image = self._undo_stack.pop()
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Error during undo: {str(e)}")

    def redo(self):
        try:
            if not self._redo_stack:
                raise Exception("Nothing to redo")

            if self._modified_image is not None:
                self._undo_stack.append(self._modified_image.copy())
            
            self._modified_image = self._redo_stack.pop()
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Error during redo: {str(e)}")

    def slider(self, value):
        if self._original_image is not None:
            self.display_image()

    def save_image(self):
        try:
            if self._modified_image is None and self._original_image is None:
                raise Exception("No image to save")

            image_to_save = self._modified_image if self._modified_image is not None else self._original_image

            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ]
            )

            if not save_path:
                return

            image_to_save_bgr = cv2.cvtColor(image_to_save, cv2.COLOR_RGB2BGR)
            cv2.imwrite(save_path, image_to_save_bgr)
            messagebox.showinfo("Success", f"Image saved to: {save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Error saving image: {str(e)}")

def main():
    root = Tk()
    app = ImageEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()