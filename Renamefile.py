from pathlib import Path
from glob import glob
import shutil


if False: #yali
    base_path = '/Users/xyz/Desktop/音频数据和评估结果/新增数据/yl/8.25'
    out_path = '/Users/xyz/Desktop/音频数据和评估结果/新增数据/yl/bgm_record_20220825/original/'
    Path(out_path).mkdir(parents=True, exist_ok=True)

    number_list = glob(f'{base_path}/*')
    for number in sorted(number_list):
        number_id = Path(number).name
        # print(str(number_id))
        for file in glob(f'{base_path}/{number_id}/*'):
            new_num = str(number_id).zfill(3)
            if Path(file).suffix == '.mid':
                shutil.copy2(file, out_path + f'20220825export-{new_num}.mid')
            if Path(file).name == 'bgm.wav' or Path(file).name == 'BGM.wav':
                shutil.copy2(file, out_path + f'20220825export-{new_num}_bgm.wav')
            if Path(file).name == 'iPad.wav' or Path(file).name == 'ipad.wav':
                shutil.copy2(file, out_path + f'20220825export-{new_num}.wav')


if True:#jinshi -qingchen_bgm
    base_dir = '/Users/xyz/Desktop/音频数据和评估结果/新增数据/js/清晨伴奏&无伴奏录制音频/qingchen_bgm'
    file_list = glob(f'{base_dir}/*')
    print(len(file_list))
    for i, file in enumerate(sorted(file_list)):
        new_num = str(i).zfill(3)
        # print(new_num)
        if i == 2:
            print(file)
        # Path(file).rename(base_dir + '/' + new_num +'.wav')











