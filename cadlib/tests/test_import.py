import unittest

class LibraryImportTests(unittest.TestCase):
    def test_package_imports(self):
        import cadlib
        self.assertIsNotNone(cadlib)
