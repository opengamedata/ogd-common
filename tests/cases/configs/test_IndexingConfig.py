# import libraries
import logging
import unittest
from pathlib import Path
from unittest import TestCase
from urllib.parse import urlparse
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
from ogd.common.schemas.locations.DirectoryLocationSchema import DirectoryLocationSchema
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
# import locals
from src.ogd.common.configs.IndexingConfig import FileIndexingConfig
from tests.config.t_config import settings

class test_IndexingConfig(TestCase):
    """Testbed for the GameSourceSchema class.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        cls.test_schema = FileIndexingConfig(
            name="Indexing Schema",
            local_dir=DirectoryLocationSchema(name="LocalDir", folder_path=Path("./data")),
            remote_url=URLLocationSchema(name="RemoteURL", url=urlparse("https://fieldday-web.ad.education.wisc.edu/opengamedata/")),
            templates_url=URLLocationSchema(name="TemplateURL", url=urlparse("https://github.com/opengamedata/opengamedata-samples")),
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
        self.assertIsInstance(_dir, DirectoryLocationSchema)
        self.assertIsInstance(_dir.FolderPath, Path)
        self.assertEqual(_dir.FolderPath, Path("./data/"))

    def test_RemoteURL(self):
        _url = self.test_schema.RemoteURL
        self.assertIsInstance(_url, URLLocationSchema)
        self.assertIsInstance(_url.Location, str)
        self.assertEqual(_url.Location, "https://fieldday-web.ad.education.wisc.edu/opengamedata/")

    def test_TemplatesURL(self):
        _url = self.test_schema.TemplatesURL
        self.assertIsInstance(_url, URLLocationSchema)
        self.assertIsInstance(_url.Location, str)
        self.assertEqual(_url.Location, "https://github.com/opengamedata/opengamedata-samples")

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
        _schema = FileIndexingConfig.FromDict(name="FILE_INDEXING", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "FILE_INDEXING")
        self.assertIsInstance(_schema.LocalDirectory, DirectoryLocationSchema)
        self.assertEqual(_schema.LocalDirectory.FolderPath, Path("./data"))
        self.assertIsInstance(_schema.RemoteURL, URLLocationSchema)
        self.assertEqual(_schema.RemoteURL.Location, "https://fieldday-web.ad.education.wisc.edu/opengamedata/")
        self.assertIsInstance(_schema.TemplatesURL, URLLocationSchema)
        self.assertEqual(_schema.TemplatesURL.Location, "https://github.com/opengamedata/opengamedata-samples")

    def test_parseLocalDir(self):
        unparsed_elements = { "LOCAL_DIR" : "./data/" }
        result = FileIndexingConfig._parseLocalDir(unparsed_elements=unparsed_elements)
        self.assertIsInstance(result, DirectoryLocationSchema)
        self.assertEqual(result.FolderPath, Path("./data"))

    @unittest.skip("Not yet implemented")
    def test_parseRemoteURL(self):
        pass

    @unittest.skip("Not yet implemented")
    def test_parseTemplatesURL(self):
        pass

if __name__ == '__main__':
    unittest.main()
