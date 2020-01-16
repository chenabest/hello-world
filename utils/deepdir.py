#!/usr/bin/python3
# achen 2019/12/10 10:19 PM
# appium_robot.robot.tools.deepdir
# /Users/achen/workspaces/data_automation/appium_robot/robot/tools/deepdir.py
from config import SENTRY
from traceback import print_exc
import os
import json
from config import get_archive_path
from appium_robot.robot.tools.function_tools import show_dir_details, pretty_print, show_module, is_basic, \
    get_module_path, is_valid_identifier
from collections import Iterable
import socket
import re

MY_PATH = '/Users/achen/workspaces/data_automation/my_files'
if socket.gethostname() == 'achens-iMac.lan':
    DIR_PATH = get_archive_path(base=True)
else:
    DIR_PATH = get_archive_path(base=False)

DIR_PATH = MY_PATH if os.path.exists(MY_PATH) else DIR_PATH
COMMONS = (int, float, bool, list, str, dict, tuple, set)
MY_FUNCTION_SPECIAL_CASES = ('__module__', '__name__', '__qualname__', '__annotations__',
                             '__defaults__', '__kwdefaults__', '__code__',)
CODE_SPECIAL_CASES = ('co_filename', 'co_firstlineno', 'co_name',
                      'co_varnames', 'co_names', 'co_cellvars', 'co_freevars',
                      'co_argcount', 'co_kwonlyargcount', 'co_nlocals', 'co_stacksize',)
DEEPER_CLASS_NAMES = ('function', 'type', 'module', 'method-wrapper')


def is_valid_name(name: str, other_error_cases=('__abstractmethods__',)):
    if '.' in name:
        p = name.split('.')[-1]
    else:
        p = name
    if p not in other_error_cases and is_valid_identifier(p):
        return True
    else:
        return False


