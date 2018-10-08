from prtg_base_test_case import PrtgBaseTestCase
from lib.base import BaseAction
from st2common.runners.base_action import Action

import mock
import requests


class TestBaseAction(PrtgBaseTestCase):
    __test__ = True
    action_cls = BaseAction

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, BaseAction)
        self.assertIsInstance(action, Action)

    def test_connect(self):
        action = self.get_action_instance({})

        action.connect(transport='https',
                       server='prtg.domain.tld',
                       username='user',
                       password='password',
                       verify_ssl=True)

        self.assertEquals(action.transport, 'https')
        self.assertEquals(action.server, 'prtg.domain.tld')
        self.assertEquals(action.username, 'user')
        self.assertEquals(action.password, 'password')
        self.assertIsInstance(action.session, requests.Session)
        self.assertEquals(action.session.verify, True)

    def test_make_params_columns(self):
        action = self.get_action_instance({})
        result = action.make_params({'columns': ['a', 'b', 'c'],
                                     'output': 'json',
                                     'username': 'user',
                                     'password': 'pass'})
        self.assertEquals(result, {'columns': 'a,b,c',
                                   'output': 'json',
                                   'username': 'user',
                                   'password': 'pass'})

    def test_make_params_columns_not_list(self):
        action = self.get_action_instance({})
        result = action.make_params({'columns': 'abc',
                                     'output': 'json',
                                     'username': 'user',
                                     'password': 'pass'})
        self.assertEquals(result, {'columns': 'abc',
                                   'output': 'json',
                                   'username': 'user',
                                   'password': 'pass'})

    def test_make_params_no_columns(self):
        action = self.get_action_instance({})
        result = action.make_params({'output': 'json',
                                     'username': 'user',
                                     'password': 'pass'})
        self.assertEquals(result, {'output': 'json',
                                   'username': 'user',
                                   'password': 'pass'})

    def test_make_params_output(self):
        action = self.get_action_instance({})
        result = action.make_params({'output': 'abc',
                                     'username': 'user',
                                     'password': 'pass'})
        self.assertEquals(result, {'output': 'abc',
                                   'username': 'user',
                                   'password': 'pass'})

    def test_make_params_no_output(self):
        action = self.get_action_instance({})
        result = action.make_params({'username': 'user',
                                     'password': 'pass'})
        self.assertEquals(result, {'output': 'json',
                                   'username': 'user',
                                   'password': 'pass'})

    def test_make_params_username_password(self):
        action = self.get_action_instance({})
        action.username = 'instance_user'
        action.password = 'instance_pass'
        result = action.make_params({'output': 'abc',
                                     'username': 'user',
                                     'password': 'pass'})
        self.assertEquals(result, {'output': 'abc',
                                   'username': 'user',
                                   'password': 'pass'})

    def test_make_params_user_pass_from_instance(self):
        action = self.get_action_instance({})
        action.username = 'instance_user'
        action.password = 'instance_pass'
        result = action.make_params({})
        self.assertEquals(result, {'output': 'json',
                                   'username': 'instance_user',
                                   'password': 'instance_pass'})

    def test_make_headers_json(self):
        action = self.get_action_instance({})
        result = action.make_headers('json')
        self.assertEquals(result, {'Accept': 'application/json',
                                   'Content-Type': 'application/json'})

    def test_make_headers_xml(self):
        action = self.get_action_instance({})
        result = action.make_headers('xml')
        self.assertEquals(result, {'Accept': 'application/xml',
                                   'Content-Type': 'application/xml'})

    def test_make_headers_bad_raises(self):
        action = self.get_action_instance({})
        with self.assertRaises(ValueError):
            action.make_headers('junk')

    def test_response_data_json(self):
        # setup
        action = self.get_action_instance({})
        mock_response = mock.MagicMock()
        mock_response.json.return_value = 'expected'

        # execute
        result = action.response_data(mock_response, 'json')

        # assert
        self.assertEquals(result, 'expected')

    def test_response_data_xml(self):
        # setup
        action = self.get_action_instance({})
        mock_response = mock.MagicMock()
        mock_response.content = '<data><stuff>xxx</stuff></data>'

        # execute
        result = action.response_data(mock_response, 'xml')

        # assert
        self.assertEquals(result, {
            'data': {
                'stuff': 'xxx'
            }
        })

    def test_response_data_content(self):
        # setup
        action = self.get_action_instance({})
        mock_response = mock.MagicMock(content='expected')

        # execute
        result = action.response_data(mock_response, 'something')

        # assert
        self.assertEquals(result, 'expected')

    def test_get(self):
        # setup
        action = self.get_action_instance({})
        action.transport = 'https'
        action.server = 'prtg.domain.tld'
        action.username = 'user'
        action.password = 'pass'

        mock_response = mock.MagicMock()
        mock_response.json.return_value = 'expected'

        action.session = mock.MagicMock()
        action.session.get.return_value = mock_response

        params = {'columns': ['a', 'b', 'c']}

        # execute
        result = action.get('/api/test', params=params)

        # assert
        self.assertEquals(result, 'expected')
        action.session.get.assert_called_with('https://prtg.domain.tld/api/test',
                                              params={'output': 'json',
                                                      'username': 'user',
                                                      'password': 'pass',
                                                      'columns': 'a,b,c'},
                                              headers={'Accept': 'application/json',
                                                       'Content-Type': 'application/json'})

    def test_ensure_list(self):
        action = self.get_action_instance({})
        result = action.ensure_list(['a'])
        self.assertEquals(result, ['a'])

    def test_ensure_list_not_list(self):
        action = self.get_action_instance({})
        result = action.ensure_list('abcdef')
        self.assertEquals(result, ['abcdef'])

    @mock.patch('lib.base.BaseAction.get')
    @mock.patch('lib.base.BaseAction.connect')
    def test_call(self, mock_connect, mock_get):
        # setup
        action = self.get_action_instance({})
        mock_get.return_value = 'expected'

        # execute
        result = action.call(endpoint='/api/test')

        # assert
        self.assertEquals(result, 'expected')
        mock_connect.assert_called_with(endpoint='/api/test')
        mock_get.assert_called_with('/api/test', params={})

    @mock.patch('lib.base.BaseAction.get')
    @mock.patch('lib.base.BaseAction.connect')
    def test_call_params(self, mock_connect, mock_get):
        # setup
        action = self.get_action_instance({})
        mock_get.return_value = 'expected'

        # execute
        result = action.call(endpoint='/api/test',
                             id=1234,
                             columns=['a', 'b', 'c'],
                             params={'test': 'data'})

        # assert
        self.assertEquals(result, 'expected')
        mock_connect.assert_called_with(endpoint='/api/test',
                                        id=1234,
                                        columns=['a', 'b', 'c'],
                                        params={'test': 'data'})
        mock_get.assert_called_with('/api/test', params={
            'id': 1234,
            'columns': ['a', 'b', 'c'],
            'test': 'data'
        })
