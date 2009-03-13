import unittest
import os.path
import flashbake
import logging

class FilesTestCase(unittest.TestCase):
    def setUp(self):
        # TODO add captive zip. fixture
        self.files = flashbake.HotFiles('../foo')
        # TODO add tear down

    def testcorrect(self):
        self.files.addfile('todo.txt')
        self.assertTrue('todo.txt' in self.files.control_files, 'Should contain relative file')
        self.files.addfile(os.path.join(self.files.project_dir, 'bar/novel.txt'))
        self.assertTrue('bar/novel.txt' in self.files.control_files, 'Should contain absolute file')


    def testabsent(self):
        pass

    def testoutside(self):
        pass
