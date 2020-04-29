# Owner: <achen>
# !/usr/bin/python3
# 2020/3/20 11:10 PM
# data_filter.py

from appium_robot.robot.tools.function_tools import *
from datetime import datetime, timedelta
from copy import deepcopy
from wcwidth import wcswidth as ww


class DataFilterBase(object):
    """
    功能：筛选过滤数据，支持根据字段值筛选、使用正则匹配筛选和过滤，支持筛选指定时间范围内的数据
    """
    def __init__(self, data: list):
        self.__data = deepcopy(data)
        self.data = deepcopy(data)

    def field_filter(self, **kwargs):
        """
        根据指定字段筛选，选取指定字段名称存在并且值等于所传参数的数据
        支持多个字段筛选。relation表示逻辑关系，默认为and
        使用例子：self.field_filter(city='上海')
        :param kwargs: 
        :return: 
        """
        relation = 'and' if 'relation' not in kwargs else kwargs['relation']
        data = []
        if relation == 'and':
            for record in self.data:
                flag = True
                for key, value in kwargs.items():
                    if key not in record or record[key] != value:
                        flag = False
                        break
                if flag:
                    data.append(record)
        elif relation == 'or':
            for record in data:
                for key, value in kwargs.items():
                    if key in record and record[key] == value:
                        data.append(record)
                        break
        else:
            raise ValueError('relation值只能是and或or!')
        self.data = data

    def field_filter_in(self, **kwargs):
        """
        根据指定字段筛选，选取指定字段名称存在并且值in所传参数的数据
        支持多个字段筛选。relation表示逻辑关系，默认为and
        使用例子：self.field_filter_in(city=['上海', '北京'])
        :param kwargs: 
        :return: 
        """
        relation = 'and' if 'relation' not in kwargs else kwargs['relation']
        data = []
        if relation == 'and':
            for record in self.data:
                flag = True
                for key, values in kwargs.items():
                    if key not in record or record[key] not in values:
                        flag = False
                        break
                if flag:
                    data.append(record)
        elif relation == 'or':
            for record in data:
                for key, values in kwargs.items():
                    if key in record and record[key] in values:
                        data.append(record)
                        break
        else:
            raise ValueError('relation值只能是and或or!')
        self.data = data

    def field_interval_filter(self, field: str, min_value=None, max_value=None):
        min_value = min_value or 0.0
        max_value = max_value or 10000000000000
        data = []
        for record in self.data:
            if field in record:
                if min_value <= float(record[field]) <= max_value:
                    data.append(record)
        self.data = data

    def field_bool_filter(self, field: str, key=bool):
        data = []
        for record in self.data:
            if field in record and key(record[field]):
                    data.append(record)
        self.data = data

    def field_re_filter(self, field: str, pattern='.*'):
        """
        筛选指定字段存在并且值满足pattern模式的数据
        :param field: 字段名称
        :param pattern: 正则模式
        :return: 
        """
        data = []
        for record in self.data:
            if field in record and re.search(pattern, record[field]):
                data.append(record)
        self.data = data

    def field_re_exclude(self, field: str, pattern='\.\.\.'):
        """
        过滤掉指定字段存在并且值满足pattern模式的数据
        :param field: 字段名称
        :param pattern: 正则模式
        :return: 
        """
        data = []
        for record in self.data:
            if field not in record or not re.search(pattern, record[field]):
                data.append(record)
        self.data = data

    @staticmethod
    def strp_datetime(date_time: str):
        """
        将时间转化成datetime对象，目的是可以比较大小，根据时间筛选
        :param date_time: 
        :return: 
        """
        return datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def strp_date(date: str):
        """
        将日期转化成datetime对象，目的是可以比较大小，根据日期筛选
        :param date: 
        :return: 
        """
        return datetime.strptime(date, '%Y_%m_%d')

    def date_filter(self, time_field: str, start_date=None, end_date=None):
        """
        根据日期筛选数据
        :param time_field: 日期字段名称
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 
        """
        data = []
        if start_date and end_date:
            start_date = self.strp_date(start_date)
            end_date = self.strp_date(end_date) + timedelta(days=1)
            for record in self.data:
                if time_field in record:
                    record_datetime = self.strp_datetime(record[time_field])
                    if record_datetime and start_date <= record_datetime <= end_date:
                        data.append(record)
        elif start_date:
            start_date = self.strp_date(start_date)
            for record in self.data:
                if time_field in record:
                    record_datetime = self.strp_datetime(record[time_field])
                    if record_datetime and record_datetime >= start_date:
                        data.append(record)
        elif end_date:
            end_date = self.strp_date(end_date) + timedelta(days=1)
            for record in self.data:
                if time_field in record:
                    record_datetime = self.strp_datetime(record[time_field])
                    if record_datetime and record_datetime <= end_date:
                        data.append(record)
        else:
            data = self.data
        self.data = data

    def timedelta_filter(self, time_field: str, time_delta=None, **kwargs):
        """
        筛选距离现在一定时间范围内的数据，可以精确到秒级，在数据实时性要求高的时候使用
        :param time_field: 时间字段名称
        :param time_delta: timedelta对象
        :param kwargs: 使用该参数生成timedelta对象
        :return: 
        """
        time_delta = time_delta or timedelta(**kwargs)
        now = datetime.now()
        start_time = now - time_delta
        data = []
        for record in self.data:
            if time_field in record:
                record_datetime = self.strp_datetime(record[time_field])
                if record_datetime and record_datetime >= start_time:
                    data.append(record)
        self.data = data

    def field_distinct(self, field: str):
        values = set()
        for record in self.data:
            if field in record:
                values.add(record[field])
        return values

    def field_min(self, field: str, key=lambda x: x, default=None):
        if self.size >= 1:
            values = []
            for record in self.data:
                if field in record:
                    values.append(key(record[field]))
            if values:
                return min(values)
            elif default is not None:
                return default

    def field_max(self, field: str, key=lambda x: x, default=None):
        if self.size >= 1:
            values = []
            for record in self.data:
                if field in record:
                    values.append(key(record[field]))
            if values:
                return max(values)
            elif default is not None:
                return default

    def _field_sum(self, field: str, key=float):
        if self.size >= 1:
            count = 0
            s = 0
            for record in self.data:
                if field not in record:
                    continue
                try:
                    value = key(record[field])
                    s += value
                    count += 1
                except Exception as e:
                    pass
                    # print(record[field])
                    # print(e.__repr__())
            print('count:', count)
            return s, count

    def field_sum(self, field: str, key=float):
        s, _ = self._field_sum(field=field, key=key)
        return s

    def field_average(self, field: str, key=float, ndigits=2):
        s, count = self._field_sum(field=field, key=key)
        return round(s/count, ndigits=ndigits)

    def order_by_field(self, field: str, key=lambda x: x, default='', reverse=False):
        self.data.sort(key=lambda record: key(record.get(field, default)), reverse=reverse)

    def order_by(self, key, reverse=False):
        self.data.sort(key=key, reverse=reverse)

    def display(self, fields: list=None, hide_fields=None, default='', limit=None, width_limit=100, blank_line_between_records=False):
        """
        展示数据
        :return: 
        """
        if not self.data:
            print('[]')
            return
        if not fields:
            fields = []
            for record in self.data:
                for field in record:
                    if field not in fields:
                        fields.append(field)
        if hide_fields:
            for field in hide_fields:
                fields.remove(field)
        data = list()
        data.append(fields)
        if limit is None:
            start_index, end_index = 0, len(self.data)
        elif isinstance(limit, int):
            start_index, end_index = 0, limit
        else:
            start_index, end_index = limit
        field_width = dict()
        for record in self.data[start_index: end_index]:
            data.append([])
            for field in fields:
                value = record.get(field, default)
                data[-1].append(value)
                width = ww(str(value))
                if width > field_width.get(field, ww(str(field))):
                    field_width[field] = min(width, width_limit)
        for record in data:
            for i in range(len(fields)):
                print(str(record[i]) + ' ' * (field_width.get(fields[i], ww(str(fields[i])))-ww(str(record[i]))), end=' '*3)
            print()
            if blank_line_between_records:
                print()

    def commit(self):
        """
        提交当前数据到备份
        :return: 
        """
        self.__data = deepcopy(self.data)

    def revert(self):
        """
        回滚数据
        :return: 
        """
        self.data = deepcopy(self.__data)

    def __len__(self):
        return len(self.data)

    @property
    def size(self):
        return len(self.data)


if __name__ == '__main__':
    show_module(form='*')
