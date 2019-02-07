from flask import (abort, jsonify, g, session, render_template, redirect,
                   request, url_for)
from manage import app, client
from . import main
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
    response_obj = {
        'response': 'endpoint for song generation (wip)'
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
