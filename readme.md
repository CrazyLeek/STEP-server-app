# Useful commands

- Activate the virtual env (to enable flask): `pyenv activate website`
- Run the server: `FLASK_RUN_PORT=8003 nohup flask run &` (bad, we need to use a production server)
- Check if everything is fine after launching the server: `cat nohup.out`
- Kill the server: `sudo fuser -k 8003/tcp`

# Routes for https://step.tcdrail.com/

## Web pages
- GPS Recorder: `/apps/gps_recorder`

## End points
- api/journey_data
    - GET (password needed)
    - POST