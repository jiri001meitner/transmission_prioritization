# transmission_prioritization
adjusting priorities for transmission via python and transmissionrpc

## prerekvizity:
* nainstalované transmission
* povolená vzdálená správa na localhostu
* ověření jménem a heslem
* soubor s credentials pro transmission v umístění: /.config/transmission/pass.json
* soubor s příponami nechtěných souborů ~/.config/transmission/unwanted.json

## zatím funguje jen transmission_prioritizace_simple.py
Zatím funguje jen transmission_prioritizace_simple.py

### formát souboru ~/.config/transmission/pass.json
	{
	"username": "username",
	"password": "changeme"
	}	

### formát souboru ~/.config/transmission/unwanted.json
	{
	"unwanted":
	[
	".txt",
	".nfo",
	".exe"
	]
	}

### Největší užitek přináší použití v crontabu
	*/1 * * * * ${HOME}/github/transmission_prioritization/transmission_prioritizace_simple.py

