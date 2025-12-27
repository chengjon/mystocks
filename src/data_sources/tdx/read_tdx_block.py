## -*- coding: utf-8 -*-

import pandas as pd
from struct import unpack
from loguru import logger

"""
通达信行业板块，概念板块，风格板块，指数板块，细分行业成分股数据读取获取
https://github.com/trading4/tdx_block_data/tree/main
通达信板块数据存储在new_tdx/T0002/hq_cache/目录下，主要文件包括：
block_zs.dat（指数板块）
block_gn.dat（概念板块）
block_fg.dat（自定义板块）

通达信对不同的板块更新的频率不同，每天登录通达信行情软件，
自动会更新本地数据库文件，在上午9：00之后登录通达信行情软件就会自动更新。
"""

# 本地通达信安装路径 C:/tdx
# PATH = 'C:/tdx/T0002/hq_cache/'
# PATH = r'D:\AutoCAT\TDX_new\T0002\hq_cache\'
# PATH = 'D:/AutoCAT/TDX_new/T0002/hq_cache/'
PATH = "D:/ProgramData/tdx_new/T0002/hq_cache/"


@logger.catch
def get_block_file(block="gn"):
    """file= block_gn.dat, _fg.dat, _zs.dat"""
    if block == "hy":
        return hy_block("hy")

    file_name = f"block_{block}.dat"
    logger.info(f"开始读取文件 {file_name}")
    # print(PATH + file_name)
    with open(PATH + file_name, "rb") as f:
        buff = f.read()

    head = unpack("<384sh", buff[:386])
    blk = buff[386:]
    blocks = [blk[i * 2813 : (i + 1) * 2813] for i in range(head[1])]
    bk_list = []
    for bk in blocks:
        name = bk[:8].decode("gbk").strip("\x00")
        num, t = unpack("<2h", bk[9:13])
        stks = bk[13 : (12 + 7 * num)].decode("gbk").split("\x00")
        bk_list = bk_list + [[name, block, num, stks]]
    df = pd.DataFrame(bk_list, columns=["name", "tp", "num", "stocks"])
    csv_file = file_name + ".csv"
    df.to_csv(csv_file, encoding="utf_8_sig")
    logger.info(f"文件 {csv_file} 已成功保存")
    return df


def read_file_loc(file_name, splits):
    with open(file_name, "r") as f:
        buf_lis = f.read().split("\n")
    return [x.split(splits) for x in buf_lis[:-1]]


@logger.catch
def get_block_zs_tdx_loc(block="hy"):
    file = PATH + "tdxzs3.cfg"
    logger.info(f"开始读取文件 {file}")
    buf_line = read_file_loc(file, "|")
    mapping = {"hy": "2", "dq": "3", "gn": "4", "fg": "5", "yjhy": "12", "zs": "6"}
    df = pd.DataFrame(buf_line, columns=["name", "code", "type", "t1", "t2", "block"])
    dg = df.groupby(by="type")
    if block == "zs":
        return df
    temp = dg.get_group(mapping[block]).reset_index(drop=True)
    temp.drop(temp.columns[[2, 3, 4]], axis=1, inplace=True)
    return temp


@logger.catch
def get_stock_hyblock_tdx_loc():
    file = PATH + "tdxhy.cfg"
    logger.info(f"开始读取文件 {file}")
    buf_line = read_file_loc(file, "|")
    buf_lis = []
    for x in buf_line:
        # x[1] = mapping[x[0]] + x[1]
        buf_lis.append(x)
    df = pd.DataFrame(buf_lis, columns=["c0", "code", "block", "c1", "c2", "c3"])
    df.drop(df.columns[[0, 3, 4, 5]], axis=1, inplace=True)
    df = df[(df["block"] != "")]
    df["block5"] = df["block"].str[0:5]
    return df


@logger.catch
def hy_block(blk="hy"):
    logger.info("开始生成行业板块数据")
    stocklist = get_stock_hyblock_tdx_loc()
    blocklist = get_block_zs_tdx_loc(blk)
    blocklist["block5"] = blocklist["block"].str[0:5]
    blocklist["num"] = 0
    blocklist["stocks"] = ""
    for i in range(len(blocklist)):
        blockkey = blocklist.iat[i, 2]
        if len(blockkey) == 5:
            datai = stocklist[stocklist["block5"] == blockkey]  # 根据板块名称过滤
        else:
            datai = stocklist[stocklist["block"] == blockkey]  # 根据板块名称过滤
        # 板块内进行排序填序号
        datai = datai.sort_values(by=["code"], ascending=[True])
        codelist = datai["code"].tolist()
        blocklist.iat[i, 4] = len(codelist)
        blocklist.iat[i, 5] = str(codelist)
    df = blocklist.drop(blocklist[blocklist["num"] == 0].index)
    df.to_csv("block_hy.dat.csv", encoding="utf_8_sig", index=False)
    logger.info("行业板块数据已保存为 block_hy.dat.csv")
    return df


if __name__ == "__main__":
    logger.info("程序开始执行")
    # 最后把文件写入本地 block_xx.dat.csv
    get_block_file("hy")
    get_block_file("gn")
    get_block_file("zs")
    get_block_file("fg")
    logger.success("所有文件处理完成，程序执行结束")
