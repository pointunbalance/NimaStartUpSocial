import unittest
from utils.strings import get_string

class TestStringsLogic(unittest.TestCase):
    def test_get_valid_key(self):
        # Basic check for common keys
        app_name = get_string("app_name")
        self.assertIsNotNone(app_name)
        self.assertEqual(app_name, "NimaStartupSocial")

    def test_get_missing_key(self):
        # Should return key itself if missing
        missing = get_string("non_existent_key_123")
        self.assertEqual(missing, "non_existent_key_123")

    def test_category_strings(self):
        # cat_social is a tuple, should return first element by default
        cat = get_string("cat_social")
        self.assertEqual(cat, "تواصل")
        
        # Test English index
        cat_en = get_string("cat_social", lang_idx=1)
        self.assertEqual(cat_en, "Social")

if __name__ == "__main__":
    unittest.main()
