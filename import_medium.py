import requests

def get_medium():
    return requests.get('https://api.medium.com/v1/me', headers={"Authorization": "Bearer 2591021aa5554d38e2856a5a42e349b60119934357789fc5ea4049f62452b34f6"})

