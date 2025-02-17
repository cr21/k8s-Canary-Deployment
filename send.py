import requests
import json

url = "http://a7352fc5c5fd84b64a4381b964dcc123-1841539688.us-east-1.elb.amazonaws.com/v1/models/cat-classifier:predict"

with open("input.json") as f:
    payload = json.load(f)
headers = {"Host": "cat-classifier.default.emlo.tsai", "Content-Type": "application/json"}

response = requests.request("POST", url, headers=headers, json=payload)

print(response.headers)
print(response.status_code)
print(response.json())
