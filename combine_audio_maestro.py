import sox
from glob import glob
from pathlib import Path
import os
import shutil
import logging
import csv

# def test():
#     audio1 = './combine_data/000000.wav'
#     audio2 = './combine_data/000001.wav'
#     audio3 = './combine_data/000002.wav'
#     audio4 = './combine_data/000003.wav'
#     new_file = './combine_data/total.wav'
#     cbn = sox.Combiner()
#     data = [audio1, audio2, audio3, audio4]
#     cbn.build(data, new_file, 'concatenate')

def combine_wav(data:list, new_file):
    cbn = sox.Combiner()
    cbn.build(data, new_file, 'concatenate')


def getdatapairfromcsv(csv_file, midi_path):
    # csv_file = './maestro_csv/maestro-v3.0.0.csv'
    # base_path = '/deepiano_data/yuxiaofei/work/data_0718/mix_changpu_metronome/noise_trans/maestro-v3.0.0_20220723_105736/'
    wav_midi_pairs = []
    with open(csv_file) as f:
        items = csv.reader(f)
        for item in items:
            if items.line_num == 1:
                continue
            split = item[2]
            midi_filename = item[4]
            wav_filename = item[5]
            if split == 'test':
                wav_file = os.path.join(midi_path, wav_filename)
                midi_file = os.path.join(midi_path, midi_filename)
                if os.path.isfile(midi_file):
                    wav_midi_pairs.append((wav_file, midi_file))
        print(len(wav_midi_pairs))
    return wav_midi_pairs



if __name__ == '__main__':
    base_path = '/deepiano_data/yuxiaofei/work/data_0718/mix_changpu_metronome/noise_trans/maestro-v3.0.0_20220723_105736'
    # csv_file = '/deepiano_data/dataset/maestro-v3.0.0_mix/maestro-v3.0.0.csv'
    csv_file = './maestro_csv/maestro-v3.0.0.csv'
    out_dir_base ='/deepiano_data/dataset/maestro-v3.0.0_mix'
    midi_path = '/deepiano_data/dataset/maestro-v3.0.0'

    wav_midi_pairs = getdatapairfromcsv(csv_file, midi_path)
    print(len(wav_midi_pairs))
    for test_wav_file, test_midi_file in wav_midi_pairs:
        # year = test_midi_file.split('/')[-2]
        # print(year)
        # out_dir = out_dir_base + '/' + year
        # if not os.path.isdir(out_dir):
        #     os.makedirs(out_dir)
        #     print(out_dir)
        # shutil.copy2(test_midi_file, test_midi_file.replace(midi_path, out_dir_base))
        # # shutil.copy2(test_wav_file, test_wav_file.replace(midi_path, out_dir_base))
        #
        # wav_id = test_wav_file.split('/')[-1].split('.')[0]
        # print('wav_id is:', )
        pending_wav_dir = test_wav_file.replace(midi_path, base_path).replace('.wav', '')
        # print(pending_wav_dir)
        if os.path.isdir(pending_wav_dir):
            print(pending_wav_dir)

            song_id = pending_wav_dir.split('/')[-1]
            years = pending_wav_dir.split('/')[-2]
            out_dir_pend = out_dir_base + '/' + years
            if not os.path.isdir(out_dir_pend):
                os.makedirs(out_dir_pend)
            shutil.copy2(test_midi_file, test_midi_file.replace(midi_path, out_dir_base))

            wav_list = []
            bgm_wav_list = []
            for file in glob(f'{pending_wav_dir}/*'):
                if Path(file).suffix == '.wav':
                    if file.endswith('_bgm.wav'):
                        bgm_wav_list.append(file)
                    else:
                        wav_list.append(file)

            new_wav = out_dir_pend + '/' + song_id + '.wav'
            new_bgm_wav = out_dir_pend + '/' + song_id + '_bgm.wav'
            if len(wav_list) >= 2:
                combine_wav(sorted(wav_list), new_wav)
                combine_wav(sorted(bgm_wav_list), new_bgm_wav)
            else:
                print("此歌曲只有一个片段")
                shutil.copy2(wav_list[0], new_wav)
                shutil.copy2(bgm_wav_list[0], new_bgm_wav)
        else:
            print('文件不存在')








    # wav_list = []
    # bgm_wav_list = []
    # for song_ID_dir in glob(f'{base_path}/*'):
    #     # song_id = Path(song_ID_dir).stem
    #     song_id = song_ID_dir.split('/')[-1]
    #     print(f'当前处理歌曲为：{song_id}')
    #     for file in glob(f'{base_path}/{song_id}/*'):
    #         # print(Path(file).suffix)
    #         if Path(file).suffix == '.wav':
    #             if file.endswith('_bgm.wav'):
    #                 bgm_wav_list.append(file)
    #             else:
    #                 wav_list.append(file)
    #     new_wav = out_dir + '/' + song_id + '.wav'
    #     new_bgm_wav = out_dir + '/' + song_id + '_bgm.wav'
    #     # print(sorted(bgm_wav_list))
    #     # print(sorted(wav_list))
    #     if len(wav_list) >= 2:
    #         combine_wav(sorted(wav_list), new_wav)
    #         combine_wav(sorted(bgm_wav_list), new_bgm_wav)
    #     else:
    #         print("此歌曲只有一个片段")
    #         shutil.copy2(wav_list[0], new_wav)
    #         shutil.copy2(bgm_wav_list[0], new_bgm_wav)
    # print('合并完成')


    # song_ = Path('/Users/xyz/Desktop/音频数据/ai-tagging/original/15224-拜厄钢琴基本教程-拜厄 No.81-3662897.wav')
    # print(Path(song_).stem)
    # shutil.copy2('./save/song1.wav', './save/new.wav')























