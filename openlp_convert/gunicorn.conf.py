from pathlib import Path


# basic gunicorn config
bind = '0.0.0.0:8000'
timeout = '120'
loglevel = 'info'
workers = 2

# set certfile if file exists
certfile_path = 'fullchain.pem'
keyfile_path = 'privkey.pem'
if (Path(certfile_path).is_file() and Path(keyfile_path).is_file()):
    certfile = certfile_path
    keyfile = keyfile_path

