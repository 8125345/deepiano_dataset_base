import sox
from glob import glob
from pathlib import Path
import os
import shutil

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


if __name__ == '__main__':
    # base_path = '/deepiano_data/yuxiaofei/work/data_0718/mix_changpu_metronome/noise_trans/ai-tagging_20220721_183306/original/'
    # for song_ID_dir in glob(f'{base_path}/*'):
    #     for wav_dir in glob(f'{base_path}/{Path(song_ID_dir).stem}/*'):
    #         song_id = Path(song_ID_dir).stem
    #         print(f'正在处理歌曲：{song_id}')
    #         if

    base_path = '/deepiano_data/yuxiaofei/work/data_0718/mix_changpu_metronome/noise_trans/ai-tagging_20220721_183306/original/'
    out_dir ='/deepiano_data/dataset/ai-tagging_mix/original'
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    wav_list = []
    bgm_wav_list = []
    for song_ID_dir in glob(f'{base_path}/*'):
        # song_id = Path(song_ID_dir).stem
        song_id = song_ID_dir.split('/')[-1]
        print(f'当前处理歌曲为：{song_id}')
        for file in glob(f'{base_path}/{song_id}/*'):
            # print(Path(file).suffix)
            if Path(file).suffix == '.wav':
                if file.endswith('_bgm.wav'):
                    bgm_wav_list.append(file)
                else:
                    wav_list.append(file)
        new_wav = out_dir + '/' + song_id + '.wav'
        new_bgm_wav = out_dir + '/' + song_id + '_bgm.wav'
        # print(sorted(bgm_wav_list))
        # print(sorted(wav_list))
        if len(wav_list) >= 2:
            combine_wav(sorted(wav_list), new_wav)
            combine_wav(sorted(bgm_wav_list), new_bgm_wav)
        else:
            print("此歌曲只有一个片段")
            shutil.copy2(wav_list[0], new_wav)
            shutil.copy2(bgm_wav_list[0], new_bgm_wav)
    print('合并完成')


    # song_ = Path('/Users/xyz/Desktop/音频数据/ai-tagging/original/15224-拜厄钢琴基本教程-拜厄 No.81-3662897.wav')
    # print(Path(song_).stem)
    # shutil.copy2('./save/song1.wav', './save/new.wav')










