import json, requests
from flask import jsonify

url = "http://127.0.0.1:5000/webservice_insert"

dato = "Hola"

data = {"dato" : dato}

response = requests.post(url, json= data)

if response.ok:
    print (response.json())
