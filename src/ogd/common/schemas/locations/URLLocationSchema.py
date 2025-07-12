## import standard libraries
import logging
from urllib.parse import urlparse, urlunparse
from typing import Any, Dict, Optional, Tuple
## import local files
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class TableStructureSchema
class URLLocationSchema(LocationSchema):

    _DEFAULT_HOST_NAME = "DEFAULT HOST"
    _DEFAULT_PORT      = 3306 # default assumption is this is for a MySQL DB
    _DEFAULT_PATH      = "/"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, host_name:str, port:int, path:str, other_elements:Optional[Map]=None):
        unparsed_elements : Map = other_elements or {}

        self._host : str
        self._port : int
        self._path : Optional[str]

        # 1. If we at least have the host, then we're expecting to get host and path as separate pieces
        if host_name:
            self._host = host_name
            self._port = port      or self._parsePort(unparsed_elements=unparsed_elements)
            self._path = path      or self._parsePath(unparsed_elements=unparsed_elements)
        # 2. Otherwise, we try to get as a URL from dict as first try. If it returns something, then we've got it.
        else:
            url = self._parseURL(unparsed_elements=unparsed_elements)
            if url:
                self._host = url[0]
                self._port = url[1]
                self._path = url[2]
        # 3. If there wasn't a URL element, then we move on to just parse host and path from dict directly.
            else:
                self._host = host_name or self._parseHost(unparsed_elements=unparsed_elements)
                self._port = port      or self._parsePort(unparsed_elements=unparsed_elements)
                self._path = path      or self._parsePath(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=unparsed_elements)

    @property
    def Host(self) -> str:
        return self._host

    @property
    def Port(self) -> int:
        return self._port

    @property
    def Path(self) -> Optional[str]:
        return self._path

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        return f"{self.Host}:{self.Port}/{self.Path}"

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.Location}"
        return ret_val

    @classmethod
    def Default(cls) -> "URLLocationSchema":
        return URLLocationSchema(
            name="DefaultURLLocation",
            host_name=cls._DEFAULT_HOST_NAME,
            port=cls._DEFAULT_PORT,
            path=cls._DEFAULT_PATH,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "URLLocationSchema":
        """Create a TableLocationSchema from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_
        :type logger: Optional[logging.Logger]
        :param data_sources: _description_
        :type data_sources: Dict[str, DataStoreConfig]
        :return: _description_
        :rtype: GameSourceSchema
        """
        _host : str
        _port : int
        _path : Optional[str]

        # 1. First, we try to get as a URL from dict as first try. If it returns something, then we've got it.
        url = cls._parseURL(unparsed_elements=unparsed_elements)
        _used = {"url"}
        if url:
            _host = url[0]
            _port = url[1]
            _path = url[2]
        # 2. If there wasn't a URL element, then we move on to just parse host and path from dict directly.
        else:
            _host = cls._parseHost(unparsed_elements=unparsed_elements)
            _port = cls._parsePort(unparsed_elements=unparsed_elements)
            _path = cls._parsePath(unparsed_elements=unparsed_elements)
            _used = _used.union({"host", "path"})

        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return URLLocationSchema(name=name, host_name=_host, port=_port, path=_path, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseURL(unparsed_elements:Map) -> Optional[Tuple[str, int, str]]:
        """Attempt to parse from a straight-up URL element.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: Optional[Tuple[str, str]]
        """
        ret_val : Optional[Tuple[str, int, str]] = None

        raw_url = URLLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["url"],
            to_type=str,
            default_value=None,
            remove_target=True
        )
        if raw_url:
            parsed_url = urlparse(raw_url)
            ret_val = (parsed_url.hostname, parsed_url.hostname, parsed_url.path)

        return ret_val

    @staticmethod
    def _parseHost(unparsed_elements:Map) -> str:
        return URLLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["host"],
            to_type=str,
            default_value=URLLocationSchema._DEFAULT_HOST_NAME,
            remove_target=True
        )

    @staticmethod
    def _parsePort(unparsed_elements:Map) -> int:
        return URLLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["port"],
            to_type=int,
            default_value=URLLocationSchema._DEFAULT_PORT,
            remove_target=True
        )

    @staticmethod
    def _parsePath(unparsed_elements:Map) -> str:
        return URLLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["path"],
            to_type=str,
            default_value=URLLocationSchema._DEFAULT_PATH,
            remove_target=True
        )
