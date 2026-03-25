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

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

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

    # *** Tests for _parseLocalDir ***

    def test_parseLocalDir_str(self):
        unparsed_elements = { "LOCAL_DIR" : "./data/" }
        result = RepositoryIndexingConfig._parseLocalDir(unparsed_elements=unparsed_elements)
        self.assertIsInstance(result, DirectoryLocationSchema)
        self.assertEqual(result.FolderPath, Path("./data"))

    def test_parseLocalDir_path(self):
        unparsed_elements = { "LOCAL_DIR" : Path("./data") }
        result = RepositoryIndexingConfig._parseLocalDir(unparsed_elements=unparsed_elements)
        self.assertIsInstance(result, DirectoryLocationSchema)
        self.assertEqual(result.FolderPath, Path("./data"))

    def test_parseLocalDir_dict(self):
        unparsed_elements = { "LOCAL_DIR" : {"folder":"./data"} }
        result = RepositoryIndexingConfig._parseLocalDir(unparsed_elements=unparsed_elements)
        self.assertIsInstance(result, DirectoryLocationSchema)
        self.assertEqual(result.FolderPath, Path("./data"))

    def test_parseLocalDir_key_filesbase(self):
        unparsed_elements = { "files_base" : "./data/" }
        result = RepositoryIndexingConfig._parseLocalDir(unparsed_elements=unparsed_elements)
        self.assertIsInstance(result, DirectoryLocationSchema)
        self.assertEqual(result.FolderPath, Path("./data"))

    def test_parseLocalDir_key_folder(self):
        unparsed_elements = { "folder" : "./data/" }
        result = RepositoryIndexingConfig._parseLocalDir(unparsed_elements=unparsed_elements)
        self.assertIsInstance(result, DirectoryLocationSchema)
        self.assertEqual(result.FolderPath, Path("./data"))

    def test_parseLocalDir_key_path(self):
        unparsed_elements = { "path" : "./data/" }
        result = RepositoryIndexingConfig._parseLocalDir(unparsed_elements=unparsed_elements)
        self.assertIsInstance(result, DirectoryLocationSchema)
        self.assertEqual(result.FolderPath, Path("./data"))

    def test_parseLocalDir_missing(self):
        unparsed_elements = { "fakekey" : "foo" }
        result = RepositoryIndexingConfig._parseLocalDir(unparsed_elements=unparsed_elements)
        self.assertIsInstance(result, DirectoryLocationSchema)
        self.assertEqual(result, RepositoryIndexingConfig._DEFAULT_LOCAL_DIR)

    def test_parseLocalDir_badtype(self):
        unparsed_elements = { "LOCAL_DIR" : 42 }
        result = RepositoryIndexingConfig._parseLocalDir(unparsed_elements=unparsed_elements)
        self.assertIsInstance(result, DirectoryLocationSchema)
        self.assertEqual(result, RepositoryIndexingConfig._DEFAULT_LOCAL_DIR)

    # *** Tests for _parseRemoteURL ***

    def test_parseRemoteURL_str(self):
        _map = {
            "remote_url":"https://opengamedata.fielddaylab.wisc.edu/",
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseRemoteURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, "https://opengamedata.fielddaylab.wisc.edu/")
        self.assertNotIn("remote_url", _map)

    def test_parseRemoteURL_urldict(self):
        _map = {
            "remote_url":{"url":"https://opengamedata.fielddaylab.wisc.edu/"},
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseRemoteURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, "https://opengamedata.fielddaylab.wisc.edu/")
        self.assertNotIn("remote_url", _map)

    def test_parseRemoteURL_spliturldict(self):
        _map = {
            "remote_url" : {
                "scheme" : "https",
                "host" : "opengamedata.fielddaylab.wisc.edu",
                "port" : 443
            },
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseRemoteURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, "https://opengamedata.fielddaylab.wisc.edu:443/")
        self.assertNotIn("remote_url", _map)

    def test_parseRemoteURL_key_url(self):
        """Test parsing URL from the secondary key option, i.e. "url"
        """
        _map = {
            "url":"https://opengamedata.fielddaylab.wisc.edu/",
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseRemoteURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, "https://opengamedata.fielddaylab.wisc.edu/")
        self.assertNotIn("url", _map)

    def test_parseRemoteURL_missing(self):
        """Test that we get default remote URL when it's missing from the dict
        """
        _map = {
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseRemoteURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, RepositoryIndexingConfig._DEFAULT_REMOTE_URL)

    # *** Tests for _parseTemplatesURL ***

    def test_parseTemplatesURL(self):
        _map = {
            "templates_url":"https://opengamedata.fielddaylab.wisc.edu/",
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseTemplatesURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, "https://opengamedata.fielddaylab.wisc.edu/")
        self.assertNotIn("templates_url", _map)

    def test_parseTemplatesURL_urldict(self):
        _map = {
            "templates_url":{"url":"https://opengamedata.fielddaylab.wisc.edu/"},
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseTemplatesURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, "https://opengamedata.fielddaylab.wisc.edu/")
        self.assertNotIn("templates_url", _map)

    def test_parseTemplatesURL_spliturldict(self):
        _map = {
            "templates_url" : {
                "scheme" : "https",
                "host" : "opengamedata.fielddaylab.wisc.edu",
                "port" : 443
            },
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseTemplatesURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, "https://opengamedata.fielddaylab.wisc.edu:443/")
        self.assertNotIn("templates_url", _map)

    def test_parseTemplatesURL_key_tempbase(self):
        """Test parsing URL from the secondary key option, i.e. "templates_base"
        """
        _map = {
            "templates_base":"https://opengamedata.fielddaylab.wisc.edu/",
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseTemplatesURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, "https://opengamedata.fielddaylab.wisc.edu/")
        self.assertNotIn("templates_base", _map)

    def test_parseTemplatesURL_key_url(self):
        """Test parsing URL from the secondary key option, i.e. "url"
        """
        _map = {
            "url":"https://opengamedata.fielddaylab.wisc.edu/",
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseTemplatesURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, "https://opengamedata.fielddaylab.wisc.edu/")
        self.assertNotIn("url", _map)

    def test_parseTemplatesURL_missing(self):
        """Test that we get default templates URL when missing from dict.
        """
        _map = {
            "fakekey" : "Bar"
        }
        url = RepositoryIndexingConfig._parseTemplatesURL(unparsed_elements=_map)
        self.assertIsInstance(url, URLLocationSchema)
        self.assertEqual(url, RepositoryIndexingConfig._DEFAULT_TEMPLATE_URL)
        self.assertNotIn("url", _map)
