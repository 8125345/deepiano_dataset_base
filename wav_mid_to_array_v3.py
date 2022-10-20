import librosa
import math
import tensorflow as tf
import numpy as np
from shutil import copyfile
from deepiano.music import audio_io
from deepiano.music import midi_io
from deepiano.music import sequences_lib
from deepiano.server.wav2spec import wav2spec
from deepiano.wav2mid import configs
from deepiano.wav2mid import constants
from deepiano.wav2mid.data import wav_to_spec
from deepiano.wav2mid.data import hparams_frames_per_second
from deepiano.wav2mid.audio_label_data_utils import velocity_range_from_sequence

import os
import glob
import logging
import csv

DATASET_DIR = '/deepiano_data/dataset'
DST_DIR = '/deepiano_data/dataset/data_npy'
SPLIT_LEN = 1.023 # ms
SAMPLE_RATE = 16000
CONFIG = configs.CONFIG_MAP['onsets_frames']

front_chunk_padding = 27
back_chunk_padding = 3
frames_nopadding = 2

def get_wav_mid_pairs(dirs):
    file_pairs =[]
    for dir in dirs:
        path = os.path.join(DATASET_DIR, dir)
        path = os.path.join(path, '*.wav')
        wav_files = glob.glob(path)
        dst_path = os.path.join(DST_DIR, dir)
        for wav_file in wav_files:
            dirct, file = os.path.split(wav_file)
            name, _ = os.path.splitext(file)
            mid_file = dirct + '/' + name + '.mid'
            dst_file_path = os.path.join(dst_path,name)
            if os.path.isfile(mid_file):
                file_pairs.append((wav_file, mid_file, dst_file_path))
    return file_pairs

def get_wav_mid_pairs_form_csv(dir):
  train_data_set = []
  test_data_set = []
  
  input_dir = DATASET_DIR + '/' + dir
  logging.info('Generate dataset from csv: %s' % input_dir)
  csv_file_name = os.path.join(input_dir, 'maestro-v3.0.0.csv')
  logging.info('csv file: %s' %csv_file_name)
  with open(csv_file_name) as f:
    items = csv.reader(f)
    for item in items:
        if items.line_num == 1:
            continue
        midi_filename = DATASET_DIR+ '/' + dir + '/' + item[4]
        audio_filename = DATASET_DIR+ '/' + dir + '/' + item[5]
        split = item[2]
        
        name, _ = os.path.splitext(item[4])
        
#         print('split: %s, mid: %s, wav: %s' % (split, midi_filename, audio_filename))
#         print('dst_file: %s' % dst_file_path)

        if split=='train':
          dst_file_path = DST_DIR+'/train/'+dir+'/'+name
          train_data_set.append((midi_filename, audio_filename, dst_file_path))
        else:
          dst_file_path = DST_DIR+'/test/'+dir+'/'+name
          test_data_set.append((midi_filename, audio_filename, dst_file_path))
  return train_data_set, test_data_set


def sequence_to_pianoroll_fn(sequence, velocity_range, hparams):
    """Converts sequence to pianorolls."""
    #sequence = sequences_lib.apply_sustain_control_changes(sequence)
    roll = sequences_lib.sequence_to_pianoroll(
        sequence,
        frames_per_second=hparams_frames_per_second(hparams),
        min_pitch=constants.MIN_MIDI_PITCH,
        max_pitch=constants.MAX_MIDI_PITCH,
        min_frame_occupancy_for_label=hparams.min_frame_occupancy_for_label,
        onset_mode=hparams.onset_mode,
        onset_length_ms=hparams.onset_length,
        offset_length_ms=hparams.offset_length,
        onset_delay_ms=hparams.onset_delay,
        min_velocity=velocity_range.min,
        max_velocity=velocity_range.max)
    return (roll.active, roll.weights, roll.onsets, roll.onset_velocities,
            roll.offsets)


def gen_test_input(wav_filename, ns, dst_path):
    print('wav_file: ', wav_filename)
    spec = wav2spec(wav_filename)
    velocity_range = velocity_range_from_sequence(ns)
    split_cnt = 0
    for i in range(front_chunk_padding, spec.shape[0],frames_nopadding):
        split_cnt = split_cnt+1
        start = i-front_chunk_padding
        end = i + frames_nopadding + back_chunk_padding
        chunk_spec = spec[start:end]
        dst_chunk_spec_name = os.path.join(dst_path, '%04d_spec.npy'%split_cnt)
        np.save(dst_chunk_spec_name, chunk_spec)

