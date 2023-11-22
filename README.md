# transmission_prioritization
adjusting priorities for transmission via python and transmissionrpc

## prerekvizity:
* nainstalované transmission
* povolená vzdálená správa na localhostu
* ověření jménem a heslem
* soubor s credentials pro transmission v umístění: /.config/transmission/pass.json
* soubor s příponami nechtěných souborů ~/.config/transmission/unwanted.json


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
