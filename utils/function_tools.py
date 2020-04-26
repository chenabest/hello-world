# achen 2019/11/28 1:24 PM
# function_tools

import pendulum
import time
import sys
import os
from collections import Iterable
from traceback import print_exc
from functools import wraps
import re
import string
import keyword
import hashlib
import socket
import random
import logging
import xlwt
from ctypes import *

PROJECT_NAME = 'data_automation'
BASIC = ('str', 'int', 'float', 'bool', 'list', 'dict', 'tuple', 'NoneType', 'set', 'type')


def timer(f, name=None):
    """计时器，作为装饰器使用，被装饰的函数或方法会自动显示自身耗费时间"""
    if name is None:
        try:
            name = f.__name__
        except AttributeError:
            name = f.__class__.__name__

        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            print(f'{name}开始...')
            result = f(*args, **kwargs)
            time_use = time.time() - start_time
            if 1 <= time_use < 100:
                time_use = round(time_use, 2)
            elif time_use >= 100:
                time_use = round(time_use)
            print(f'{name}结束，耗费时间: {time_use}')
            return result

        return wrapper


def get_valid_serial(serial=None, auto=None):
    """
    功能：自动检测serial是否连接到电脑，如果未连接，可以自动获取可用手机序列号
    :param serial: 序列号
    :param auto: 是否自动获取手机序列号
    :return: 
    """
    if auto is None:
        hostname = socket.gethostname()
        if hostname not in ["ubuntu_10_core", "hetao-automation-1"]:
            auto = True
    lines = os.popen('adb devices | grep -v attached | grep device ').readlines()
    if lines:
        serials = []
        for line in lines:
            serials.append(line.split('\t')[0])
        if serial in serials:
            return serial
        else:
            if not auto:
                raise RuntimeError('设备号为空或未检测到')
            if serial:
                print('adb没有检测到您的设备序列号，请确认是否输入有误.')
            if len(serials) == 1:
                print('检测到一个设备：%s, 在该设备上运行?' % serials[0])
                input()
                return serials[0]
            else:
                print('检测到多个设备:')
                for serial in serials:
                    print(serial)
                serial = input('请输入设备序列号：')
                while serial not in serials:
                    serial = input('输入有误，请重新输入：')
                return serial
    else:
        raise RuntimeError('无设备连接！')


def get_valid_port(port=None, auto=True):
    """
     功能：自动检测端口号是否被占用，如果时，可以自动获取可用端口号
    :param port: 端口号
    :param auto: 是否自动获取可用端口号
    :return: 
    """
    hostname = socket.gethostname()
    if hostname in ["ubuntu_10_core", "hetao-automation-1"]:
        serial_port = {}
        path = get_project_path()
        f = open(os.path.join(path, 'appium_robot/robot/__init__.py'), 'r')
        text = f.read()
        f.close()
        match = re.search('serial_port = {.*?}', text, re.DOTALL)
        exec(match.group())
        ports = serial_port.values()
    else:
        ports = []
    port = port if port else random.randint(2000, 10000)
    lines = True
    if port and port not in ports:
        lines = os.popen('lsof -i -P | grep -i "listen" | grep %s' % port).readlines()
        if not lines:
            return port
    if not auto:
        raise RuntimeError('端口号为空或者被占用')
    while lines or port in ports:
        port = random.randint(2000, 10000)
        lines = os.popen('lsof -i -P | grep -i "listen" | grep %s' % port).readlines()
    print(port)
    return port


def get_timestamp_of_next_work_start_time(hour_start: int, minute_start=0, second_start=0):
    now = pendulum.now()
    hour_now = int(now.format('HH'))
    minute_now = int(now.format('mm'))
    second_now = int(now.format('ss'))
    if hour_now >= hour_start and minute_now >= minute_start and second_now >= second_start:
        timestamp = pendulum.now().add(days=1).replace(
            hour=hour_start, minute=minute_start, second=second_start).timestamp()
    else:
        timestamp = pendulum.now().replace(
            hour=hour_start, minute=minute_start, second=second_start).timestamp()
    return timestamp


