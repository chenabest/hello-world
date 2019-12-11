#!/usr/bin/python3
# achen 2019/12/10 10:19 PM
# function_tools
# /Users/achen/PythonProjects/chena_project/utils/function_tools.py

from traceback import print_exc
import re


BASIC = ('str', 'int', 'float', 'bool', 'list', 'dict', 'tuple', 'NoneType', 'type', 'set')


def is_basic(name, basic=BASIC):
    if eval('{}.__class__.__name__'.format(name)) in basic:
        return True
    else:
        return False


def show_dir_details(name, max_depth=1, re_filter='.*', re_exclude=None, special_cases=('__doc__$', ), ignore_basic=False):
    """
    功能：显示一个函数、方法、类、模块、变量的所有相关的详细信息，帮助快速了解其用法。
    :param name: 变量或类、方法等的名称
    :param max_depth: 最大深度
    :param re_filter: 过滤出想要看的信息
    :param re_exclude: 在filter之后再排除一些模式
    :param special_cases: 属于special_case的模式不会被exclude
    :param ignore_basic: True,False或序列(列表、元组等)。表示忽略的类型，不显示其详细信息。False不忽略任何类型，True将忽略默认类型，序列将忽略指定类型。
    :return: 
    """
    if max_depth == 0:
        return
    if ignore_basic:
        if isinstance(ignore_basic, bool):
            if is_basic(name):
                return
        elif is_basic(name, ignore_basic):
            return
    flag = False
    for p in eval('dir(%s)' % name):
        try:
            if p not in ['__abstractmethods__'] and re.search(re_filter, f'{name}.{p}'):
                if re_exclude:
                    is_in_special_cases = False
                    if special_cases:
                        for case in special_cases:
                            if re.search(case, f'{name}.{p}'):
                                print(name + '.' + p + ':', eval(f'{name}.{p}'))
                                flag = True
                                is_in_special_cases = True
                                break
                    if not is_in_special_cases and not re.search(re_exclude, f'{name}.{p}'):
                        print(name + '.' + p + ':', eval(f'{name}.{p}'))
                        flag = True
                else:
                    print(name + '.' + p + ':', eval(f'{name}.{p}'))
                    flag = True
        except Exception as e:
            print(f'获取信息：{name}.{p}出错')
            print(e)
            print_exc()
            raise
        show_dir_details(name + '.' + p, max_depth - 1, re_filter, re_exclude, special_cases, ignore_basic)
    if flag:
        print()


if __name__ == '__main__':
    a = 889
    print(is_basic('a'))
    show_dir_details('a', ignore_basic=True)
    show_dir_details('str', max_depth=2, re_exclude='__', special_cases=('__doc__$', ))
