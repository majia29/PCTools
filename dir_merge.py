#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

__usage__ = """
Directory Merge

Usage:
  dir_merge.py <source-path> <dest-path> [--ignore=<pattern>] [--ignorehide=<on/off>] [--ignorelink=<on/off>] [--quiet|--verbose]
  dir_merge.py -h | --help
  dir_merge.py --version

Options:
  --ignore=<pattern>        ignore patterns [default: none]
  --ignorehide=<on/off>     ignore hide files [default: on]
  --ignorelink=<on/off>     ignore link files [default: on]
  -q --quiet        print less log
  -v --verbose      print more log
  -h --help         show help
  --version         show version
"""

__version__ = "0.1b"

__all__ = ("dir_merge",)

import hashlib
import os
import shutil
import sys

from docopt import docopt

reload(sys)
sys.setdefaultencoding("utf-8")

def checksum(filename, hashname="md5", chucksize=8192):
    """ 计算文件 checksum 值
    基于 hashlib 库支持 md5/sha1/sha224/ripemd160 等
    todo: 基于 zlib 库支持 crc32/adler32 等
    """
    # 参数检查
    assert os.path.isfile(filename)
    hash_name  = hashname or "md5"
    chuck_size = chucksize or 8192
    # 读取文件, 计算 hash
    with open(filename, "rb") as handle:
        codec = hashlib.new(hash_name)
        while 1:
            data = handle.read(chuck_size)
            if not data:
                break
            codec.update(data)
    return codec.hexdigest()

def duplicate_file(f0, f1):
    """ 判断是否重复文件
    """
    # 参数检查
    assert os.path.isfile(f0)
    assert os.path.isfile(f1)
    # 先比较文件大小, 再比较 checksum 值
    if os.path.getsize(f0)==os.path.getsize(f1):
        if checksum(f0, "md5", chucksize=128*1024)==checksum(f1, "md5", chucksize=128*1024):
            return True
    return False

