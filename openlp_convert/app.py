import os
import sys
import traceback
from pathlib import Path
import urllib.parse
import json

import requests
import dropbox
import logging
import tomllib
from datetime import timedelta
from flask import Flask, session, redirect, render_template, request, url_for, current_app, send_from_directory
from flask_session import Session


app = Flask(__name__)
app.config.from_file("config.toml", load=tomllib.load, text=False)
app.config.from_prefixed_env()
app.logger.setLevel(logging.INFO)
Session(app)
app.permanent_session_lifetime = timedelta(hours=4)


@app.route('/openlp-convert/convert', methods=['GET'])
def index():
    session.permanent = True
    return render_template('convert.html')


@app.route('/openlp-convert/convert', methods=['POST'])
def convert():
    # save form to static dir
    notes_path = os.path.join(current_app.root_path, app.config['NOTES_DIR'])
    Path(notes_path).mkdir(parents=True, exist_ok=True)

    service_name = request.form['name']

    # debug, would do actual conversion here
    converted_notes = request.form['notes']

    # write file to local dir for download link
    with open(os.path.join(notes_path, f'{service_name}.xml'), 'w') as fh:
        fh.write(request.form['notes'])

    dropbox_status = 'NOT_SENT'

    if request.form.get('isUploadToDropBox') == 'on':
        dropbox_status = 'FAILURE'  # assume failure
        if 'access_token' in session:
            app.logger.info('uploading to dropbox')
            dbx = dropbox.Dropbox(session['access_token'])
            dbx.files_upload(bytes(converted_notes, 'UTF-8'), f'/{service_name}.xml', mode=dropbox.files.WriteMode("overwrite"))
            dropbox_status = 'SUCCESS'

        else:
            app.logger.info('no access token in session; minting new one')
            try:
                # create url to authorize with dropbox
                url = f"{app.config['DROPBOX']['AUTHORIZE_URI']}?" + urllib.parse.urlencode({
                    'client_id': app.config['DROPBOX']['APP_KEY'],
                    'redirect_uri': url_for('dropbox_ouath_callback', _external=True),
                    'response_type': 'code',
                    'token_access_type': 'online'
                })
                session['name'] = request.form['name']
                return redirect(url)

            except Exception:
                app.logger.exception('Unable to upload notes to dropbox')
                traceback.print_exc(file=sys.stdout)

    return render_template('convert-status.html',
        name=request.form['name'],
        dropbox_status=dropbox_status
    )


@app.route('/openlp-convert/download_notes', methods=['GET'])
def download_notes():
    notes_path = os.path.join(current_app.root_path, app.config['NOTES_DIR'])

    return send_from_directory(notes_path, f"{request.args.get('name')}.xml", as_attachment=True)


@app.route('/openlp-convert/dropbox-oauth-callback', methods=['GET'])
def dropbox_ouath_callback():
    app.logger.info('received dropbox callback with auth code')
    authorization_code = request.args['code']
    data = {
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'client_id': app.config['DROPBOX']['APP_KEY'],
        'client_secret': app.config['DROPBOX']['APP_SECRET'],
        'redirect_uri': url_for('dropbox_ouath_callback', _external=True),
    }
    
    app.logger.info('using auth code to get access token')

    try:
        resp = requests.post(app.config['DROPBOX']['TOKEN_URI'], data=data)
        resp.raise_for_status()
        access_token = resp.json()['access_token']
        session['access_token'] = access_token
        service_name = session['name']

        app.logger.info('reading in notes file content')
        notes_path = os.path.join(current_app.root_path, app.config['NOTES_DIR'])
        with open(os.path.join(notes_path, f'{service_name}.xml')) as fh:
            converted_notes = fh.read()
        
        dropbox_status = 'FAILURE'

        app.logger.info('uploading to dropbox')
        dbx = dropbox.Dropbox(access_token)
        dbx.files_upload(bytes(converted_notes, 'UTF-8'), f'/{service_name}.xml', mode=dropbox.files.WriteMode("overwrite"))
        dropbox_status = 'SUCCESS'

    except Exception:
        app.logger.error('Unable to upload notes to dropbox')
        traceback.print_exc(file=sys.stdout)

    app.logger.info('rendering template')

    return render_template('convert-status.html',
        name=service_name,
        dropbox_status=dropbox_status
    )