def search(iterable, filter_pattern='.*', exclude_pattern='\.\.\.', index: int=1):
    """
    搜索可迭代对象中满足filter_pattern模式并且不满足exclude_pattern模式的元素
    :param filter_pattern: 正则表达式，过滤出想要的信息
    :param exclude_pattern: 正则表达式，在filter之后再排除一些模式
    :param iterable: 
    :param index: 搜索方式标号，当可迭代对象是字典型的时候，index==1，搜索key; index==2,搜索value; 
                  index==3，搜索key和value, key或者value满足筛选条件即可
                  index==4，搜索key和value, key和value同时满足筛选条件          
    :return: 字典或者列表
    """
    if 'get' not in dir(iterable):
        return [element for element in iterable if
                re.search(filter_pattern, str(element)) and not re.search(exclude_pattern, str(element))]
    else:
        if index == 1:
            return {key: iterable.get(key) for key in iterable if
                    re.search(filter_pattern, str(key)) and not re.search(exclude_pattern, str(key))}
        elif index == 2:
            return {key: iterable.get(key) for key in iterable if
                    re.search(filter_pattern, str(iterable.get(key))) and
                    not re.search(exclude_pattern, str(iterable.get(key)))}
        elif index == 3:
            return {key: iterable.get(key) for key in iterable
                    if re.search(filter_pattern, str(key)) and not re.search(exclude_pattern, str(key)) or
                    re.search(filter_pattern, str(iterable.get(key))) and
                    not re.search(exclude_pattern, str(iterable.get(key)))}
        elif index == 4:
            return {key: iterable.get(key) for key in iterable
                    if re.search(filter_pattern, str(key)) and not re.search(exclude_pattern, str(key)) and
                    re.search(filter_pattern, str(iterable.get(key))) and
                    not re.search(exclude_pattern, str(iterable.get(key)))}
        else:
            raise ValueError('index只能是1，2，3，4')


def is_valid_identifier(s: str):
    """功能：判断是否为合法标识符"""
    kw = keyword.kwlist
    if s in kw:  # 判断是否为python关键字
        return False
    elif s[0] == '_' or s[0] in string.ascii_letters:  # 判断是否为字母或下划线开头
        for i in s:
            if i == '_' or i in string.ascii_letters or i in string.digits:  # 判断是否由字母数字或下划线组成
                pass
            else:
                return False
        return True
    else:
        return False


def is_valid_container(ob):
    """
    判断是否为合法的容器，为_show_dir_details函数服务
    :param ob: 对象
    :return: 
    """
    if ob.__class__.__name__ in ('TextIOWrapper',):
        return False
    elif isinstance(ob, str) or not isinstance(ob, Iterable):
        return False
    elif ob.__class__.__name__ in BASIC and not ob:
        return False
    else:
        return True


def is_basic(o, basic=BASIC):
    """
    判断对象o是否是基本类型
    :param o: 对象
    :param basic: 基本类型列表
    :return: bool
    """
    try:
        name = o.__name__.split('.')[-1]
    except AttributeError:
        name = o.__class__.__name__.split('.')[-1]
    if name in basic:
        return True
    else:
        return False


def _show_dir_details(name: str, depth=1, filter_pattern='.*', exclude_pattern=None, special_cases=('[a-zA-Z0-9]+\.__doc__$',),
                      ignore_basic=False):
    """
    功能：显示一个函数、方法、类、模块、变量的所有相关的详细信息，帮助快速了解其用法。
    :param name: 变量或类、方法等的名称
    :param depth: 最大深度
    :param filter_pattern: 正则表达式，过滤出想要看的信息
    :param exclude_pattern: 正则表达式，在filter之后再排除一些模式
    :param special_cases: 属于special_cases的模式不会被exclude
    :param ignore_basic: True,False或序列(列表、元组等)。表示忽略的类型，不显示其详细信息。False不忽略任何类型，True将忽略默认类型，序列将忽略指定类型。
    :param update_globals: 同步globals，不然会导致新导入的模块无法识别（报" NameError: name [名称] not defined "错误）
    :return: 
    """
    exclude_pattern = '__dir__' if exclude_pattern is None else '__dir__|' + exclude_pattern
    if depth == 0 or name.split('.')[-1] in ['__abstractmethods__']:
        return
    if ignore_basic:
        if isinstance(ignore_basic, bool):
            if is_basic(eval(name)):
                return
        elif is_basic(eval(name), ignore_basic):
            return
    flag = False
    for p in eval('dir(%s)' % name):
        try:
            if p not in ['__abstractmethods__'] and re.search(filter_pattern, f'{name}.{p}'):
                if exclude_pattern:
                    is_in_special_cases = False
                    if special_cases:
                        for case in special_cases:
                            if re.search(case, f'{name}.{p}'):
                                print(name + '.' + p + ':', eval(f'{name}.{p}'))
                                flag = True
                                is_in_special_cases = True
                                break
                    if not is_in_special_cases and not re.search(exclude_pattern, f'{name}.{p}'):
                        print(name + '.' + p + ':', eval(f'{name}.{p}'))
                        flag = True
                else:
                    print(name + '.' + p + ':', eval(f'{name}.{p}'))
                    flag = True
        except Exception as e:
            print(f'获取信息：{name}.{p}出错:', end='')
            print(e)
            # print_exc()
            # raise
        _show_dir_details(name + '.' + p, depth - 1, filter_pattern, exclude_pattern, special_cases, ignore_basic)
    if flag:
        print()


