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
class MajorVersionOnlyCase(TestCase):
    """SemanticVersion test case when the instance is given a version with only a major version
    
    Fixture:
    * Initialize a SemanticVersion object with the major-only version string "2"
    
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
        cls.instance = SemanticVersion.FromString("2")

    # *** Test == operator ***

    def test_eqSameVersion(self):
        other = SemanticVersion.FromString("2")
        self.assertTrue(self.instance == other)
    def test_eqSameMajorPointZero(self):
        other = SemanticVersion.FromString("2.0")
        self.assertTrue(self.instance == other)
    def test_eqOtherVersion(self):
        other = SemanticVersion.FromString("1")
        self.assertFalse(self.instance == other)
    def test_eqSameMajorPointOne(self):
        other = SemanticVersion.FromString("2.1")
        self.assertFalse(self.instance == other)

    # *** Test > operator ***

    def test_gtInvalid(self):
        other = SemanticVersion.FromString("Invalid")
        self.assertTrue(self.instance > other)
    def test_gtSameVersion(self):
        other = SemanticVersion.FromString("2")
        self.assertFalse(self.instance > other)
    def test_gtSameMajorPointZero(self):
        other = SemanticVersion.FromString("2.0")
        self.assertFalse(self.instance > other)
    def test_gtSmallerMajor(self):
        other = SemanticVersion.FromString("1")
        self.assertTrue(self.instance > other)
    def test_gtSmallerMajorLargerMinor(self):
        other = SemanticVersion.FromString("1.3")
        self.assertTrue(self.instance > other)
    def test_gtLargerMajor(self):
        other = SemanticVersion.FromString("3")
        self.assertFalse(self.instance > other)
    def test_gtLargerMajorSmallerMinor(self):
        other = SemanticVersion.FromString("3.1")
        self.assertFalse(self.instance > other)

    # *** Test >= operator ***

    def test_geInvalid(self):
        other = SemanticVersion.FromString("Invalid")
        self.assertTrue(self.instance >= other)
    def test_geSameVersion(self):
        other = SemanticVersion.FromString("2")
        self.assertTrue(self.instance >= other)
    def test_geSameMajorPointZero(self):
        other = SemanticVersion.FromString("2.0")
        self.assertTrue(self.instance >= other)
    def test_geSmallerMajor(self):
        other = SemanticVersion.FromString("1")
        self.assertTrue(self.instance >= other)
    def test_geSmallerMajorLargerMinor(self):
        other = SemanticVersion.FromString("1.3")
        self.assertTrue(self.instance >= other)
    def test_geLargerMajor(self):
        other = SemanticVersion.FromString("3")
        self.assertFalse(self.instance >= other)
    def test_geLargerMajorSmallerMinor(self):
        other = SemanticVersion.FromString("3.1")
        self.assertFalse(self.instance >= other)

    # *** Test < operator ***

    def test_ltInvalid(self):
        other = SemanticVersion.FromString("Invalid")
        self.assertFalse(self.instance < other)
    def test_ltSameVersion(self):
        other = SemanticVersion.FromString("2")
        self.assertFalse(self.instance < other)
    def test_ltSameMajorPointZero(self):
        other = SemanticVersion.FromString("2.0")
        self.assertFalse(self.instance < other)
    def test_ltSmallerMajor(self):
        other = SemanticVersion.FromString("1")
        self.assertFalse(self.instance < other)
    def test_ltSmallerMajorLargerMinor(self):
        other = SemanticVersion.FromString("1.3")
        self.assertFalse(self.instance < other)
    def test_ltLargerMajor(self):
        other = SemanticVersion.FromString("3")
        self.assertTrue(self.instance < other)
    def test_ltLargerMajorSmallerMinor(self):
        other = SemanticVersion.FromString("3.1")
        self.assertTrue(self.instance < other)

    # *** Test >= operator ***

    def test_leInvalid(self):
        other = SemanticVersion.FromString("Invalid")
        self.assertFalse(self.instance <= other)
    def test_leSameVersion(self):
        other = SemanticVersion.FromString("2")
        self.assertTrue(self.instance <= other)
    def test_leSameMajorPointZero(self):
        other = SemanticVersion.FromString("2.0")
        self.assertTrue(self.instance <= other)
    def test_leSmallerMajor(self):
        other = SemanticVersion.FromString("1")
        self.assertFalse(self.instance <= other)
    def test_leSmallerMajorLargerMinor(self):
        other = SemanticVersion.FromString("1.3")
        self.assertFalse(self.instance <= other)
    def test_leLargerMajor(self):
        other = SemanticVersion.FromString("3")
        self.assertTrue(self.instance <= other)
    def test_leLargerMajorSmallerMinor(self):
        other = SemanticVersion.FromString("3.1")
        self.assertTrue(self.instance <= other)
