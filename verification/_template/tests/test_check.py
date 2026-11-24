import unittest
from cad_verification import VerificationFailure
from example_check import verify_body_count

class CheckTests(unittest.TestCase):
    def test_matching_measurement(self):
        evidence = verify_body_count(expected=2, actual=2)
        self.assertTrue(evidence["pass"])

    def test_mismatch_fails(self):
        with self.assertRaises(VerificationFailure):
            verify_body_count(expected=2, actual=1)
