# import libraries
import logging
import unittest
from pathlib import Path
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.configs.IndexingConfig import FileIndexingConfig
from tests.config.t_config import settings

class t_IndexingConfig(TestCase):
    """Testbed for the GameSourceSchema class.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings, logger=None)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        cls.test_schema = FileIndexingConfig(
            name="Indexing Schema",
            local_dir=Path("./data/"),
            remote_url="https://fieldday-web.ad.education.wisc.edu/opengamedata/",
            templates_url="https://github.com/opengamedata/opengamedata-samples",
            other_elements={ "foo":"bar" }
        )

    @staticmethod
    def RunAll():
        pass

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Indexing Schema")

    def test_LocalDirectory(self):
        _dir = self.test_schema.LocalDirectory
        self.assertIsInstance(_dir, Path)
        self.assertEqual(_dir, Path("./data/"))

    def test_RemoteURL(self):
        _str = self.test_schema.RemoteURL
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "https://fieldday-web.ad.education.wisc.edu/opengamedata/")

    def test_TemplatesURL(self):
        _str = self.test_schema.TemplatesURL
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "https://github.com/opengamedata/opengamedata-samples")

    def test_NonStandardElements(self):
        _elems = {
            "foo":"bar"
        }
        self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        self.assertEqual(self.test_schema.NonStandardElements, _elems)

    def test_NonStandardElementNames(self):
        _elem_names = ["foo"]
        self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)

    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.
        """
        _dict = {
            "LOCAL_DIR"     : "./data/",
            "REMOTE_URL"    : "https://fieldday-web.ad.education.wisc.edu/opengamedata/",
            "TEMPLATES_URL" : "https://github.com/opengamedata/opengamedata-samples"
        }
        _schema = FileIndexingConfig.FromDict(name="FILE_INDEXING", all_elements=_dict, logger=None)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "FILE_INDEXING")
        self.assertIsInstance(_schema.LocalDirectory, Path)
        self.assertEqual(_schema.LocalDirectory, Path("./data"))
        self.assertIsInstance(_schema.RemoteURL, str)
        self.assertEqual(_schema.RemoteURL, "https://fieldday-web.ad.education.wisc.edu/opengamedata/")
        self.assertIsInstance(_schema.TemplatesURL, str)
        self.assertEqual(_schema.TemplatesURL, "https://github.com/opengamedata/opengamedata-samples")

    @unittest.skip("Not yet implemented")
    def test_parseLocalDir(self):
        pass
        # _name = Schema._parseName("Foo")
        # self.assertIsInstance(_name, str)
        # self.assertEqual(_name, "Foo")

    @unittest.skip("Not yet implemented")
    def test_parseRemoteURL(self):
        pass

    @unittest.skip("Not yet implemented")
    def test_parseTemplatesURL(self):
        pass

if __name__ == '__main__':
    unittest.main()
