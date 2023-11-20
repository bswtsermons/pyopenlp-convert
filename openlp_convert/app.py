import sys
import traceback
import urllib.parse

import requests
import dropbox
import logging
import tomllib
from datetime import timedelta
from flask import Flask, Response, session, redirect, render_template, request, url_for
from flask_session import Session
from openlyrics import tostring

from convert import notes_to_song


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
    # get request data
    service_name = request.form['name']
    minister = request.form['minister']
    notes = request.form['notes']
    isUploadToDropBox = request.form.get('isUploadToDropBox')

    # magic happens here
    converted_notes = tostring(notes_to_song(service_name, minister, notes))

    # write converted service to session
    session['name'] = service_name
    session[f'notes_{service_name}'] = converted_notes

    dropbox_status = 'NOT_SENT'  # default status is to do nothing

    if isUploadToDropBox == 'on':
        dropbox_status = 'FAILURE'  # assume failure
        if 'access_token' in session:
            app.logger.info('uploading to dropbox')
            dbx = dropbox.Dropbox(session['access_token'])
            dbx.files_upload(
                bytes(converted_notes, 'UTF-8'),
                f'/{service_name}.xml',
                mode=dropbox.files.WriteMode("overwrite")
            )
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
                return redirect(url)

            except Exception:
                app.logger.exception('Unable to upload notes to dropbox')
                traceback.print_exc(file=sys.stdout)

    return render_template(
        'convert-status.html',
        name=service_name,
        dropbox_status=dropbox_status
    )


@app.route('/openlp-convert/download_notes', methods=['GET'])
def download_notes():
    # pull service name and converted notes from session
    service_name = session['name']
    converted_notes = session[f'notes_{service_name}']
    app.logger.info(f'downloading notes for {service_name}')

    return Response(
        converted_notes,
        mimetype='text/xml',
        headers={'Content-disposition': f'attachment; filename={service_name}.xml'}
    )


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

    try:
        app.logger.info('using auth code to get access token')
        resp = requests.post(app.config['DROPBOX']['TOKEN_URI'], data=data)
        resp.raise_for_status()

        access_token = resp.json()['access_token']
        session['access_token'] = access_token
        service_name = session['name']

        # pull notes from session
        converted_notes = session[f'notes_{service_name}']

        dropbox_status = 'FAILURE'  # assume failure

        app.logger.info('uploading to dropbox')
        dbx = dropbox.Dropbox(access_token)
        dbx.files_upload(
            f=bytes(converted_notes, 'UTF-8'),
            path=f'/{service_name}.xml',
            mode=dropbox.files.WriteMode("overwrite")
        )
        dropbox_status = 'SUCCESS'

    except Exception:
        app.logger.error('Unable to upload notes to dropbox')
        traceback.print_exc(file=sys.stdout)

    app.logger.info('rendering template')

    return render_template(
        'convert-status.html',
        name=service_name,
        dropbox_status=dropbox_status
    )
