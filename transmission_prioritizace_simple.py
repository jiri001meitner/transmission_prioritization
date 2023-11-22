#!/usr/bin/env python3
"""
Nastavuje prioritu stouborů transmission tak, aby se preferovalo stahování souboru s nejvyšším poměrem stažení
"""
import json
import os
import transmissionrpc

# Načtení přihlašovacích údajů
with open(os.path.expanduser("~/.config/transmission/pass.json"),
          "r", encoding="utf-8") as file:
    credentials = json.load(file)

username = credentials["username"]
password = credentials["password"]

# Načtení nechtěných přípon souborů
with open(os.path.expanduser("~/.config/transmission/unwanted.json"),
          "r", encoding="utf-8") as file:
    unwanted = json.load(file)["unwanted"]

try:
    tc = transmissionrpc.Client('localhost', port=9091, user=username, password=password)

    torrents = tc.get_torrents(arguments=['id', 'status', 'peersConnected', 'name'])
    for torrent in torrents:
        if torrent.status not in ["downloading", "seeding"]:
            continue

        print(f"Processing torrent {torrent.id} ({torrent.name})...")
        files = tc.get_files(torrent.id)[torrent.id]
        if not files:
            print(f"No files for torrent {torrent.id} ({torrent.name})")
            continue

        # Nastavit všechny soubory na nízkou prioritu a jako požadované, pokud nesplňují podmínku
        for file_id, file_info in files.items():
            if file_info["name"].endswith(tuple(unwanted)):
                tc.change_torrent(torrent.id, files_unwanted=[file_id])
                print(f"File {file_info['name']} set to unwanted for torrent {torrent.id} ({torrent.name})")
            else:
                tc.change_torrent(torrent.id, files_wanted=[file_id])
                tc.change_torrent(torrent.id, priority_low=[file_id])

        # Zjistit počet dostupných peerů
        print(f"Available peers for torrent {torrent.id} ({torrent.name}): {torrent.peersConnected}")

        # Požádat tracker o více peerů
        tc.reannounce([torrent.id])
        print(f"Requested more peers for torrent {torrent.id} ({torrent.name})")

        percent_done = {file_id: file["completed"] / file["size"] for file_id, file in files.items() if file["completed"] < file["size"] and not file["name"].endswith(tuple(unwanted))}

        if not percent_done:
            print(f"No files in progress for torrent {torrent.id} ({torrent.name})")
            continue

        file_id_to_download = max(percent_done, key=percent_done.get)

        # Nastavit vybraný soubor na vysokou prioritu
        tc.change_torrent(torrent.id, priority_high=[file_id_to_download])

        print(f"Set file {file_id_to_download} to high priority for torrent {torrent.id} ({torrent.name})")

except Exception as e:
    print("Nastala chyba: ", e)
