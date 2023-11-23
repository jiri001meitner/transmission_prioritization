#!/bin/bash
# vytvoření přihlašovacích údajů
GIT_DIR="$(dirname "$(realpath "$0")")"
pip_install()
{
if ! command -v pip; then
python3 -m pip install --upgrade pip setuptools wheel
pip install transmissionrpc
fi
}
pip_install
cd "${GIT_DIR}"||exit 1
git pull
genpass()
{
paste <(curl -sk 'https://raw.githubusercontent.com/titoBouzout/Dictionaries/master/English%20(American).dic'|shuf|head -n1|cut -f1 -d/) \
      <(seq 001 999|shuf|head -n1) \
      <(curl -sk 'https://raw.githubusercontent.com/titoBouzout/Dictionaries/master/English%20(American).dic'|shuf|head -n1|cut -f1 -d/) -d_
}
PASSWD="$(genpass)"
if ! [[ -f ~/.config/transmission/pass.json ]]; then
mkdir -p ~/.config/transmission
read -erp 'zadej přihlašovací jméno pro uživatele transmission: ' -i "${USER}" uzivatel
read -erp 'zadej přihlašovací heslo nebo použij nabídnuté (nezapoomeň ho v transmission nastavit): ' -i "${PASSWD}" heslo
cat <<"EOF"|sed "s@USER@${uzivatel}@"|sed "s@PASSWORD@${heslo}@">~/.config/transmission/pass.json
{
"username": "USER",
"password": "PASSWORD"
}
EOF
chmod 0600 ~/.config/transmission/pass.json
fi
read -erp "Pokračuj jen když máš povolenou vzdálenou správu na adrese 127.0.0.1 a portu 9091 s autentizaci prostřednictvím jména ${uzivatel} a hesla ${PASSWORD} " -i "Y" continue
transmission_session_id()
{
base64_auth="$(echo -n "${uzivatel}:${heslo}"|base64)"
base64_auth="authorization: Basic ${base64_auth}"
curl -sI --request POST --header "${base64_auth}" http://127.0.0.1:9091/transmission/rpc|grep 'X-Transmission-Session-Id'|awk '{print $2}'
}
if transmission_session_id=$(transmission_session_id); then transmission_session_id="X-Transmission-Session-Id: ${transmission_session_id}"; else
echo "kecáš, nepodařilo se získat X-Transmission-Session-Id"; exit 1
fi

# vytvoření seznamu nechtěných souborů
if ! [[ -f ~/.config/transmission/unwanted.json ]]; then
cat <<'EOF'>~/.config/transmission/unwanted.json
{
"unwanted":
[
".txt",
".nfo",
".exe"
]
}
EOF
fi

# nainstaluje magnet pro uživatele
cat <<"EOF"|sed "s@HOME@${HOME}@">"${HOME}/.local/share/applications/magnet.desktop"
#!/usr/bin/env xdg-open
[Desktop Entry]
Name=Magnet
Exec=HOME/bin/magnet %U
Terminal=false
Type=Application
MimeType=x-scheme-handler/magnet;
Icon=transmission
Categories=Network;FileTransfer;P2P;
EOF
chmod 0700 "${HOME}/.local/share/applications/magnet.desktop"

# vytváření symlinků
mkdir ~/bin -p
transmission_add_magnet="$(realpath ./transmission_add_magnet.py)"
transmission_prioritizace="$(realpath ./transmission_prioritizace_simple.py)"
magnet="$(realpath ./magnet)"
blocklist="$(realpath ./transmission_blocklist.py)"

ln -svTf "${transmission_add_magnet}" ~/bin/transmission_add_magnet.py
ln -svTf "${transmission_prioritizace}" ~/bin/transmission_prioritizace.py
ln -svTf "${magnet}" ~/bin/magnet
ln -svTf "${blocklist}" ~/bin/transmission_blocklist.py

~/bin/transmission_blocklist.py
# install cronjob
add_cronjob()
{
paste <(printf '*/1 * * * *') <(realpath ~/bin/transmission_prioritizace.py) -d' '
paste <(printf '5 1 * * *') <(realpath ~/bin/transmission_blocklist.py) -d ' '
}
if ! crontab -l|grep -q 'transmission_prioritizace.py\|transmission_blocklist.py'; then
   (crontab -l 2>/dev/null; add_cronjob) | crontab -
   "echo blocklist installed"; else echo "blocklist already installed"
fi

exit
