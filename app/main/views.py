import json
from flask import (abort, jsonify, g, session, render_template, redirect,
                   request, url_for)
from manage import app, client
from . import main
from datetime import datetime
import random

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

    genre_nouns = {
        'classical': ['strings', 'zeitgest', 'orchestra', 'duets', 'singularities'],
        'hip hop': ['streets', 'corners', 'paradise', 'beef', 'punch', 'rut'],
        'jazz': ['ska', 'boo bop', 'bing bang', 'ska da doo da da', 'zimbibby doo wa'],
        'rock': ['trouble', 'yesterday', 'human', 'dancer', 'prize fighter', 'love'],
        'pop': ['nights', 'days', 'forever', 'life', 'youth', 'midnight', 'halo']
    }

    tempo_adjectives = {
        'fast': ['Boltin\'', 'Zoomin\'', 'Rushing', 'Quick', 'Fast', 'Snapping'
                 'Crackin\'', 'Zippy', 'Quick little', 'Chasing'],
        'medium': ['Just a normal', 'Another day in the', 'Red', 'Living', 'Big'],
        'slow': ['Dragging', 'Waltzing', 'Scraping', 'Holding back',
                 'Waiting for', 'Wandering']
    }

    response_obj = {
        'timestamp': datetime.utcnow(),
        'location': 'http://www.hochmuth.com/mp3/Haydn_Cello_Concerto_D-1.mp3'
    }

    adjective = random.choice(tempo_adjectives[data['tempo']])
    noun = random.choice(genre_nouns[data['genre']])

    response_obj['song_name'] = adjective + ' ' + noun

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
    response_obj = {
        'response': 'endpoint for getting a link to download a song (wip)'
    }

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
