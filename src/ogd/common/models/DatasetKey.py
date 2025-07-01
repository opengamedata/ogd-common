# standard imports
import logging

# ogd imports
from ogd.common.utils.Logger import Logger

class DatasetKey:
    """
    DatasetKey dumb struct.

    TODO : Rework this to be more like other schemas.
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_KEY = "UNKNOWN"
    _DEFAULT_GAME_ID = "UNKOWN_GAME"

    """Simple little class to make logic with dataset keys easier
    """
    def __init__(self, key:str, game_id:str):
    # 1. Get Game ID from key
        if key[:len(game_id)] != game_id:
            Logger.Log(f"Got a mismatch between expected game ID and ID in the dataset key: {key[:len(game_id)]} != {game_id}. Defaulting to {game_id}", logging.WARNING)
        self._game_id = game_id
    # 2. Get Dates from key
        _date_range = key[len(game_id):]
        _date_range_parts = _date_range.split("_")
        # If this _dataset_key matches the expected format,
        # i.e. spit is: ["", "YYYYMMDD", "to", "YYYYMMDD"]
        self._from_year  = int(_date_range_parts[-3][0:4]) if len(_date_range_parts[-3]) == 8 else None
        self._from_month = int(_date_range_parts[-3][4:6]) if len(_date_range_parts[-3]) == 8 else None
        self._to_year    = int(_date_range_parts[-1][0:4]) if len(_date_range_parts[-1]) == 8 else None
        self._to_month   = int(_date_range_parts[-1][4:6]) if len(_date_range_parts[-1]) == 8 else None
        self._original_key = key

    def __str__(self):
        return self._original_key
    
    @property
    def IsValid(self) -> bool:
        return  self._from_year  is not None \
            and self._from_month is not None \
            and self._to_year    is not None \
            and self._to_month   is not None
    @property
    def GameID(self) -> str:
        return self._game_id
    @property
    def FromYear(self) -> int:
        return self._from_year or -1
    @property
    def FromMonth(self) -> int:
        return self._from_month or -1
    @property
    def ToYear(self) -> int:
        return self._to_year or -1
    @property
    def ToMonth(self) -> int:
        return self._to_month or -1

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetKey":
        return DatasetKey(
            key=cls._DEFAULT_KEY,
            game_id=cls._DEFAULT_GAME_ID
        )


    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