def show_dir_details(o, depth=1, filter_pattern='.*', exclude_pattern=None,
                     special_cases=('[a-zA-Z0-9]+\.__doc__$',), ignore_basic=False, name=None):
    """参见_show_dir_details"""
    if not name:
        try:
            name = o.__name__.split('.')[-1]
        except AttributeError:
            name = o.__class__.__name__.split('.')[-1]
    globals().update({name: o})
    _show_dir_details(name=name, depth=depth, filter_pattern=filter_pattern, exclude_pattern=exclude_pattern, special_cases=special_cases, ignore_basic=ignore_basic)


def show_dir_details_act_on(belong_to_object, *args, **kwargs):
    """
    功能：查看一个对象的所有属性和方法具体信息，并且尽可能显示方法作用于给定参数的结果
    实例：
    show_dir_details_act_on(inspect, pretty_print, re_exclude='__|mod_dict|getmembers|findsource|linecache|modulesbyfile|_filesbymodname|classify_class_attrs')
    """
    re_filter_pattern = '.*'
    re_exclude_pattern = '\.\.\.'
    if 'filter_pattern' in kwargs:
        re_filter_pattern = kwargs['filter_pattern']
        kwargs.pop('filter_pattern')
    if 'exclude_pattern' in kwargs:
        re_exclude_pattern = kwargs['exclude_pattern']
        kwargs.pop('exclude_pattern')
    if 'ob_name' in kwargs:
        name = kwargs['ob_name']
        kwargs.pop('ob_name')
    else:
        name = belong_to_object.__name__ if hasattr(belong_to_object, '__name__') else belong_to_object.__class__.__name__
    args_str_list = list()
    for arg in args:
        if hasattr(arg, '__name__'):
            args_str_list.append(arg.__name__)
        else:
            args_str_list.append(f"'{str(arg)}'")
    kwargs_str_list = list()
    for key, value in kwargs.items():
        if hasattr(value, '__name__'):
            kwargs_str_list.append(f'{key}={value.__name__}')
        else:
            kwargs_str_list.append(f"'{key}'='{str(value)}'")
    args_str = ','.join(args_str_list)
    kwargs_str = ','.join(kwargs_str_list)
    param_str = ','.join([args_str, kwargs_str]).strip(',')
    for p in dir(belong_to_object):
        if not re.search(re_filter_pattern, p) or re.search(re_exclude_pattern, p):
            continue
        if eval(f'belong_to_object.{p}.__class__.__name__') in ['function', 'method', 'method_descriptor', 'builtin_function_or_method']:
            try:
                result = eval(f'belong_to_object.{p}(*args, **kwargs)')
                if isinstance(result, str) and '\n' in result:
                    result = '\n' + result
                print(f'{name}.{p}({param_str}):', result)
            except Exception:
                try:
                    result = belong_to_object.attr()
                    print(f'{name}.{p}():', result)
                except Exception:
                    print(f'{name}.{p}:', eval(f'belong_to_object.{p}'))
        else:
            try:
                print(f'{name}.{p}:', eval(f'belong_to_object.{p}'))
            except Exception as e:
                print(f'{name}.{p}出错:', e.__repr__())


