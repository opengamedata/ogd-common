import logging
import os
import traceback
import unittest
from pathlib import Path
from unittest import TestCase
# local import(s)
from ogd.common.utils import fileio

@unittest.skip("Not implemented")
class FileAPICase(TestCase):
    """FileAPI test case where no initialization is used, since it's basically all just static functions.

    *Really* stretching the definition of what is considered a proper fixture/test case,
    but willing to make an exception for a utility module with just static members.

    Fixture:
    * No initialization of FileAPI

    Case Categories:
    * Loading functions.
        * Really all there is to this class.
    """