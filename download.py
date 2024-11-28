import requests
import pandas as pd

def download_files_from_excel(file_path):
    data = pd.read_excel(file_path)
    for i, url in enumerate(data.iloc[:, 1]):
        response = requests.get(url)
        with open(f"data/{i}.mp4", "wb") as file:
            file.write(response.content)

download_files_from_excel("data.xlsx")

