from ogd.common.models.enums.FilterMode import FilterMode
class Filter:
    def __init__(self, mode:FilterMode):
        self._mode = mode
    
    @property
    def FilterMode(self) -> FilterMode:
        return self._mode