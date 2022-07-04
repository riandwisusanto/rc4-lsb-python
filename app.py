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

        image[0][position1][0] = int(r[:-1] + binary, 2)
        image[0][position1][1] = int(g[:-1] + binary, 2)
        image[0][position1][2] = int(b[:-1] + binary, 2)
            
        index += 1

    return image

# insert lsb in image
def lsb_to_bin(image, secret_data, prn): 
    secret_data += "#####" 

    binary_data = data2binary(secret_data)

    im    = []
    index = 0
    for binary in binary_data:
        position1 = prn[index]
        pixel = image[0][position1]
        r,g,b = data2binary(pixel)

        ar = [
            r[:-1] + binary,
            g[:-1] + binary,
            b[:-1] + binary
        ]

        im.append(ar)
            
        index += 1

    return im

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

# pretty size mapping
UNITS_MAPPING = [
    (1<<50, ' PB'),
    (1<<40, ' TB'),
    (1<<30, ' GB'),
    (1<<20, ' MB'),
    (1<<10, ' KB'),
    (1, (' byte', ' bytes')),
]

# convert size to pretty size (ex. KB, MB, TB)
def pretty_size(bytes, units=UNITS_MAPPING):
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix

@app.route('/', methods=['GET'])
def home():
    return render_template("home.html", error = "")

@app.route('/encode', methods=['POST'])
def encode():
    # pra proses 1
    time_execute = time.time()
    picture = request.files['picture']
    savepath = os.path.join("assets/img/"+picture.filename)
    picture.save(savepath)

    # pra proses 2
    image = cv2.imread("assets/img/" + picture.filename)
    message  = request.form['hidden_text']
    password = request.form['password']

    # check max text
    maxText = int(image.shape[0] / 8) - 24
    if len(message) > maxText:
        error = "Gagal, maksimal karakter " + str(maxText) + ", jumlah karakter " + str(len(message))
        return render_template("home.html", error = error)
    else:
        # convert prng and rc4
        position = prng(password, image.shape[0])
        chipper  = rc4(password, message)

        # encode to lsb and save to img_lsb as image
        encode  = lsb(image, chipper, position)
        cv2.imwrite("assets/img_lsb/"+ picture.filename.split('.')[0] + '.png' ,encode)

        # display array image and array image lsb
        ar_ori = cv2.imread("assets/img/" + picture.filename)
        ar_lsb = cv2.imread("assets/img_lsb/" + picture.filename.split('.')[0] + '.png')
        arr_ori = []
        arr_lsb = []
        bin_ori = []
        bin_lsb = []
        i = 0
        for pos in position:
            arr_ori.append(ar_ori[0][pos])
            arr_lsb.append(ar_lsb[0][pos])

            bin_ori.append(data2binary(ar_ori[0][pos]))
            bin_lsb.append(data2binary(ar_lsb[0][pos]))

            i += 1
            if i == (len(message) * 8):
                break

        # set ori image to display result
        ori_img = {
            "path": picture.filename,
            "size": pretty_size(os.path.getsize('assets/img/'+picture.filename)),
            "arr" : arr_ori,
            "bin" : bin_ori
        }
        
        # set lsb image to display result
        lsb_img = {
            "path": picture.filename.split('.')[0] + '.png',
            "size": pretty_size(os.path.getsize('assets/img_lsb/'+picture.filename.split('.')[0] + '.png')),
            "arr" : arr_lsb,
            "bin" : bin_lsb
        }
        
        time_execute = time.time() - time_execute

        # compress all to one variabel
        data = {
            # proses
            "text"   : message,
            "pass"   : password,
            "tahap1" : ', '.join([str(elem) for elem in position]),
            "tahap2" : chipper,
            "tahap3" : data2binary(chipper),
            "tahap4" : ar_ori[0],
            "tahap5" : [data2binary(elem) for elem in ar_ori[0]],
            "tahap6" : lsb_to_bin(ar_ori, "pppppp", position),
            # hasil
            "ori_img": ori_img,
            "lsb_img": lsb_img,
            "time_execute": time_execute
        }

        return render_template("encode.html", data = data)

@app.route('/decode', methods=['GET','POST'])
def decode():
    time_execute = time.time()
    dekrip = ""
    status = "get"
    path   = ""

    if request.method == 'POST':
        password = request.form['password']
        picture  = request.files['picture']

        picture = request.files['picture']
        path    = picture.filename
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
        
    return render_template("decode.html", path = path, dekrip_text = dekrip, status = status, time_execute = time_execute)

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(port=5000, debug=True)