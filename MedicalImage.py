from tkinter import messagebox, filedialog, Tk, Label, Text, Scrollbar, Button, END, Frame
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os
from hashlib import sha1
from dna import dna_decode, dna_encode, decompose_matrix
import random
from skimage.metrics import structural_similarity as ssim
import threading

main = Tk()
main.title("DNA-Based Medical Image Encryption") 
main.geometry("1200x850")
main.configure(bg="#eaf6f6")

# Global Variables
global filename, plain_image, public_key
global encrypt_image, dna_encoding, blue_e, green_e, red_e
global h, w, x0, random_value

def upload(): 
    global filename, plain_image
    filename = filedialog.askopenfilename(initialdir="testImages")
    text_output.delete('1.0', END)
    text_output.insert(END, filename + " loaded\n")
    plain_image = cv2.imread(filename)
    plain_image = cv2.resize(plain_image, (300, 300))
    cv2.imwrite("test.png", plain_image)
    plain_image = cv2.imread("test.png")
    filename = "test.png"
    text_output.insert(END, "Image successfully loaded and resized.\n")

def generateRandomValue():
    global x0, random_value, plain_image
    sha = sha1(plain_image).hexdigest()
    x0 = sum([ord(sha[i]) for i in range(16)])
    random_value = sum([ord(sha[i]) for i in range(16, 32)])
    x0 = x0 / random.randrange(150, 255)
    random_value = int(random_value / 510)
    text_output.insert(END, f"Random Value (x0 + r): {random_value + x0:.4f}\n\n")

def dnaEncoding():
    threading.Thread(target=run_dna_encoding).start()

def run_dna_encoding():
    global filename, dna_encoding, blue_e, green_e, red_e
    text_output.insert(END, "Encoding in progress... Please wait.\n")
    blue, green, red = decompose_matrix(filename)
    blue_e, green_e, red_e = dna_encode(blue, green, red)
    dna_encoding = np.dstack((red_e, green_e, blue_e))
    text_output.insert(END, "DNA Encoding Completed.\n")

def correlation(original, encrypted):
    original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    encrypted = cv2.cvtColor(encrypted, cv2.COLOR_BGR2GRAY)
    original = cv2.resize(original, (100, 100))
    encrypted = cv2.resize(encrypted, (100, 100))
    return ssim(original, encrypted, data_range=encrypted.max() - encrypted.min())

def runEncryption():
    global dna_encoding, h, w, random_value, encrypt_image, plain_image, public_key
    text_output.delete('1.0', END)
    generateRandomValue()
    h, w = dna_encoding.shape[0], dna_encoding.shape[1]
    public_key = random.randrange(29, 31)
    for y in range(h):
        for x in range(w):
            for c in range(3):
                dna_encoding[y, x, c] = ord(dna_encoding[y, x, c]) ^ random_value
    encrypt_image = dna_encoding.astype(int) * public_key
    cv2.imwrite("test.png", encrypt_image)
    corr = correlation(plain_image, cv2.imread("test.png"))
    text_output.insert(END, f"Image Correlation: {corr:.4f}\n\n")
    showPlots(plain_image, encrypt_image)

def runDecryption():
    global encrypt_image, public_key, random_value, dna_encoding, blue_e, green_e, red_e
    enc = dna_encoding
    h, w = enc.shape[0], enc.shape[1]
    for y in range(h):
        for x in range(w):
            for c in range(3):
                enc[y, x, c] = chr(int(enc[y, x, c]) ^ random_value)
    b, g, r = dna_decode(blue_e, green_e, red_e)
    decrypt_img = np.dstack((r, g, b))
    showPlots(plain_image, encrypt_image, decrypt_img)

def showPlots(original, encrypted, decrypted=None):
    if decrypted is not None:
        fig, axs = plt.subplots(1, 3, figsize=(12, 5))
        axs[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        axs[0].set_title("Original Image")
        axs[1].imshow(encrypted / 255)
        axs[1].set_title("Encrypted Image")
        axs[2].imshow(decrypted)
        axs[2].set_title("Decrypted Image")
    else:
        fig, axs = plt.subplots(1, 3, figsize=(12, 5))
        axs[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        axs[0].set_title("Original Image")
        axs[1].imshow(encrypted / 255)
        axs[1].set_title("Encrypted Image")
        axs[2].hist(encrypted.ravel(), 256, [0, 256])
        axs[2].set_title("Histogram")
    for ax in axs:
        ax.axis('off')
    plt.tight_layout()
    plt.show()

def close():
    main.destroy()

# UI Components
font_title = ('Helvetica', 20, 'bold')
font_btn = ('Helvetica', 12, 'bold')

Label(main, text='🔐 DNA-Based Medical Image Encryption', bg='#112d4e', fg='white', font=font_title,
      height=2, width=80).pack(pady=10)

frame_output = Frame(main, bg='#eaf6f6')
frame_output.pack(pady=10)

text_output = Text(frame_output, height=18, width=130, font=('Consolas', 11), bg='#ffffff', fg='#222')
scroll = Scrollbar(frame_output, command=text_output.yview)
text_output.configure(yscrollcommand=scroll.set)
text_output.pack(side='left')
scroll.pack(side='right', fill='y')

frame_buttons = Frame(main, bg='#eaf6f6')
frame_buttons.pack(pady=15)

Button(frame_buttons, text="📁 Upload Image", command=upload, bg='#3f72af', fg='white', font=font_btn, width=20).grid(row=0, column=0, padx=10, pady=10)
Button(frame_buttons, text="🧬 DNA Encoding", command=dnaEncoding, bg='#3f72af', fg='white', font=font_btn, width=20).grid(row=0, column=1, padx=10, pady=10)
Button(frame_buttons, text="🔒 Encrypt Image", command=runEncryption, bg='#3f72af', fg='white', font=font_btn, width=20).grid(row=0, column=2, padx=10, pady=10)
Button(frame_buttons, text="🔓 Decrypt Image", command=runDecryption, bg='#3f72af', fg='white', font=font_btn, width=20).grid(row=0, column=3, padx=10, pady=10)
Button(frame_buttons, text="❌ Exit", command=close, bg='#f67280', fg='white', font=font_btn, width=20).grid(row=0, column=4, padx=10, pady=10)

main.mainloop()
