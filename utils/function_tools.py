# achen 2019/11/28 1:24 PM
# function_tools

import pendulum
from collections import Iterable
from traceback import print_exc


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


def is_valid_container(content):
    if not content or isinstance(content, str) or not isinstance(content, Iterable):
        return False
    else:
        return True


def pretty_print(content, prefix='', is_root_container=True):
    """
    当遇到多层嵌套复杂的数据类型的变量焦头烂额时，试试用pretty_print的方法打印下，你会豁然开朗。
    功能：美化容器对象（列表、字典等及其任意嵌套形式）的显示，不同的元素换行显示，并自动对齐同一层元素，实际使用时一般不用传prefix和is_root_container参数
    :param content: 请传一个复杂的多层嵌套的组合数据对象
    :param prefix: 递归时使用, 用于对齐
    :param is_root_container: 递归时使用，当设置为False时，如果content是容器类型，会打印出content的类型
    :return: None
    """
    try:
        if not is_valid_container(content):
            print(prefix, end='')
            print(content)
        else:
            if not is_root_container:
                print(prefix, end='')
                type_name = '<'+content.__class__.__name__+'>'
                print(type_name)
                prefix += ' '*(len(type_name)-1)  # 减1使与上一行最后一个字符对齐
            if 'get' in dir(content):     # 字典型容器
                for key in content:
                    print(prefix + key + ':', end='')
                    if content.get(key) == content:   # 避免递归死循环
                        print('{...}')
                    elif not is_valid_container(content.get(key)):
                        print(content.get(key))
                    else:
                        type_name = '<'+content.get(key).__class__.__name__+'>'
                        print(type_name)
                        new_prefix = prefix + ' '*(len(key+':'))+' '*(len(type_name)-1)
                        pretty_print(content.get(key), new_prefix, True)
            else:  # 非字典型容器
                for element in content:
                    pretty_print(element, prefix, False)
    except Exception as e:
        import time
        print(e)
        time.sleep(3)
        print_exc()
        import ipdb
        ipdb.set_trace()
        raise


if __name__ == '__main__':
    pretty_print(988)
    pretty_print(([1,2,3]))
    lg = globals()
    lg.update({'1111test': [1, 2, 3]})
    ll = locals()
    pretty_print([1, 2, 3, {'09wo', 78.99, 'fa'}, 3, 4, 5])
    pretty_print(lg)
    a = [1, 2, {'a22': 67, 'fff': 9.09}, 89293488989, [1, 2, (6, 'ff', 9)], 45, 'helloworld']
    pretty_print(a)
    import ipdb
    ipdb.set_trace()
