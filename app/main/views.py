import json
from flask import (abort, jsonify, g, session, render_template, redirect,
                   request, url_for)
from manage import app, client, bucket, bcolors
from . import main
from datetime import datetime
import sys
from boto.s3.key import Key
from .helper import names, authentication
from .neural_net import sample
import uuid
import time
import random
from subprocess import Popen, PIPE
from random import randint
from google.oauth2 import id_token
from google.auth.transport import requests


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
        resp = jsonify({'error': 'the API is not in debug mode, hence it will not test the database'})
        resp.status_code = 404
        return resp

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
        resp = jsonify({'error': 'unable to parse the sent data OR you are not passing values for the keys "genre" and "tempo"'})
        resp.status_code = 400
        return resp
    
    duration_dict = {
        'short': 90,
        'medium': 180,
        'long': 300
    }
    
    try:
        duration = duration_dict[data['duration'].lower()] + (randint(0,20)-10)
    except KeyError:
        resp = jsonify({'error': 'you are not passing values for the key "duration"'})
        resp.status_code = 400
        return resp
    
    valid_genres = ['game', 'jazz', 'classical', 'folk']
    
    if(not(data['genre'] in valid_genres)):
        resp = jsonify({'error': 'Invalid genre passed, valid genres are "game", "jazz", "classical", and "folk"'})
        resp.status_code = 400
        return resp

    instrument_dict = {
                'game': [76, 72, 75],
                'classical': [48, 42, 46],
                'folk': [24, 25, 27],
                'jazz': [26, 34, 36]
            }

    tempo_dict = {
            'slow': random.randint(0,2),
            'medium': random.randint(3, 5),
            'normal': random.randint(3,5),
            'fast': random.randint(6,8)
        }

    genre_dict = {
            'game': 'game',
            'classical': 'classical',
            'folk': 'folk',
            'jazz': 'jazz'
        }

    pitch = 0
    if(data['genre'] == 'jazz'):
        pitch = -30

    pitch_dict = {
            'game':(-10, 14),
            'classical':(-10,20),
            'folk':(-10, 20),
            'jazz':(-30, -15)
        }

    drums = False

    gen_params = {
        'data_dir': './app/main/neural_net/data/' + data['genre'],
        'experiment_dir': './app/main/neural_net/experiments/' + genre_dict[data['genre']],
        'file_length': duration, 
        'midi_instrument': random.choice(instrument_dict[data['genre']]),
        'num_files': 1,
        'prime_file': None,
        'save_dir': None,
        'tempo': tempo_dict[data['tempo']],
        'pitch': random.randint(pitch_dict[data['genre']][0],pitch_dict[data['genre']][1]),
        'drum': drums
    }

    begin = time.time()
    generated_file = sample.main(gen_params)
    print('done generating\ngenerated: ' + str(generated_file) + bcolors.ENDC)
    print('time elapsed: ' + str(time.time() - begin))
    if(generated_file):
        db = client.music_gen

        file_id = str(uuid.uuid4())
        
        file_prefix = './app/main/music/' + file_id
        outfile = sample.midi_to_mp3(generated_file, file_prefix)
        print(outfile)
        # check to make sure file has been converted

        file_name = 'music/' + file_id + '.mp3'

        key = bucket.new_key(file_name)
        key.set_contents_from_filename(outfile)
        key.set_canned_acl('public-read')
        file_url = key.generate_url(0, query_auth=False, force_http=True)
        
        new_file = './app/main/g_midis/{0}.mid'.format(file_id)

        # remove file
        cp_string = 'cp {0} {1}'.format(generated_file, new_file)
        rm_string = 'rm {0}; rm {1}; rm {2}'.format(file_prefix + '.mp3', file_prefix + '.wav', generated_file)
        
        Popen(cp_string, stdout=PIPE, stderr=PIPE, shell=True).wait()
        Popen(rm_string, stdout=PIPE, stderr=PIPE, shell=True).wait()
        
        print('MIDI PATH: ' + new_file)

        response_obj = {
            'timestamp': datetime.utcnow(),
            'location': file_url,
            'sheet_location': None,
            'song_id': file_id,
            'genre': data['genre'],
            'tempo': data['tempo'],
            'duration': data['duration'],
            'song_name': names.generate_name(data['genre'], data['tempo']),
            'midi_path': new_file
        }

        resp = jsonify(response_obj)
        resp.status_code = 200

        
        if('profileID' in data.keys() and 'profileEmail' in data.keys()):
            
            verified_id = authentication.verify(data['profileID'])
            profile_email = str(data['profileEmail']).lower()
            if(verified_id):
                db.users.update({'$and': [{'profileID': verified_id}, {'profileEmail': profile_email}]},
                        {'$set': {'profileID': verified_id, 'profileEmail': profile_email}}, upsert=True)
                try:
                    user_obj = db.users.find_one({'$and': [{'profileID': verified_id}, {'profileEmail': profile_email}]})
                    
                    current_songs = user_obj['songs']
                    current_songs.append(response_obj)
                except Exception as e:
                    current_songs = [response_obj]
                db.users.update({'$and': [{'profileID': verified_id}, {'profileEmail': profile_email}]},
                        {'$set': {'songs': current_songs}}, upsert=True)
         
        db.songs.insert(response_obj)
    else:
        response_obj = {
            'timestamp': datetime.utcnow(),
            'location': None,
            'song_id': file_id,
            'sheet_location': None,
            'genre': data['genre'],
            'tempo': data['tempo'],
            'duration': data['duration'],
            'midi_path': new_file,
            'song_name': names.generate_name(data['genre'], data['tempo'])
        }

        resp = jsonify(response_obj)
        resp.status_code = 200

    return resp

