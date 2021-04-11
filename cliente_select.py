import urllib.request, json

url = "http://127.0.0.1:5000/webservice_select"

response = urllib.request.urlopen(url)
data = json.loads(response.read())

print (data)