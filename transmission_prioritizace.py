#!/usr/bin/env python3
"""
Modul pro správu a výpis informací o torrentech získaných z Transmission.
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

# Připojení k Transmission RPC
client = transmissionrpc.Client('localhost', port=9091, 
                                user=username, password=password)

torrents_info = {}

def pridat_torrent_info(tr_id, torrent_data):
    """
    Přidá informace o jednom torrentu do slovníku torrents_info.
    """
    torrents_info[tr_id] = torrent_data

def vypsat_torrent_info():
    """
    Vypíše informace o všech torrentech uložených ve slovníku torrents_info.
    """
    for tr_id, info in torrents_info.items():
        print(f"Torrent ID: {tr_id}")
        for key, value in info.items():
            if key != "soubory":
                print(f"  {key}: {value}")
        print("  Soubory:")
        for fname, file_info in info["soubory"].items():
            print(f"    {fname}:")
            for file_key, file_value in file_info.items():
                print(f"      {file_key}: {file_value}")
        print("")

# Načtení a zpracování torrentů
torrenty = client.get_torrents()
if torrenty:
    for torrent in torrenty:
        soubory_info = [
            {
                "name": file['name'],
                "size": file['size'],
                "completed": file['completed'],
                "priority": file['priority'],
                "selected": file['selected'],
                "fronta": "nezpracovano",
                "zpracovano": False
            }
            for file in torrent.files().values()
        ]
        data_torrentu = {
            "jmeno_torrentu": torrent.name,
            "hash_torrentu": torrent.hashString,
            "error": torrent.error,
            "errorString": torrent.errorString,
            "comment": torrent.comment,
            "creator": torrent.creator,
            "activityDate": torrent.activityDate,
            "bandwidthPriority": torrent.bandwidthPriority,
            "magnetLink": torrent.magnetLink,
            "downloadDir": torrent.downloadDir,
            "status": torrent.status,
            "isFinished": torrent.isFinished,
            "isPrivate": torrent.isPrivate,
            "isStalled": torrent.isStalled,
            "progress": torrent.progress,
            "download_rate": torrent.rateDownload,
            "downloadLimit": torrent.downloadLimit,
            "honorsSessionLimits": torrent.honorsSessionLimits,
            "upload_rate": torrent.rateUpload,
            "peers_connected": torrent.peersConnected,
            "queue_position": torrent.queuePosition,
            "total_size": torrent.totalSize,
            "uploaded": torrent.uploadedEver,
            "downloaded": torrent.downloadedEver,
            "addedDate": torrent.addedDate,
            "startDate": torrent.startDate,
            "doneDate": torrent.doneDate,
            "peer_limit": torrent.peer_limit,
            "peersConnected": torrent.peersConnected,
            "peers": torrent.peers,
            "peersFrom": torrent.peersFrom,
            "peersGettingFromUs": torrent.peersGettingFromUs,
            "peersSendingToUs": torrent.peersSendingToUs,
            "percentDone": torrent.percentDone,
            "uploadRatio": torrent.uploadRatio,
            "soubory": {file["name"]: file for file in soubory_info}
        }
        pridat_torrent_info(torrent.id, data_torrentu)

fronta_snizit = []
fronta_zvysit = []

def logika_snizeni_priority():
    """
    Logika pro snížení priority souborů v torrentech.
    """
    for tr_id, info in torrents_info.items():
        if info['bandwidthPriority'] == -1:
            for file_info in info['soubory'].values():
                file_info['fronta'] = 'preskoceno_snizit'
            continue

        if info['progress'] == 100.0 and info['bandwidthPriority'] in [0, 1]:
            for file_info in info['soubory'].values():
                file_info['fronta'] = 'snizit'
            continue

        for file_info in info['soubory'].values():
            if file_info['fronta'] == 'nezpracovano':
                if file_info['priority'] == 'low':
                    file_info['fronta'] = 'preskoceno_snizit'
                    continue

                if not file_info['selected']:
                    file_info['fronta'] = 'snizit'
                    continue

                if any(file_info['name'].endswith(ext) for ext in unwanted):
                    file_info['fronta'] = 'snizit'
                    continue

                if info['status'] != 'downloading':
                    file_info['fronta'] = 'snizit'
                    continue

                if file_info['completed'] == file_info['size']:
                    file_info['fronta'] = 'snizit'
                    continue

                file_info['fronta'] = 'preskoceno_snizit'

def pridani_do_fronty_snizit():
    """
    Přidání souborů do fronty pro snížení priority.
    """
    for tr_id, info in torrents_info.items():
        for file_info in info['soubory'].values():
            if file_info['fronta'] == 'snizit':
                fronta_snizit.append((tr_id, file_info['name']))

def logika_zvyseni_priority():
    """
    Logika pro zvýšení priority souborů v torrentech.
    """
    for tr_id, info in torrents_info.items():
        if info['progress'] == 100.0:
            continue

        soubory_ke_zpracovani = [file for file in info['soubory'].values() 
                                 if file['fronta'] == 'preskoceno_snizit' 
                                 and file['completed'] / file['size'] < 1]
        if soubory_ke_zpracovani:
            nejvetsi_pomer_stazeni_soubor = max(soubory_ke_zpracovani, 
                                                key=lambda file: file['completed'] / file['size'])
            nejvetsi_pomer_stazeni_soubor['fronta'] = 'zvysit'

def pridani_do_fronty_zvysit():
    """
    Přidání souborů do fronty pro zvýšení priority.
    """
    for tr_id, info in torrents_info.items():
        for file_info in info['soubory'].values():
            if file_info['fronta'] == 'zvysit':
                fronta_zvysit.append((tr_id, file_info['name']))

# Volání funkcí
logika_snizeni_priority()
pridani_do_fronty_snizit()
logika_zvyseni_priority()
pridani_do_fronty_zvysit()

# Výpis informací o torrentech
vypsat_torrent_info()

# Výpis front
print("Fronta snížit prioritu:")
for tr_id, fname in fronta_snizit:
    print(f"  Torrent ID: {tr_id}, Soubor: {fname}")

print("\nFronta zvýšit prioritu:")
for tr_id, fname in fronta_zvysit:
    print(f"  Torrent ID: {tr_id}, Soubor: {fname}")
