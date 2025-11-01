#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API映射配置文件
根据byapi_info_all.md文档中的接口定义，提供API接口的类型、名称、URL、描述及返回字段映射。
"""

# API映射配置 - 按接口类型分类
API_MAPPING_TYPE = {
    "股票列表": {
        "股票列表": {
            "api_url": "http://api.biyingapi.com/hslt/list/您的licence",
            "description": "获取基础的股票代码和名称，用于后续接口的参数传入。",
            "fields": {
                "dm": {
                    "data_type": "string",
                    "name": "股票代码",
                    "description": "如：000001"
                },
                "mc": {
                    "data_type": "string",
                    "name": "股票名称",
                    "description": "如：平安银行"
                },
                "jys": {
                    "data_type": "string",
                    "name": "交易所",
                    "description": "sh表示上证，sz表示深证"
                }
            }
        },
        "新股日历": {
            "api_url": "http://api.biyingapi.com/hslt/new/您的licence",
            "description": "新股日历，按申购日期倒序。",
            "fields": {
                "zqdm": {
                    "data_type": "string",
                    "name": "股票代码",
                    "description": ""
                },
                "zqjc": {
                    "data_type": "string",
                    "name": "股票简称",
                    "description": ""
                },
                "sgdm": {
                    "data_type": "string",
                    "name": "申购代码",
                    "description": ""
                },
                "fxsl": {
                    "data_type": "number",
                    "name": "发行总数（股）",
                    "description": ""
                },
                "swfxsl": {
                    "data_type": "number",
                    "name": "网上发行（股）",
                    "description": ""
                },
                "sgsx": {
                    "data_type": "number",
                    "name": "申购上限（股）",
                    "description": ""
                },
                "dgsz": {
                    "data_type": "number",
                    "name": "顶格申购需配市值(元)",
                    "description": ""
                },
                "sgrq": {
                    "data_type": "string",
                    "name": "申购日期",
                    "description": ""
                },
                "fxjg": {
                    "data_type": "number",
                    "name": "发行价格（元）",
                    "description": "null为“未知”"
                },
                "zxj": {
                    "data_type": "number",
                    "name": "最新价（元）",
                    "description": "null为“未知”"
                },
                "srspj": {
                    "data_type": "number",
                    "name": "首日收盘价（元）",
                    "description": "null为“未知”"
                },
                "zqgbrq": {
                    "data_type": "string",
                    "name": "中签号公布日",
                    "description": "null为未知"
                },
                "zqjkrq": {
                    "data_type": "string",
                    "name": "中签缴款日",
                    "description": "null为未知"
                },
                "ssrq": {
                    "data_type": "string",
                    "name": "上市日期",
                    "description": "null为未知"
                },
                "syl": {
                    "data_type": "number",
                    "name": "发行市盈率",
                    "description": "null为“未知”"
                },
                "hysyl": {
                    "data_type": "number",
                    "name": "行业市盈率",
                    "description": ""
                },
                "wszql": {
                    "data_type": "number",
                    "name": "中签率（%）",
                    "description": "null为“未知”"
                },
                "yzbsl": {
                    "data_type": "number",
                    "name": "连续一字板数量",
                    "description": "null为“未知”"
                },
                "zf": {
                    "data_type": "number",
                    "name": "涨幅（%）",
                    "description": "null为“未知”"
                },
                "yqhl": {
                    "data_type": "number",
                    "name": "每中一签获利（元）",
                    "description": "null为“未知”"
                },
                "zyyw": {
                    "data_type": "string",
                    "name": "主营业务",
                    "description": ""
                }
            }
        }
    },
    "指数行业概念": {
        "指数、行业、概念树": {
            "api_url": "http://api.biyingapi.com/hszg/list/您的licence",
            "description": "获取指数、行业、概念（包括基金，债券，美股，外汇，期货，黄金等的代码），其中isleaf为1（叶子节点）的记录的code（代码）可以作为下方接口的参数传入，从而得到某个指数、行业、概念下的相关股票。",
            "fields": {
                "name": {
                    "data_type": "string",
                    "name": "名称",
                    "description": ""
                },
                "code": {
                    "data_type": "string",
                    "name": "代码",
                    "description": ""
                },
                "type1": {
                    "data_type": "number",
                    "name": "一级分类",
                    "description": "0:A股,1:创业板,2:科创板,3:基金,4:香港股市,5:债券,6:美国股市,7:外汇,8:期货,9:黄金,10:英国股市"
                },
                "type2": {
                    "data_type": "number",
                    "name": "二级分类",
                    "description": "0:A股-申万行业,1:A股-申万二级,2:A股-热门概念,3:A股-概念板块,4:A股-地域板块,5:A股-证监会行业,6:A股-分类,7:A股-指数成分,8:A股-风险警示,9:A股-大盘指数,10:A股-次新股,11:A股-沪港通,12:A股-深港通,13:基金-封闭式基金,14:基金-开放式基金,15:基金-货币型基金,16:基金-ETF基金净值,17:基金-ETF基金行情,18:基金-LOF基金行情,21:基金-科创板基金,22:香港股市-恒生行业,23:香港股市-全部港股,24:香港股市-热门港股,25:香港股市-蓝筹股,26:香港股市-红筹股,27:香港股市-国企股,28:香港股市-创业板,29:香港股市-指数,30:香港股市-A+H,31:香港股市-窝轮,32:香港股市-ADR,33:香港股市-沪港通,34:香港股市-深港通,35:香港股市-中华系列指数,36:债券-沪深债券,37:债券-深市债券,38:债券-沪市债券,39:债券-沪深可转债,40:美国股市-中国概念股,41:美国股市-科技类,42:美国股市-金融类,43:美国股市-制造零售类,44:美国股市-汽车能源类,45:美国股市-媒体类,46:美国股市-医药食品类,48:外汇-基本汇率,49:外汇-热门汇率,50:外汇-所有汇率,51:外汇-交叉盘汇率,52:外汇-美元相关汇率,53:外汇-人民币相关汇率,54:期货-全球期货,55:期货-中国金融期货交易所,56:期货-上海期货交易所,57:期货-大连商品交易所,58:期货-郑州商品交易所,59:黄金-黄金现货,60:黄金-黄金期货"
                },
                "level": {
                    "data_type": "number",
                    "name": "层级",
                    "description": "从0开始，根节点为0，二级节点为1，以此类推"
                },
                "pcode": {
                    "data_type": "string",
                    "name": "父节点代码",
                    "description": ""
                },
                "pname": {
                    "data_type": "string",
                    "name": "父节点名称",
                    "description": ""
                },
                "isleaf": {
                    "data_type": "number",
                    "name": "是否为叶子节点",
                    "description": "0：否，1：是"
                }
            }
        },
        "根据指数、行业、概念找相关股票": {
            "api_url": "http://api.biyingapi.com/hszg/gg/指数、行业、概念代码/您的licence",
            "description": "根据“指数、行业、概念树”接口得到的代码作为参数，得到相关的股票。",
            "fields": {
                "dm": {
                    "data_type": "string",
                    "name": "代码",
                    "description": "根据接口参数可能是A股股票代码，也可能是其他指数、行业、概念的股票代码"
                },
                "mc": {
                    "data_type": "string",
                    "name": "名称",
                    "description": ""
                },
                "jys": {
                    "data_type": "string",
                    "name": "交易所",
                    "description": "sh表示上证，sz表示深证"
                }
            }
        },
        "根据股票找相关指数、行业、概念": {
            "api_url": "http://api.biyingapi.com/hszg/zg/股票代码(如000001)/您的licence",
            "description": "根据股票代码获取相关的指数、行业、概念。",
            "fields": {
                "code": {
                    "data_type": "string",
                    "name": "指数、行业、概念代码",
                    "description": "如：sw2_650300"
                },
                "name": {
                    "data_type": "string",
                    "name": "指数、行业、概念名称",
                    "description": "如：沪深股市-申万二级-国防军工-地面兵装"
                }
            }
        }
    },
    "涨跌股池": {
        "涨停股池": {
            "api_url": "http://api.biyingapi.com/hslt/ztgc/日期(如2020-01-15)/您的licence",
            "description": "根据日期（格式yyyy-MM-dd，从2019-11-28开始到现在的每个交易日）作为参数，得到每天的涨停股票列表，根据封板时间升序。",
            "fields": {
                "dm": {
                    "data_type": "string",
                    "name": "代码",
                    "description": "股票代码"
                },
                "mc": {
                    "data_type": "string",
                    "name": "名称",
                    "description": "股票名称"
                },
                "p": {
                    "data_type": "number",
                    "name": "价格（元）",
                    "description": "当前价格"
                },
                "zf": {
                    "data_type": "number",
                    "name": "涨幅（%）",
                    "description": "涨跌幅百分比"
                },
                "cje": {
                    "data_type": "number",
                    "name": "成交额（元）",
                    "description": "成交额"
                },
                "lt": {
                    "data_type": "number",
                    "name": "流通市值（元）",
                    "description": "流通市值"
                },
                "zsz": {
                    "data_type": "number",
                    "name": "总市值（元）",
                    "description": "总市值"
                },
                "hs": {
                    "data_type": "number",
                    "name": "换手率（%）",
                    "description": "换手率百分比"
                },
                "lbc": {
                    "data_type": "number",
                    "name": "连板数",
                    "description": "连续涨停板数量"
                },
                "fbt": {
                    "data_type": "string",
                    "name": "首次封板时间",
                    "description": "HH:mm:ss格式"
                },
                "lbt": {
                    "data_type": "string",
                    "name": "最后封板时间",
                    "description": "HH:mm:ss格式"
                },
                "zj": {
                    "data_type": "number",
                    "name": "封板资金（元）",
                    "description": "封板资金量"
                },
                "zbc": {
                    "data_type": "number",
                    "name": "炸板次数",
                    "description": "炸板次数"
                },
                "tj": {
                    "data_type": "string",
                    "name": "涨停统计",
                    "description": "x天/y板格式"
                }
            }
        },
        "跌停股池": {
            "api_url": "http://api.biyingapi.com/hslt/dtgc/日期(如2020-01-15)/您的licence",
            "description": "根根据日期（格式yyyy-MM-dd，从2019-11-28开始到现在的每个交易日）作为参数，得到每天的跌停股票列表，根据封单资金升序。",
            "fields": {
                "dm": {
                    "data_type": "string",
                    "name": "代码",
                    "description": "股票代码"
                },
                "mc": {
                    "data_type": "string",
                    "name": "名称",
                    "description": "股票名称"
                },
                "p": {
                    "data_type": "number",
                    "name": "价格（元）",
                    "description": "当前价格"
                },
                "zf": {
                    "data_type": "number",
                    "name": "跌幅（%）",
                    "description": "跌幅百分比"
                },
                "cje": {
                    "data_type": "number",
                    "name": "成交额（元）",
                    "description": "成交额"
                },
                "lt": {
                    "data_type": "number",
                    "name": "流通市值（元）",
                    "description": "流通市值"
                },
                "zsz": {
                    "data_type": "number",
                    "name": "总市值（元）",
                    "description": "总市值"
                },
                "pe": {
                    "data_type": "number",
                    "name": "动态市盈率",
                    "description": "动态市盈率"
                },
                "hs": {
                    "data_type": "number",
                    "name": "换手率（%）",
                    "description": "换手率百分比"
                },
                "lbc": {
                    "data_type": "number",
                    "name": "连续跌停次数",
                    "description": "连续跌停次数"
                },
                "lbt": {
                    "data_type": "string",
                    "name": "最后封板时间",
                    "description": "HH:mm:ss格式"
                },
                "zj": {
                    "data_type": "number",
                    "name": "封单资金（元）",
                    "description": "封单资金量"
                },
                "fba": {
                    "data_type": "number",
                    "name": "板上成交额（元）",
                    "description": "板上成交额"
                },
                "zbc": {
                    "data_type": "number",
                    "name": "开板次数",
                    "description": "开板次数"
                }
            }
        },
        "强势股池": {
            "api_url": "http://api.biyingapi.com/hslt/qsgc/日期(如2020-01-15)/您的licence",
            "description": "根据日期（格式yyyy-MM-dd，从2019-11-28开始到现在的每个交易日）作为参数，得到每天的次新股票列表，根据开板几日升序。",
            "fields": {
                "dm": {
                    "data_type": "string",
                    "name": "代码",
                    "description": "股票代码"
                },
                "mc": {
                    "data_type": "string",
                    "name": "名称",
                    "description": "股票名称"
                },
                "p": {
                    "data_type": "number",
                    "name": "价格（元）",
                    "description": "当前价格"
                },
                "ztp": {
                    "data_type": "number",
                    "name": "涨停价（元）",
                    "description": "涨停价格"
                },
                "zf": {
                    "data_type": "number",
                    "name": "涨幅（%）",
                    "description": "涨幅百分比"
                },
                "cje": {
                    "data_type": "number",
                    "name": "成交额（元）",
                    "description": "成交额"
                },
                "lt": {
                    "data_type": "number",
                    "name": "流通市值（元）",
                    "description": "流通市值"
                },
                "zsz": {
                    "data_type": "number",
                    "name": "总市值（元）",
                    "description": "总市值"
                },
                "nh": {
                    "data_type": "number",
                    "name": "是否新高",
                    "description": "0：否，1：是"
                },
                "lb": {
                    "data_type": "number",
                    "name": "量比",
                    "description": "量比指标"
                },
                "hs": {
                    "data_type": "number",
                    "name": "换手率（%）",
                    "description": "换手率百分比"
                },
                "tj": {
                    "data_type": "string",
                    "name": "涨停统计",
                    "description": "x天/y板格式"
                }
            }
        },
        "次新股池": {
            "api_url": "http://api.biyingapi.com/hslt/cxgc/日期(如2020-01-15)/您的licence",
            "description": "根据日期得到每天的次新股票列表。",
            "fields": {
                "dm": {
                    "data_type": "string",
                    "name": "代码",
                    "description": "股票代码"
                },
                "mc": {
                    "data_type": "string",
                    "name": "名称",
                    "description": "股票名称"
                },
                "p": {
                    "data_type": "number",
                    "name": "价格（元）",
                    "description": "当前价格"
                },
                "ztp": {
                    "data_type": "number",
                    "name": "涨停价（元）",
                    "description": "无涨停价为null"
                },
                "zf": {
                    "data_type": "number",
                    "name": "涨跌幅（%）",
                    "description": "涨跌幅百分比"
                },
                "cje": {
                    "data_type": "number",
                    "name": "成交额（元）",
                    "description": "成交额"
                },
                "lt": {
                    "data_type": "number",
                    "name": "流通市值（元）",
                    "description": "流通市值"
                },
                "zsz": {
                    "data_type": "number",
                    "name": "总市值（元）",
                    "description": "总市值"
                },
                "nh": {
                    "data_type": "number",
                    "name": "是否新高",
                    "description": "0：否，1：是"
                },
                "hs": {
                    "data_type": "number",
                    "name": "转手率（%）",
                    "description": "换手率百分比"
                },
                "tj": {
                    "data_type": "string",
                    "name": "涨停统计",
                    "description": "x天/y板格式"
                },
                "kb": {
                    "data_type": "number",
                    "name": "开板几日",
                    "description": "开板几日"
                },
                "od": {
                    "data_type": "string",
                    "name": "开板日期",
                    "description": "yyyyMMdd格式"
                },
                "ipod": {
                    "data_type": "string",
                    "name": "上市日期",
                    "description": "yyyyMMdd格式"
                }
            }
        },
        "炸板股池": {
            "api_url": "http://api.biyingapi.com/hslt/zbgc/日期(如2020-01-15)/您的licence",
            "description": "根据日期得到每天的炸板股票列表。",
            "fields": {
                "dm": {
                    "data_type": "string",
                    "name": "代码",
                    "description": "股票代码"
                },
                "mc": {
                    "data_type": "string",
                    "name": "名称",
                    "description": "股票名称"
                },
                "p": {
                    "data_type": "number",
                    "name": "价格（元）",
                    "description": "当前价格"
                },
                "ztp": {
                    "data_type": "number",
                    "name": "涨停价（元）",
                    "description": "涨停价格"
                },
                "zf": {
                    "data_type": "number",
                    "name": "涨跌幅（%）",
                    "description": "涨跌幅百分比"
                },
                "cje": {
                    "data_type": "number",
                    "name": "成交额（元）",
                    "description": "成交额"
                },
                "lt": {
                    "data_type": "number",
                    "name": "流通市值（元）",
                    "description": "流通市值"
                },
                "zsz": {
                    "data_type": "number",
                    "name": "总市值（元）",
                    "description": "总市值"
                },
                "zs": {
                    "data_type": "number",
                    "name": "涨速（%）",
                    "description": "涨速百分比"
                },
                "hs": {
                    "data_type": "number",
                    "name": "转手率（%）",
                    "description": "换手率百分比"
                },
                "tj": {
                    "data_type": "string",
                    "name": "涨停统计",
                    "description": "x天/y板格式"
                },
                "fbt": {
                    "data_type": "string",
                    "name": "首次封板时间",
                    "description": "HH:mm:ss格式"
                },
                "zbc": {
                    "data_type": "number",
                    "name": "炸板次数",
                    "description": "炸板次数"
                }
            }
        }
    },
    "上市公司详情": {
        "公司简介": {
            "api_url": "http://api.biyingapi.com/hscp/gsjj/股票代码(如000001)/您的licence",
            "description": "获取上市公司的公司简介信息。",
            "fields":  {
                "name": {
                    "data_type": "string",
                    "name": "公司名称",
                    "description": ""
                },
                "ename": {
                    "data_type": "string",
                    "name": "公司英文名称",
                    "description": ""
                },
                "market": {
                    "data_type": "string",
                    "name": "上市市场",
                    "description": ""
                },
                "idea": {
                    "data_type": "string",
                    "name": "概念及板块",
                    "description": "多个概念由英文逗号分隔"
                },
                "ldate": {
                    "data_type": "string",
                    "name": "上市日期",
                    "description": "格式yyyy-MM-dd"
                },
                "sprice": {
                    "data_type": "string",
                    "name": "发行价格（元）",
                    "description": ""
                },
                "principal": {
                    "data_type": "string",
                    "name": "主承销商",
                    "description": ""
                },
                "rdate": {
                    "data_type": "string",
                    "name": "成立日期",
                    "description": ""
                },
                "rprice": {
                    "data_type": "string",
                    "name": "注册资本",
                    "description": ""
                },
                "instype": {
                    "data_type": "string",
                    "name": "机构类型",
                    "description": ""
                },
                "organ": {
                    "data_type": "string",
                    "name": "组织形式",
                    "description": ""
                },
                "secre": {
                    "data_type": "string",
                    "name": "董事会秘书",
                    "description": ""
                },
                "phone": {
                    "data_type": "string",
                    "name": "公司电话",
                    "description": ""
                },
                "sphone": {
                    "data_type": "string",
                    "name": "董秘电话",
                    "description": ""
                },
                "fax": {
                    "data_type": "string",
                    "name": "公司传真",
                    "description": ""
                },
                "sfax": {
                    "data_type": "string",
                    "name": "董秘传真",
                    "description": ""
                },
                "email": {
                    "data_type": "string",
                    "name": "公司电子邮箱",
                    "description": ""
                },
                "semail": {
                    "data_type": "string",
                    "name": "董秘电子邮箱",
                    "description": ""
                },
                "site": {
                    "data_type": "string",
                    "name": "公司网站",
                    "description": ""
                },
                "post": {
                    "data_type": "string",
                    "name": "邮政编码",
                    "description": ""
                },
                "infosite": {
                    "data_type": "string",
                    "name": "信息披露网址",
                    "description": ""
                },
                "oname": {
                    "data_type": "string",
                    "name": "证券简称更名历史",
                    "description": ""
                },
                "addr": {
                    "data_type": "string",
                    "name": "注册地址",
                    "description": ""
                },
                "oaddr": {
                    "data_type": "string",
                    "name": "办公地址",
                    "description": ""
                },
                "desc": {
                    "data_type": "string",
                    "name": "公司简介",
                    "description": ""
                },
                "bscope": {
                    "data_type": "string",
                    "name": "经营范围",
                    "description": ""
                },
                "printype": {
                    "data_type": "string",
                    "name": "承销方式",
                    "description": ""
                },
                "referrer": {
                    "data_type": "string",
                    "name": "上市推荐人",
                    "description": ""
                },
                "putype": {
                    "data_type": "string",
                    "name": "发行方式",
                    "description": ""
                },
                "pe": {
                    "data_type": "string",
                    "name": "发行市盈率",
                    "description": "按发行后总股本"
                },
                "firgu": {
                    "data_type": "string",
                    "name": "首发前总股本",
                    "description": "（万股）"
                },
                "lastgu": {
                    "data_type": "string",
                    "name": "首发后总股本",
                    "description": "（万股）"
                },
                "realgu": {
                    "data_type": "string",
                    "name": "实际发行量",
                    "description": "（万股）"
                },
                "planm": {
                    "data_type": "string",
                    "name": "预计募集资金",
                    "description": "（万元）"
                },
                "realm": {
                    "data_type": "string",
                    "name": "实际募集资金合计",
                    "description": "（万元）"
                },
                "pubfee": {
                    "data_type": "string",
                    "name": "发行费用总额",
                    "description": "（万元）"
                },
                "collect": {
                    "data_type": "string",
                    "name": "募集资金净额",
                    "description": "（万元）"
                },
                "signfee": {
                    "data_type": "string",
                    "name": "承销费用",
                    "description": "（万元）"
                },
                "pdate": {
                    "data_type": "string",
                    "name": "招股公告日",
                    "description": ""
                }
            }
        },
        "所属指数": {
            "api_url": "http://api.biyingapi.com/hscp/sszs/股票代码(如000001)/您的licence",
            "description": "根据《股票列表》得到的股票代码获取上市公司的所属指数。",
            "fields": {
                "mc": {
                    "data_type": "string",
                    "name": "指数名称",
                    "description": ""
                },
                "dm": {
                    "data_type": "string",
                    "name": "指数代码",
                    "description": ""
                },
                "ind": {
                    "data_type": "string",
                    "name": "进入日期",
                    "description": "yyyy-MM-dd"
                },
                "outd": {
                    "data_type": "string",
                    "name": "退出日期",
                    "description": "yyyy-MM-dd"
                }
            }
        },
        "历届高管成员": {
            "api_url": "http://api.biyingapi.com/hscp/ljgg/股票代码(如000001)/您的licence",
            "description": "获取上市公司历届高管成员信息。",
            "fields": {
                "name": {
                    "data_type": "string",
                    "name": "姓名",
                    "description": ""
                },
                "title": {
                    "data_type": "string",
                    "name": "职务",
                    "description": ""
                },
                "sdate": {
                    "data_type": "string",
                    "name": "起始日期",
                    "description": "yyyy-MM-dd"
                },
                "edate": {
                    "data_type": "string",
                    "name": "终止日期",
                    "description": "yyyy-MM-dd"
                }
            }
        },
        "历届董事会成员": {
            "api_url": "http://api.biyingapi.com/hscp/ljds/股票代码(如000001)/您的licence",
            "description": "根据《股票列表》得到的股票代码获取上市公司的历届董事会成员名单",
            "fields": {
                "name": {
                    "data_type": "string",
                    "name": "姓名",
                    "description": ""
                },
                "title": {
                    "data_type": "string",
                    "name": "职务",
                    "description": ""
                },
                "sdate": {
                    "data_type": "string",
                    "name": "起始日期",
                    "description": "yyyy-MM-dd"
                },
                "edate": {
                    "data_type": "string",
                    "name": "终止日期",
                    "description": "yyyy-MM-dd"
                }
            }
        },
        "历届监事会成员": {
            "api_url": "http://api.biyingapi.com/hscp/ljjj/股票代码(如000001)/您的licence",
            "description": "根据《股票列表》得到的股票代码获取上市公司的历届监事会成员名单",
            "fields": {
                "name": {
                    "data_type": "string",
                    "name": "姓名",
                    "description": ""
                },
                "title": {
                    "data_type": "string",
                    "name": "职务",
                    "description": ""
                },
                "sdate": {
                    "data_type": "string",
                    "name": "起始日期",
                    "description": "yyyy-MM-dd"
                },
                "edate": {
                    "data_type": "string",
                    "name": "终止日期",
                    "description": "yyyy-MM-dd"
                }
            }
        },
        "近年分红": {
            "api_url": "http://api.biyingapi.com/hscp/jnfh/股票代码(如000001)/您的licence",
            "description": "获取上市公司近年分红信息。",
            "fields": {
                "sdate": {
                    "data_type": "string",
                    "name": "公告日期",
                    "description": "yyyy-MM-dd"
                },
                "give": {
                    "data_type": "string",
                    "name": "每10股送股",
                    "description": "(单位：股)"
                },
                "change": {
                    "data_type": "string",
                    "name": "每10股转增",
                    "description": "(单位：股)"
                },
                "send": {
                    "data_type": "string",
                    "name": "每10股派息",
                    "description": "(税前，单位：元)"
                },
                "line": {
                    "data_type": "string",
                    "name": "进度",
                    "description": ""
                },
                "cdate": {
                    "data_type": "string",
                    "name": "除权除息日",
                    "description": "yyyy-MM-dd"
                },
                "edate": {
                    "data_type": "string",
                    "name": "股权登记日",
                    "description": "yyyy-MM-dd"
                },
                "hdate": {
                    "data_type": "string",
                    "name": "红股上市日",
                    "description": "yyyy-MM-dd"
                }
            }
        },
        "近年增发": {
            "api_url": "http://api.biyingapi.com/hscp/jnzf/股票代码(如000001)/您的licence",
            "description": "根据《股票列表》得到的股票代码获取上市公司的近年来的增发情况。按公告日期倒序",
            "fields": {
                "sdate": {
                    "data_type": "string",
                    "name": "公告日期",
                    "description": "yyyy-MM-dd"
                },
                "type": {
                    "data_type": "string",
                    "name": "发行方式",
                    "description": ""
                },
                "price": {
                    "data_type": "string",
                    "name": "发行价格",
                    "description": ""
                },
                "tprice": {
                    "data_type": "string",
                    "name": "实际公司募集资金总额",
                    "description": ""
                },
                "fprice": {
                    "data_type": "string",
                    "name": "发行费用总额",
                    "description": ""
                },
                "amount": {
                    "data_type": "string",
                    "name": "实际发行数量",
                    "description": ""
                }
            }
        },
        "解禁限售": {
            "api_url": "http://api.biyingapi.com/hscp/jjxs/股票代码(如000001)/您的licence",
            "description": "获取上市公司解禁限售信息。",
            "fields": {
                "rdate": {
                    "data_type": "string",
                    "name": "解禁日期",
                    "description": "yyyy-MM-dd"
                },
                "ramount": {
                    "data_type": "number",
                    "name": "解禁数量",
                    "description": "(万股)"
                },
                "rprice": {
                    "data_type": "number",
                    "name": "解禁股流通市值",
                    "description": "(亿元)"
                },
                "batch": {
                    "data_type": "number",
                    "name": "上市批次",
                    "description": ""
                },
                "pdate": {
                    "data_type": "string",
                    "name": "公告日期",
                    "description": "yyyy-MM-dd"
                }
            }
        },
        "近一年各季度利润": {
            "api_url": "http://api.biyingapi.com/hscp/jdlr/股票代码(如000001)/您的licence",
            "description": "根据《股票列表》得到的股票代码获取上市公司近一年各个季度的利润。按截止日期倒序。",
            "fields": {
                "quarter": {
                    "data_type": "string",
                    "name": "季度",
                    "description": ""
                },
                "revenue": {
                    "data_type": "string",
                    "name": "营业收入（元）",
                    "description": ""
                },
                "profit": {
                    "data_type": "string",
                    "name": "净利润（元）",
                    "description": ""
                },
                "growthRate": {
                    "data_type": "string",
                    "name": "同比增长（%）",
                    "description": ""
                }
            }
        },
        "近一年各季度现金流": {
            "api_url": "http://api.biyingapi.com/hscompany/jlxsl/股票代码(如000001)/您的licence",
            "description": "获取上市公司近一年各季度现金流信息。",
            "fields": {
                "quarter": {
                    "data_type": "string",
                    "name": "季度",
                    "description": ""
                },
                "operatingCashFlow": {
                    "data_type": "string",
                    "name": "经营活动现金流（元）",
                    "description": ""
                },
                "investmentCashFlow": {
                    "data_type": "string",
                    "name": "投资活动现金流（元）",
                    "description": ""
                },
                "financingCashFlow": {
                    "data_type": "string",
                    "name": "筹资活动现金流（元）",
                    "description": ""
                }
            }
        },
        "近年业绩预告": {
            "api_url": "http://api.biyingapi.com/hscompany/jlyj/股票代码(如000001)/您的licence",
            "description": "获取上市公司近年业绩预告信息。",
            "fields": {
                "announcementDate": {
                    "data_type": "string",
                    "name": "公告日期",
                    "description": ""
                },
                "forecastPeriod": {
                    "data_type": "string",
                    "name": "预告期间",
                    "description": ""
                },
                "forecastType": {
                    "data_type": "string",
                    "name": "预告类型",
                    "description": ""
                },
                "forecastContent": {
                    "data_type": "string",
                    "name": "预告内容",
                    "description": ""
                },
                "profitRange": {
                    "data_type": "string",
                    "name": "预计净利润范围（元）",
                    "description": ""
                }
            }
        }
    },
    "财务指标": {
        "财务指标": {
            "api_url": "http://api.biyingapi.com/hscompany/cwzb/股票代码(如000001)/您的licence",
            "description": "获取上市公司的财务指标数据。",
            "fields": {
                "date": {
                    "data_type": "string",
                    "name": "日期",
                    "description": ""
                },
                "totalAssets": {
                    "data_type": "string",
                    "name": "总资产（元）",
                    "description": ""
                },
                "totalLiabilities": {
                    "data_type": "string",
                    "name": "总负债（元）",
                    "description": ""
                },
                "shareholdersEquity": {
                    "data_type": "string",
                    "name": "股东权益（元）",
                    "description": ""
                },
                "revenue": {
                    "data_type": "string",
                    "name": "营业收入（元）",
                    "description": ""
                },
                "profit": {
                    "data_type": "string",
                    "name": "净利润（元）",
                    "description": ""
                },
                "roe": {
                    "data_type": "string",
                    "name": "净资产收益率（%）",
                    "description": ""
                },
                "roa": {
                    "data_type": "string",
                    "name": "总资产收益率（%）",
                    "description": ""
                },
                "debtRatio": {
                    "data_type": "string",
                    "name": "资产负债率（%）",
                    "description": ""
                },
                "grossMargin": {
                    "data_type": "string",
                    "name": "毛利率（%）",
                    "description": ""
                },
                "netMargin": {
                    "data_type": "string",
                    "name": "净利率（%）",
                    "description": ""
                },
                "eps": {
                    "data_type": "string",
                    "name": "每股收益（元）",
                    "description": ""
                },
                "bps": {
                    "data_type": "string",
                    "name": "每股净资产（元）",
                    "description": ""
                },
                "cfps": {
                    "data_type": "string",
                    "name": "每股现金流（元）",
                    "description": ""
                }
            }
        }
    },
    "十大股东": {
        "十大股东": {
            "api_url": "http://api.biyingapi.com/hscompany/sdgd/股票代码(如000001)/您的licence",
            "description": "获取上市公司的十大股东信息。",
            "fields": {
                "shareholderName": {
                    "data_type": "string",
                    "name": "股东名称",
                    "description": ""
                },
                "shareholdingRatio": {
                    "data_type": "string",
                    "name": "持股比例（%）",
                    "description": ""
                },
                "shareholdingQuantity": {
                    "data_type": "string",
                    "name": "持股数量（股）",
                    "description": ""
                },
                "shareholdingChange": {
                    "data_type": "string",
                    "name": "持股变动（股）",
                    "description": ""
                },
                "shareholdingType": {
                    "data_type": "string",
                    "name": "股份类型",
                    "description": ""
                },
                "reportDate": {
                    "data_type": "string",
                    "name": "报告日期",
                    "description": ""
                }
            }
        }
    },
    "十大流通股东": {
        "十大流通股东": {
            "api_url": "http://api.biyingapi.com/hscompany/sdltgd/股票代码(如000001)/您的licence",
            "description": "获取上市公司的十大流通股东信息。",
            "fields": {
                "shareholderName": {
                    "data_type": "string",
                    "name": "股东名称",
                    "description": ""
                },
                "shareholdingRatio": {
                    "data_type": "string",
                    "name": "持股比例（%）",
                    "description": ""
                },
                "shareholdingQuantity": {
                    "data_type": "string",
                    "name": "持股数量（股）",
                    "description": ""
                },
                "shareholdingChange": {
                    "data_type": "string",
                    "name": "持股变动（股）",
                    "description": ""
                },
                "shareholdingType": {
                    "data_type": "string",
                    "name": "股份类型",
                    "description": ""
                },
                "reportDate": {
                    "data_type": "string",
                    "name": "报告日期",
                    "description": ""
                }
            }
        }
    },
    "股东变化趋势": {
        "股东变化趋势": {
            "api_url": "http://api.biyingapi.com/hscompany/gdbs/股票代码(如000001)/您的licence",
            "description": "获取上市公司的股东变化趋势信息。",
            "fields": {
                "reportDate": {
                    "data_type": "string",
                    "name": "报告日期",
                    "description": ""
                },
                "shareholderCount": {
                    "data_type": "string",
                    "name": "股东户数（户）",
                    "description": ""
                },
                "avgShareholding": {
                    "data_type": "string",
                    "name": "户均持股（股）",
                    "description": ""
                }
            }
        }
    },
    "实时交易数据": {
        "实时交易(公开数据)": {
            "api_url": "http://api.biyingapi.com/hsmarket/sj/股票代码(如000001)/您的licence",
            "description": "获取股票的实时交易数据（公开数据）。",
            "fields": {
                "code": {
                    "data_type": "string",
                    "name": "股票代码",
                    "description": ""
                },
                "name": {
                    "data_type": "string",
                    "name": "股票名称",
                    "description": ""
                },
                "price": {
                    "data_type": "string",
                    "name": "最新价",
                    "description": ""
                },
                "open": {
                    "data_type": "string",
                    "name": "今开价",
                    "description": ""
                },
                "close": {
                    "data_type": "string",
                    "name": "昨收价",
                    "description": ""
                },
                "high": {
                    "data_type": "string",
                    "name": "最高价",
                    "description": ""
                },
                "low": {
                    "data_type": "string",
                    "name": "最低价",
                    "description": ""
                },
                "volume": {
                    "data_type": "string",
                    "name": "成交量",
                    "description": ""
                },
                "amount": {
                    "data_type": "string",
                    "name": "成交额",
                    "description": ""
                },
                "zf": {
                    "data_type": "string",
                    "name": "涨跌幅",
                    "description": ""
                }
            }
        },
        "当天逐笔交易": {
            "api_url": "http://api.biyingapi.com/hsmarket/zb/股票代码(如000001)/您的licence",
            "description": "获取股票的当天逐笔交易数据。",
            "fields": {
                "time": {
                    "data_type": "string",
                    "name": "时间",
                    "description": ""
                },
                "price": {
                    "data_type": "string",
                    "name": "价格",
                    "description": ""
                },
                "volume": {
                    "data_type": "string",
                    "name": "成交量",
                    "description": ""
                },
                "amount": {
                    "data_type": "string",
                    "name": "成交额",
                    "description": ""
                },
                "type": {
                    "data_type": "string",
                    "name": "交易类型",
                    "description": ""
                }
            }
        },
        "实时交易数据": {
            "api_url": "http://api.biyingapi.com/hsmarket/sj/股票代码(如000001)/您的licence",
            "description": "获取股票的实时交易数据。",
            "fields": {
                "code": {
                    "data_type": "string",
                    "name": "股票代码",
                    "description": ""
                },
                "name": {
                    "data_type": "string",
                    "name": "股票名称",
                    "description": ""
                },
                "price": {
                    "data_type": "string",
                    "name": "最新价",
                    "description": ""
                },
                "open": {
                    "data_type": "string",
                    "name": "今开价",
                    "description": ""
                },
                "close": {
                    "data_type": "string",
                    "name": "昨收价",
                    "description": ""
                },
                "high": {
                    "data_type": "string",
                    "name": "最高价",
                    "description": ""
                },
                "low": {
                    "data_type": "string",
                    "name": "最低价",
                    "description": ""
                },
                "volume": {
                    "data_type": "string",
                    "name": "成交量",
                    "description": ""
                },
                "amount": {
                    "data_type": "string",
                    "name": "成交额",
                    "description": ""
                },
                "zf": {
                    "data_type": "string",
                    "name": "涨跌幅",
                    "description": ""
                }
            }
        },
        "实时交易数据（多股）": {
            "api_url": "http://api.biyingapi.com/hsmarket/dgs/股票代码1,股票代码2/您的licence",
            "description": "同时获取多只股票的实时交易数据。",
            "fields": {
                "code": {
                    "data_type": "string",
                    "name": "股票代码",
                    "description": "股票代码"
                },
                "name": {
                    "data_type": "string",
                    "name": "股票名称",
                    "description": "股票名称"
                },
                "price": {
                    "data_type": "string",
                    "name": "最新价",
                    "description": "当前最新价格"
                },
                "open": {
                    "data_type": "string",
                    "name": "今开价",
                    "description": "今日开盘价格"
                },
                "close": {
                    "data_type": "string",
                    "name": "昨收价",
                    "description": "昨日收盘价格"
                },
                "high": {
                    "data_type": "string",
                    "name": "最高价",
                    "description": "今日最高价"
                },
                "low": {
                    "data_type": "string",
                    "name": "最低价",
                    "description": "今日最低价"
                },
                "volume": {
                    "data_type": "string",
                    "name": "成交量",
                    "description": "今日成交量"
                },
                "amount": {
                    "data_type": "string",
                    "name": "成交额",
                    "description": "今日成交额"
                },
                "zf": {
                    "data_type": "string",
                    "name": "涨跌幅",
                    "description": "涨跌幅百分比"
                },
                "avg": {
                    "data_type": "string",
                    "name": "均价",
                    "description": "今日均价"
                }
            }
        },
        "资金流向数据": {
            "api_url": "http://api.biyingapi.com/hsmarket/zj/股票代码(如000001)/您的licence",
            "description": "获取股票的资金流向数据。",
            "fields": {
                "t": {
                    "data_type": "string",
                    "name": "时间",
                    "description": "数据更新时间"
                },
                "zmbzds": {
                    "data_type": "string",
                    "name": "主板变动手数",
                    "description": "主板变动手数"
                },
                "zmjye": {
                    "data_type": "string",
                    "name": "主板交易金额",
                    "description": "主板交易金额"
                },
                "zmbzmoney": {
                    "data_type": "string",
                    "name": "主板变动金额",
                    "description": "主板变动金额"
                },
                "zmbzper": {
                    "data_type": "string",
                    "name": "主板变动比例",
                    "description": "主板变动比例"
                },
                "zmbzmoneyin": {
                    "data_type": "string",
                    "name": "主板流入金额",
                    "description": "主板流入金额"
                },
                "zmbzmoneyout": {
                    "data_type": "string",
                    "name": "主板流出金额",
                    "description": "主板流出金额"
                },
                "dnbzds": {
                    "data_type": "string",
                    "name": "大单变动手数",
                    "description": "大单变动手数"
                },
                "dnbzmoney": {
                    "data_type": "string",
                    "name": "大单变动金额",
                    "description": "大单变动金额"
                },
                "dnbzper": {
                    "data_type": "string",
                    "name": "大单变动比例",
                    "description": "大单变动比例"
                },
                "dnbzmoneyin": {
                    "data_type": "string",
                    "name": "大单流入金额",
                    "description": "大单流入金额"
                },
                "dnbzmoneyout": {
                    "data_type": "string",
                    "name": "大单流出金额",
                    "description": "大单流出金额"
                },
                "zbzds": {
                    "data_type": "string",
                    "name": "中变动手数",
                    "description": "中变动手数"
                },
                "zbzmoney": {
                    "data_type": "string",
                    "name": "中变动金额",
                    "description": "中变动金额"
                },
                "zbzper": {
                    "data_type": "string",
                    "name": "中变动比例",
                    "description": "中变动比例"
                },
                "zbzmoneyin": {
                    "data_type": "string",
                    "name": "中单流入金额",
                    "description": "中单流入金额"
                },
                "zbzmoneyout": {
                    "data_type": "string",
                    "name": "中单流出金额",
                    "description": "中单流出金额"
                },
                "xbzds": {
                    "data_type": "string",
                    "name": "小变动手数",
                    "description": "小变动手数"
                },
                "xbzmoney": {
                    "data_type": "string",
                    "name": "小变动金额",
                    "description": "小变动金额"
                },
                "xbzper": {
                    "data_type": "string",
                    "name": "小变动比例",
                    "description": "小变动比例"
                },
                "xbzmoneyin": {
                    "data_type": "string",
                    "name": "小单流入金额",
                    "description": "小单流入金额"
                },
                "xbzmoneyout": {
                    "data_type": "string",
                    "name": "小单流出金额",
                    "description": "小单流出金额"
                },
                "zmbzmoneyinrate": {
                    "data_type": "string",
                    "name": "主板流入比例",
                    "description": "主板流入比例"
                },
                "zmbzmoneyoutrate": {
                    "data_type": "string",
                    "name": "主板流出比例",
                    "description": "主板流出比例"
                },
                "dnbzmoneyinrate": {
                    "data_type": "string",
                    "name": "大单流入比例",
                    "description": "大单流入比例"
                },
                "dnbzmoneyoutrate": {
                    "data_type": "string",
                    "name": "大单流出比例",
                    "description": "大单流出比例"
                },
                "zbzmoneyinrate": {
                    "data_type": "string",
                    "name": "中单流入比例",
                    "description": "中单流入比例"
                },
                "zbzmoneyoutrate": {
                    "data_type": "string",
                    "name": "中单流出比例",
                    "description": "中单流出比例"
                },
                "xbzmoneyinrate": {
                    "data_type": "string",
                    "name": "小单流入比例",
                    "description": "小单流入比例"
                },
                "xbzmoneyoutrate": {
                    "data_type": "string",
                    "name": "小单流出比例",
                    "description": "小单流出比例"
                }
            }
        },
        "买卖五档盘口": {
            "api_url": "http://api.biyingapi.com/hsmarket/mw5/股票代码(如000001)/您的licence",
            "description": "获取股票的买卖五档盘口数据。",
            "fields": {
                "time": {
                    "data_type": "string",
                    "name": "更新时间",
                    "description": "数据更新时间"
                },
                "code": {
                    "data_type": "string",
                    "name": "股票代码",
                    "description": "股票代码"
                },
                "name": {
                    "data_type": "string",
                    "name": "股票名称",
                    "description": "股票名称"
                },
                "open": {
                    "data_type": "string",
                    "name": "今开价",
                    "description": "今日开盘价格"
                },
                "close": {
                    "data_type": "string",
                    "name": "昨收价",
                    "description": "昨日收盘价格"
                },
                "price": {
                    "data_type": "string",
                    "name": "最新价",
                    "description": "当前最新价格"
                },
                "high": {
                    "data_type": "string",
                    "name": "最高价",
                    "description": "今日最高价"
                },
                "low": {
                    "data_type": "string",
                    "name": "最低价",
                    "description": "今日最低价"
                },
                "volume": {
                    "data_type": "string",
                    "name": "成交量",
                    "description": "今日成交量"
                },
                "amount": {
                    "data_type": "string",
                    "name": "成交额",
                    "description": "今日成交额"
                },
                "asks": {
                    "data_type": "array",
                    "name": "卖盘",
                    "description": "卖一到卖五价格和数量"
                },
                "bids": {
                    "data_type": "array",
                    "name": "买盘",
                    "description": "买一到买五价格和数量"
                }
            }
        }
    },
    "行情数据": {
        "最新分时交易": {
            "api_url": "http://api.biyingapi.com/hsmarket/fs/股票代码(如000001)/您的licence",
            "description": "获取股票的最新分时交易数据。",
            "fields": {
                "time": {
                    "data_type": "string",
                    "name": "时间",
                    "description": "交易时间"
                },
                "price": {
                    "data_type": "string",
                    "name": "价格",
                    "description": "交易价格"
                },
                "volume": {
                    "data_type": "string",
                    "name": "成交量",
                    "description": "成交量"
                },
                "amount": {
                    "data_type": "string",
                    "name": "成交额",
                    "description": "成交额"
                }
            }
        },
        "历史分时交易": {
            "api_url": "http://api.biyingapi.com/hsmarket/lfs/股票代码(如000001)/日期(如2020-01-15)/您的licence",
            "description": "获取股票的历史分时交易数据。",
            "fields": {
                "time": {
                    "data_type": "string",
                    "name": "时间",
                    "description": "交易时间"
                },
                "price": {
                    "data_type": "string",
                    "name": "价格",
                    "description": "交易价格"
                },
                "volume": {
                    "data_type": "string",
                    "name": "成交量",
                    "description": "成交量"
                },
                "amount": {
                    "data_type": "string",
                    "name": "成交额",
                    "description": "成交额"
                }
            }
        },
        "历史涨跌停价格": {
            "api_url": "http://api.biyingapi.com/hsmarket/ztjg/股票代码(如000001)/您的licence",
            "description": "获取股票的历史涨跌停价格数据。",
            "fields": {
                "t": {
                    "data_type": "string",
                    "name": "交易日期",
                    "description": "交易日期"
                },
                "h": {
                    "data_type": "string",
                    "name": "涨停价格",
                    "description": "涨停价格"
                },
                "l": {
                    "data_type": "string",
                    "name": "跌停价格",
                    "description": "跌停价格"
                }
            }
        },
        "行情指标": {
            "api_url": "http://api.biyingapi.com/hsmarket/hqzb/股票代码(如000001)/您的licence",
            "description": "获取股票的实时行情指标数据。",
            "fields": {
                "time": {
                    "data_type": "string",
                    "name": "更新时间",
                    "description": "数据更新时间"
                },
                "lb": {
                    "data_type": "string",
                    "name": "量比",
                    "description": "量比指标"
                },
                "om": {
                    "data_type": "string",
                    "name": "1分钟涨速",
                    "description": "1分钟涨速指标"
                },
                "tm": {
                    "data_type": "string",
                    "name": "5分钟涨速",
                    "description": "5分钟涨速指标"
                },
                "fm": {
                    "data_type": "string",
                    "name": "15分钟涨速",
                    "description": "15分钟涨速指标"
                },
                "sm": {
                    "data_type": "string",
                    "name": "30分钟涨速",
                    "description": "30分钟涨速指标"
                },
                "hm": {
                    "data_type": "string",
                    "name": "60分钟涨速",
                    "description": "60分钟涨速指标"
                },
                "zs": {
                    "data_type": "string",
                    "name": "涨速",
                    "description": "涨速指标"
                },
                "hs": {
                    "data_type": "string",
                    "name": "换手率(%)",
                    "description": "换手率百分比"
                },
                "sj": {
                    "data_type": "string",
                    "name": "振幅(%)",
                    "description": "振幅百分比"
                },
                "pe": {
                    "data_type": "string",
                    "name": "市盈率(TTM)",
                    "description": "市盈率(TTM)指标"
                },
                "pb": {
                    "data_type": "string",
                    "name": "市净率",
                    "description": "市净率指标"
                },
                "ps": {
                    "data_type": "string",
                    "name": "市销率",
                    "description": "市销率指标"
                },
                "pcf": {
                    "data_type": "string",
                    "name": "市现率",
                    "description": "市现率指标"
                },
                "lt": {
                    "data_type": "string",
                    "name": "流通市值(元)",
                    "description": "流通市值"
                },
                "zsz": {
                    "data_type": "string",
                    "name": "总市值(元)",
                    "description": "总市值"
                }
            }
        },
        "股票基础信息": {
            "api_url": "http://api.biyingapi.com/hsmarket/jcxx/股票代码(如000001)/您的licence",
            "description": "获取股票的基础信息数据。",
            "fields": {
                "code": {
                    "data_type": "string",
                    "name": "股票代码",
                    "description": "股票代码"
                },
                "name": {
                    "data_type": "string",
                    "name": "股票名称",
                    "description": "股票名称"
                },
                "jys": {
                    "data_type": "string",
                    "name": "交易所",
                    "description": "sh表示上证，sz表示深证"
                },
                "jyzt": {
                    "data_type": "string",
                    "name": "交易状态",
                    "description": "交易状态"
                },
                "market": {
                    "data_type": "string",
                    "name": "市场类型",
                    "description": "市场类型"
                },
                "industry": {
                    "data_type": "string",
                    "name": "所属行业",
                    "description": "所属行业"
                },
                "concept": {
                    "data_type": "string",
                    "name": "所属概念",
                    "description": "所属概念"
                },
                "ltgb": {
                    "data_type": "string",
                    "name": "流通股本(股)",
                    "description": "流通股本"
                },
                "zgb": {
                    "data_type": "string",
                    "name": "总股本(股)",
                    "description": "总股本"
                },
                "ssrq": {
                    "data_type": "string",
                    "name": "上市日期",
                    "description": "上市日期"
                },
                "ssr": {
                    "data_type": "string",
                    "name": "上市板块",
                    "description": "上市板块"
                },
                "ssgs": {
                    "data_type": "string",
                    "name": "上市公司",
                    "description": "上市公司名称"
                },
                "zspj": {
                    "data_type": "string",
                    "name": "最新评级",
                    "description": "最新评级"
                },
                "zspjjg": {
                    "data_type": "string",
                    "name": "最新评级机构",
                    "description": "最新评级机构"
                }
            }
        }
    },
    "财务数据": {
        "资产负债表": {
            "api_url": "http://api.biyingapi.com/hscompany/zb/股票代码(如000001)/您的licence",
            "description": "获取上市公司的资产负债表数据。",
            "fields": {
                "reportDate": {
                    "data_type": "string",
                    "name": "报告日期",
                    "description": ""
                },
                "currency": {
                    "data_type": "string",
                    "name": "货币单位",
                    "description": ""
                },
                "totalAssets": {
                    "data_type": "string",
                    "name": "总资产",
                    "description": ""
                },
                "currentAssets": {
                    "data_type": "string",
                    "name": "流动资产",
                    "description": ""
                },
                "fixedAssets": {
                    "data_type": "string",
                    "name": "固定资产",
                    "description": ""
                },
                "intangibleAssets": {
                    "data_type": "string",
                    "name": "无形资产",
                    "description": ""
                },
                "totalLiabilities": {
                    "data_type": "string",
                    "name": "总负债",
                    "description": ""
                },
                "currentLiabilities": {
                    "data_type": "string",
                    "name": "流动负债",
                    "description": ""
                },
                "longTermLiabilities": {
                    "data_type": "string",
                    "name": "长期负债",
                    "description": ""
                },
                "shareholdersEquity": {
                    "data_type": "string",
                    "name": "股东权益",
                    "description": ""
                },
                "debtRatio": {
                    "data_type": "string",
                    "name": "资产负债率(%)",
                    "description": ""
                },
                "currentRatio": {
                    "data_type": "string",
                    "name": "流动比率",
                    "description": ""
                },
                "quickRatio": {
                    "data_type": "string",
                    "name": "速动比率",
                    "description": ""
                }
            }
        },
        "现金流量表": {
            "api_url": "http://api.biyingapi.com/hscompany/xl/股票代码(如000001)/您的licence",
            "description": "获取上市公司的现金流量表数据。",
            "fields": {
                "reportDate": {
                    "data_type": "string",
                    "name": "报告日期",
                    "description": ""
                },
                "currency": {
                    "data_type": "string",
                    "name": "货币单位",
                    "description": ""
                },
                "operatingCashFlow": {
                    "data_type": "string",
                    "name": "经营活动现金流",
                    "description": ""
                },
                "investmentCashFlow": {
                    "data_type": "string",
                    "name": "投资活动现金流",
                    "description": ""
                },
                "financingCashFlow": {
                    "data_type": "string",
                    "name": "筹资活动现金流",
                    "description": ""
                },
                "netCashFlow": {
                    "data_type": "string",
                    "name": "现金及现金等价物净增加额",
                    "description": ""
                }
            }
        },
        "财务主要指标": {
            "api_url": "http://api.biyingapi.com/hscompany/cwzb/股票代码(如000001)/您的licence",
            "description": "获取上市公司的财务主要指标数据。",
            "fields": {
                "reportDate": {
                    "data_type": "string",
                    "name": "报告日期",
                    "description": ""
                },
                "revenue": {
                    "data_type": "string",
                    "name": "营业收入",
                    "description": ""
                },
                "revenueGrowth": {
                    "data_type": "string",
                    "name": "营收同比增长(%)",
                    "description": ""
                },
                "profit": {
                    "data_type": "string",
                    "name": "净利润",
                    "description": ""
                },
                "profitGrowth": {
                    "data_type": "string",
                    "name": "净利润同比增长(%)",
                    "description": ""
                },
                "eps": {
                    "data_type": "string",
                    "name": "每股收益(元)",
                    "description": ""
                },
                "roe": {
                    "data_type": "string",
                    "name": "净资产收益率(%)",
                    "description": ""
                },
                "roa": {
                    "data_type": "string",
                    "name": "总资产收益率(%)",
                    "description": ""
                },
                "grossMargin": {
                    "data_type": "string",
                    "name": "毛利率(%)",
                    "description": ""
                },
                "netMargin": {
                    "data_type": "string",
                    "name": "净利率(%)",
                    "description": ""
                },
                "debtRatio": {
                    "data_type": "string",
                    "name": "资产负债率(%)",
                    "description": ""
                }
            }
        },
        "公司股本表": {
            "api_url": "http://api.biyingapi.com/hscompany/gb/股票代码(如000001)/您的licence",
            "description": "获取上市公司的公司股本表数据。",
            "fields": {
                "reportDate": {
                    "data_type": "string",
                    "name": "报告日期",
                    "description": ""
                },
                "totalShares": {
                    "data_type": "string",
                    "name": "总股本(股)",
                    "description": ""
                },
                "circulatingShares": {
                    "data_type": "string",
                    "name": "流通股(股)",
                    "description": ""
                },
                "nonCirculatingShares": {
                    "data_type": "string",
                    "name": "非流通股(股)",
                    "description": ""
                },
                "aShares": {
                    "data_type": "string",
                    "name": "A股(股)",
                    "description": ""
                },
                "bShares": {
                    "data_type": "string",
                    "name": "B股(股)",
                    "description": ""
                },
                "hShares": {
                    "data_type": "string",
                    "name": "H股(股)",
                    "description": ""
                },
                "otherShares": {
                    "data_type": "string",
                    "name": "其他股(股)",
                    "description": ""
                }
            }
        }
    },
    "技术指标": {
        "历史分时MACD": {
            "api_url": "http://api.biyingapi.com/hsmarket/macd/股票代码(如000001)/您的licence",
            "description": "获取股票的历史分时MACD指标数据。",
            "fields": {
                "time": {
                    "data_type": "string",
                    "name": "时间",
                    "description": "交易时间"
                },
                "dif": {
                    "data_type": "string",
                    "name": "DIF线",
                    "description": "DIF线数值"
                },
                "dea": {
                    "data_type": "string",
                    "name": "DEA线",
                    "description": "DEA线数值"
                },
                "macd": {
                    "data_type": "string",
                    "name": "MACD柱",
                    "description": "MACD柱数值"
                }
            }
        },
        "历史分时MA": {
            "api_url": "http://api.biyingapi.com/hsmarket/ma/股票代码(如000001)/您的licence",
            "description": "获取股票的历史分时MA指标数据。",
            "fields": {
                "time": {
                    "data_type": "string",
                    "name": "时间",
                    "description": "交易时间"
                },
                "ma5": {
                    "data_type": "string",
                    "name": "MA5",
                    "description": "5日均线数值"
                },
                "ma10": {
                    "data_type": "string",
                    "name": "MA10",
                    "description": "10日均线数值"
                },
                "ma20": {
                    "data_type": "string",
                    "name": "MA20",
                    "description": "20日均线数值"
                },
                "ma30": {
                    "data_type": "string",
                    "name": "MA30",
                    "description": "30日均线数值"
                },
                "ma60": {
                    "data_type": "string",
                    "name": "MA60",
                    "description": "60日均线数值"
                }
            }
        },
        "历史分时BOLL": {
            "api_url": "http://api.biyingapi.com/hsmarket/boll/股票代码(如000001)/您的licence",
            "description": "获取股票的历史分时BOLL指标数据。",
            "fields": {
                "time": {
                    "data_type": "string",
                    "name": "时间",
                    "description": "交易时间"
                },
                "upper": {
                    "data_type": "string",
                    "name": "上轨线",
                    "description": "上轨线数值"
                },
                "middle": {
                    "data_type": "string",
                    "name": "中轨线",
                    "description": "中轨线数值"
                },
                "lower": {
                    "data_type": "string",
                    "name": "下轨线",
                    "description": "下轨线数值"
                }
            }
        },
        "历史分时KDJ": {
            "api_url": "http://api.biyingapi.com/hsmarket/kdj/股票代码(如000001)/您的licence",
            "description": "获取股票的历史分时KDJ指标数据。",
            "fields": {
                "time": {
                    "data_type": "string",
                    "name": "时间",
                    "description": "交易时间"
                },
                "k": {
                    "data_type": "string",
                    "name": "K值",
                    "description": "K值"
                },
                "d": {
                    "data_type": "string",
                    "name": "D值",
                    "description": "D值"
                },
                "j": {
                    "data_type": "string",
                    "name": "J值",
                    "description": "J值"
                }
            }
        }
    },
    "股东总数": {
        "股东总数": {
            "api_url": "http://api.biyingapi.com/hscompany/gdjs/股票代码(如000001)/您的licence",
            "description": "获取上市公司的股东总数信息。",
            "fields": {
                "reportDate": {
                    "data_type": "string",
                    "name": "报告日期",
                    "description": ""
                },
                "shareholderCount": {
                    "data_type": "string",
                    "name": "股东总数（户）",
                    "description": ""
                }
            }
        }
    }
}

# API映射配置 - 按接口URL分类
API_MAPPING_BY_URL = {
    "http://api.biyingapi.com/hslt/list/您的licence": {
        "type": "股票列表",
        "name": "股票列表",
        "description": "获取基础的股票代码和名称，用于后续接口的参数传入。"
    },
    "http://api.biyingapi.com/hslt/new/您的licence": {
        "type": "股票列表",
        "name": "新股日历",
        "description": "新股日历，按申购日期倒序。"
    },
    "http://api.biyingapi.com/hszg/list/您的licence": {
        "type": "指数行业概念",
        "name": "指数、行业、概念树",
        "description": "获取指数、行业、概念（包括基金，债券，美股，外汇，期货，黄金等的代码），其中isleaf为1（叶子节点）的记录的code（代码）可以作为下方接口的参数传入，从而得到某个指数、行业、概念下的相关股票。"
    },
    "http://api.biyingapi.com/hszg/gg/指数、行业、概念代码/您的licence": {
        "type": "指数行业概念",
        "name": "根据指数、行业、概念找相关股票",
        "description": "根据“指数、行业、概念树”接口得到的代码作为参数，得到相关的股票。"
    },
    "http://api.biyingapi.com/hszg/zg/股票代码(如000001)/您的licence": {
        "type": "指数行业概念",
        "name": "根据股票找相关指数、行业、概念",
        "description": "根据股票代码获取相关的指数、行业、概念。"
    },
    "http://api.biyingapi.com/hslt/ztgc/日期(如2020-01-15)/您的licence": {
        "type": "涨跌股池",
        "name": "涨停股池",
        "description": "根据日期得到每天的涨停股票列表。"
    },
    "http://api.biyingapi.com/hslt/dtgc/日期(如2020-01-15)/您的licence": {
        "type": "涨跌股池",
        "name": "跌停股池",
        "description": "根据日期得到每天的跌停股票列表。"
    },
    "http://api.biyingapi.com/hslt/qsgc/日期(如2020-01-15)/您的licence": {
        "type": "涨跌股池",
        "name": "强势股池",
        "description": "根据日期得到每天的强势股票列表。"
    },
    "http://api.biyingapi.com/hslt/cxgc/日期(如2020-01-15)/您的licence": {
        "type": "涨跌股池",
        "name": "次新股池",
        "description": "根据日期得到每天的次新股票列表。"
    },
    "http://api.biyingapi.com/hslt/zbgc/日期(如2020-01-15)/您的licence": {
        "type": "涨跌股池",
        "name": "炸板股池",
        "description": "根据日期得到每天的炸板股票列表。"
    }
}

# 辅助函数 - 获取API接口信息
def get_api_info(api_type=None, api_name=None, api_url=None):
    """
    根据API类型、名称或URL获取API接口信息
    
    参数:
        api_type: API类型
        api_name: API名称
        api_url: API URL
        
    返回:
        dict: API接口信息
    """
    if api_type and api_name:
        if api_type in API_MAPPING_BY_TYPE and api_name in API_MAPPING_BY_TYPE[api_type]:
            return API_MAPPING_BY_TYPE[api_type][api_name]
    elif api_url:
        if api_url in API_MAPPING_BY_URL:
            return API_MAPPING_BY_URL[api_url]
    return None

# 辅助函数 - 获取所有API类型
def get_all_api_types():
    """
    获取所有API类型
    
    返回:
        list: 所有API类型的列表
    """
    return list(API_MAPPING_BY_TYPE.keys())

# 辅助函数 - 获取特定类型的所有API名称
def get_api_names_by_type(api_type):
    """
    获取特定类型的所有API名称
    
    参数:
        api_type: API类型
        
    返回:
        list: 特定类型的所有API名称列表
    """
    if api_type in API_MAPPING_BY_TYPE:
        return list(API_MAPPING_BY_TYPE[api_type].keys())
    return []

# 辅助函数 - 获取字段映射
def get_field_mapping(api_type, api_name):
    """
    获取特定API的字段映射
    
    参数:
        api_type: API类型
        api_name: API名称
        
    返回:
        dict: 字段映射字典
    """
    if api_type in API_MAPPING_BY_TYPE and api_name in API_MAPPING_BY_TYPE[api_type]:
        return API_MAPPING_BY_TYPE[api_type][api_name].get("fields", {})
    return {}

# 辅助函数 - 根据API名称获取API文档信息
def get_api_documentation(api_name):
    """
    根据API名称获取API文档信息
    
    参数:
        api_name: API中文名称
        
    返回:
        dict: 包含API文档信息的字典
    """
    for api_type, apis in API_MAPPING_BY_TYPE.items():
        if api_name in apis:
            api_info = apis[api_name]
            return {
                'name': api_name,
                'type': api_type,
                'description': api_info.get('description', ''),
                'api_url': api_info.get('api_url', ''),
                'fields': api_info.get('fields', {})
            }
    return None

if __name__ == "__main__":
    # 示例用法
    print("所有API类型:", get_all_api_types())
    print("\n股票列表类型的所有API名称:", get_api_names_by_type("股票列表"))
    print("\n股票列表API的字段映射:", get_field_mapping("股票列表", "股票列表"))
    print("\n股票列表API的文档信息:", get_api_documentation("股票列表"))