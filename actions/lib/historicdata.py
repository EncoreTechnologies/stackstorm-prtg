#!/usr/bin/env python
from base import BaseAction

import re

# date format = yyyy-mm-dd-hh-mm-ss
PRTG_DATETIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
PRTG_DATETIME_REGEX = '[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}'
PRTG_DATETIME_PATTERN = re.compile(PRTG_DATETIME_REGEX)


class HistoricDataAction(BaseAction):

    def validate_datetime_str(self, datetime_str, name):
        if not PRTG_DATETIME_PATTERN.search(datetime_str):
            raise ValueError("{} doesn't match the PRTG date/time format"
                             " 'yyyy-mm-dd-hh-mm-ss' : {}".format(name, datetime_str))
        return True

    def run(self, start_date, end_date, average_interval_sec, **kwargs):
        self.validate_datetime_str(start_date, 'start_date')
        self.validate_datetime_str(end_date, 'end_date')

        params = kwargs.get('params', {})
        params['sdate'] = start_date
        params['edate'] = end_date
        params['avg'] = average_interval_sec

        kwargs['params'] = params
        return self.call(**kwargs)
