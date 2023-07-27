import unittest
import json
import yaml
import platformdirs
from src.config_builder.config_builder import load_config, _build_file_list
from os import path, environ

MYDIR = path.split(__file__)[0]
OVERRIDE = path.join(MYDIR, 'override.yml')
BASECONF = path.join(MYDIR, 'base.yml')
JSON_BASECONF = path.join(MYDIR, 'base.json')
CONF_NAME = 'test.yml'
APPLICATION = 'TestApp'


class MyTestCase(unittest.TestCase):
    def test_base(self):
        conf = load_config(CONF_NAME, base_config=BASECONF)
        self.validate_base_only(conf)

    def validate_base_only(self, conf):
        self.assertEqual(conf.get('v1'), 'base')
        d1 = conf.get('d1')
        self.assertTrue(isinstance(d1, dict), 'd1 should be dict')
        self.assertEqual(d1.get('v2'), 'base')
        d2 = conf.get('d2')
        self.assertTrue(isinstance(d2, dict), 'd2 should be dict')
        self.assertEqual(d2.get('v1'), 'base')
        d2v2 = d2.get('v2')
        self.assertTrue(isinstance(d2v2, dict), 'd2:v2 should be dict')
        self.assertEqual(d2v2.get('v1'), 'base')

    def test_override(self):
        conf = load_config(CONF_NAME, base_config=BASECONF, overrides=OVERRIDE)
        self.validate_override(conf)

    def validate_override(self, conf):
        self.assertEqual(conf.get('v1'), 'base')
        self.assertEqual(conf.get('v2'), 'override')
        d1 = conf.get('d1')
        self.assertTrue(d1 is None, "d1 should be None")
        d2 = conf.get('d2')
        self.assertTrue(isinstance(d2, dict), 'd2 should be dict')
        self.assertEqual(d2.get('v1'), 'base')
        d2v2 = d2.get('v2')
        self.assertTrue(isinstance(d2v2, dict), 'd2:v2 should be dict')
        self.assertEqual(d2v2.get('v1'), 'base')
        self.assertEqual(d2v2.get('v2'), 'override')

    def test_base_as_dict(self):
        with open(BASECONF) as f:
            baseconf = yaml.safe_load(f)
        conf = load_config(CONF_NAME, base_config=baseconf, overrides=OVERRIDE)
        # ensure baseconf param wasn't munged
        self.assertEqual(baseconf.get('v1'), 'base', "baseconf v1 munged")
        self.assertEqual(baseconf.get('v2'), 'base', "baseconf v2 munged")
        self.assertTrue(isinstance(baseconf.get('d1'), dict), "baseconf d1 munged")

        self.assertEqual(conf.get('v1'), 'base')
        self.assertEqual(conf.get('v2'), 'override')
        d1 = conf.get('d1')
        self.assertTrue(d1 is None, "d1 should be None")
        d2 = conf.get('d2')
        self.assertTrue(isinstance(d2, dict), 'd2 should be dict')
        self.assertEqual(d2.get('v1'), 'base')
        d2v2 = d2.get('v2')
        self.assertTrue(isinstance(d2v2, dict), 'd2:v2 should be dict')
        self.assertEqual(d2v2.get('v1'), 'base')
        self.assertEqual(d2v2.get('v2'), 'override')

    def test_json_load(self):
        conf = load_config(CONF_NAME, base_config=JSON_BASECONF, overrides=OVERRIDE)
        self.validate_override(conf)

    def test_file_list(self):
        files = _build_file_list(CONF_NAME,
                                 application=APPLICATION,
                                 base_config=BASECONF,
                                 overrides=OVERRIDE)
        self.assertEqual(files[0], BASECONF)
        files = files[1:]
        site_dirs = platformdirs.site_config_dir(APPLICATION, multipath=True)
        for sd in site_dirs.split(':'):
            self.assertEqual(files[0], path.join(sd, CONF_NAME))
            files = files[1:]
        self.assertEqual(files[0], path.join(platformdirs.user_config_dir(APPLICATION), CONF_NAME))
        files = files[1:]
        venv = environ.get('VIRTUAL_ENV')
        if venv:
            self.assertEqual(files[0], path.join(venv, 'config', APPLICATION, CONF_NAME))
            files = files[1:]
        self.assertEqual(files[0], OVERRIDE)
        files = files[1:]
        self.assertEqual(len(files), 0)


if __name__ == '__main__':
    unittest.main()
