import importlib.util
import unittest
from unittest.mock import patch

from cad_library_verification import verify_body_count


class CheckBoundaryTests(unittest.TestCase):
    @patch("cad_library_verification._require_equal")
    def test_explicit_expectation_is_delegated(self, require_equal):
        require_equal.return_value = {"pass": True}
        self.assertEqual(verify_body_count(expected=2, actual=2), {"pass": True})
        require_equal.assert_called_once_with(2, 2, label="body count")


@unittest.skipUnless(importlib.util.find_spec("cad_verification"), "external CAD verification dependency not installed")
class ExternalVerificationTests(unittest.TestCase):
    def test_matching_measurement(self):
        self.assertTrue(verify_body_count(expected=2, actual=2)["pass"])

    def test_mismatch_fails(self):
        from cad_verification import VerificationFailure

        with self.assertRaises(VerificationFailure):
            verify_body_count(expected=2, actual=1)
