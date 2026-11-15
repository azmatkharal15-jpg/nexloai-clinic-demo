import unittest
from clinic_config import ClinicNotFound, load_clinic, public_config

class ClinicConfigTests(unittest.TestCase):
    
    def test_main_clinic_is_enabled_and_uses_existing_files(self):
        # Aapki main clinic ka test
        c = load_clinic("zia-medical-center")
        self.assertEqual(c["name"], "Zia Medical Center")
        self.assertTrue(c["enabled"])
        
    def test_all_5_clinics_are_configured(self):
        # Check karein ke aapki 5 clinics ka config theek hai
        clinics = ["zia-medical-center", "dr-humeira", "dr-michael", "evergreen", "amwaj"]
        for slug in clinics:
            c = load_clinic(slug)
            self.assertTrue(c["enabled"])
            self.assertIn("prompt_file", c)
            self.assertIn("knowledge_base_file", c)

    def test_unknown_slug_is_rejected(self):
        with self.assertRaises(ClinicNotFound):
            load_clinic("not-a-real-clinic")

    def test_path_traversal_is_rejected(self):
        with self.assertRaises(ClinicNotFound):
            load_clinic("../data")

    def test_public_config_does_not_expose_file_paths(self):
        c = public_config(load_clinic("zia-medical-center"))
        self.assertNotIn("prompt_file", c)
        self.assertNotIn("knowledge_base_file", c)

if __name__ == "__main__":
    unittest.main()