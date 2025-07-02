# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.events.DataElementSchema import DataElementSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class GameStateSchema(Schema):
    """
    Dumb struct to contain a specification of a game's GameState in a EventCollectionSchema file.

    These essentially are just a set of elements in the GameState attribute of the game's Events.
    """

    _DEFAULT_GAME_STATE = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_state:Dict[str, DataElementSchema], other_elements:Optional[Map]=None):
        unparsed_elements = other_elements or {}

        self._game_state  : Dict[str, DataElementSchema] = game_state or self._parseGameStateElements(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def GameStateElements(self) -> Dict[str, DataElementSchema]:
        return self._game_state

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    @property
    def AsMarkdown(self) -> str:
        return "\n\n".join([
            f"### **{self.Name}**",
            "\n".join(
                  [elem.AsMarkdown for elem in self.GameStateElements.values()]
                + (["- Other Elements:"] +
                   [f"  - **{elem_name}**: {elem_desc}" for elem_name,elem_desc in self.NonStandardElements]
                  ) if len(self.NonStandardElements) > 0 else []
            )
        ])

    @property
    def AsMarkdownTable(self) -> str:
        ret_val = [
            f"### **{self.Name}**",
            "#### Event Data",
            "\n".join(
                ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                 "| ---      | ---      | ---             | ---              |"]
              + [elem.AsMarkdownRow for elem in self.GameStateElements.values()]
            ),
        ]
        if len(self.NonStandardElements) > 0:
            ret_val.append("#### Other Elements")
            ret_val.append(
                "\n".join( [f"- **{elem_name}**: {elem_desc}  " for elem_name,elem_desc in self.NonStandardElements] )
            )
        return "\n\n".join(ret_val)

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "GameStateSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: GameStateSchema
        """
        _game_state  : Dict[str, DataElementSchema]

        if not isinstance(unparsed_elements, dict):
            unparsed_elements   = {}
            Logger.Log(f"For {name} Event config, unparsed_elements was not a dict, defaulting to empty dict", logging.WARN)
        _game_state = cls._parseGameStateElements(unparsed_elements=unparsed_elements)

        _leftovers = {}
        return GameStateSchema(name=name, game_state=_game_state, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "GameStateSchema":
        return GameStateSchema(
            name="DefaultGameStateSchema",
            game_state=cls._DEFAULT_GAME_STATE,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseGameStateElements(unparsed_elements:Map):
        ret_val : Dict[str, DataElementSchema]
        if isinstance(unparsed_elements, dict):
            ret_val = {
                name : DataElementSchema.FromDict(name=name, unparsed_elements=elems)
                for name,elems in unparsed_elements.items()
            }
        else:
            ret_val = {}
            Logger.Log(f"unparsed_elements was unexpected type {type(unparsed_elements)}, defaulting to {ret_val}.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
