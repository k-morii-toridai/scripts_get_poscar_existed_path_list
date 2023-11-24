import os
import re
import sys
import itertools
from tqdm import tqdm
from pathlib import Path
from multiprocessing import Pool, cpu_count

import numpy as np


def iterdir_func(poscar_dir):
    return list(poscar_dir.iterdir())


def flatten_func(list_2dim):
    return list(itertools.chain.from_iterable(list_2dim))


def get_subdir_list(dir_list):
    return flatten_func(list(map(iterdir_func, dir_list)))


args = sys.argv  # コマンドラインからcifディレクトリのパスを受け取る
p = Path(args[1])
# p = Path('/mnt/ssd_elecom_black_c2c_480G/cif')
p_s_list = [p_sub_folder for p_sub_folder in p.glob('[1-9]')]
p_ssss_list = get_subdir_list(get_subdir_list(get_subdir_list(p_s_list)))


def poscar_folder_filter(path):
    pattern = '[0-9]{6}$'  # 正規表現（：末尾が数字６文字で終わる）
    string = str(path)
    return bool(re.search(pattern, string))


# make filter
poscar_folder_path_list_filter = list(map(poscar_folder_filter, p_ssss_list))
# apply poscar_folder_filter to p_ssss_list
poscar_folder_path_list = np.array(p_ssss_list)[poscar_folder_path_list_filter]
print(f'len(poscar_folder_path_list): {len(poscar_folder_path_list)}')


# 並列化(数字６桁のフォルダ下のファイルorフォルダ一覧を取得)
try:
    p = Pool(cpu_count() - 1)
    print("Now getting poscar folder sub path list!!!")
    # iterdir
    poscar_folder_sub_path_list = list(tqdm(p.imap(iterdir_func, poscar_folder_path_list), total=len(poscar_folder_path_list)))
    # flatten
    poscar_folder_sub_path_list = flatten_func(poscar_folder_sub_path_list)
finally:
    p.close()
    p.join()


def poscar_file_filter(path):
    pattern = '[0-9]{6}/POSCAR$'  # 正規表現（：末尾が '数字６桁/POSCAR'で終わる）
    string = str(path)
    return bool(re.search(pattern, string))


# make filter
poscar_file_path_list_filter = list(map(poscar_file_filter, poscar_folder_sub_path_list))
# apply poscar_file_filter to poscar_existed_folder_path_list
poscar_existed_file_path_list = np.array(poscar_folder_sub_path_list)[poscar_file_path_list_filter]
print(f'len(poscar_existed_file_path_list): {len(poscar_existed_file_path_list)}')

# make folder_path from file_path
poscar_existed_folder_path_list = [os.path.split(p)[0] for p in poscar_existed_file_path_list]

# input 1or2or3 which decide to save choice.
inputted_num = input('Please input 1 or 2 or 3.: \n\
If want to save Folder path list of poscar exsited, input 1.\n\
If save File path list, input 2.\n\
If save both Folder and File path list, input 3.')

if inputted_num == '1':
    # save poscar_existed_file_path_list as .npy
    np.save('poscar_existed_file_path_list.npy', poscar_existed_file_path_list)
    print("poscar_existed_file_path_list was saved as .npy")
elif inputted_num == '2':
    # save poscar_existed_folder_path_list as .npy
    np.save('poscar_existed_folder_path_list.npy', poscar_existed_folder_path_list)
    print("poscar_existed_folder_path_list was saved as .npy")
elif inputted_num == '3':
    np.save('poscar_existed_file_path_list.npy', poscar_existed_file_path_list)
    np.save('poscar_existed_folder_path_list.npy', poscar_existed_folder_path_list)
    print("Both poscar_existed_file_path_list and poscar_existed_folder_path_list were saved as .npy")
else:
    print("Please choose again from choices, 1 or 2 or 3.")
