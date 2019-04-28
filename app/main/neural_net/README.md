# neural-net

## Setup:
Use pip to set all libraries to expected version (may need sudo if not using virtual environment)
```bash
pip install -r requirements.txt
```

## Training:

### usage: 
```bash
python train.py [--data_dir GENRE] [--experiment_dir GENRE]
example: python train.py --data_dir data/classical --experiment_dir experiments/classical
```
### optional arguments:
```bash
[--rnn_size RNN_SIZE] 
[--num_layers NUM_LAYERS]
[--learning_rate LEARNING_RATE] 
[--window_size WINDOW_SIZE]
[--batch_size BATCH_SIZE] 
[--num_epochs NUM_EPOCHS]
[--dropout DROPOUT]
[--optimizer {sgd,rmsprop,adagrad,adadelta,adam,adamax,nadam}]
[--grad_clip GRAD_CLIP] 
[--message MESSAGE] 
[--n_jobs N_JOBS]
[--max_files_in_ram MAX_FILES_IN_RAM]
```
## Generating:

### usage: 
```bash
python sample.py [--data_dir GENRE][--experiment_dir GENRE]
example: python sample.py --data_dir data/classical --experiment_dir experiments/classical
```
### optional arguments:
```bash
[--midi_instrument MIDI_INSTRUMENT] 
[--num_files NUM_FILES]
[--file_length FILE_LENGTH] 
[--save_dir SAVE_DIR]
[--tempo TEMPO]
[--pitch  PITCH ADJUSTMENT(add or substract)]
[--drum True/False]
```
### List of instruments:
https://www.midi.org/specifications-old/item/gm-level-1-sound-set