def dir_merge(source, dest, ignore=None, ignorehide=True, ignorelink=True):
    """ 目录合并
    """
    # 参数检查
    assert os.path.isdir(source)
    assert os.path.isdir(dest)
    # 内部函数
    def rename(path):
        head, tail = os.path.split(path)
        base, ext = os.path.splitext(tail)
        return os.path.join(head, base+"_copy"+ext)
    # 生成 ignore_patterns 对象, 在接下来的循环中用来生成忽略列表
    if ignore is None or ignore=="none":
        ignore_patterns = None
    else:
        # 过滤掉为""的 ignore 子表达式
        ignore_list = filter( lambda _: _!="", ignore.split(",") )
        ignore_patterns = shutil.ignore_patterns( *ignore_list )
    # 循环查询源目录
    for path, dirs, files in os.walk(source, topdown=True, followlinks=False):
        # 检查"忽略隐藏项"开关, 并确认源目录是否为隐藏子目录(目录名包含"/.")
        if ignorehide and path.find("/.")>-1:
            # 不做任何处理
            print("hide pass...", path)
            continue
        rel_path = os.path.relpath(path, source)
        print("current directory:", rel_path)
        # 开始处理文件
        # 基于 ignore_patterns, 生成忽略文件列表
        if ignore_patterns is not None:
            ignored_names = ignore_patterns(source, files)
        else:
            ignored_names = set()
        # 循环处理文件
        # 文件的基本处理逻辑: 如果文件存在, 则重命名复制的文件; 如果文件不存在, 则复制文件. 
        for f in files:
            old_file = os.path.join(source, rel_path, f)
            new_file = os.path.join(dest, rel_path, f)
            print("file:", old_file, "to", new_file, "...")
            # 检查"忽略隐藏项"开关, 并确认源文件是否为隐藏文件(文件名以"."开头)
            if ignorehide and f.startswith("."):
                # 不做任何处理
                print("hide pass...")
                continue
            # 检查"忽略链接项"开关, 并确认源文件是否为链接文件
            if ignorelink and os.path.islink(old_file):
                # 不做任何处理
                print("link pass...")
                continue
            # 检查是否匹配忽略文件列表
            if f in ignored_names:
                # 不做任何处理
                print("ignore pass...")
                continue
            # 检查目标文件路径是否存在
            if os.path.exists(new_file):
                # 检查目标文件路径是否为文件
                if os.path.isfile(new_file):
                    # 检查是否为重复文件
                    if duplicate_file(old_file, new_file):
                        # 如果为重复文件, 则不做处理
                        print("duplicate pass...")
                        continue
                # 否则, 重命名目标文件
                print("rename...")
                new_file = rename(new_file)
            # copy源文件到目标文件
            print("copy...", new_file)
            shutil.copyfile(old_file, new_file)
        # 开始处理目录
        # 基于 ignore_patterns, 生成忽略目录列表
        if ignore_patterns is not None:
            ignored_names = ignore_patterns(source, dirs)
        else:
            ignored_names = set()
        # 循环处理目录
        # 目录的基本处理逻辑: 如果目录存在, 则不用处理; 如果目录不存在, 则创建目录. 
        for d in dirs:
            old_dir = os.path.join(source, rel_path, d)
            new_dir = os.path.join(dest, rel_path, d)
            print("dir:", old_dir, "to", new_dir, "...")
            # 检查"忽略隐藏项"开关, 并确认源目录是否为隐藏目录(目录名以"."开头)
            if ignorehide and d.startswith("."):
                # 不做任何处理
                print("hide pass...")
                continue
            # 检查"忽略链接项"开关, 并确认源目录是否为链接目录
            if ignorelink and os.path.islink(old_dir):
                # 不做任何处理
                print("link pass...")
                continue
            # 检查是否匹配忽略文件列表
            if d in ignored_names:
                # 不做任何处理
                print("ignore pass...")
                continue
            # 检查目标文件路径是否存在
            if os.path.exists(new_dir):
                # 检查目标文件路径是否为目录
                if os.path.isdir(new_dir):
                    # 如果目标目录是已有目录, 则无需做什么
                    print("exist pass...")
                    continue
                else:
                    # 否则, 原目标文件重命名(move方式)
                    shutil.move(new_dir, rename(new_dir))
            # 创建目标目录
            print("mkdir...", new_dir)
            os.mkdir(new_dir)

def main(*argv, **kwargs):
    """
    main()

    :return: exit code
    """
    # 命令行参数抽取
    try:
        args = docopt(__usage__, argv=argv[1:], version=__version__)
        # patch docopt
        # 限制只使用"="进行命令行参数赋值
        for i in range(0, len(argv)):
            if argv[i] in args:
                assert args[argv[i]] != argv[i+1]
        # 检查 PATH 类型有效性
        assert os.path.isdir(args["<source-path>"]) 
        assert os.path.isdir(args["<dest-path>"])
        # 检查 BOOL/SWITCH 类型有效性
        assert args["--ignorehide"] in ("on","off")
        assert args["--ignorelink"] in ("on","off")
    except AssertionError:
        print(args, file=sys.stderr)
        raise ValueError
    except:
        raise
    print(args)
    # 参数检查
    arg_source_path = os.path.abspath( args["<source-path>"] )
    arg_dest_path   = os.path.abspath( args["<dest-path>"] )
    arg_ignore      = args["--ignore"].replace('"','').replace("'","").lower()
    arg_ignorehide  = True if args["--ignorehide"]=="on" else False
    arg_ignorelink  = True if args["--ignorelink"]=="on" else False
    # 通用参数
    arg_quiet   = args["--quiet"]
    arg_verbose = args["--verbose"]
    # 处理合并
    dir_merge( arg_source_path, arg_dest_path, 
        ignore=arg_ignore,
        ignorehide=arg_ignorehide, 
        ignorelink=arg_ignorelink
        )
    # 退出
    print("ok")
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv))
