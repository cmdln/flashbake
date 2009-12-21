import commands
import flashbake
import os.path
import unittest

class FilesTestCase(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.join(os.getcwd(), 'test')
        test_zip = os.path.join(test_dir, 'project.zip')
        commands.getoutput('unzip -d %s %s' % (test_dir, test_zip))
        self.files = flashbake.HotFiles(os.path.join(test_dir, 'project'))
        self.project_files = [ 'todo.txt', 'stickies.txt', 'my stuff.txt',
        'bar/novel.txt', 'baz/novel.txt', 'quux/novel.txt' ]

    def tearDown(self):
        commands.getoutput('rm -rf %s' % self.files.project_dir)

    def testrelative(self):
        for file in self.project_files:
            self.files.addfile(file)
            self.assertTrue(file in self.files.control_files,
                    'Should contain relative file, %s' % file)
        count = len(self.files.control_files)
        self.files.addfile('*add*')
        self.assertEquals(len(self.files.control_files), count + 3,
                'Should have expanded glob.')

    def testabsolute(self):
        for file in self.project_files:
            abs_file = os.path.join(self.files.project_dir, file)
            self.files.addfile(abs_file)
            self.assertTrue(file in self.files.control_files,
                    'Should contain absolute file, %s, as relative path, %s.'
                    % (abs_file, file))
        count = len(self.files.control_files)
        self.files.addfile(os.path.join(self.files.project_dir, '*add*'))
        self.assertEquals(len(self.files.control_files), count + 3,
                'Should have expanded glob.')

    def testabsent(self):
        self.files.addfile('does not exist.txt')
        self.files.addfile('doesn\'t exist.txt')
        self.files.addfile('does{not}exist.txt')
        self.assertEquals(len(self.files.not_exists), 3,
                'None of the provided files should exist')

    def testoutside(self):
        self.files.addfile('/tmp')
        self.assertEquals(len(self.files.outside_files), 1,
                'Outside files should get caught')

    def testlinks(self):
        self.files.addfile('link/novel.txt')
        self.assertEquals(len(self.files.linked_files.keys()), 1,
                'Linked files should get caught')
