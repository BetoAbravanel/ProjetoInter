import urllib.request
import requests
import json
import sqlite3
from datetime import datetime
import time

############ Banco
conn = sqlite3.connect('ProjetoInter.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Streamer (
    id_streamer INTEGER NOT NULL,
    username TEXT NOT NULL,
    viewers INTEGER NOT NULL,
    dt_update DATETIME NOT NULL 
    )
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Live (
    id_live INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    id_categoria INTEGER NOT NULL,
    id_streamer INTEGER NOT NULL,
    data_live DATETIME NOT NULL,
    tipo TEXT NOT NULL,
    titulo TEXT NOT NULL,
    dt_update DATETIME NOT NULL

)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Categoria (
    id_categoria INTEGER NOT NULL,
    categoria_nome TEXT NOT NULL,
    dt_update DATETIME NOT NULL
)
''')

conn.commit()

############## API

CLIENT_ID     = "6exyizv1kpmvpz76ew1jbf5ay4gdqw"
CLIENT_SECRET = "nqyv6lsf65qoxhzwilwcgdw82ckl0l"


def make_request(URL):
    header    = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {get_access_token()}" }

    req  = urllib.request.Request(URL, headers=header)
    recv = urllib.request.urlopen(req)
    
    return json.loads(recv.read().decode("utf-8"))

def get_access_token():
    x = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials")
    
    return json.loads(x.text)["access_token"]

    
def get_current_online_streams():
    streamer  = [
        "gafallen",
        "gaules",
        "adolfz",
        "rakin",
        "hiko",
        "brtt",
        "tenz",
        "hayashii",
        "tfue",
        "flowpodcast",
        "castro_1021",
        "thedarkness",
        "alanzoka"
    ]

    URL = "https://api.twitch.tv/helix/streams?user_login="   
    resps = []
    online_streams = []

    for nome in streamer:
        resps.append(make_request(URL + nome))

    GAME_URL = "https://api.twitch.tv/helix/games?id="
    for i, r in enumerate(resps, 0):
        if r["data"]:
            id_categoria   = r["data"][0]["game_id"]
            id_streamer = r["data"][0]["user_id"]

            username = r["data"][0]["user_name"]
            categoria_resp = make_request(GAME_URL + id_categoria)
            categoria_nome = categoria_resp["data"][0]["name"]

            viewers = r["data"][0]["viewer_count"]
            data_live = r["data"][0]["started_at"]
            tipo = r["data"][0]["type"]
            titulo = r["data"][0]["title"]
            data = datetime.now()
            online_streams.append((username, categoria_nome, viewers))

            ########### Insert Streamer
            conn = sqlite3.connect('ProjetoInter.db')
            cursor.execute("INSERT INTO Streamer (id_streamer, username, viewers, dt_update) VALUES (?, ?, ?, ?)", (id_streamer, username, viewers, data))
            conn.commit()

            ########### Insert Live
            cursor.execute("INSERT INTO Live (id_streamer, id_categoria, data_live, tipo, titulo, dt_update)  VALUES (?, ?, ?, ?, ?, ?)", (id_streamer, id_categoria, data_live, tipo, titulo, data))

            conn.commit()
            ########## Insert Categoria
            cursor.execute("INSERT INTO Categoria (id_categoria, categoria_nome, dt_update) VALUES (?, ?, ?)",(id_categoria, categoria_nome, data))
            conn.commit()


    return online_streams




if __name__ == "__main__":
    for i in range(1,8640):
        get_current_online_streams()
        print("Execução: " + str(i) + " data " + str(datetime.now()))
        time.sleep(300)

        