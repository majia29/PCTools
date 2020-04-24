#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

__usage__ = """
Bing Background Image Download

Usage:
  bing_bgimage.py [<download-path>] [--quiet|--verbose]
  bing_bgimage.py -h | --help
  bing_bgimage.py --version

Options:
  <download-path>   download path [default: .]
  -q --quiet        print less log
  -v --verbose      print more log
  -h --help         show help
  --version         show version
"""

__version__ = "0.1a"

__all__ = ()

import datetime
import os
import sys
import urllib
import urlparse

from docopt import docopt

reload(sys)
sys.setdefaultencoding("utf-8")

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
        assert os.path.isdir(args["<download-path>"] or ".") 
    except AssertionError:
        print(args, file=sys.stderr)
        raise ValueError
    except:
        raise
    print(args)
    # 参数检查
    arg_download_path = os.path.abspath( args["<download-path>"] or "." )
    # 通用参数
    arg_quiet   = args["--quiet"]
    arg_verbose = args["--verbose"]
    # 获取页面 html
    url = "http://cn.bing.com/"
    split_tuple = urlparse.urlsplit(url)
    base_url = "{}://{}".format(split_tuple.scheme, split_tuple.netloc)
    page = urllib.urlopen(url)
    html = page.read().decode("utf-8")
    # 获取 backgroud-image url
    #<div id="bgDiv" style="...; backgroud-image:...;" >
    #<div id="bgImgProgLoad" data-ultra-definition-src="..." >
    idx = html.find('<div id="bgDiv"')
    if idx<0:
        print("read html error")
        return -1
    print("bgDiv:", html[ idx:idx+200 ])
    if html.find("backgroud-image:", idx)>0:
        feature = "backgroud-image:"
        idx0 = html.find(feature, idx)
        idx1 = html.find(";", idx0+len(feature))
        image_url = html[ idx0+len(feature):idx1 ]
    elif html.find('data-ultra-definition-src="', idx)>0:
        feature = 'data-ultra-definition-src="'
        idx0 = html.find(feature, idx)
        idx1 = html.find('"', idx0+len(feature))
        image_url = html[ idx0+len(feature):idx1 ]
    else:
        print("read image error")
        return -1
    print("image_url:", image_url)
    # 下载图片
    image_file = "bing-cn-{}.jpg".format(datetime.date.today())
    urllib.urlretrieve( base_url+image_url, os.path.join(arg_download_path,image_file) )
    # 退出
    print("ok")
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv))
