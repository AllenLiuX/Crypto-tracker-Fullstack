# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, url_for
from flask_restful import Api, Resource
#from werkzeug import secure_filename
import pandas as pd
import json
import datetime
import traceback
import os, sys
import numpy as np

# sys.path.append('/home/bank_dev/Aita-Tech/Liushui/')
import bitcoin as bt
import mail

app = Flask(__name__)
api = Api(app)
app.debug = True
app.config['JSON_AS_ASCII'] = False
# pd.set_option('display.max_columns', None)

# ========================================================

# 公共函数, 可以单独放在一个文件里, 供工程其他模块调用
def timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_errlog(api_name, service_name):
    content = ['\n' + api_name + '\n']
    mkdir_if_not_exists(os.getcwd() + '/log_err')
    errlog_file = os.getcwd() + '/log_err/errlog_%s.txt' % (service_name)

    try:
        with open(errlog_file, 'a+') as f:
            f.writelines(content)
        traceback.print_exc(file=open(errlog_file, 'a+'))
    except:
        pass


def get_lost_keys(args, keys):
    lost_keys = []
    for k in keys:
        if k not in args:
            lost_keys.append(k)
    return lost_keys


def return_df(df):
    rs = json.loads(df.fillna('').to_json(orient='records'))
    return rs


# ========================================================
# api 函数样例
def api1(args):
    # 检查必要入参
    keys = [
        'arg1',
        'arg2',
        'arg3',
        'arg4'
    ]
    lost_keys = get_lost_keys(args, keys)
    if lost_keys:
        return {'respCode': '9999',
                'respMsg': '缺少参数: %s' % ' '.join(lost_keys)}

    # 检查数据类型
    try:
        arg1 = args['arg1']  # str
        arg2 = int(args['arg2'])  # int
        arg3 = float(args['arg3'])  # float
        arg4 = json.loads(args['arg4'])  # 反序列前端传递的 list, dict 等序列化字符
    except Exception as e:
        return {'respCode': '9999',
                'respMsg': '数据类型错误: %s' % str(e),
                'sample_args': {'arg1': '文本',
                                'arg2': '1',
                                'arg3': '0.99',
                                'arg4': '["2020-01","2020-02"]'
                                }  # 后端传递入参都是字符, 需要检查数据类型
                }

    # 接口函数主内容

    pass

    # 特殊返回数据结构样例

    # 返回 DataFrame 格式
    df_data = pd.DataFrame([{'a': 'foo', 'b': 1, 'c': 0.99, 'd': np.nan}, {'a': 'bar', 'b': 2, 'c': 0.88, 'd': None}])

    # 返回 dict
    dic_data = {'name': 'lily'}

    # 返回 list
    lis_data = ['lily', 1, 0.88]

    # 结果集成
    res = {
        'respCode': '0000', 'respMsg': 'success', 'data': {
            'df_data': return_df(df_data),
            'dic_data': dic_data,
            'lis_data': lis_data,
            'args': args
         }
           }
    return res

def add_tracker(args):
    keys = [
        'user_mail', 'raise_line', 'change_interval', 'crypto'
    ]
    lost_keys = get_lost_keys(args, keys)
    if lost_keys:
        return {'respCode': '9999',
                'respMsg': '缺少参数: %s' % ' '.join(lost_keys)}

    # 检查数据类型
    try:
        user_mail = args['user_mail']  # str
        raise_line = float(args['raise_line'])  # float
        change_interval = float(args['change_interval'])  # float
        crypto = args['crypto']
        # arg4 = json.loads(args['arg4'])  # 反序列前端传递的 list, dict 等序列化字符
    except Exception as e:
        return {'respCode': '9999',
                'respMsg': '数据类型错误: %s' % str(e),
                'sample_args': {'arg1': '文本',
                                'arg2': '1',
                                'arg3': '0.99',
                                'arg4': '["2020-01","2020-02"]'
                                }  # 后端传递入参都是字符, 需要检查数据类型
                }

    status = bt.set_mg(user_mail, raise_line, change_interval, crypto)
    mail.thanks_email(crypto, raise_line, change_interval, [user_mail])

    res = {
        'respCode': '0000', 'respMsg': 'success', 'data': {
            'status': status,
            'args': args
        }
    }
    return res

def remove_tracker(args):
    keys = [
        'user_mail', 'crypto'
    ]
    lost_keys = get_lost_keys(args, keys)
    if lost_keys:
        return {'respCode': '9999',
                'respMsg': '缺少参数: %s' % ' '.join(lost_keys)}

    # 检查数据类型
    try:
        user_mail = args['user_mail']  # str
        crypto = args['crypto']
        # arg4 = json.loads(args['arg4'])  # 反序列前端传递的 list, dict 等序列化字符
    except Exception as e:
        return {'respCode': '9999',
                'respMsg': '数据类型错误: %s' % str(e),
                'sample_args': {'arg1': '文本',
                                'arg2': '1',
                                'arg3': '0.99',
                                'arg4': '["2020-01","2020-02"]'
                                }  # 后端传递入参都是字符, 需要检查数据类型
                }

    status = bt.remove_mg(user_mail, crypto)
    mail.cancel_email(crypto, [user_mail])

    res = {
        'respCode': '0000', 'respMsg': 'success', 'data': {
            'status': status,
            'args': args
        }
    }
    return res


# 接口字典, api名称:api函数, 新增接口地址更新此字典
dic_api = {
    'api1': api1,
    'add_tracker': add_tracker,
    'remove_tracker': remove_tracker,
}


# restful接口类
class Service_name(Resource):
    def post(self, api_name):
        # 获取入参
#        print(request.form)
        try:
            file = request.files['file']
        except Exception:
            pass
        args = request.form.to_dict()
#        print(args)

        # api接口
        if api_name in dic_api:
            try:
                print(args)
                if api_name == 'upload' or api_name == 'process_file':
                    res = dic_api[api_name](file, args)
                else:
                    res = dic_api[api_name](args)
            except:
                res = {'respCode': '9999', 'respMsg': 'fail'}
                save_errlog('%s %s %s' % (timestamp(), api_name, json.dumps(args)), 'sample')  # 错误日志
        else:
            res = {'respCode': '9999', 'respMsg': 'wrong api address'}
        return json.dumps(res, ensure_ascii=False)


api.add_resource(Service_name, '/bitcoin/<string:api_name>')  # sample 替换为service_name

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5101)
