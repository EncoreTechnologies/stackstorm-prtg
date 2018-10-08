#!/usr/bin/env python
#
# API docs
# https://www.paessler.com/manuals/prtg/application_programming_interface_api_definition
# https://<prtgserver>/api.htm
from st2common.runners.base_action import Action

import requests
import xmltodict


class BaseAction(Action):

    def connect(self, **kwargs):
        self.transport = kwargs['transport']
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.server = kwargs['server']
        self.session = requests.Session()
        self.session.verify = kwargs['verify_ssl']

    def make_params(self, params):
        # PRTG needs the columns in a CSV list, so if we passed in a list
        # convert it to a CSV string
        if params.get('columns') and isinstance(params['columns'], list):
            params['columns'] = ','.join(params['columns'])

        # default output is JSON so we can parse it easily
        if not params.get('output'):
            params['output'] = 'json'

        # add in our credentials
        if 'username' not in params:
            params['username'] = self.username
        if 'password' not in params:
            params['password'] = self.password
        return params

    def make_headers(self, output, headers=None):
        # Create headers as a dict if none were passed in
        if not headers:
            headers = {}

        # set headers for the type of data we would like back
        if output == 'json':
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'
        elif output == 'xml':
            headers['Accept'] = 'application/xml'
            headers['Content-Type'] = 'application/xml'
        else:
            raise ValueError("Unsupported output type: {}".format(output))
        return headers

    def response_data(self, response, output):
        # return the data based on output format
        if output == 'json':
            return response.json()
        elif output == 'xml':
            return xmltodict.parse(response.content)
        else:
            return response.content

    def get(self, endpoint, params=None, headers=None):
        params = self.make_params(params)
        headers = self.make_headers(params['output'], headers=headers)

        # make the call
        url = '{}://{}{}'.format(self.transport, self.server, endpoint)
        response = self.session.get(url, params=params, headers=headers)

        # check for errors
        response.raise_for_status()

        # extract data from the response, based on the output format
        return self.response_data(response, params['output'])

    def ensure_list(self, d):
        if not isinstance(d, list):
            return [d]
        return d

    def call(self, **kwargs):
        self.connect(**kwargs)
        endpoint = kwargs['endpoint']
        params = {}
        if kwargs.get('id'):
            params['id'] = kwargs['id']
        if kwargs.get('columns'):
            params['columns'] = kwargs['columns']
        if kwargs.get('params'):
            params.update(kwargs['params'])
        return self.get(endpoint, params=params)

    def run(self, **kwargs):
        return self.call(**kwargs)
