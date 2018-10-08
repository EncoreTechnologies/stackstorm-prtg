from prtg_base_test_case import PrtgBaseTestCase
from lib.base import BaseAction
from lib.historicdata import HistoricDataAction
from st2common.runners.base_action import Action

import mock


class TestHistoricDataAction(PrtgBaseTestCase):
    __test__ = True
    action_cls = HistoricDataAction

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, HistoricDataAction)
        self.assertIsInstance(action, BaseAction)
        self.assertIsInstance(action, Action)

    def test_validate_datetime_str(self):
        action = self.get_action_instance({})
        result = action.validate_datetime_str('2018-10-03-19-56-22', 'Nick')
        self.assertEquals(result, True)

    def test_validate_datetime_str_fail(self):
        action = self.get_action_instance({})
        with self.assertRaises(ValueError):
            action.validate_datetime_str('2018-10-03 19:56:22', 'Nick')

    @mock.patch('lib.historicdata.HistoricDataAction.call')
    def test_run(self, mock_call):
        action = self.get_action_instance({})
        mock_call.return_value = 'expected'

        kwargs = {
            'start_date': '2018-10-08-00-00-00',
            'end_date': '2018-10-10-00-00-00',
            'average_interval_sec': 900,
            'params': {
                'existing': 'data',
            }
        }

        result = action.run(**kwargs)

        self.assertEquals(result, 'expected')
        mock_call.assert_called_with(params={
            'sdate': '2018-10-08-00-00-00',
            'edate': '2018-10-10-00-00-00',
            'avg': 900,
            'existing': 'data',
        })

    @mock.patch('lib.historicdata.HistoricDataAction.call')
    def test_run_create_params_if_empty(self, mock_call):
        action = self.get_action_instance({})
        mock_call.return_value = 'expected'

        kwargs = {
            'start_date': '2018-10-08-00-00-00',
            'end_date': '2018-10-10-00-00-00',
            'average_interval_sec': 900,
        }

        result = action.run(**kwargs)

        self.assertEquals(result, 'expected')
        mock_call.assert_called_with(params={
            'sdate': '2018-10-08-00-00-00',
            'edate': '2018-10-10-00-00-00',
            'avg': 900,
        })

    def test_run_invalid_start_raises(self):
        action = self.get_action_instance({})
        kwargs = {
            'start_date': 'blah',
            'end_date': '2018-10-10-00-00-00',
            'average_interval_sec': 900,
        }

        with self.assertRaises(ValueError):
            action.run(**kwargs)

    def test_run_invalid_start_raises(self):
        action = self.get_action_instance({})
        kwargs = {
            'start_date': '2018-10-10-00-00-00',
            'end_date': 'blah',
            'average_interval_sec': 900,
        }

        with self.assertRaises(ValueError):
            action.run(**kwargs)
