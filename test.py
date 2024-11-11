import requests

subscription_key = '106c8f6b95a4460fae580599a6c74348'
endpoint = 'https://api.cognitive.microsofttranslator.com/'
path = '/translate?api-version=3.0'
params = '&to=es'
constructed_url = endpoint + path + params

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-type': 'application/json',
    'Ocp-Apim-Subscription-Region': 'uaenorth'  # Include if required
}

body = [{
    'text': 'Hello, world!'
}]

response = requests.post(constructed_url, headers=headers, json=body)
print(response.status_code)
print(response.json())
