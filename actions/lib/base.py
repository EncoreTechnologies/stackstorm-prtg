#!/usr/bin/env python
from st2common.runners.base_action import Action

import requests
import re
import xmltodict

# API docs
# https://www.paessler.com/manuals/prtg/application_programming_interface_api_definition
# https://<prtgserver>/api.htm

# date format = yyyy-mm-dd-hh-mm-ss
PRTG_DATETIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
PRTG_DATETIME_REGEX = '[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}'
PRTG_DATETIME_PATTERN = re.compile(PRTG_DATETIME_REGEX)


class BaseAction(Action):

    def connect(self, **kwargs):
        self.transport = kwargs['transport']
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.server = kwargs['server']
        self.session = requests.Session()
        self.session.verify = kwargs['verify_ssl']

    def get(self, endpoint, params=None, headers=None):
        # Create headers as a dict if none were passed in
        if not headers:
            headers = {}

        # PRTG needs the columns in a CSV list, so if we passed in a list
        # convert it to a CSV string
        if params.get('columns') and isinstance(params['columns'], list):
            params['columns'] = ','.join(params['columns'])

        # default output is JSON so we can parse it easily
        if not params.get('output'):
            params['output'] = 'json'

        # set headers for the type of data we would like back
        if params['output'] == 'json':
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'
        elif params['output'] == 'xml':
            headers['Accept'] = 'application/xml'
            headers['Content-Type'] = 'application/xml'
        else:
            raise ValueError("Unsupported output type: {}".format(params['output']))

        # add in our credentials
        if 'username' not in params:
            params['username'] = self.username
        if 'password' not in params:
            params['password'] = self.password

        # make the call
        url = '{}://{}{}'.format(self.transport, self.server, endpoint)
        response = self.session.get(url, params=params, headers=headers)

        # check for errors
        response.raise_for_status()

        # return the data
        if params['output'] == 'json':
            return response.json()
        elif params['output'] == 'xml':
            return xmltodict.parse(response.content)
        else:
            return response.content

    def validate_datetime_str(self, datetime_str, name):
        if not PRTG_DATETIME_PATTERN.search(datetime_str):
            raise ValueError("{} doesn't match the PRTG date/time format"
                             " 'yyyy-mm-dd-hh-mm-ss' : {}".format(name, datetime_str))
        return True

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
