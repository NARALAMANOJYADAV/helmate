import requests
import os

def download(url, filename):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

download("https://images.tribuneindia.com/cms/gall_content/2019/8/2019_8$largeimg06_Tuesday_2019_072203914.jpg", "no_helmet_ref.jpg")
download("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkeeJtSYhQBl0RBPXeQXM4_Qb3qbzuudoOsQ&s", "helmet_ref.jpg")
