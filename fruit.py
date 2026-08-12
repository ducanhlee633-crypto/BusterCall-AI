import requests
url = "https://api.api-onepiece.com/v2/fruits/en"

response = requests.get(url)

data = response.json()
answer = data[0]["roman_name"]
print (answer)