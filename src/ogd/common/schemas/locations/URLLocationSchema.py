## import standard libraries
from urllib.parse import urlparse, ParseResult
from typing import Dict, List, Optional, Self
## import local files
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.typing import Map

## @class TableStructureSchema
class URLLocationSchema(LocationSchema):

    _DEFAULT_SCHEME    = "http"
    _DEFAULT_HOST_NAME = "DEFAULTHOST"
    _DEFAULT_PORT      = None
    _DEFAULT_PATH      = "/"
    _DEFAULT_URL = ParseResult(
        scheme=_DEFAULT_SCHEME,
        netloc=_DEFAULT_HOST_NAME,
        path=_DEFAULT_PATH,
        params="",
        query="",
        fragment=""
    )

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, url:ParseResult, other_elements:Optional[Map]=None):
        """Constructor for the `URLLocationSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "url" : "http://subdomain.host.com/url/path"
        },
        ```

        :param name: _description_
        :type name: str
        :param url: _description_
        :type url: ParseResult
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._url = url or self._parseURL(unparsed_elements=unparsed_elements) or self._parseSplitURL(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=unparsed_elements)

    @property
    def Scheme(self) -> str:
        return self._url.scheme or self._DEFAULT_SCHEME

    @property
    def Host(self) -> str:
        return self._url.hostname or self._DEFAULT_HOST_NAME

    @property
    def Port(self) -> Optional[int]:
        return self._url.port

    @property
    def Path(self) -> Optional[str]:
        return self._url.path

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        _port = f":{self.Port}" if self.Port else ""
        return f"{self.Host}{_port}/{self.Path}"

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.Location}"
        return ret_val

    @classmethod
    def Default(cls) -> "URLLocationSchema":
        return URLLocationSchema(
            name="DefaultURLLocation",
            url=cls._DEFAULT_URL,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "URLLocationSchema":
        """Create a URLLocationSchema from a given dictionary

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
        # 1. First, we try to get as a URL from dict as first try. If it returns something, then we've got it.
        url = cls._parseURL(unparsed_elements=unparsed_elements, key_overrides=key_overrides)
        _used = {"url"}
        if not url:
            url = cls._parseSplitURL(unparsed_elements=unparsed_elements, key_overrides=key_overrides)
            _used = _used.union({"host", "port", "path"})

        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return URLLocationSchema(name=name, url=url, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseURL(unparsed_elements:Map,
                  key_overrides:Optional[Dict[str, str]]=None) -> Optional[ParseResult]:
        """Attempt to parse from a straight-up URL element.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: Optional[Tuple[str, str]]
        """
        ret_val : Optional[ParseResult] = None

        default_keys : List[str] = ["url"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys

        raw_url = URLLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=None, # default to None, if it doesn't exist we return None
            remove_target=True
        )
        ret_val = urlparse(raw_url) if raw_url else None

        return ret_val

    @staticmethod
    def _parseSplitURL(unparsed_elements:Map,
                       key_overrides:Optional[Dict[str, str]]=None,
                       default_override:Optional["URLLocationSchema"]=None) -> ParseResult:
        default_keys : List[str]
        search_keys  : List[str]

        default_keys = ["scheme"]
        search_keys = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        default_scheme : str = default_override.Scheme if default_override else URLLocationSchema._DEFAULT_SCHEME
        _scheme = URLLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=default_scheme,
            remove_target=True
        )

        default_keys = ["host"]
        search_keys = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        default_host : str = default_override.Host if default_override else URLLocationSchema._DEFAULT_HOST_NAME
        _host = URLLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=default_host,
            remove_target=True
        )
        default_keys = ["port"]
        search_keys  = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        default_port : Optional[str] = default_override.Port if default_override else URLLocationSchema._DEFAULT_PORT
        _port = URLLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=int,
            default_value=default_port,
            remove_target=True
        )
        _port_str = f":{_port}" if _port else ""
        default_keys = ["path"]
        search_keys  = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        default_path : Optional[str] = default_override.Path if default_override else URLLocationSchema._DEFAULT_PATH
        _path = URLLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=default_path,
            remove_target=True
        )

        return ParseResult(scheme=_scheme, netloc=f"{_host}{_port_str}", path=_path, params="", query="", fragment="")
