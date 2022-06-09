from flask import Flask, render_template, request

import os
from PIL import Image
from numpy import array, asarray

app = Flask(__name__)

# pseudo random generate algoritm
def prga(key): 
    x = 0
    box = list(range(256))
    for i in range(256):
        x = (x + box[i] + ord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    
    return box

def rc4(data, box):
    x = y = 0
    out = []
    for char in data:
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))

    return ''.join(out)

def toBin(txt):
    return ' '.join(format(ord(x), 'b').zfill(8) for x in txt)

def toStr(bin):
    return "".join([chr(int(binary, 2)) for binary in bin.split(" ")])

def imgToMatrix(name):
    img = Image.open("img/"+name)
    ar = array(img)

    new_ar = [[[0 for k in range(len(ar[0][0]))] for j in range(len(ar[0]))] for i in range(len(ar))]

    i = 0
    while i < len(ar):
        j = 0
        while j < len(ar[i]):
            k = 0
            while k < len(ar[i][j]):
                new_ar[i][j][k] = ar[i][j][k]
                k = k + 1
            j = j + 1
        i = i + 1
    
    return new_ar

def arrayToImg(arr, name):
    img = Image.fromarray(asarray(arr), 'RGB')
    img.save('img_lsb/'+name)

# def inputLsb(matrixImg, arRc):


@app.route('/', methods=['GET', 'POST'])
def loadPage():
    if request.method == 'POST':
        picture = request.files['picture']
        savepath = os.path.join("img/"+picture.filename)
        picture.save(savepath)

    return render_template("app.html")


app.run(debug=True, host='0.0.0.0', port=5000)