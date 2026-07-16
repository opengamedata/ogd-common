# import libraries
import logging
import unittest
from pathlib import Path
from unittest import TestCase
from urllib.parse import urlparse
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.configs.locations.URLLocationConfig import URLLocationConfig
# import locals
from src.ogd.common.configs.storage.RepositoryLocationConfig import RepositoryLocationConfig
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class BasicInitCase(TestCase):
    """RepositoryLocationConfig test case where basic initialization is used.
    
    Fixture:
    * Initialize a RepositoryLocationConfig object with hardcoded values for all `__init__(...)` params
    
    Case Categories:
    * Property functions.
        * Appropriate for this case, since we are hardcoding initial values and can then test we get them back directly.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common attributes across the class.

        Since this class currently just tests properties, we go ahead and use a single instance of `RepositoryLocationConfig` shared across the class.
        If any tests are added that have expected side effects, initialization of the instance should be moved to a `setUp(self)` function.
        """
        cls.test_schema = RepositoryLocationConfig(
            name="Indexing Schema",
            local_dir=DirectoryLocationConfig(name="LocalDir", folder_path=Path("./data")),
            public_url=URLLocationConfig(name="RemoteURL", url=urlparse("https://fieldday-web.ad.education.wisc.edu/opengamedata/")),
            templates_url=URLLocationConfig(name="TemplateURL", url=urlparse("https://github.com/opengamedata/opengamedata-samples")),
            other_elements={ "foo":"bar" }
        )

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Indexing Schema")

    def test_LocalDirectory(self):
        _dir = self.test_schema.LocalDirectory
        self.assertIsInstance(_dir, DirectoryLocationConfig)
        if _dir is not None:
            self.assertIsInstance(_dir.FolderPath, Path)
            self.assertEqual(_dir.FolderPath, Path("./data/"))

    def test_RemoteURL(self):
        _url = self.test_schema.PublicURL
        self.assertIsNotNone(_url)
        self.assertIsInstance(_url, URLLocationConfig)
        if _url:
            self.assertIsInstance(_url.Location, str)
            self.assertEqual(_url.Location, "https://fieldday-web.ad.education.wisc.edu/opengamedata/")

    def test_TemplatesURL(self):
        _url = self.test_schema.TemplatesURL
        self.assertIsInstance(_url, URLLocationConfig)
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
