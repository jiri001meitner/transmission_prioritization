#!/home/medved/PythonEnvs/transmissionrpc-env/bin/python3
"""
Předá magnet link transmission, je využíváno shellovým scriptem magnet
"""
import sys
import os
import json
import transmissionrpc
from unidecode import unidecode

# zkontrolovat argumenty a požádat o magnet link, pokud nebyl poskytnut
if len(sys.argv) > 2:
    print("Usage: python3 transmission_add_magnet.py <magnet_link>")
    sys.exit(1)
elif len(sys.argv) == 2:
    magnet_link = sys.argv[1]
else:
    magnet_link = input("Please enter a magnet link: ")

# Načtení přihlašovacích údajů
with open(os.path.expanduser("~/.config/transmission/pass.json"),
          "r", encoding="utf-8") as file:
    credentials = json.load(file)

username = credentials["username"]
password = credentials["password"]

# připojit se k Transmission
try:
    tc = transmissionrpc.Client('127.0.0.1', port=9091, user=username, password=password, timeout=30)

    # přidat magnet link
    torrent = tc.add_torrent(magnet_link)

    # získat informace o souborech
    files = tc.get_files(torrent.id)[torrent.id]

    for file_id, file_info in files.items():
        # odstranit bílé znaky a diakritiku z názvů souborů a složek
        new_name = unidecode(file_info["name"]).replace(" ", "_").replace("\t", "_")

        if new_name != file_info["name"]:
            # změnit název souboru nebo složky
            tc.change_torrent(torrent.id, {"files": {file_id: {"name": new_name}}})

    print(f"Torrent {torrent.id} ({torrent.name}) byl úspěšně přidán a zpracován.")

except Exception as e:
    print("Nastala chyba: ", e)
