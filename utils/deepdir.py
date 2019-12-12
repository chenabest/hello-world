from traceback import print_exc
import re
import os


BASIC = ('str', 'int', 'float', 'bool', 'list', 'dict', 'tuple', 'NoneType', 'set')


def is_basic(name, basic=BASIC):
    if eval('{}.__class__.__name__'.format(name)) in basic:
        return True
    else:
        return False


def show_dir_details(name: str, max_depth=1, filter_pattern='.*', exclude_pattern=None, special_cases=('[a-zA-Z0-9]+.__doc__$',), ignore_basic=False):
    """
    功能：显示一个函数、方法、类、模块、变量的所有相关的详细信息，帮助快速了解其用法。
    :param name: 变量或类、方法等的名称
    :param max_depth: 最大深度
    :param filter_pattern: 正则表达式，过滤出想要看的信息
    :param exclude_pattern: 正则表达式，在filter之后再排除一些模式
    :param special_cases: 属于special_cases的模式不会被exclude
    :param ignore_basic: True,False或序列(列表、元组等)。表示忽略的类型，不显示其详细信息。False不忽略任何类型，True将忽略默认类型，序列将忽略指定类型。
    :return: 
    """
    exclude_pattern = '__dir__' if exclude_pattern is None else '__dir__|' + exclude_pattern
    if max_depth == 0 or name.split('.')[-1] in ['__abstractmethods__']:
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
            print(f'获取信息：{name}.{p}出错')
            print(e)
            print_exc()
            raise
        show_dir_details(name + '.' + p, max_depth - 1, filter_pattern, exclude_pattern, special_cases, ignore_basic)
    if flag:
        print()


class deepdir(object):
    def __init__(self, name: str, max_depth=1, filter_pattern='.*', exclude_pattern=None,
                 special_cases=('[a-zA-Z0-9]+.__doc__$',), ignore_basic=False):
        self.name = name
        self.max_depth = max_depth
        self.filter_pattern = filter_pattern
        self.exclude_pattern = exclude_pattern
        self.special_cases = special_cases
        self.ignore_basic = ignore_basic
        self.result = self.dir_deep(self.name, self.max_depth, self.filter_pattern, self.exclude_pattern, self.special_cases,
                               self.ignore_basic)

    @staticmethod
    def dir_deep(name: str, max_depth=1, filter_pattern='.*', exclude_pattern=None,
                 special_cases=('[a-zA-Z0-9]+\.__doc__$',), ignore_basic=False):
        exclude_pattern = '__dir__' if exclude_pattern is None else '__dir__|' + exclude_pattern
        result = []

        def _dir_filter(name, max_depth, re_filter, re_exclude, special_cases, ignore_basic):
            if max_depth == 0 or name.split('.')[-1] in ['__abstractmethods__']:
                return
            if ignore_basic:
                if isinstance(ignore_basic, bool):
                    if is_basic(name):
                        return
                elif is_basic(name, ignore_basic):
                    return
            for p in eval('dir(%s)' % name):
                try:
                    if p not in ['__abstractmethods__'] and re.search(re_filter, f'{name}.{p}'):
                        if re_exclude:
                            is_in_special_cases = False
                            if special_cases:
                                for case in special_cases:
                                    if re.search(case, f'{name}.{p}'):
                                        result.append(name + '.' + p)
                                        is_in_special_cases = True
                                        break
                            if not is_in_special_cases and not re.search(re_exclude, f'{name}.{p}'):
                                result.append(name + '.' + p)
                        else:
                            result.append(name + '.' + p)
                except Exception as e:
                    print(f'获取信息：{name}.{p}出错')
                    print(e)
                    print_exc()
                    raise
                _dir_filter(name + '.' + p, max_depth - 1, re_filter, re_exclude, special_cases, ignore_basic)

        _dir_filter(name, max_depth, filter_pattern, exclude_pattern, special_cases, ignore_basic)
        return result

    def show(self):
        show_dir_details(self.name, self.max_depth, self.filter_pattern, self.exclude_pattern, self.special_cases,
                         self.ignore_basic)

    def get_result(self):
        return self.result

    @property
    def size(self):
        return len(self.result)

    def __contains__(self, item):
        return item in self.result

    def __len__(self):
        return len(self.result)

    def __call__(self, *args, **kwargs):
        return self._DirFilter(self.result)

    class _DirFilter:
        def __init__(self, iterable):
            self.__origin = iterable
            self._iterable = iterable
            self._index = 1

        def re_filter(self, pattern):
            self._iterable = [name for name in self._iterable if re.search(pattern, name)]
            return self

        def re_exclude(self, pattern):
            self._iterable = [name for name in self._iterable if not re.search(pattern, name)]
            return self

        def exclude_common(self, commons: list, special_cases=('__doc__',)):
            excludes = []
            for common in commons:
                excludes.extend(eval('dir({})'.format(common)))
            for case in special_cases:
                excludes.remove(case)
            exclude_pattern = '|'.join(excludes)
            self.re_exclude(exclude_pattern)
            return self

        def get_result(self):
            return self._iterable

        def display(self):
            for name in self._iterable:
                print(name + ':', eval(name))

        def revert(self):
            self._iterable = self.__origin
            return self

        def commit(self):
            self.__origin = self._iterable

        def save_to_json(self, filename='python_learning.json', dir_path='/Users/achen/workspaces/data_automation'):
            file_path = os.path.join(dir_path, filename)
            dir_details_dict = {}
            for name in self._iterable:
                dir_details_dict[name] = eval(name)
            with open(file_path, 'w') as f:
                json.dump(dir_details_dict, f)
                print(f'写入文件完成,文件路径：{file_path},请查看!')

        def save_to_txt(self, filename='python_learning.txt', dir_path='/Users/achen/workspaces/data_automation'):

            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'w') as f:
                for name in self._iterable:
                    f.write(name + ':' + str(eval(name))+'\n')
                print(f'写入文件完成,文件路径：{file_path},请查看!')

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
        
        
dir_deep = deepdir.dir_deep


