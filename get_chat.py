import requests

TOKEN = '...'
CHAT_ID = None

def get_updates():
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
    response = requests.get(url)
    return response.json()

updates = get_updates()
print(updates)
