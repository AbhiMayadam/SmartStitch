from tkinter import filedialog
from tkinter import *
from tkinter import ttk
from PIL import Image as pil
import numpy as np
import os
import time

class SmartStitch(Tk):
    def __init__(self, *args, **kwargs):
        # Initalizes a tk window with the give parameters of the constructor.
        Tk.__init__(self, *args, **kwargs)

        # Global Variables
        self.input_folder = StringVar()
        self.output_folder = StringVar()
        self.split_height = StringVar(value="5000")
        self.senstivity = StringVar(value="90")
        self.status = StringVar(value="Idle")
        self.progress = ""
        self.actionbutton = ""

        # Componant Setup
        self.SetupWindow()
        self.SetupBrowseFrame().grid(row=0, column=0, padx=(15), pady=(15), sticky="new")
        self.SetupSettingsFrame().grid(row=1, column=0, padx=(15), pady=(0,15), sticky="new")
        self.SetupStatusFrame().grid(row=2, column=0, padx=(15), pady=(0,15), sticky="new")
        self.SetupActionFrame().grid(row=3, column=0, padx=(15), pady=(0,15), sticky="new")

    def SetupWindow(self):
        # Sets up Title and Logo
        self.title('SmartStitch by MechTechnology')
        self.iconphoto(False, PhotoImage(file = "SmartStitchLogo.png"))

        # Sets Window Size, centers it on Launch and Prevents Resize.
        window_height = 280
        window_width = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        self.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.columnconfigure(0, weight=1)
        self.resizable(False, False)

    def SetupBrowseFrame(self):
        # Browse Button and Input and Output Field
        browse_frame = Frame(self)
        browse_label = ttk.Label(browse_frame, text = 'Input Path')
        browse_field = ttk.Entry(browse_frame, textvariable=self.input_folder)
        browse_button = ttk.Button(browse_frame, text = 'Browse', command=self.BrowseToCommand)
        output_label = ttk.Label(browse_frame, text = 'Output Path')
        output_field = ttk.Entry(browse_frame, textvariable=self.output_folder)
        browse_label.grid(row = 0,column = 0, sticky="new")
        browse_field.grid(row = 1, column = 0, pady=(2,0), sticky="new")
        browse_button.grid(row = 1,column = 1, padx=(15, 0), sticky="ne")
        output_label.grid(row = 2, column = 0, sticky="new")
        output_field.grid(row = 3, column = 0, columnspan=2, pady=(2,0), sticky="new")
        browse_frame.columnconfigure(0, weight=1)
        return browse_frame

    def BrowseToCommand(self):
        # Allow user to select a directory and updates input_folder and output_folder
        foldername = filedialog.askdirectory()
        self.input_folder.set(foldername)
        self.output_folder.set(foldername + " [Stitched]")

    def SetupSettingsFrame(self):
        # Browse Split Field and Senstivity Fields
        settings_frame = Frame(self)
        split_label = ttk.Label(settings_frame, text = 'Rough Panel Height (In Pixels):')
        split_field = ttk.Entry(settings_frame, textvariable=self.split_height, validate='all')
        split_field['validatecommand'] = (split_field.register(self.AllowNumOnly),'%P','%d','%s')
        senstivity_label = ttk.Label(settings_frame, text = 'Bubble Detection Senstivity (0-100%):')
        senstivity_field = ttk.Entry(settings_frame, textvariable=self.senstivity, validate='all')
        senstivity_field['validatecommand'] = (senstivity_field.register(self.AllowPercentOnly),'%P','%d','%s')
        split_label.grid(row=0, column=0, sticky="new")
        split_field.grid(row=1, column=0, pady=(2,0), sticky="new")
        senstivity_label.grid(row = 0, column = 1, padx=(15, 0), sticky="new")
        senstivity_field.grid(row = 1, column = 1, padx=(15, 0), pady=(2,0), sticky="new")
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        return settings_frame
    
    def AllowNumOnly(self,P,d,s):
        #If the Keyboard is trying to insert value
        if d == '1': 
            if not (P.isdigit()):
                return False
        return True
    
    def AllowPercentOnly(self,P,d,s):
        #If the Keyboard is trying to insert value
        if d == '1': 
            if not (P.isdigit() and len(s) < 3 and int(P)<=100):
                return False
        return True
    
    def SetupStatusFrame(self):
        status_frame = Frame(self)
        status_label = ttk.Label(status_frame, text = 'Status:')
        status_field = ttk.Entry(status_frame, textvariable=self.status)
        status_field.config(state=DISABLED)
        status_label.grid(row = 0,column = 0, sticky="new")
        status_field.grid(row = 1, column = 0, pady=(2,0), sticky="new")
        status_frame.columnconfigure(0, weight=1)
        return status_frame

    def SetupActionFrame(self):
        action_frame = Frame(self)
        self.progress = ttk.Progressbar(action_frame)
        self.actionbutton = ttk.Button(action_frame, text = 'Start Process', command=self.RunStitchProcess)
        self.progress.grid(row = 0, column = 0, columnspan = 2, pady=(2,0), sticky="new")
        self.actionbutton.grid(row = 0, column = 2, padx=(15, 0), sticky="new")
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        action_frame.columnconfigure(2, weight=1)
        return action_frame

    def LoadImages(self):
        # Loads all image files in a given folder into a list of pillow image objects
        images = []
        if (self.input_folder.get() == ""):
            return images
        folder = os.path.abspath(str(self.input_folder.get()))
        for imgFile in os.listdir(folder):
            if imgFile.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga')):
                imgPath = os.path.join(folder, imgFile)
                image = pil.open(imgPath)
                images.append(image)
        return images

    def CombineVertically(self, images):
        # All this does is combine all the files into a single image in the memory.
        widths, heights = zip(*(image.size for image in images))
        new_image_width = max(widths)
        new_image_height = sum(heights)
        new_image = pil.new('RGB', (new_image_width, new_image_height))

        combine_offset = 0
        for image in images:
            new_image.paste(image, (0, combine_offset))
            combine_offset += image.size[1]
        return new_image

    def SmartAdjust(self, combined_pixels, split_height, split_offset, senstivity):
        # Where the smart magic happens, compares pixels of each row, to decide if it's okay to cut there
        AdjustSensitivity = int(255 * (1-(senstivity/100)))
        adjust_in_progress = True
        new_split_height = split_height
        countdown = True
        while (adjust_in_progress):
            adjust_in_progress = False
            split_row = split_offset + new_split_height
            pixel_row = combined_pixels[split_row]
            prev_pixel = pixel_row[0]
            for x in range(1, len(pixel_row)):
                current_pixel = pixel_row[x]
                diff_pixel = int(current_pixel - prev_pixel)
                if (diff_pixel > AdjustSensitivity):
                    if (countdown):
                        new_split_height -= 1
                    else:
                        new_split_height += 1
                    adjust_in_progress = True
                    break
                current_pixel = prev_pixel
            if (new_split_height < 0.5*split_height):
                new_split_height = split_height
                countdown = False
                adjust_in_progress = True
        return new_split_height

    def SplitVertical(self, combined_img):
        # Splits the gaint combined img into small images passed on desired height.
        split_height = int(self.split_height.get())
        senstivity = int(self.senstivity.get())
        max_width = combined_img.size[0]
        max_height = combined_img.size[1]
        combined_pixels = np.array(combined_img.convert('L'))
        images = []

        # The spliting starts here (calls another function to decide where to slice)
        split_offset = 0
        while((split_offset + split_height) < max_height):
            new_split_height = self.SmartAdjust(combined_pixels, split_height, split_offset, senstivity)
            split_image = pil.new('RGB', (max_width, new_split_height))
            split_image.paste(combined_img,(0,-split_offset))
            split_offset += new_split_height
            images.append(split_image)
        # Final image (What ever is remaining in the combined img, will be smaller than the rest for sure)
        split_image = pil.new('RGB', (max_width, max_height-split_offset))
        split_image.paste(combined_img,(0,-split_offset))
        images.append(split_image)
        return images

    def SaveData(self, data):
        # Saves the given images/date in the output folder!
        new_folder = str(self.output_folder.get())
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
        imageIndex = 1
        for image in data:
            image.save(new_folder + '/' + str(f'{imageIndex:02}') + '.png')
            imageIndex += 1
            progress_value = 40 + (60 * imageIndex/len(data))
            self.progress['value'] = progress_value
            Tk.update_idletasks(self)
        return

    def RunStitchProcess(self):
        # Fires the process sequence from the GUI
        self.actionbutton['state'] = "disabled"
        self.actionbutton.update()
        if(self.split_height.get() == "" or self.split_height.get() =="0"):
            self.status.set("Idle - Split height value was not set!")
            self.actionbutton['state'] = "normal"
            return
        if(self.senstivity.get() == "" or self.senstivity.get() == "0"):
            self.status.set("Idle - Senstivity value was not set!")
            self.actionbutton['state'] = "normal"
            return
        start = time.time()
        self.status.set("Working - Loading Image Files!")
        self.progress['value'] = 0
        Tk.update_idletasks(self)
        images = self.LoadImages()
        if len(images) == 0:
            self.status.set("Idle - No Image Files Found!")
            self.actionbutton['state'] = "normal"
            return
        self.status.set("Working - Combining Image Files!")
        self.progress['value'] = 10
        Tk.update_idletasks(self)
        combined_image = self.CombineVertically(images)
        self.status.set("Working - Slicing Combined Image into Finalized Images!")
        self.progress['value'] = 20
        Tk.update_idletasks(self)
        final_images = self.SplitVertical(combined_image)
        self.status.set("Working - Saving Finalized Images!")
        self.progress['value'] = 40
        Tk.update_idletasks(self)
        self.SaveData(final_images)
        end = time.time()
        delta = end - start
        self.status.set("Idle - Files successfully stitched in " +  str(f'{delta:.2}') + "sec!")
        self.progress['value'] = 100
        self.actionbutton['state'] = "normal"
    

SmartStitch().mainloop()