if __name__ == '__main__':
    # a = 889
    # print(is_basic('a'))
    # show_dir_details('a', ignore_basic=True)
    # show_dir_details('str', max_depth=2, re_exclude='__', special_cases=('__doc__$', ), ignore_basic=False)
    # show_dir_details('get_timestamp_of_next_work_start_time', 3,
    #                  re_filter='_time\.__code__[a-zA-Z0-9_]*(\.co_[a-zA-Z0-9]*)?(.__doc__)?$')
    # show_dir_details('get_timestamp_of_next_work_start_time', re_filter='\.co_[a-zA-Z0-9_]*(\.[a-zA-Z0-9_]*)*$')
    # show_dir_details('my_driver_and_element', max_depth=3, re_filter='(\.[a-zA-Z_]+){1,2}|(\.[a-zA-Z_]+){2}\.__doc__$',
    #                  re_exclude='__|sys', ignore_basic=True)
    dirm = show_dir_details
    dirm('DAG', max_depth=2, filter_pattern='__', ignore_basic=True)
    ls = dir_deep('re', max_depth=3, exclude_pattern='__|._')
    # a = 889
    # print(is_basic('a'))
    # show_dir_details('a', ignore_basic=True)
    # show_dir_details('str', max_depth=2, re_exclude='__', special_cases=('__doc__$', ), ignore_basic=False)
    # show_dir_details('get_timestamp_of_next_work_start_time', 3,
    #                  re_filter='_time\.__code__[a-zA-Z0-9_]*(\.co_[a-zA-Z0-9]*)?(.__doc__)?$')

    # show_dir_details('get_timestamp_of_next_work_start_time', re_filter='\.co_[a-zA-Z0-9_]*(\.[a-zA-Z0-9_]*)*$')

    # dir_deep使用实例
    # In[10]: ls = dir_deep('re', max_depth=3, re_exclude='__|._')
    #
    # In[11]: len(ls)
    # Out[11]: 3725
    #
    # In[12]: ls = dir_deep('re', max_depth=3, re_exclude='__|._', ignore_basic=True)
    #
    # In[13]: len(ls)
    # Out[13]: 1402

    import ipdb
    ipdb.set_trace()