class DeepDir(object):
    def __init__(self, o, depth=3, filter_pattern='.*', exclude_pattern=None,
                 special_cases=('[a-zA-Z0-9]+.__doc__$',), ignore_basic=False, name=None):
        if not name:
            try:
                name = o.__name__.split('.')[-1]
            except AttributeError:
                name = o.__class__.__name__.split('.')[-1]
        globals().update({name: o})
        self.name = name
        self.o = o
        self.depth = depth
        self.filter_pattern = filter_pattern
        self.exclude_pattern = exclude_pattern
        if special_cases and isinstance(special_cases, str):
            special_cases = [special_cases]
        self.special_cases = special_cases
        self.ignore_basic = ignore_basic
        self.__result = []
        self.module_path = get_module_path(o)
        self.dir_deep(self.depth, self.filter_pattern, self.exclude_pattern, self.special_cases, self.ignore_basic)

    def dir_deep(self, depth=1, filter_pattern='.*', exclude_pattern=None,
                 special_cases=('[a-zA-Z0-9]+\.__doc__$',), ignore_basic=False):
        exclude_pattern = '__dir__' if exclude_pattern is None else '__dir__|' + exclude_pattern
        self._dir_filter(self.name, depth, filter_pattern, exclude_pattern, special_cases, ignore_basic)

    def _dir_filter(self, name, depth, re_filter, re_exclude, special_cases, ignore_basic):
        if depth == 0 or not is_valid_name(name):
            return
        if ignore_basic:
            if isinstance(ignore_basic, bool):
                if is_basic(eval(name)):
                    return
            elif is_basic(eval(name), ignore_basic):
                return
        for p in eval('dir(%s)' % name):
            try:
                if re.search(re_filter, f'{name}.{p}'):
                    if re_exclude:
                        is_in_special_cases = False
                        if special_cases:
                            for case in special_cases:
                                if re.search(case, f'{name}.{p}'):
                                    self.__result.append(name + '.' + p)
                                    is_in_special_cases = True
                                    break
                        if not is_in_special_cases and not re.search(re_exclude, f'{name}.{p}'):
                            self.__result.append(name + '.' + p)
                    else:
                        self.__result.append(name + '.' + p)
            except Exception as e:
                print(f'获取信息{name}.{p}出错:', end='')
                print(e)
                # print_exc()
                print('/Users/achen/workspaces/data_automation/appium_robot/robot/tools/deepdir.py, line:78')
            self._dir_filter(name + '.' + p, depth - 1, re_filter, re_exclude, special_cases, ignore_basic)

    def show(self):
        show_dir_details(self.o, self.depth, self.filter_pattern, self.exclude_pattern,
                         self.special_cases, self.ignore_basic)

    def get_result(self):
        return self.__result

    def search(self, re_pattern: str):
        result = []
        for name in self.__result:
            if re.search(re_pattern, name):
                result.append(name)
        return result

    def get_dict(self):
        dir_details_dict = {}
        for name in self.__result:
            if is_valid_name(name):
                dir_details_dict[name] = eval(name)
            else:
                dir_details_dict[name] = f'无法获取{name}的值！'
        return dir_details_dict

    def pretty_show(self, depth=2, prefix='', is_root_container=True):
        dir_details_dict = self.get_dict()
        pretty_print(dir_details_dict, depth=depth, prefix=prefix, is_root_container=is_root_container)

    @property
    def size(self):
        return len(self.__result)

    def __contains__(self, item):
        return item in self.__result

    def __len__(self):
        return len(self.__result)

    def __call__(self, *args, **kwargs):
        return self._DirFilter(self.name, self.__result, self.depth, self.module_path)

    class _DirFilter:
        def __init__(self, name, iterable, depth, module_path):
            self.name = name
            self.__origin = iterable
            self._iterable = iterable
            self.depth = depth
            self.module_path = module_path
            self._index = 1

        def re_filter(self, pattern, depth=1):
            self._iterable = [name for name in self._iterable if len(name.split('.')) <= depth or
                              re.search(pattern, '.'.join(name.split('.')[depth:]))]
            return self

        def re_exclude(self, pattern, depth=1):
            self._iterable = [name for name in self._iterable if len(name.split('.')) <= depth or
                              not re.search(pattern, '.'.join(name.split('.')[depth:]))]
            return self

        def exclude_common(self, commons: tuple=COMMONS, depth=2, special_cases=('__doc__',)):
            if commons and not isinstance(commons, Iterable):
                commons = [commons]
            if special_cases and (isinstance(special_cases, str) or not isinstance(special_cases, Iterable)):
                special_cases = [special_cases]
            excludes = set()
            for common in commons:
                excludes.update(dir(common))
            for case in special_cases:
                excludes.remove(case)
            result = []
            for name in self._iterable:
                try:
                    if len(name.split('.')) <= depth:
                        result.append(name)
                        continue
                except Exception as e:
                    print(e)
                    print_exc()
                    import ipdb
                    ipdb.set_trace()
                for p in excludes:
                    is_p_in_excludes = False
                    if p in name.split('.')[depth:]:
                        is_p_in_excludes = True
                        break
                if not is_p_in_excludes:
                    result.append(name)
            self._iterable = result
            return self

        def exclude_doc_of_common(self, commons: tuple=COMMONS):
            if commons and not isinstance(commons, Iterable):
                commons = [commons]
            result = []
            for name in self._iterable:
                if name.endswith('.__doc__') and eval(f'{name[:-8]}.__class__') in commons:
                    continue
                result.append(name)
            self._iterable = result
            return self

        def cls_filter(self, class_names=('function', 'type', 'property'), depth=1, special_cases: tuple=None):
            if class_names and isinstance(class_names, str):
                class_names = [class_names]
            if special_cases and isinstance(special_cases, str):
                special_cases = [special_cases]
            result = []
            for name in self._iterable:
                if len(name.split('.')) <= depth:
                    result.append(name)
                    continue
                if special_cases:
                    for case in special_cases:
                        if re.search(case, name):
                            result.append(name)
                            break
                elif not name.endswith('.__doc__'):
                    if eval(f'{name}.__class__.__name__') in class_names:
                        result.append(name)
                elif eval(f'{name[:-8]}.__class__.__name__') in class_names:
                    result.append(name)
            self._iterable = result
            return self

        def cls_exclude(self, class_names=('int',), depth=2, special_cases: tuple=None):
            if class_names and isinstance(class_names, str):
                class_names = [class_names]
            if special_cases and isinstance(special_cases, str):
                special_cases = [special_cases]
            result = []
            for name in self._iterable:
                if len(name.split('.')) <= depth:
                    result.append(name)
                    continue
                if special_cases:
                    for case in special_cases:
                        if re.search(case, name):
                            result.append(name)
                            break
                elif not name.endswith('.__doc__'):
                    if eval(f'{name}.__class__.__name__') not in class_names:
                        result.append(name)
                elif eval(f'{name[:-8]}.__class__.__name__') not in class_names:
                    result.append(name)
            self._iterable = result
            return self

        def current_module_filter(self, depth: int=2, special_cases: tuple=None):
            """
            功能：筛选源出路径就是当前模块路径的name，这样会过滤掉导入的包和标准模块的对象，类，方法和属性等。使用后效果非常明显。
            :param depth: 当name的层数达到depth后才对其进行过滤。
            :param special_cases: 符合special_cases的name不会被过滤
            :return: self
            """
            if special_cases and isinstance(special_cases, str):
                special_cases = [special_cases]
            result = []
            for name in self._iterable:
                if not is_valid_name(name):
                    continue
                try:
                    if len(name.split('.')) <= depth:
                        result.append(name)
                        continue
                    if special_cases:
                        for case in special_cases:
                            if re.search(case, name):
                                result.append(name)
                                break
                    elif not name.endswith('.__doc__'):
                        if get_module_path(eval(name)).startswith(self.module_path):
                            result.append(name)
                    elif get_module_path(eval(name[:-8])).startswith(self.module_path):
                        result.append(name)
                except Exception as e:
                    print(f"执行eval('{name}')出错:", end='')
                    print(e)
                    print(case, name)
                    print(special_cases)
                    print(self, self.module_path)
                    # print_exc()
                    result.append(name)
                    import ipdb
                    ipdb.set_trace()
            self._iterable = result
            return self

        def deduplicate(self, class_names: tuple=None, pattern='.*'):
            pass

        def insert_my_function_special_cases(self, special_cases=MY_FUNCTION_SPECIAL_CASES, pattern='.*', current_module_only=True):
            pass

        def insert_code_special_cases(self, special_cases=CODE_SPECIAL_CASES, pattern='.*', current_module_only=True):
            pass

        def insert_special_cases(self, class_names: tuple=None, special_cases=None, pattern='.*', current_module_only=True):
            pass

        def deeper(self, deeper_class_names: tuple=DEEPER_CLASS_NAMES, current_module_doc_only=True, filter_pattern=None, exclude_pattern=None):
            if deeper_class_names and isinstance(deeper_class_names, str):
                deeper_class_names = [deeper_class_names]
            result = []
            for name in self._iterable:
                # result.append(name)
                # import ipdb
                ipdb.set_trace()
                if deeper_class_names and eval(f'{name}.__class__.__name__') not in deeper_class_names:
                    continue
                ls = name.split('.')
                if len(ls) == self.depth+1 and is_valid_name(ls[-1]):
                    for p in eval('dir(%s)' % name):
                        if is_valid_name(p):
                            if filter_pattern and not re.search(filter_pattern, f'{name}.{p}'):
                                break
                            if exclude_pattern and re.search(exclude_pattern, f'{name}.{p}'):
                                break
                            if current_module_doc_only:
                                if p == '__doc__' and not get_module_path(eval(name)).startswith(self.module_path):
                                    break
                            result.append(f'{name}.{p}')
                            print(f'append: {name}.{p}   ok')
            self._iterable = result
            self.depth += 1
            return self

        def get_result(self):
            return self._iterable

        def search(self, re_pattern: str):
            result = []
            for name in self._iterable:
                if re.search(re_pattern, name):
                    result.append(name)
            return result

        def depth_filter(self, depth):
            if isinstance(depth, int):
                depth = [depth]
            result = []
            for n in depth:
                if n <= self.depth:
                    result.extend(self.search('([a-zA-Z0-9_]+\.){%s}[a-zA-Z0-9_]+' % n))
            self._iterable = result
            return self

        def get_dict(self):
            dir_details_dict = {}
            for name in self._iterable:
                try:
                    if is_valid_name(name):
                        dir_details_dict[name] = eval(name)
                    else:
                        dir_details_dict[name] = f'无法获取{name}的值'
                except Exception as e:
                    print(name + ':' + f"执行eval('{name}')语句出错:", end='')
                    print(e)
                    # print_exc()
                    dir_details_dict[name] = f"执行eval('{name}')语句出错,{e}"
            return dir_details_dict

        def _generate_result_for_display(self):
            i = 0
            result = self._iterable[:]
            while i < len(result)-1:
                ls = result[i+1].split('.')
                if len(ls) < len(result[i].split('.')) or not '.'.join(ls[:-1]) in result[i]:
                    i += 1
                    result.insert(i, '\n')
                i += 1
                # flag = True
            return result

        def display(self, result=None):
            result = result or self._generate_result_for_display()
            if not result:
                return
            for name in result:
                if name == '\n':
                    print()
                    continue
                try:
                    print(name + ':', eval(name))
                except Exception as e:
                    print(name + ':' + f"执行eval('{name}')语句出错:", end='')
                    print(e)
                    # print_exc()

        def pretty_display(self, depth=2, prefix='', is_root_container=True):
            dir_details_dict = self.get_dict()
            pretty_print(dir_details_dict, depth=depth, prefix=prefix, is_root_container=is_root_container)

        def revert(self):
            self._iterable = self.__origin
            return self

        def commit(self):
            self.__origin = self._iterable

        def save_to_json(self, filename='', dir_path=DIR_PATH):
            filename = filename if filename else '%s.json' % self.name
            file_path = os.path.join(dir_path, filename)
            dir_details_dict = {}
            for name in self._iterable:
                if is_valid_name(name):
                    dir_details_dict[name] = eval(name)
                else:
                    dir_details_dict[name] = f'无法获取{name}的值'
            with open(file_path, 'w') as f:
                json.dump(dir_details_dict, f)
                print(f'写入文件完成,数据量:{len(self._iterable)},文件路径：{file_path},请查看!')

        def save_to_txt(self, filename='', dir_path=DIR_PATH, n_lines=1):
            filename = filename if filename else '%s.txt' % self.name
            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'w') as f:
                for name in self._generate_result_for_display():
                    if name == '\n':
                        f.write('\n'*n_lines)
                        continue
                    try:
                        f.write(name + ':')
                        if is_valid_name(name):
                            f.write(str(eval(name))+'\n')
                        else:
                            f.write(f'无法获取{name}的值\n')
                    except Exception as e:
                        print(f"写入str(eval('{name}')出错:", end='')
                        f.write(f"写入str(eval('{name}')出错！\n")
                        print(e)
                        # print_exc()
                print(f'写入文件完成,数据量:{len(self._iterable)},文件路径：{file_path},请查看!')

        def __contains__(self, item):
            return item in self._iterable

        def __getitem__(self, i):
            return self._iterable[i]

        def __next__(self):
            value = self._iterable[self._index]
            self._index += 1
            return value

        def __len__(self):
            return len(self._iterable)

        @property
        def size(self):
            return len(self._iterable)

        def __repr__(self):
            return '<{0.__module__}.{0.__name__}, length:{1}>'.format(type(self), len(self._iterable))


