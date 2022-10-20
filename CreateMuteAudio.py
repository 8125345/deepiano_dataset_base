import os
import random
import subprocess
import sox
import logging
import glob
import csv

from deepiano.wav2mid.audio_transform import get_audio_duration, read_noise_files


def space_to_string(input_str):
    s_dict = []
    s_dict = list(input_str)
    for i, s_char in enumerate(s_dict):
      if s_char == ' ':
        s_dict.pop(i)
        s_dict.insert(i, '\ ')
    s_str = [str(j) for j in s_dict]
    output_str = ''.join(s_str)
    return output_str

def generate_predict_set_from_csv(input_dirs):
    predict_file_pairs = []
    logging.info('generate_predict_set_from_csv %s' % input_dirs)
    for input_dir in input_dirs.split(","):
        input_dir = input_dir.strip()
        csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
        for csv_file in csv_files:
            with open(csv_file) as f:
                items = csv.reader(f)
                for item in items:
                    if items.line_num == 1:
                        continue
                    if "maestro-v3.0.0.csv" in csv_file:
                        split = item[2]
                        midi_filename = item[4]
                        mix_filename = item[5]
                    else:
                        split = item[0]
                        midi_filename = item[1]
                        mix_filename = item[2]

                    # bgm_filename = os.path.splitext(mix_filename)[0] + '_bgm.wav'

                    if split == 'test':
                        mix_file = os.path.join(input_dirs, mix_filename)
                        # bgm_file = os.path.join(input_dirs, bgm_filename)
                        mid_file = os.path.join(input_dirs, midi_filename)
                        if os.path.isfile(mid_file):
                            # predict_file_pairs.append((mix_file, bgm_file, mid_file))
                            predict_file_pairs.append((mix_file, mid_file))
    logging.info('generate_predict_set_from_csv %d' % len(predict_file_pairs))
    return predict_file_pairs


def SplitMutefile(noise_dir, wav_file):

    output_noise_file = wav_file.replace('.wav', '_bgm.wav')
    output_noise_file_str = space_to_string(output_noise_file)
    start = 0
    input_duration = get_audio_duration(wav_file)
    print(input_duration)  # 单位是s
    trim_command = 'sox {noise_file} {output_noise_file} trim {start} {input_duration}'.format(**{
        'noise_file': noise_dir,
        'output_noise_file': output_noise_file_str,
        'start': start,
        'input_duration': input_duration,
    })
    print(trim_command)
    process_handle = subprocess.Popen(trim_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process_handle.communicate()

    if os.path.isfile(output_noise_file):
        # noise_duration = get_audio_duration(output_noise_file)
        start = 0
        mute_command = 'sox -n -r 16000 -b 16 {output_noise_file} trim {start} {input_duration}'.format(**{
            'output_noise_file': output_noise_file_str,
            'start': start,
            'input_duration': input_duration,
        })
        print(mute_command)
        process_handle = subprocess.Popen(mute_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process_handle.communicate()

def muteaudio(output_noise_file):
    output_noise_file = space_to_string(output_noise_file)
    if os.path.isfile(output_noise_file):
        noise_duration = get_audio_duration(output_noise_file)
        start = 0
        mute_command = 'sox -n -r 16000 -b 16 {output_noise_file} trim {start} {input_duration}'.format(**{
            'output_noise_file': output_noise_file,
            'start': start,
            'input_duration': noise_duration,
        })
        print("....................")
        print(mute_command)
        process_handle = subprocess.Popen(mute_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process_handle.communicate()


if __name__ == '__main__':
    dataset_dir = '/Users/xyz/PycharmProjects/deepiano_dataset_zl/data/ai-tagging_test'
    predict_file_pairs = generate_predict_set_from_csv(dataset_dir)
    noise_dir = '/Users/xyz/PycharmProjects/deepiano_dataset_zl/data/noise/env.wav'
    for wav_file, label_midi_file in predict_file_pairs:
        SplitMutefile(noise_dir, wav_file)
        print('done')






