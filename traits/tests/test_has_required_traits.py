import unittest
from traits.api import Int, Float, String, HasRequiredTraits, TraitError

class TestHasRequiredTraits(unittest.TestCase):

    def test_trait_value_assignment(self):
        test_instance = RequiredTest(i_trait=4, f_trait=2.2, s_trait="test")
        self.assertEqual(test_instance.i_trait, 4)
        self.assertEqual(test_instance.f_trait, 2.2)
        self.assertEqual(test_instance.s_trait, "test")
        self.assertEqual(test_instance.non_req_trait, 4.4)


    def test_missing_required_trait(self):
        with self.assertRaises(TraitError) as exc:
            test_instance = RequiredTest(i_trait=3)
        self.assertEqual(
            exc.exception.args[0], "The following required traits were not "
            "passed as a keyword argument: f_trait, s_trait."
        )

    def test_overwrite_required(self):
        test_instance = RequiredTest(
            i_trait=6, f_trait=3.3, s_trait="hi"
        )
        self.assertEqual(test_instance.i_trait, 6)
        self.assertEqual(test_instance.f_trait, 3.3)
        self.assertEqual(test_instance.s_trait, "hi")
        self.assertEqual(test_instance.non_req_trait, 4.4)
        test_instance.i_trait = 7
        self.assertEqual(test_instance.i_trait, 7)


class RequiredTest(HasRequiredTraits):
    i_trait = Int(required=True)
    f_trait = Float(required=True)
    s_trait = String(required=True)
    non_req_trait = Float(4.4, required=False)