def show_details(variable_names, belong_to_ob=None, filter_pattern='.*', exclude_pattern='\.\.\.'):
    """
    功能：显示变量的值, 可以通过变量名过滤
    使用实例：show_details(globals(),exclude_pattern='__|_[i0-9]|_oh|_dh|In|Out|exit|quit')
    """
    if belong_to_ob is not None:
        prefix = 'belong_to_ob.'
    else:
        prefix = ''
    for name in variable_names:
        if re.search(filter_pattern, name) and not re.search(exclude_pattern, name):
            try:
                print(name+':', eval(prefix+name))
            except Exception as e:
                print(name, 'eval出错：', e.__repr__())


def my_print(ob='', prefix='', end=None):
    if isinstance(ob, str):
        text = ob
    else:
        text = ob.__repr__()
    text = prefix + text.replace('\n', f'\n{prefix}')
    if end is not None:
        print(text, end=end)
    else:
        print(text)


def pretty_print(ob, depth=1, prefix='', is_root_container=True):
    """
    功能：美化容器对象（列表、字典等及其任意嵌套形式）的显示，不同的元素换行显示，并自动对齐同一层元素，实际使用时一般不用传prefix和is_root_container参数
    :param ob: 请传一个复杂的多层嵌套的组合数据对象
    :param prefix: 递归时使用, 用于对齐
    :param is_root_container: 递归时使用，当设置为False时，如果object是容器类型，会打印出object的类型
    :param depth: 显示深度，设置为-1时，展开所有层。
    :return: None
    """
    try:
        if depth == 0 or not is_valid_container(ob):
            my_print(ob, prefix=prefix)
        else:
            if not is_root_container:
                type_name = '<' + ob.__class__.__name__ + '>'
                my_print(type_name, prefix)
                prefix += ' '*(len(type_name)-1)  # 减1使与上一行最后一个字符对齐
            if 'get' in dir(ob):     # 字典型容器
                for key in ob:
                    try:
                        print(prefix + str(key) + ':', end='')
                        if ob.get(key) == ob:   # 避免递归死循环
                            print('{...}')
                        elif depth == 1 or not is_valid_container(ob.get(key)):
                            print(ob.get(key))
                        else:
                            type_name = '<' + ob.get(key).__class__.__name__ + '>'
                            print(type_name)
                            new_prefix = prefix + ' '*(len(str(key)+':'))+' '*(len(type_name)-1)
                            pretty_print(ob.get(key), depth - 1, new_prefix, True)
                    except Exception as e:
                        print('未知错误:', end='')
                        print(e.__repr__())
                        print('ob=', ob, ', key=', key)
            else:  # 非字典型容器
                for element in ob:
                    pretty_print(element, depth-1, prefix, False)
    except Exception as e:
        print('未知错误:', end='')
        print(e)
        # time.sleep(2)
        # print_exc()
        # time.sleep(1)
        print(ob.__class__, ':', ob)
        # import ipdb
        # ipdb.set_trace()
        # raise


def search_globals(ob=None, filter_pattern='.*', exclude_pattern='\.\.\.', show=False):
    if hasattr(ob, '__globals__'):
        globals().update(ob.__globals__)
    elif isinstance(ob, dict):
        globals().update(ob)
    var_names = [key for key in globals()]
    result = []
    for name in var_names:
        if re.search(filter_pattern, name) and not re.search(exclude_pattern, name):
            result.append(name)
    if show:
        for name in result:
            print(name+':', end='')
            print(eval(name))
    return result


def show_globals(ob=None):
    if ob is not None:
        pretty_print(ob.__globals__)
    else:
        pretty_print(globals())


def show_dir(o):
    pretty_print(dir(o))


def show_module(file_path=None, form='*', show=True, project_name=None):
    """
    将相对路径或绝对路径转化为模块，方便import
    """
    project_name = project_name or PROJECT_NAME
    if not file_path:
        file_path = sys.argv[0]
    ls = file_path.split('/')
    index = -1
    for i in range(len(ls)):
        if ls[i] == project_name:
            index = i
            break
    module_name = '.'.join(ls[index + 1:])[:-3]
    if module_name.endswith('__init__'):
        module_name = module_name[:-(len('__init__')+1)]
    if show:
        if form == 'from':
            print('from', module_name, 'import')
        elif form == 'import':
            print('import', module_name, 'as', module_name.split('.')[-1])
        elif form == '*':
            print('from', module_name, 'import', '*')
        else:
            print(module_name)
        print()
    return module_name


