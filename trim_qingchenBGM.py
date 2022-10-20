import os
import glob
import subprocess

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


def trim_audio():
    input_dir = '/Users/xyz/Desktop/清晨BGM录音原版/'

    record_wav = '/Users/xyz/Desktop/清晨BGM设备录音版/ipad_pro新录音 2-glued.wav'
    record_wav_str = space_to_string(record_wav)
    out_dir = '/Users/xyz/Desktop/清晨BGM-ipadpro_record'
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    wav_files = glob.glob(os.path.join(input_dir, '*.wav'))
    # print(sorted(wav_files))
    changpu = sorted(wav_files)[0:50]
    wuchangpu = sorted(wav_files)[50:]

    changpu_temp = sorted(changpu, key=lambda item: eval(item.split('/')[-1].split('.')[0].split('-')[1]))
    wuchangpu_temp = sorted(wuchangpu, key=lambda item: eval(item.split('/')[-1].split('.')[0].split('-')[1]))

    start = 4.3
    for wav_changpu in changpu_temp:
        print(wav_changpu)
        input_duration = get_audio_duration(wav_changpu)
        output_file = out_dir + '/' + wav_changpu.split('/')[-1].replace('原版', '')
        output_file_str = space_to_string(output_file)
        # print(output_file)
        # print(output_file_str)
        if os.path.isfile(output_file):
            continue
        print("开始时间是：", start)
        trim_command = 'sox {noise_file} {output_noise_file} trim {start} {input_duration}'.format(**{
            'noise_file': record_wav_str,
            'output_noise_file': output_file_str,
            'start': start,
            'input_duration': input_duration,
        })
        print(trim_command)
        process_handle = subprocess.Popen(trim_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process_handle.communicate()
        start = start + input_duration + 0.6

input_dir = '/Users/xyz/Desktop/清晨伴奏_金石的备份/'

wav_files = glob.glob(os.path.join(input_dir, '*.wav'))
# print(sorted(wav_files))
changpu = sorted(wav_files)[0:50]
wuchangpu = sorted(wav_files)[50:]

changpu_temp = sorted(changpu, key=lambda item: eval(item.split('/')[-1].split('.')[0].split('-')[1]))
wuchangpu_temp = sorted(wuchangpu, key=lambda item: eval(item.split('/')[-1].split('.')[0].split('-')[1]))

total_audio = changpu_temp + wuchangpu_temp
for wav in total_audio:
    print(wav)
    input_duration = get_audio_duration(wav)
    print(input_duration)





