def generate_dir_file(ob, filename='', dir_path=DIR_PATH, file_type='txt', depth=3, filter_pattern='.*',
                      exclude_pattern='__', re_special_cases=('[a-zA-Z0-9]+\.__doc__$',), ignore_basic=False,
                      commons=COMMONS, special_cases=('__doc__',),
                      module_filter_depth: int=2, only_doc: bool=False):
    if special_cases and isinstance(special_cases, str):
        special_cases = [special_cases]
    if re_special_cases and isinstance(re_special_cases, str):
        re_special_cases = [re_special_cases]
    resource = DeepDir(ob, depth=depth, filter_pattern=filter_pattern, exclude_pattern=exclude_pattern,
                       ignore_basic=ignore_basic, special_cases=re_special_cases)
    print('raw:', resource.size)
    flt = resource()
    if only_doc:
        flt.re_filter('__doc__$', depth=1)
        print(len(flt))
    flt.exclude_common(commons, special_cases=special_cases)
    print('exclude_common:', flt.size)
    flt.exclude_doc_of_common(commons)
    print('exclude_doc_of_common:', flt.size)
    flt.re_exclude('__builtins__', depth=1)
    print('re_exclude_builtins:', len(flt))
    if module_filter_depth:
        flt.current_module_filter(module_filter_depth)
        print('current_module_filter:', flt.size)
    if file_type == 'txt':
        flt.save_to_txt(filename=filename, dir_path=dir_path)
    elif file_type == 'json':
        flt.save_to_json(filename=filename, dir_path=dir_path)
    else:
        raise ValueError('不支持其他文件类型！')
    return flt


ddir = DeepDir


if __name__ == '__main__':
    show_module()
    # test = deepdir(re, depth=3, exclude_pattern='__|._', ignore_basic=True)
    # test.show()
    # flt = test()
    # import numpy
    # test = deepdir(numpy, depth=2, exclude_pattern='__|._', ignore_basic=True)
    # test.pretty_show()
    # flt.re_filter('__doc__$')
    # flt.save_to_txt()
    # from appium_robot.robot.tools import my_driver_and_element
    # generate_dir_file(my_driver_and_element)
    # flt.display()
    # flt.save_to_txt()
    # import appium_robot
    # flt = generate_dir_file(appium_robot, depth=3)
    # flt.deeper(deeper_class_names=('function', 'type', 'module', 'method-wrapper'))
    # import ipdb
    # ipdb.set_trace()
