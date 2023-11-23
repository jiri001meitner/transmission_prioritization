#!/usr/bin/env python3
"""
Stahuje blocklist
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

try:
    tc = transmissionrpc.Client('localhost', port=9091, user=username, password=password)

    # Get current blocklist
    current_blocklist = tc.get_session().blocklist_size

    print(f"Current blocklist size: {current_blocklist}")

    # Enable blocklist
    tc.set_session(blocklist_enabled=True)

    # Set blocklist_url
    tc.set_session(blocklist_url="https://vps.meitner.cz/blocklist.gz")

    # Force blocklist update
    tc.blocklist_update()

    print("Blocklist updated...")

    # Get updated blocklist
    updated_blocklist = tc.get_session().blocklist_size

    print(f"Updated blocklist size: {updated_blocklist}")

except Exception as e:
    print("Nastala chyba: ", e)
