import requests

def fetch_data(url, path):
    r = requests.get(url)
    with open(path, 'w') as f:
        f.write(r.text)

url  = 'https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1.'

fetch_data(url, "outputs/rawchapter1.txt")
#print("Data fetched and saved to ouputs/rawchapter1.txt")
