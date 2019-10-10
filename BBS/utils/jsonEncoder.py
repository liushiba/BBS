# -*- coding: utf-8 -*-

import json
import decimal

from datetime import date, datetime


class JsonEncoder(json.JSONEncoder):  # JSON序列化器
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        else:
            super(JsonEncoder, self).default(obj)