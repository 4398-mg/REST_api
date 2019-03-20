import json
from flask import (abort, jsonify, g, session, render_template, redirect,
                   request, url_for)
from manage import app, client, bucket, bcolors
from . import main
from datetime import datetime
import sys
from boto.s3.key import Key
from .helper import names
from .neural_net import sample
import uuid


# import self written modules from modules dir
# from ..modules import ...


@main.route('/', methods=['GET', 'POST'])
def home():

    response_obj = {
        'endpoints': {
            '/help': '[GET, POST] help endpoint (general usage info)',
            '/generate_song': '[POST] generate song based on parameters',
            '/generate_song/help': '[GET, POST] help endpoint for song gen',
            '/get_song': '[POST] returns a link to download a song',
            '/get_song/help': '[GET, POST] help endpoint for song gen'
        }
    }

    resp = jsonify(response_obj)
    resp.status_code = 200

    return resp


@main.route('/test_db', methods=['GET', 'POST'])
def test_db():
    db = client.music_gen

    if(not(app.config['DEBUG'])):
        abort(404)

    resp = {}
    try:
        db.test_coll.insert({'test': 'test'})
        db.test_coll.remove({}, multi=True)
        resp = {'status': 'connected and accessed database successfully'}
    except Exception as e:
        print(app.config)
        resp = {
            'config': app.config['DB_USER'],
            'status': 'unable to connect to and access db',
            'error_text': str(e)
        }

    return jsonify(resp)


@main.route('/echo', methods=['POST'])
def echo():

    print(request)
    print(dir(request))
    print(request.data)
    try:
        print(request.json)
        print(request.values)
    except Exception as e:
        print(e)
    try:
        data = json.loads(request.data.decode('utf-8'))
    except:
        data = {}
    return jsonify(data)


@main.route('/help', methods=['GET', 'POST'])
def help():
    response_obj = {
        'response': 'all things help related (wip)'
    }

    resp = jsonify(response_obj)
    resp.status_code = 200

    return resp


@main.route('/generate_song', methods=['POST'])
def generate_song():
    try:
        data = json.loads(request.data.decode('utf-8'))
        data['genre'] = data['genre'].lower()
        data['tempo'] = data['tempo'].lower()
    except:
        abort(400)

    print(bcolors.OKBLUE + 'generating_song')
    gen_params = {
        'data_dir': './app/main/neural_net/data/blues',
        'experiment_dir': './app/main/neural_net/experiments/blues',
        'file_length': 1200,
        'midi_instrument': 'Acoustic Grand Piano',
        'midi_instrument_1': 'Acoustic Grand Piano',
        'midi_instrument_2': 'Acoustic Grand Piano',
        'midi_instrument_3': 'Acoustic Grand Piano',
        'midi_instrument_4': 'Acoustic Grand Piano',
        'num_files': 1,
        'prime_file': None,
        'save_dir': None
    }

    generated_file = sample.main(gen_params)
    print('done generating\ngenerated: ' + str(generated_file) + bcolors.ENDC)
    if(generated_file):
        db = client.music_gen

        file_id = str(uuid.uuid4())
        mp3_file = './app/main/music/' + file_id + '.mp3'
        outfile = sample.midi_to_mp3(generated_file, mp3_file)

        # check to make sure file has been converted

        file_name = 'music/' + file_id + '.mp3'

        key = bucket.new_key(file_name)
        key.set_contents_from_filename(outfile)
        key.set_canned_acl('public-read')
        file_url = key.generate_url(0, query_auth=False, force_http=True)

        # remove file

        response_obj = {
            'timestamp': datetime.utcnow(),
            'location': 'http://www.hochmuth.com/mp3/Haydn_Cello_Concerto_D-1.mp3',
            'song_id': file_id,
            'genre': data['genre'],
            'tempo': data['tempo'],
            'duration': data['duration'],
            'song_name': names.generate_name(data['genre'], data['tempo'])
        }
        resp = jsonify(response_obj)
        resp.status_code = 200

        db.songs.insert(response_obj)
    else:
        response_obj = {
            'timestamp': datetime.utcnow(),
            'location': None,
            'song_id': file_id,
            'genre': data['genre'],
            'tempo': data['tempo'],
            'duration': data['duration'],
            'song_name': names.generate_name(data['genre'], data['tempo'])
        }

        resp = jsonify(response_obj)
        resp.status_code = 200

    return resp


@main.route('/generate_song/help', methods=['GET', 'POST'])
def generate_song_help():
    response_obj = {
        'response': 'all things help related for song generation (wip)'
    }

    resp = jsonify(response_obj)
    resp.status_code = 200

    return resp


@main.route('/get_song', methods=['POST'])
def get_song():

    try:
        data = json.loads(request.data.decode('utf-8'))
        song_id = data['song_id']
    except:
        abort(400)

    db = client.music_gen

    response_obj = db.songs.find_one({'song_id': song_id}, {'_id': False})

    resp = jsonify(response_obj)
    resp.status_code = 200

    return resp


@main.route('/get_song/help', methods=['GET', 'POST'])
def get_song_help():

    response_obj = {
        'response': 'help for getting a song download link'
    }

    resp = jsonify(response_obj)
    resp.status_code = 200

    return resp
