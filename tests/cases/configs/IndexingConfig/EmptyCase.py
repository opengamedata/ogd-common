# import libraries
import logging
import unittest
from pathlib import Path
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
from ogd.common.schemas.locations.DirectoryLocationSchema import DirectoryLocationSchema
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
# import locals
from src.ogd.common.configs.storage.RepositoryIndexingConfig import RepositoryIndexingConfig
from tests.config.t_config import settings

class EmptyCase(TestCase):
    """RepositoryIndexingConfig test case where no initialization is used at class level.

    Fixture:
    * No initialization of a RepositoryIndexingConfig object

    Case Categories:
    * Loading functions.
        * Appropriate here since the fixture doesn't set up an object.
    * Parsing functions. 
        * We test these so as to get details of where loading fails.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.
        """
        _dict = {
            "LOCAL_DIR"     : "./data/",
            "REMOTE_URL"    : "https://fieldday-web.ad.education.wisc.edu/opengamedata/",
            "TEMPLATES_URL" : "https://github.com/opengamedata/opengamedata-samples"
        }
        _schema = RepositoryIndexingConfig.FromDict(name="FILE_INDEXING", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "FILE_INDEXING")
        self.assertIsInstance(_schema.LocalDirectory, DirectoryLocationSchema)
        self.assertEqual(_schema.LocalDirectory.FolderPath, Path("./data"))
        self.assertIsInstance(_schema.RemoteURL, URLLocationSchema)
        if _schema.RemoteURL:
            self.assertEqual(_schema.RemoteURL.Location, "https://fieldday-web.ad.education.wisc.edu/opengamedata/")
        self.assertIsInstance(_schema.TemplatesURL, URLLocationSchema)
        self.assertEqual(_schema.TemplatesURL.Location, "https://github.com/opengamedata/opengamedata-samples")

    def test_parseLocalDir(self):
        unparsed_elements = { "LOCAL_DIR" : "./data/" }
        result = RepositoryIndexingConfig._parseLocalDir(unparsed_elements=unparsed_elements)
        self.assertIsInstance(result, DirectoryLocationSchema)
        self.assertEqual(result.FolderPath, Path("./data"))

    @unittest.skip("Not yet implemented")
    def test_parseRemoteURL(self):
        pass

    @unittest.skip("Not yet implemented")
    def test_parseTemplatesURL(self):
        pass
