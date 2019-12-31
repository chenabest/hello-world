# achen 2019/11/28 1:24 PM
# function_tools

import pendulum
import sys
import os
from collections import Iterable
from traceback import print_exc
import re
import string
import keyword
import hashlib
import socket
import random

PROJECT_NAME = 'data_automation'
BASIC = ('str', 'int', 'float', 'bool', 'list', 'dict', 'tuple', 'NoneType', 'set', 'type')


def get_valid_serial(serial=None, auto=None):
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
    hostname = socket.gethostname()
    if hostname in ["ubuntu_10_core", "hetao-automation-1"]:
        serial_port = {}
        f = open('/Users/achen/workspaces/data_automation/appium_robot/robot/__init__.py', 'r')
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


def search(pattern, iterable, *args):
    if 'get' not in dir(iterable):
        return [element for element in iterable if re.search(pattern, str(element))]
    else:
        if not args or args[0] == 0:
            return {key: iterable.get(key) for key in iterable if str(iterable.get(key))}
        elif args[0] == 1:
            return {key: iterable.get(key) for key in iterable if re.search(pattern, str(iterable.get(key)))}
        elif args[0] == 2:
            return {key: iterable.get(key) for key in iterable
                    if re.search(pattern, re.search(pattern, str(key)) or str(iterable.get(key)))}
        else:
            raise ValueError('第三个参数值只能是0，1，2')


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
    if ob.__class__.__name__ in ('TextIOWrapper',):
        return False
    elif isinstance(ob, str) or not isinstance(ob, Iterable):
        return False
    elif ob.__class__.__name__ in BASIC and not ob:
        return False
    else:
        return True


def is_basic(o, basic=BASIC):
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
    if not name:
        try:
            name = o.__name__.split('.')[-1]
        except AttributeError:
            name = o.__class__.__name__.split('.')[-1]
    globals().update({name: o})
    _show_dir_details(name=name, depth=depth, filter_pattern=filter_pattern, exclude_pattern=exclude_pattern, special_cases=special_cases, ignore_basic=ignore_basic)


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
            print(prefix, end='')
            print(ob)
        else:
            if not is_root_container:
                print(prefix, end='')
                type_name = '<' + ob.__class__.__name__ + '>'
                print(type_name)
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
                        print(e)
                        print('ob=', ob, 'key=', key)
            else:  # 非字典型容器
                for element in ob:
                    pretty_print(element, depth-1, prefix, False)
    except Exception as e:
        import time
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


def show_globals(o=None):
    if o is not None:
        pretty_print(o.__globals__)
    else:
        pretty_print(globals())


def show_dir(o):
    pretty_print(dir(o))


def show_module(file_path=None, form='*', show=True):
    if not file_path:
        file_path = sys.argv[0]
    if file_path:
        ls = file_path.split('/')
    for i in range(len(ls)):
        if ls[i] == PROJECT_NAME:
            break
    module_name = '.'.join(ls[i + 1:])[:-3]
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
    if file_path:
        return os.path.splitext(os.path.split(file_path)[-1])[0]
    else:
        return os.path.splitext(os.path.split(sys.argv[0])[-1])[0]


def get_command():
    run_module_name = show_module(sys.argv[0], show=False)
    if len(sys.argv) > 1:
        params_content = ' ' + ' '.join(sys.argv[1:])
    else:
        params_content = ''
    command = 'python3 -m %s%s' % (run_module_name, params_content)
    return command


def get_project_path():
    ls = __file__.split('/')
    for i in range(len(ls)):
        if ls[i] == PROJECT_NAME:
            break
    return '/'.join(ls[:i+1])


def get_module_path(ob):
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


def md5(ob):
    ss = str(ob).encode(encoding='UTF-8')
    ss = hashlib.md5(ss).hexdigest()
    return ss


pprint = pretty_print


if __name__ == '__main__':
    show_module(form='*')
    a = [1, 2, {'a22': 67, 'fff': 9.09}, 89293488989, [1, 2, (6, 'ff', 9)], 45, 'helloworld']
    pretty_print(a)
    # show_dir_details(dict, depth=3, exclude_pattern='__|._', ignore_basic=('str', 'int', 'float', 'bool'))
    import ipdb
    ipdb.set_trace()
    # import numpy
    # show_dir_details(numpy)
