#!/usr/bin/env python
import argparse, os, pdb, random, sys
import pretty_midi
from subprocess import Popen, PIPE
import time

try:
    import train
except ImportError:
    from . import train

try:
    import utils
except:
    from . import utils

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--experiment_dir', type=str,
                        default='experiments/default',
                        help='directory to load saved model from. ' \
                             'If omitted, it will use the most recent directory from ' \
                             'experiments/.')
    parser.add_argument('--save_dir', type=str,
         help='directory to save generated files to. Directory will be ' \
         'created if it doesn\'t already exist. If not specified, ' \
         'files will be saved to generated/ inside --experiment_dir.')
    parser.add_argument('--midi_instrument', default='Bright Acoustic Piano',
                        help='MIDI instrument name (or number) to use for the ' \
                        'generated files. See https://www.midi.org/specifications/item/'\
                        'gm-level-1-sound-set for a full list of instrument names.')
    parser.add_argument(
        '--num_files',
        type=int,
        default=1,
        help='number of midi files to sample.')
    parser.add_argument(
        '--file_length',
        type=int,
        default= 300,
        help='Length of each file, measured in 16th notes.')
    parser.add_argument('--prime_file', type=str,
                        help='prime generated files from midi file. If not specified ' \
                        'random windows from the validation dataset will be used for ' \
                        'for seeding.')
    parser.add_argument('--data_dir', type=str, default='data/midi',
                        help='data directory containing .mid files to use for' \
                             'seeding/priming. Required if --prime_file is not specified')
    parser.add_argument(
        '--tempo',
        type=int,
        default=3,
        help='set tempo 0 is slowest and 5 is highest.')
    parser.add_argument(
        '--pitch',
        type=int,
        default=0,
        help='adjust pitch with negative or positive integer')
    parser.add_argument('--drum', type=str,
                        default='False',
                        help='input True to enable the drums. Else keep it False')
    return parser.parse_args()


def get_experiment_dir(experiment_dir):

    if experiment_dir == 'experiments/default':
        dirs_ = [os.path.join('experiments', d) for d in os.listdir('experiments') \
                 if os.path.isdir(os.path.join('experiments', d))]
        experiment_dir = max(dirs_, key=os.path.getmtime)

    if not os.path.exists(os.path.join(experiment_dir, 'model.json')):
        utils.log('Error: {} does not exist. ' \
               'Are you sure that {} is a valid experiment?' \
               'Exiting.'.format(os.path.join(args.experiment_dir), 'model.json',
                                 experiment_dir), True)
        exit(1)

    return experiment_dir


def midi_to_mp3(path, output):
    # using the default sound font in 44100 Hz sample rate

    begin = time.time()
    print('timidity convert')
    Popen(
        'timidity {0} -Ow -o {1}'.format(path, output + '.wav',
                                         output + '.mp3'),
        shell=True,
        stdout=PIPE,
        stderr=PIPE).wait()
    print('time elapsed: ' + str(time.time() - begin))

    begin = time.time()
    print('convert')
    convert_str = 'lame -V3 {1} {2}'.format(path, output + '.wav',
                                            output + '.mp3')
    print(convert_str)
    Popen(convert_str, shell=True).wait()
    print('time elapsed: ' + str(time.time() - begin))

    return output + '.mp3'


def main(args=None):
    if (not (args)):
        args = parse_args()
    else:
        args = argparse.Namespace(**args)
    args.verbose = True
    
    # prime file validation
    if args.prime_file and not os.path.exists(args.prime_file):
        utils.log(
            'Error: prime file {} does not exist. Exiting.'.format(
                args.prime_file), True)
        return None
    else:
        if not os.path.isdir(args.data_dir):
            utils.log(
                'Error: data dir {} does not exist. Exiting.'.format(
                    args.prime_file), True)
            return None

    #f = random.choice(os.listdir(args.data_dir))
    midi_files = [ args.prime_file ] if args.prime_file else \
                 [ os.path.join(args.data_dir, f) for f in os.listdir(args.data_dir) \
                 if '.mid' in f or '.midi' in f ]
    #print("Random chosen file from the dataset is:", str(midi_files))
    experiment_dir = get_experiment_dir(args.experiment_dir)
    utils.log('Using {} as --experiment_dir'.format(experiment_dir),
              args.verbose)

    if not args.save_dir:
        args.save_dir = os.path.join(experiment_dir, 'generated')

    if not os.path.isdir(args.save_dir):
        os.makedirs(args.save_dir)
        utils.log('Created directory {}'.format(args.save_dir), args.verbose)

    model, epoch = train.get_model(args, experiment_dir=experiment_dir)
    utils.log(
        'Model loaded from {}'.format(
            os.path.join(experiment_dir, 'model.json')), args.verbose)

    window_size = model.layers[0].get_input_shape_at(0)[1]
    seed_generator = utils.get_data_generator(
        midi_files,
        window_size=window_size,
        batch_size=32,
        num_threads=1,
        max_files_in_ram=5)

    # validate midi instrument name
    try:
        # try and parse the instrument name as an int
        instrument_num = int(args.midi_instrument)
        if not (instrument_num >= 0 and instrument_num <= 127):
            utils.log('Error: {} is not a supported instrument. Number values must be ' \
                   'be 0-127. Exiting'.format(args.midi_instrument), True)
            return None
        args.midi_instrument = pretty_midi.program_to_instrument_name(
            instrument_num)
    except ValueError as err:
        # if the instrument name is a string
        try:
            # validate that it can be converted to a program number
            _ = pretty_midi.instrument_name_to_program(args.midi_instrument)
        except ValueError as er:
            utils.log('Error: {} is not a valid General MIDI instrument. Exiting.'\
                   .format(args.midi_instrument), True)
            return None

    args.file_length =args.file_length*(args.tempo + 1)

    # generate 10 tracks using random seeds
    utils.log('Loading seed files...', args.verbose)
    X, y = next(seed_generator)
    generated = utils.generate(model, X, window_size, args.file_length,
                               args.num_files, args.midi_instrument, args.tempo, args.pitch, args.drum)
    for i, midi in enumerate(generated):
        file = os.path.join(args.save_dir, '{}.mid'.format(i + 1))
        midi.write(file.format(i + 1))
        utils.log('wrote midi file to {}'.format(file), True)
    return file


if __name__ == '__main__':
    main()