#         print('start: %s, end: %s, ns time: %s'%(start*0.32, end*0.32, ns.total_time))
#         chunk_ns = sequences_lib.extract_subsequence(ns, start*0.32, end*0.32)
#         _, _, chunk_onsets, _, _ = sequence_to_pianoroll_fn(chunk_ns, velocity_range, hparams=CONFIG.hparams)
#         dst_chunk_onsets_name = os.path.join(dst_path, '%04d_onsets_label.npy'%split_cnt)
#         np.save(dst_chunk_onsets_name, chunk_onsets)


def process(wav_data, ns, dst_path):
    try:
        samples = audio_io.wav_data_to_samples(wav_data, SAMPLE_RATE)
    except audio_io.AudioIOReadError as e:
        print('Exception %s' % e)
        return

    samples = librosa.util.normalize(samples, norm=np.inf)

    # Add padding to samples if notesequence is longer.
    pad_to_samples = int(math.ceil(ns.total_time * SAMPLE_RATE))
    padding_needed = pad_to_samples - samples.shape[0]
    samples = np.pad(samples, (0, max(0, padding_needed)), 'constant')
    
    splits = np.arange(0, ns.total_time, SPLIT_LEN+0.0001)
        
    velocity_range = velocity_range_from_sequence(ns)

    split_cnt = 0
    for start, end in zip(splits[:-1], splits[1:]):
        split_cnt = split_cnt+1
        if end-start < SPLIT_LEN:
            print('split time: ', end-start)
            continue

        new_ns = sequences_lib.extract_subsequence(ns, start, end)
        labels, _, onsets_label, _, _ = sequence_to_pianoroll_fn(new_ns, velocity_range, hparams=CONFIG.hparams)

        new_samples = audio_io.crop_samples(samples, SAMPLE_RATE, start, end-start)
        new_wav_data = audio_io.samples_to_wav_data(new_samples, SAMPLE_RATE)
        spec = wav_to_spec(new_wav_data, CONFIG.hparams)
        if spec.shape[0] != 32:
            print('dst_spec_name: %s, time: %s' % (dst_spec_name,end-start))
            continue
#         dst_spec_name = os.path.join(dst_path, '%04d_spec.npy'%split_cnt)
#         np.save(dst_spec_name, spec)  
        
        if onsets_label.shape[0]<spec.shape[0]:
            onsets_label = np.pad(onsets_label, ((0, spec.shape[0]-onsets_label.shape[0]),(0,0)), 'constant')
        elif onsets_label.shape[0]>spec.shape[0]:
            onsets_label = onsets_label[0:spec.shape[0]-onsets_label.shape[0]]
#         dst_label_name = os.path.join(dst_path, '%04d_onsets_label.npy'%split_cnt)
#         np.save(dst_label_name, onsets_label) 
        res_data = np.concatenate((spec, onsets_label), axis=1)
        dst_data_name = os.path.join(dst_path, '%04d.npy'%split_cnt)
        np.save(dst_data_name, res_data) 
        

def run(dirs):
    wav_mid_pairs = get_wav_mid_pairs(dirs)
    
    for idx, pair in enumerate(wav_mid_pairs):
        wav_data = tf.gfile.Open(pair[0], 'rb').read()
        ns = midi_io.midi_file_to_note_sequence(pair[1])
        if not os.path.isdir(pair[2]):
            os.makedirs(pair[2])
        print('file: %s, len: %s' % (pair[1], ns.total_time))
        process(wav_data, ns, pair[2])

def run_csv(dirs):
    for dir in dirs:
        train_data_set, test_data_set = get_wav_mid_pairs_form_csv(dir)
        for idx, pair in enumerate(train_data_set):
            wav_data = tf.gfile.Open(pair[1], 'rb').read()
            ns = midi_io.midi_file_to_note_sequence(pair[0])
            if not os.path.isdir(pair[2]):
                os.makedirs(pair[2])
            print('file: %s, len: %s' % (pair[0], ns.total_time))
            process(wav_data, ns, pair[2])
        
        for idx, pair in enumerate(test_data_set):
            ns = midi_io.midi_file_to_note_sequence(pair[0])
            print('file: %s, len: %s' % (pair[0], ns.total_time))
            if not os.path.isdir(pair[2]):
                os.makedirs(pair[2])
            gen_test_input(pair[1], ns, pair[2])

if __name__ == '__main__':
  print("start run")
  #run(['ai-tagging', 'high-note', 'single-note', 'newmusic'])
  run_csv(['maestro-v3.0.0'])