def get_run_file_name(file_path=None):
    """
    获取正常运行的文件的名称
    """
    if file_path:
        return os.path.splitext(os.path.split(file_path)[-1])[0]
    else:
        return os.path.splitext(os.path.split(sys.argv[0])[-1])[0]


def get_command():
    """
    获取启动脚本时命令行输入的完整命令
    """
    run_module_name = show_module(sys.argv[0], show=False)
    if len(sys.argv) > 1:
        params_content = ' ' + ' '.join(sys.argv[1:])
    else:
        params_content = ''
    command = 'python3 -m %s%s' % (run_module_name, params_content)
    return command


def get_command_on_cellphone(serial, command_only=True):
    import json
    result = os.popen(f'ps aux | grep {serial} | grep -v grep').read()
    if result:
        if command_only:
            lines = result.split('\n')
            commands = []
            for line in lines:
                if 'python' in line:
                    ls = line.split()
                    for i in range(len(ls)):
                        if 'python' in ls[i]:
                            commands.append(' '.join(ls[i:]))
            return '\n'.join(commands)
        else:
            lines = result.strip('\n').split('\n')
            return json.dumps(lines)
    return ''


def preparation_for_executing_command_on_cellphone(serial, port, rconn=None, wait_time=15, poll_frequency=6):
    from utils import kill_server, start_server
    import redis
    rconn = rconn or redis.from_url("redis://ubuntu_10_core:6379/13", decode_responses=True)
    command = rconn.hget(f'all_devices:{serial}', 'command')
    while rconn.hget(f'all_devices:{serial}', 'is_available') == 'False' and command and command != get_command():
        time.sleep(poll_frequency)
        command = rconn.hget(f'all_devices:{serial}', 'command')
    rconn.hset(f'all_devices:{serial}', 'is_available', 'False')
    time.sleep(3)
    command = rconn.hget(f'all_devices:{serial}', 'command')
    if command == get_command() or not command:
        kill_server(serial, get_run_file_name())
        time.sleep(3)
        start_server(serial, port)
        time.sleep(wait_time)


def switch_script_on_cellplhone_and_wait_for_availability(serial, rconn=None, wait_time=100, poll_frequency=6):
    import redis
    rconn = rconn or redis.from_url("redis://ubuntu_10_core:6379/13", decode_responses=True)
    rconn.hset(f'all_devices:{serial}', 'is_available', 'True')
    time.sleep(wait_time)
    re_init_driver = False
    if rconn.hget(f'all_devices:{serial}', 'is_available') == 'False':
        command = rconn.hget(f'all_devices:{serial}', 'command')
        while rconn.hget(f'all_devices:{serial}', 'is_available') == 'False' and command and command != get_command():
            time.sleep(poll_frequency)
            command = rconn.hget(f'all_devices:{serial}', 'command')
        re_init_driver = True
    rconn.hset(f'all_devices:{serial}', 'is_available', 'False')
    return re_init_driver


