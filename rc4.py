def rc4(data, key):
    x = 0
    box = list(range(256))
    for i in range(256):
        x = (x + box[i] + ord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    x = y = 0
    out = []
    for char in data:
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))

    return [
        ''.join(str(box)),
        ''.join(out),
        toBin(''.join(out))
    ]

def toBin(txt):
    return ' '.join(format(ord(x), 'b').zfill(6) for x in txt)

def toStr(bin):
    return "".join([chr(int(binary, 2)) for binary in bin.split(" ")])

def main():
    # print(" RC4 Encryption")
    # data = input("Input Message : ")
    # key = input("Input Key : ")
    # encrypt = rc4(data,key)
    # print("Encrypt Message : ", encrypt)
    # print("Binary Encrypt  : ", toBin(encrypt))
    # print("Binary to String Encrypt  : ", toStr(toBin(encrypt)))
    # print("Decrypt Message : ", rc4(encrypt,key))

    data = "hello world"
    key  = "1234"
    print('', rc4(data, key))

if __name__ == '__main__':
    main()