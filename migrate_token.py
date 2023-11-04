import json
import aigpy
import base64

def __decode__(string):
    try:
        sr = base64.b64decode(string)
        st = sr.decode()
        return st
    except:
        return string

def read(path):

    txt = aigpy.file.getContent(path)
    if len(txt) > 0:
        print(__decode__(txt))
        data = json.loads(__decode__(txt))
        print(data)

read("database/config/tidalrr.token.json")