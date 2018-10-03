from base import BaseAction


class HistoricDataAction(BaseAction):

    def run(self, start_date, end_date, average_interval_sec, **kwargs):
        self.validate_datetime_str(start_date, 'start_date')
        self.validate_datetime_str(end_date, 'end_date')

        params = kwargs.get('params', {})
        params['sdate'] = start_date
        params['edate'] = end_date
        params['avg'] = average_interval_sec
        kwargs['params'] = params

        return self.call(**kwargs)
