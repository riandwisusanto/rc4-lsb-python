from PIL import Image
from numpy import array, asarray

def stringToBin(txt):
    return ' '.join(format(ord(x), 'b').zfill(8) for x in txt)

def intToBin(intg):
    return format(intg, 'b').zfill(8)

def prga(key): 
    x = 0
    box = list(range(256))
    for i in range(256):
        x = (x + box[i] + ord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    
    return box

def rc4(key, data):
    box = prga(key)
    x = y = 0
    out = []
    for char in data:
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))

    return ''.join(out)

def arrayToImg(arr, name):
    img = Image.fromarray(asarray(arr), 'RGB')
    img.save('img_lsb/'+name)

def binary2int(binary): 
    int_val, i, n = 0, 0, 0
    while(binary != 0): 
        a = binary % 10
        int_val = int_val + a * pow(2, i) 
        binary = binary//10
        i += 1
    return int_val

message = "test"
password= "1234"
im_1 = Image.open("img/test.jpeg")
ar   = array(im_1)

new_ar = [[[0 for k in range(len(ar[0][0]))] for j in range(len(ar[0]))] for i in range(len(ar))]
i = 0
while i < len(ar):
    j = 0
    while j < len(ar[i]):
        k = 0
        while k < len(ar[i][j]):
            # new_ar[i][j][k] = ar[i][j][k]
            new_ar[i][j][k] = intToBin(ar[i][j][k])
            k = k + 1
        j = j + 1
    i = i + 1

print(new_ar[0][17])

prgKey = prga(password)
rcStr  = stringToBin(rc4(password, message))

print(prgKey)
print(rcStr)

# i = 0
# for j in rcStr:
#     pos1 = int(prgKey[i] / len(ar[0][0]))
#     pos2 = prgKey[i] % len(ar[0][0])
#     if pos2 > 0:
#         pos1 = pos1 + 1
#     new_ar[0][pos1][pos2] = str(new_ar[0][pos1][pos2][:-1]) + str(j)
#     i = i + 1

# i = 0
# while i < len(ar):
#     j = 0
#     while j < len(ar[i]):
#         k = 0
#         while k < len(ar[i][j]):
#             new_ar[i][j][k] = binary2int(int(new_ar[i][j][k]))
#             k = k + 1
#         j = j + 1
#     i = i + 1

# arrayToImg(new_ar, 'test1.jpg')
# print(toBin(message))