# TDX目录解析



通达信行业板块，概念板块，风格板块，指数板块，细分行业成分股数据读取获取
https://github.com/trading4/tdx_block_data/tree/main
通达信板块数据存储在new_tdx/T0002/hq_cache/目录下，主要文件包括：
block_zs.dat（指数板块）
block_gn.dat（概念板块）
block_fg.dat（自定义板块）

通达信对不同的板块更新的频率不同，每天登录通达信行情软件，
自动会更新本地数据库文件，在上午9：00之后登录通达信行情软件就会自动更新。
'''

# 本地通达信安装路径 C:/tdx （每个人不同）
#PATH = 'C:/tdx/T0002/hq_cache/'
#PATH = r'D:\AutoCAT\TDX_new\T0002\hq_cache\'
#PATH = 'D:/AutoCAT/TDX_new/T0002/hq_cache/'
PATH = 'D:/ProgramData/tdx_new/T0002/hq_cache/'

相关文件：
incon.dat                                       证监会行业，通达信新行业，申万行业等描述信息
T0002\hq_cache\block.dat            一般板块
T0002\hq_cache\block_gn.dat      概念板块
T0002\hq_cache\block_fg.dat       风格板块
T0002\hq_cache\block_zs.dat       指数板块:
T0002\hq_cache\tdxhy.cfg             每个股票对应通达信行业和申万行业
T0002\hq_cache\tdxzs.cfg             板块指数，部分板块的最后一个字段映射到incon.dat的TDXNHY和SWHY
T0002\blocknew\blocknew.cfg        自定义板块概要描述文件

1 行业
行业包括三个类别：证监会行业；申万行业；通达信新行业
行业在文件“incon.dat”中定义。文件格式：
1) 文件包含多个行业分类：
        a) 证监会行业：开头#ZJHHY，结束######
        b) 申万行业：开头#SWHY，结束######
        c) 通达信新行业：开头#TDXNHY，结束######
2) 每个分类中，每一行包含一个细分行业的代码和名称，以“|”分隔
        a) 证监会行业：一级分类为A~M，二级分类A99，三级分类为A9999
        b) 申万行业：一级分类为990000，二级分类为999900，三级分类为999999
        c) 通达信新行业：一级分类为T99，二级分类为T9999，三级分类为T999999
示例如下：
incon.dat
代码|名称
#ZJHHY
A|农业
A01|农业
A0101|种植业
A0199|其他农业
A03|林业
A0301|林业
……
######
#TDXNHY
T01|能源
T0101|煤炭
T010101|煤炭开采
T010102|焦炭加工
T0102|电力
T010201|水力发电
T010202|火力发电
T010203|新型电力
……
######
#SWHY
110000|农业
110100|种植业
110101|种子生产
110102|粮食种植
110103|其他种植业
110200|渔业
……
######


每个股票对应的申万行业和通达信行业记录在文件T0002\hq_cache\tdxhy.cfg中。
T0002\hq_cache\tdxhy.cfg
市场|股票代码|通达信新行业代码|申万行业代码
0|000001|T1001|440101
0|000002|T110201|430101
0|000004|T040502|370301
0|000005|T110202|430101
0|000006|T110202|430101
0|000007|T0604|460201
0|000008|T1301|510101
0|000009|T110201|430101
0|000010|T110101|250202
0|000011|T110202|430101
0|000012|T020603|250101
0|000014|T110201|430101

2 通达信自定义板块
通达信定义的板块通过如下四个板块文件描述：
T0002\hq_cache\block.dat             一般板块
T0002\hq_cache\block_gn.dat       概念板块
T0002\hq_cache\block_fg.dat        风格板块
T0002\hq_cache\block_zs.dat        指数板块:
数据格式的C语言描述如下：
// 股票板块信息文件头格式，T0002/hq_cache/block.dat block_fg.dat block_gn.dat block_zs.dat
struct TTDXBlockHeader
{
    char         szVersion[64];        // 0, Registry ver:1.0 (1999-9-28)
    int            nIndexOffset;            // 64, 0x00000054
    int            nDataOffset;            // 68, 0x00000180
    int            nData1;                // 72, 0x00000003
    int            nData2;                // 76, 0x00000000
    int            nData3;                // 80, 0x00000003
};

struct TTDXBlockIndex
{
    char        szName[64];            // 0, Root, Block, Val
    int            nData1;                // 64
    int            nData2;                // 68
    int            nLength;                // 72, length of the block
    int            nOffset;                // 76, offset of the data part
    int            nData3;                // 80
    int            nData4;                // 84
    int            nData5;                // 88, root=-1,block=0,val=1
    int            nData6;                // 92, root=1,block=2,val=-1
    int            nStatus;                // 96, 1
};

struct TTDXBlockRecord
{
    char         szName;
    short        nCount;
    short        nLevel;
    char         szCode[400];
};

3 用户自定义板块
基本目录：T0002\blocknew
配置文件：blocknew.cfg        记录自定义的板块名称和文件头
配置文件存储格式：
1) 每个板块120字节
2) 板块名称50字节
3) 板块文件名头70字节
// 自定义板块概述文件格式，T0002\blocknew\blocknew.cfg
struct TTDXUserBlockRecord
{
    char        szName[50];
    char        szAbbr[70];        // 也是文件名称前缀 T0002\blocknew\xxxx.blk
};

板块列表文件: *.blk
1) 每行一条记录：每个记录7个数字：
    a) 市场代码1位：0 – 深市；1 – 沪市
    b) 股票代码6位
    c) 行结束符：\r\n
T0002\blocknew\ZXG.blk
市场 股票代码
1999999
0399001
0399005
0399006
1000016
1000300
0399330

4 通达信自定义指数
通达信自定义指数记录在文件T0002\hq_cache\tdxzs.cfg中，每行一条记录，每个记录包含6个字段，字段之间用“|”分隔。字段依次为：
1) 指数名称
2) 指数代码
3) 对应板块/行业类别：2-通达信行业板块 3-地区板块 4-概念板块 5-风格板块 8-申万行业
4) 未知字段：都为1
5) 未知字段：为0或1
6) 行业代码或板块名称：
    a) 类别为2对应通达信行业代码
    b) 类别为3对应地域编号，与base.dbf中的DY字段对应
    c) 类别为4对应概念板块名称
    d) 类别为5对应风格板块名称
    e) 类别为8对应申万行业代码
T0002\hq_cache\tdxzs.cfg
指数名称|指数代码|类别|未知字段|未知字段|行业代码或板块代码
黑龙江|880201|3|1|0|1
新疆板块|880202|3|1|0|2
吉林板块|880203|3|1|0|3
甘肃板块|880204|3|1|0|4
……
煤炭|880301|2|1|0|T0101
煤炭开采|880302|2|1|1|T010101
焦炭加工|880303|2|1|1|T010102
电力|880305|2|1|0|T0102
水力发电|880306|2|1|1|T010201


数据格式说明
支持读取通达信日线数据文件（.day）文件名即股票代码，每32个字节为一个数据，其中每4个字节为一个字段，每个字段内低字节在前。


00 ~ 03 字节：年月日, 整型

04 ~ 07 字节：开盘价*1000， 整型

08 ~ 11 字节：最高价*1000,  整型

12 ~ 15 字节：最低价*1000,  整型

16 ~ 19 字节：收盘价*1000,  整型

20 ~ 23 字节：成交额（元），float型

24 ~ 27 字节：成交量（手），整型

28 ~ 31 字节：上日收盘*1000, 整型
支持读取通达信1分钟数据文件（.lc1）,5分钟数据文件（.lc5）,15分钟数据文件（.lc15）,30分钟数据文件（.lc30）,60分钟数据文件（.lc60）。文件名即股票代码，每32个字节为一个数据，其中每4个字节为一个字段，每个字段内低字节在前。

00 ~ 01 字节：日期，整型，设其值为num，则日期计算方法为：
      year=floor(num/2048)+2004;
      month=floor(mod(num,2048)/100);
      day=mod(mod(num,2048),100);

02 ~ 03 字节：从0点开始至目前的分钟数，整型

04 ~ 07 字节：开盘价（分），整型

08 ~ 11 字节：最高价（分），整型

12 ~ 15 字节：最低价（分），整型

16 ~ 19 字节：收盘价（分），整型

20 ~ 23 字节：成交额（元），float型

24 ~ 27 字节：成交量（股）

28 ~ 31 字节：保留，一般都是0
Python码示例
日线数据读取

import os
import struct

def read_day_data(file_path):
  with open(file_path, 'rb') as f:
    buf = f.read()
    size = len(buf)
    rec_count = int(size / 32)

    result = []
    for i in range(rec_count):
      data = unpack('=IIIIIfII', buf[i * 32:(i + 1) * 32])
      result.append({
        'date': data[0],
        'open': data[1] / 100.0,
        'high': data[2] / 100.0,
        'low': data[3] / 100.0,
        'close': data[4] / 100.0,
        'amount': data[5],
        'volume': data[6]
      })

    return pd.DataFrame(result)
分钟数据读取

import os
import struct

def read_minute_data(file_path):
  with open(file_path, 'rb') as f:
    buf = f.read()
    size = len(buf)
    rec_count = int(size / 32)

    result = []
    for i in range(rec_count):
      data = unpack('=IIIIIfII', buf[i * 32:(i + 1) * 32])
      result.append({
        'time': data[0],
        'open': data[1] / 100.0,
        'high': data[2] / 100.0,
        'low': data[3] / 100.0,
        'close': data[4] / 100.0,
        'amount': data[5],
        'volume': data[6]
      })

    return pd.DataFrame(result)
使用示例

# 读取日线数据
day_data = read_day_data('path/to/stock.day')
print(day_data.head())

# 读取分钟数据
minute_data = read_minute_data('path/to/stock.lc1')
print(minute_data.head())