def size_humanize(size, unit='KB'):
    units = ['B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    index = units.index(unit[0].upper())
    size = float(size)
    if size < 0:
        raise ValueError('size必须为非负整数')
    for unit in units[index:]:
        if size >= 1024:
            size /= 1024
        else:
            size_h = '{} {}'.format(round(size, 2), unit)
            return size_h

    size_h = '{} {}'.format(round(size, 2), units[-1])
    return size_h


def size_unify(size, unit='B'):
    """统一内存单位为B"""
    units = ['B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    index = units.index(unit[0].upper())
    size = float(size)
    if size < 0:
        raise ValueError('size必须为非负整数')
    while index > 0:
        size *= 1024
        index -= 1
    return size


def get_project_path(project_name=PROJECT_NAME):
    """
    获取项目路径
    """
    ls = __file__.split('/')
    for i in range(len(ls)):
        if ls[i] == project_name:
            break
    return '/'.join(ls[:i+1])


def get_module_path(ob):
    """
    功能：获取ob对象所在的文件路径
    """
    try:
        class_name = ob.__class__.__name__
        if class_name == 'function':
            return ob.__code__.co_filename
        elif class_name == 'module':
            try:
                path = ob.__file__
            except AttributeError as e:
                try:
                    package_name = ob.__name__
                    path = os.path.join(get_project_path(), '/'.join(package_name.split('.')))+'/'
                    if os.path.exists(path):
                        return path
                except AttributeError:
                    pass
                if 'sys' in class_name:
                    print(ob, class_name)
                    return ob.exec_prefix+'/'
                print(ob,  f';执行语句{ob.__name__}.__file__出错:', end='')
                print(e)
                return 'builtins'
            if not path.endswith('__init__.py'):
                return path
            else:
                return path[:-11]
        elif class_name == 'type':
            try:
                module_name = ob.__module__
                if '.' in module_name:
                    path = os.path.join(get_project_path(), '/'.join(module_name.split('.')))+'.py'
                    if os.path.exists(path):
                        return path
                return module_name
            except Exception as e:
                print(ob)
                print(e)
                print_exc()
                return 'builtins'
        else:
            try:
                return ob.__class__.__module__
            except Exception as e:
                print(ob, f'执行{class_name}.__class__.__module__', '出错:', end='')
                print(e)
                print_exc()
                # import ipdb
                # ipdb.set_trace()
                return 'builtins'
    except Exception as e:
        print(ob, '未知错误:', end='')
        print(e)
        # print_exc()
        # import ipdb
        # ipdb.set_trace()


def get_headers(text=None):
    """
    可将浏览器调试的请求信息文本转化成字典，作为请求的headers
    :param text: 
    :return: 
    """
    if text is None:
        text = """Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: zh,zh-CN;q=0.9,en;q=0.8
Cache-Control: max-age=0
Connection: keep-alive
Cookie: bid="ej4uI0m/AvM"; ll="108288"; _vwo_uuid_v2=D827053B8471B94A4F7E1774CD6EF97DC|93f9c364a293a415b8a10c401a715b2b; __yadk_uid=24jhpr8p8Oi5f7YuQgBPI2Q4hSrydY28; viewed="1770782"; gr_user_id=e7758bae-b713-4f56-8ff5-3e7090201a60; __utmz=30149280.1574695001.5.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __gads=ID=f96a1422cf093c1f:T=1574959156:S=ALNI_MYzwJIKY5egUvIyuhM26WjHLNTLPg; __utmc=30149280; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1577245957%2C%22https%3A%2F%2Fbook.douban.com%2Fsubject%2F1770782%2F%22%5D; ap_v=0,6.0; __utma=30149280.644434162.1574078799.1577173311.1577245958.34; _pk_id.100001.8cb4=7495de8919720908.1574078815.34.1577245965.1577173309.
Host: www.douban.com
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36"""
    result = re.findall('([A-Z][a-zA-Z-]*: ?.*)\n?', text)
    headers_dict = {}
    for header_content in result:
        key, value = header_content.split(': ')
        headers_dict[key] = value
    return headers_dict


def my_md5(ob):
    ss = str(ob).encode(encoding='UTF-8')
    ss = hashlib.md5(ss).hexdigest()
    return ss


def set_logger(log_file_path=None, output=None, name='my_logger'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(name)s.py:%(lineno)d - %(levelname)s: %(message)s')
    if log_file_path is None:
        output = True
    # 创建一个handler，用于输出到控制台：
    if output:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)   # 给logger添加handler
    # 创建一个handler，用于写入日志文件：
    if log_file_path:
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger


def write_data_to_excel(data: list, file_name='unnamed.xls', column_name_list: list=None, encoding_mode='utf-8'):
    from utils import ARCHIVE_PATH
    if not file_name.endswith('.xls'):
        file_name += '.xls'
    file_path = file_name if file_name.startswith('/') else os.path.join(ARCHIVE_PATH, file_name)
    work_book = xlwt.Workbook(encoding=encoding_mode)
    sheet_name = file_name.split('/')[-1][:-4]
    for _ in range(3):
        if len(sheet_name) < 32:
            break
        print('sheet名称超过长度限制，自动裁剪')
        sheet_name = '_'.join(sheet_name.split('_')[1:])
    sheet = work_book.add_sheet(sheet_name)
    if column_name_list is None:
        column_name_list = []
        for dic in data:
            for key in dic:
                if key not in column_name_list:
                    column_name_list.append(key)
    row = 0
    for i, column_name in enumerate(column_name_list):
        sheet.write(row, i, column_name)
    for dic in data:
        row += 1
        for i, column_name in enumerate(column_name_list):
            if column_name_list[i] in dic:
                sheet.write(row, i, dic[column_name_list[i]])
    work_book.save(file_path)
    print(f'写入excel文件完成，文件位置：{file_path}, 请查看')


def get_data_from_txt(file_path, headers: bool=True, sep=None):
    """从文本文件读取格式化数据，要求文本遵循统一的格式，不同字段的值用统一分隔符隔开，一条记录占一行，如果有表头的话，请放在第一行"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    if headers:
        headers = lines[0].split(sep)
    else:
        headers = list(range(1, len(lines[0].split(sep))+1))
    n = len(headers)
    data = []
    for line in lines[1:]:
        dic = dict()
        record = line.split(sep)
        if not record:
            # 跳过空行
            continue
        for i in range(n):
            dic[headers[i]] = record[i]
        data.append(dic)
    return data


def all_in(items, container):
    for item in items:
        if item not in container:
            return False
    return True


def any_in(items, container):
    for item in items:
        if item in container:
            return True
    return False


def a_input(prompt='', default='', timeout=30):
    """
    get input from terminal asynchronously
    :param prompt: 输入说明文字
    :param default: 超时且未输入任何字符时的默认返回值
    :param timeout: 静默超时时间（在timeout时间内未输入任何文字，自动return）
    :return: str
    """
    from appium_robot.robot.tools.key_getter import KeyGetter
    print(prompt, end='', flush=True)
    with KeyGetter() as k:
        start_time = time.time()
        s = ''
        while True:
            if time.time() - start_time > timeout:
                break
            char = k.getchar(False)
            if char in ['\n', '\r']:
                return s or default
            elif char:
                if char == '\x7f':   # 删除键
                    if len(s) >= 1:
                        s = s[:-1]
                else:
                    s += char
                start_time = time.time()
            else:
                time.sleep(0.0005)
        print()
        return s or default


def ssh_command(command, user='ubuntu', host='ubuntu_10_core', password='420blazeit', has_added_key=True):
    """
    使用ssh登录远程服务器执行command
    :param command: 要在服务器执行的命令
    :param user: 服务器用户名
    :param host: 服务器域名或ip
    :param password: 密码
    :param has_added_key: 是否把自己的公钥添加到了服务器上
    :return: 命令的的输出内容
    """
    import pexpect
    if has_added_key:
        child = pexpect.spawn('''ssh -l %s %s "%s"''' % (user, host, command))
    else:
        ssh_new_key = 'Are you sure you want to continue connecting'
        child = pexpect.spawn('''ssh -l %s %s "%s"''' % (user, host, command))
        i = child.expect([pexpect.TIMEOUT, ssh_new_key, 'password: '])
        # import ipdb
        # ipdb.set_trace()
        if i == 0:
            print('ERROR!')
            print('SSH could not login. Here is what SSH said:')
            print(child.before, child.after)
            return None
        if i == 1:
            child.sendline('yes')
            child.expect('password: ')
            i = child.expect([pexpect.TIMEOUT, 'password: '])
            if i == 0:
                print('ERROR!')
                print('SSH could not login. Here is what SSH said:')
                print(child.before, child.after)
                return None
        child.sendline(password)
    child.expect(pexpect.EOF)
    return child.before.decode()


def domain2ip(domain_name):
    text = os.popen(f'ping {domain_name} -c 1').read()
    match = re.search('(\d+\.){3}\d+', text)
    if match:
        return match.group()


def ip2domain(ip):
    text = os.popen(f'nslookup {ip}').read()
    match = re.search('name\s*=\s*(\S+)', text)
    if match:
        return match.group(1).strip('.')


def is_port_available(port, host="127.0.0.1"):
    """检测端口是否被占用"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, int(port)))
        s.shutdown(2)
        print('port %s is uesd !' % port)
        return False
    except Exception as e:
        print(e.__repr__())
        print('port %s is available!' % port)
        return True


pprint = pretty_print
logger_ch = set_logger(output=True)
PROJECT_PATH = get_project_path()


if __name__ == '__main__':
    show_module(form='*')
    a = [1, 2, {'a22': 67, 'fff': 9.09}, 89293488989, [1, 2, (6, 'ff', 9)], 45, 'helloworld']
    pretty_print(a)
    # show_dir_details(dict, depth=3, exclude_pattern='__|._', ignore_basic=('str', 'int', 'float', 'bool'))
    # import ipdb
    # ipdb.set_trace()
    # import numpy
    # show_dir_details(numpy)
