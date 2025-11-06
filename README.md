# 3D-PAWS Data Processing Tools
Algorithms or useful tidbits to help process 3D-PAWS data.<br>
Each folder contains a separate software suite to perform standard data processing procedures.<br>

## Active-Stations 
The `active-stations.py` script finds instruments on a CHORDS portal which have transmitted data in the last year. 
It works with an SSH tunnel, and consequently is only accessible to those whose public keys are registered with the CHORDS server.
1. Tunnel into the server `ssh -L 8086:localhost:8086 ubuntu@chords.portal.url`
2. Run the `active-stations.py` script locally using the INFLUX_USERNAME and INFLUX_PASSWORD credentials for that server (see CHORDS_ADMIN_PW). Configured for CLI execution: `python3 active-stations.py <path/to/download/files> <chords portal name>`
