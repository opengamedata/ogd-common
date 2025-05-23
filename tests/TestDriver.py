# Standard imports
from unittest import defaultTestLoader, TestLoader, TestSuite, runner

# Set up path
import os, sys
from pprint import pprint
from pathlib import Path

sys.path.insert(0, str(Path(os.getcwd()) / "src"))
# Set up logging
import logging
from ogd.common.utils.Logger import Logger
Logger.InitializeLogger(level=logging.INFO, use_logfile=False)
from ogd.common.configs.TestConfig import TestConfig

from config.t_config import settings

_config = TestConfig.FromDict(name="APIUtilsTestConfig", unparsed_elements=settings)

# loader = TestLoader()
# TODO : At the moment, this is just module-level, should eventually go to class-level selection.
suite = TestSuite()
if _config.EnabledTests.get('CONFIGS'):
    print("***\nAdding configs:")
    suite.addTest(defaultTestLoader.discover('./tests/cases/configs/', pattern="test_*.py", top_level_dir="./"))
    print("Done\n***")
if _config.EnabledTests.get('INTERFACES'):
    print("***\nAdding interfaces:")
    suite.addTest(defaultTestLoader.discover('./tests/cases/interfaces/', pattern="test_*.py", top_level_dir="./"))
    print("Done\n***")
if _config.EnabledTests.get('SCHEMAS'):
    print("***\nAdding schemas:")
    suite.addTest(defaultTestLoader.discover('./tests/cases/schemas/', pattern="test_*.py", top_level_dir="./"))
    print("Done\n***")
if _config.EnabledTests.get('UTILS'):
    print("***\nAdding Utils:")
    suite.addTest(defaultTestLoader.discover('./tests/cases/utils/', pattern="test_*.py", top_level_dir="./"))
    print("Done\n***")

print(f"Tests are:")
for ts in suite._tests:
    if isinstance(ts, TestSuite):
        pprint([t._tests if isinstance(t, TestSuite) else t for t in ts])

testRunner = runner.TextTestRunner()
testRunner.run(suite)