@main.route('/sheet_music', methods=['POST'])
def sheet_music():
    db = client.music_gen

    try:
        data = json.loads(request.data.decode('utf-8'))
        song_id = data['songID']

    except Exception as e:
        resp = jsonify({'error': 'unable to parse data sent OR the key "songID" was not included in the request'})
        resp.status_code = 400
        return resp

    
    song_obj = db.songs.find_one({'song_id': song_id})
    
    if('sheet_location' in song_obj.keys() and song_obj['sheet_location']):
        print('sheet music cached')
        return jsonify({'sheet_location': song_obj['sheet_location']})

    gen_str = 'mkdir ./app/main/sheets/{0}; mono sheet.exe {1} ./app/main/sheets/{0}/{0}'.format(song_obj['song_id'],
            song_obj['midi_path'])
    Popen(gen_str, stdout=PIPE, stderr=PIPE, shell=True).wait()

    zip_str = 'mv ./app/main/sheets/{0} ./; zip -r ./app/main/sheets/{0} ./{0}'.format(song_obj['song_id'])
    Popen(zip_str, stdout=PIPE, stderr=PIPE, shell=True).wait()

    sheet_path = './app/main/sheets/{0}.zip'.format(song_id)

    key = bucket.new_key('sheet_music/' + song_id + '.zip')
    key.set_contents_from_filename(sheet_path)
    key.set_canned_acl('public-read')
    file_url = key.generate_url(0, query_auth=False, force_http=True)

    db.songs.update({'song_id': song_id}, {'$set': {'sheet_location': file_url}})

    rm_str = 'rm -rf ./app/main/g_midis/{0}.mid ./app/main/sheets/{0}.zip ./{0}'.format(song_obj['song_id'])
    Popen(rm_str, stdout=PIPE, stderr=PIPE, shell=True)

   
    print(song_obj)
    
    return jsonify({'sheet_location': file_url})

@main.route('/history', methods=['POST'])
def history():
    db = client.music_gen
    
    try:
        data = json.loads(request.data.decode('utf-8'))
        profile_id = data['profileID']
        profile_email= data['profileEmail'].lower()
    except:
        resp = jsonify({'error': 'unable to parse the request body OR the keys "profileID" and "profileEmail" weren\'t passed in the request body'})
        resp.status_code = 400
        return resp

    profile_id = authentication.verify(profile_id)
    
    if(not(profile_id)):
        resp = jsonify({'error': 'invalid profileID token and profileEmail pair. Perhaps you\'re not passing the profileID token and just the profileID?'})
        resp.status_code = 404
        return resp

    found_user = db.users.find_one({'$and': [{'profileEmail': profile_email}, {'profileID': profile_id}]})

    if(not(found_user)):
        songs = []
    else:
        songs = found_user['songs']
    return jsonify({'history': songs})

@main.route('/edit_song', methods=['POST'])
def edit_song():
    db = client.music_gen

    try:
        data = json.loads(request.data.decode('utf-8'))
        profile_id = data['profileID']
        profile_email= data['profileEmail'].lower()
    except:
        resp = jsonify({'error': 'unable to parse the request body OR the keys "profileID" and "profileEmail" weren\'t passed in the request body'})
        resp.status_code = 400
        return resp

    profile_id = authentication.verify(profile_id)
    
    if(not(profile_id)):
        resp = jsonify({'error': 'invalid profileID token and profileEmail pair. Perhaps you\'re not passing the profileID token and just the profileID?'})
        resp.status_code = 404
        return resp



    found_user = db.users.find_one({'$and': [{'profileEmail': profile_email}, {'profileID': profile_id}]})

    if(not(found_user)):
        songs = []
    else:
        songs = found_user['songs']

    try:
        song_id = data['songID']
        new_name = str(data['newName'])
    except:
        resp = jsonify({'error': 'the key songID OR newName was not passed in the request body'})
        resp.status_code = 400
        return resp

    for i in range(len(songs)):
        if(song_id == songs[i]['song_id']):
            songs[i]['song_name'] = new_name
            break

    db.users.update({'$and': [{'profileID': profile_id}, {'profileEmail': profile_email}]},
                        {'$set': {'songs': songs}}, upsert=True)
    
    return jsonify({'status': 'song name updated'})

@main.route('/remove_song', methods=['POST'])
def remove_song():
    db = client.music_gen

    try:
        data = json.loads(request.data.decode('utf-8'))
        profile_id = data['profileID']
        profile_email= data['profileEmail'].lower()
    except:
        resp = jsonify({'error': 'unable to parse the request body OR the keys "profileID" and "profileEmail" weren\'t passed in the request body'})
        resp.status_code = 400
        return resp

    profile_id = authentication.verify(profile_id)
    
    if(not(profile_id)):
        resp = jsonify({'error': 'invalid profileID token and profileEmail pair. Perhaps you\'re not passing the profileID token and just the profileID?'})
        resp.status_code = 404
        return resp
    
    found_user = db.users.find_one({'$and': [{'profileEmail': profile_email}, {'profileID': profile_id}]})

    if(not(found_user)):
        songs = []
    else:
        songs = found_user['songs']

    try:
        song_id = data['songID']
    except:
        resp = jsonify({'error': 'the key "songID" was not passed in the request body'})
        resp.status_code = 400
        return resp

    for i in range(len(songs)):
        if(song_id == songs[i]['song_id']):
            del(songs[i])
            break

    db.users.update({'$and': [{'profileID': profile_id}, {'profileEmail': profile_email}]},
                        {'$set': {'songs': songs}}, upsert=True)

    return jsonify({'status': 'song removed'})
