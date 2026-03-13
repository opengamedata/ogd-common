# import libraries
import logging
import os, sys
from pathlib import Path
from typing import Final, List
from unittest import TestCase, main
# import locals
_path = Path(os.getcwd()) / "src"
sys.path.insert(0, str(_path.absolute()))
from ogd.common.models.SemanticVersion import SemanticVersion

def setUpModule():
    from ogd.common.utils.Logger import Logger
    Logger.InitializeLogger(level=logging.ERROR, use_logfile=False)

# TODO : need to test cases where we're comparing directly to a string, and directly to an int.
# TODO : need to test cases where one semver has more points than the other, e.g. 1.1 vs 1.1.1
class InvalidVersionCase(TestCase):
    """SemanticVersion test case when the instance is given an invalid version
    
    Fixture:
    * Initialize a SemanticVersion object with the invalid version string "Invalid"
    
    Case Categories:
    * Comparison functions
        * Check for appropriate behavior when comparing invalid version to other versions.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common attributes across the class.

        Since this class currently just tests comparisons, we go ahead and use a single instance of `SemanticVersion` shared across the class.
        If any tests are added that have expected side effects, initialization of the instance should be moved to a `setUp(self)` function.
        """
        cls.instance = SemanticVersion.FromString("Invalid")

    # *** Test == operator ***

    def test_eqSameInvalid(self):
        other = SemanticVersion.FromString("Invalid")
        self.assertTrue(self.instance == other)
    def test_eqUnequalInvalid(self):
        other = SemanticVersion.FromString("Not Valid")
        self.assertFalse(self.instance == other)
    def test_eqValid(self):
        other = SemanticVersion.FromString("1.2.3")
        self.assertFalse(self.instance == other)

    # *** Test > operator ***

    def test_gtSameInvalid(self):
        other = SemanticVersion.FromString("Invalid")
        self.assertFalse(self.instance > other)
    def test_gtUnequalInvalid(self):
        other = SemanticVersion.FromString("Not Valid")
        self.assertFalse(self.instance > other)
    def test_gtValid(self):
        other = SemanticVersion.FromString("1.2.3")
        self.assertFalse(self.instance > other)

    # *** Test >= operator ***

    def test_geSameInvalids(self):
        other = SemanticVersion.FromString("Invalid")
        self.assertTrue(self.instance >= other)
    def test_geOtherInvalid(self):
        other = SemanticVersion.FromString("Not Valid")
        self.assertFalse(self.instance >= other)
    def test_geValid(self):
        other = SemanticVersion.FromString("1.2.3")
        self.assertFalse(self.instance >= other)

    # *** Test < operator ***

    def test_ltSameInvalids(self):
        other = SemanticVersion.FromString("Invalid")
        self.assertTrue(self.instance < other)
    def test_ltOtherInvalid(self):
        other = SemanticVersion.FromString("Not Valid")
        self.assertTrue(self.instance < other)
    def test_ltValid(self):
        other = SemanticVersion.FromString("1.2.3")
        self.assertTrue(self.instance < other)

    # *** Test <= operator ***

    def test_leSameInvalids(self):
        other = SemanticVersion.FromString("Invalid")
        self.assertTrue(self.instance <= other)
    def test_leOtherInvalid(self):
        other = SemanticVersion.FromString("Not Valid")
        self.assertTrue(self.instance <= other)
    def test_leValid(self):
        other = SemanticVersion.FromString("1.2.3")
        self.assertTrue(self.instance <= other)
