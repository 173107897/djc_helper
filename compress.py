import lzma
import os
import shutil
import subprocess
from os.path import realpath

from log import logger


def compress_dir_with_bandizip(dirpath: str, compressed_7z_filepath: str = "", dir_src_path: str = ""):
    """
    压缩 目录dirpath 到 compressed_7z_filepath，并设定源代码根目录为dir_src_path，用于定位bz.exe
    """
    if compressed_7z_filepath == "":
        compressed_7z_filepath = dirpath + ".7z"

    compressed_7z_filepath = realpath(compressed_7z_filepath)
    dirpath = realpath(dirpath)

    # 压缩打包
    logger.info(f"开始压缩 目录 {dirpath} 为 {compressed_7z_filepath}")
    subprocess.call([get_bz_path(dir_src_path), 'c', '-y', '-r', '-aoa', '-fmt:7z', '-l:9', compressed_7z_filepath, dirpath])


def decompress_dir_with_bandizip(compressed_7z_filepath: str, dir_src_path: str = "", dst_parent_folder: str = "."):
    """
    自动解压缩 compressed_7z_filepath 到其所在目录，并设定源代码根目录为dir_src_path，用于定位bz.exe
    """
    dst_parent_folder = realpath(dst_parent_folder)

    # 尝试解压
    logger.info(f"开始解压缩 目录 {compressed_7z_filepath} 到 目录 {dst_parent_folder} 下面")
    subprocess.call([get_bz_path(dir_src_path), "x", f"-o:{dst_parent_folder}", "-aoa", "-target:auto", realpath(compressed_7z_filepath)])


def get_bz_path(dir_src_path: str = "") -> str:
    if dir_src_path == "":
        # 未传入参数，则默认当前目录为源代码根目录
        dir_src_path = os.getcwd()

    return realpath(os.path.join(dir_src_path, "bandizip_portable", "bz.exe"))


def compress_file_with_lzma(filepath: str, compressed_7z_filepath: str = ""):
    if compressed_7z_filepath == "":
        compressed_7z_filepath = filepath + ".7z"

    filepath = realpath(filepath)
    compressed_7z_filepath = realpath(compressed_7z_filepath)

    # 创建压缩版本
    logger.info(f"开始压缩 文件 {filepath} 为 {compressed_7z_filepath}")
    with open(f"{filepath}", "rb") as file_in:
        with lzma.open(f"{compressed_7z_filepath}", "wb") as file_out:
            file_out.writelines(file_in)


def decompress_file_with_lzma(compressed_7z_filepath: str, filepath: str = ""):
    if filepath == "":
        filepath = compressed_7z_filepath.removesuffix(".7z")

    compressed_7z_filepath = realpath(compressed_7z_filepath)
    filepath = realpath(filepath)

    # 解压缩
    logger.info(f"开始解压缩 {compressed_7z_filepath} 为 文件 {filepath}")
    with lzma.open(f"{compressed_7z_filepath}", "rb") as file_in:
        with open(f"{filepath}", "wb") as file_out:
            file_out.writelines(file_in)


def test():
    from util import make_sure_dir_exists
    import json

    dir_src = os.getcwd()
    test_root_dir = realpath("test/compress")

    make_sure_dir_exists(test_root_dir)
    os.chdir(test_root_dir)

    # 测试文件解压缩
    test_file_name = "test_file.json"
    test_compressed_file_name = test_file_name + ".7z"
    test_decompressed_file_name = test_compressed_file_name + ".json"
    with open(test_file_name, 'w', encoding='utf-8') as f:
        json.dump("test_file_compress", f)
    compress_file_with_lzma(test_file_name, test_compressed_file_name)
    decompress_file_with_lzma(test_compressed_file_name, test_decompressed_file_name)

    # 测试目录解压缩
    test_folder_name = "test_folder"
    test_compressed_folder_name = test_folder_name + ".7z"
    make_sure_dir_exists(test_folder_name)
    with open(os.path.join(test_folder_name, "test.json"), 'w', encoding='utf-8') as f:
        json.dump("test_folder_compress", f)

    compress_dir_with_bandizip(test_folder_name, test_compressed_folder_name, dir_src)

    shutil.rmtree(test_folder_name)
    decompress_dir_with_bandizip(test_compressed_folder_name, dir_src)

    shutil.rmtree(test_root_dir, ignore_errors=True)


if __name__ == '__main__':
    test()
