import yaml
import json

from st2tests.base import BaseActionTestCase


class PrtgBaseTestCase(BaseActionTestCase):
    __test__ = False

    def setUp(self):
        super(PrtgBaseTestCase, self).setUp()

    def load_yaml(self, filename):
        return yaml.safe_load(self.get_fixture_content(filename))

    def load_json(self, filename):
        return json.loads(self.get_fixture_content(filename))
