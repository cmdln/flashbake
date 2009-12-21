#!/usr/bin/env python

'''  test -  test runner script '''

#    copyright 2009 Thomas Gideon
#
#    This file is part of flashbake.
#
#    flashbake is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    flashbake is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with flashbake.  If not, see <http://www.gnu.org/licenses/>.

import sys
from os.path import join, realpath, abspath
import unittest
import logging



# just provide the command line hook into the tests
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
            format='%(message)s')

    LAUNCH_DIR = abspath(sys.path[0])
    flashbake_dir = join(LAUNCH_DIR, "..")

    sys.path.insert(0, realpath(flashbake_dir))
    try:
        from flashbake.commit import commit #@UnusedImport
        from flashbake.control import parse_control #@UnusedImport
        from flashbake.context import buildmessagefile #@UnusedImport
        import test.config
        import test.files
    finally:
        del sys.path[0]

    # combine classes into single suite
    config_suite = unittest.TestLoader().loadTestsFromTestCase(test.config.ConfigTestCase)
    files_suite = unittest.TestLoader().loadTestsFromTestCase(test.files.FilesTestCase)
    suite = unittest.TestSuite([config_suite, files_suite])
    unittest.TextTestRunner(verbosity=2).run(suite)
