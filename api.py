import requests

def get_details(id):
    try:
        response = requests.get(
            f"http://terabox-dl.qtcloud.workers.dev/api/get-info?shorturl={id}&pwd="
        )
        return response.json()
    except requests.RequestException as e:
        print(e)

def get_download_link(data):
    try:
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(
            "https://terabox-dl.qtcloud.workers.dev/api/get-download",
            json=data,
            headers=headers
        )
        return response.json()
    except requests.RequestException as e:
        raise e

# Usage example:
# Replace "id_value" and "data_value" with your desired values
# details = get_details("id_value")
# download_link = get_download_link("data_value")
