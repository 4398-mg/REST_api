import random


def generate_name(genre, tempo):
    genre_nouns = {
        'classical': ['strings', 'zeitgest', 'orchestra', 'duets', 'singularities'],
        'folk': ['hills', 'meadows', 'paradise', 'fields', 'valley', 'basin'],
        'jazz': ['ska', 'boo bop', 'bing bang', 'ska da doo da da', 'zimbibby doo wa'],
        'rock': ['trouble', 'yesterday', 'human', 'dancer', 'prize fighter', 'love'],
        'game': ['nights', 'days', 'forever', 'life', 'youth', 'midnight', 'halo']
    }

    tempo_adjectives = {
        'fast': ['Boltin\'', 'Zoomin\'', 'Rushing', 'Quick', 'Fast', 'Snapping'
                 'Crackin\'', 'Zippy', 'Quick little', 'Chasing'],
        'medium': ['Just a normal', 'Another day in the', 'Red', 'Living', 'Big'],
        'slow': ['Dragging', 'Waltzing', 'Scraping', 'Holding back',
                 'Waiting for', 'Wandering']
    }

    return random.choice(tempo_adjectives[tempo]) + ' ' + random.choice(genre_nouns[genre])
