import webbrowser
from flask import Flask, render_template, request, url_for, redirect

import webbrowser
import os
import cv2
import numpy as np
import time

app = Flask(__name__, static_folder='assets')

# convert data to binary
def data2binary(data):
    if type(data) == str:
        return ''.join([format(ord(i),"08b") for i in data])
    elif type(data) == bytes or type(data) == np.ndarray:
        return [format(i,"08b") for i in data]

# insert lsb in image
def lsb(image, secret_data, prn): 
    secret_data += "#####" 

    binary_data = data2binary(secret_data)

    index     = 0
    for binary in binary_data:
        position1 = prn[index]

        pixel = image[0][position1]
        r,g,b = data2binary(pixel)
        
        if position1 == 545:
            r,g,b = data2binary(image[0][545])

        image[0][position1][0] = int(r[:-1] + binary, 2)
        image[0][position1][1] = int(g[:-1] + binary, 2)
        image[0][position1][2] = int(b[:-1] + binary, 2)

        if position1 == 545:
            r,g,b = data2binary(image[0][545])
            
        index += 1

    return image

# convert key and data to chippertext with ksa and prga method
def rc4(key, data):
    x = 0
    box = list(range(256))
    for i in range(256): #ksa
        x = (x + box[i] + ord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    x = y = 0
    out = []
    for char in data: #prga
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))

    return ''.join(out)

# pseudo random generate to set position lsb byte
def prng(key, length):
    x = 0
    box = list(range(length))
    for i in range(length):
        x = (x + box[i] + ord(key[i % len(key)])) % length
        box[i], box[x] = box[x], box[i]
    
    return box

@app.route('/', methods=['GET'])
def home():
    return render_template("home.html")

@app.route('/encode', methods=['POST'])
def encode():
    time_execute = time.time()
    picture = request.files['picture']
    savepath = os.path.join("assets/img/"+picture.filename)
    picture.save(savepath)

    image = cv2.imread("assets/img/" + picture.filename)
    message  = request.form['hidden_text']
    password = request.form['password']

    position = prng(password, image.shape[0])
    chipper  = rc4(password, message)

    encode  = lsb(image, chipper, position)
    cv2.imwrite("assets/img_lsb/"+ picture.filename.split('.')[0] + '.png' ,encode)

    ori_img = [
                picture.filename, 
                os.path.getsize('assets/img/'+picture.filename)
            ]
    lsb_img = [
                picture.filename.split('.')[0] + '.png',
                os.path.getsize('assets/img_lsb/'+picture.filename.split('.')[0] + '.png')
            ]
    
    time_execute = time.time() - time_execute

    return render_template("encode.html", ori_img = ori_img, lsb_img = lsb_img, time_execute = time_execute)

@app.route('/decode', methods=['GET','POST'])
def decode():
    time_execute = time.time()
    dekrip = ""
    status = "get"

    if request.method == 'POST':
        password = request.form['password']
        picture  = request.files['picture']

        picture = request.files['picture']
        savepath = os.path.join("assets/temp_"+picture.filename)
        picture.save(savepath)

        image = cv2.imread("assets/temp_" + picture.filename)

        position = prng(password, image.shape[0])

        binary_data = ""
        for bin in position:
            r,g,b = data2binary(image[0][bin])

            binary_data += r[-1]

        all_bytes = [binary_data[i: i+8] for i in range (0,len(binary_data),8)]

        decoded_data = ""
        for byte in all_bytes:
            decoded_data += chr(int(byte,2))
            if decoded_data[-5:] == "#####":
                break
        
        cek = "#####" in decoded_data
        if cek:
            status = "success"
            dekrip = rc4(password, decoded_data[:-5])
        else:
            status = "error"

        os.remove("assets/temp_" + picture.filename)

        time_execute = time.time() - time_execute
        
    return render_template("decode.html", dekrip_text = dekrip, status = status, time_execute = time_execute)

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(port=5000)