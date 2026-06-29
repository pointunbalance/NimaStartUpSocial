import unittest
from logic.catalog_service import SiteCatalog, Shortcut

class TestCatalogLogic(unittest.TestCase):
    def test_normalize_google(self):
        url = "https://www.google.com"
        n1, n2 = SiteCatalog.normalize("جوجل", "", url)
        self.assertEqual(n1, "جوجل")
        self.assertEqual(n2, "Google")

    def test_normalize_github(self):
        url = "https://github.com/someone"
        # If name is English name, it should normalize to Arabic
        n1, n2 = SiteCatalog.normalize("GitHub", "", url)
        self.assertEqual(n1, "جيت هب")
        self.assertEqual(n2, "GitHub")

        # If name is custom, it should be preserved. name_en becomes catalog English name.
        n1, n2 = SiteCatalog.normalize("MyGit", "", url)
        self.assertEqual(n1, "MyGit")
        self.assertEqual(n2, "GitHub")

    def test_shortcut_creation(self):
        s = Shortcut("Name", "https://url.com", "default", "NameEN", "Cat")
        self.assertEqual(s.name, "Name")
        self.assertEqual(s.clicks, 0) # Default click count

if __name__ == "__main__":
    unittest.main()
