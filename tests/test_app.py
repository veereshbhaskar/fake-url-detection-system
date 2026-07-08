import unittest
from app import app


class AppRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page_serves_successfully(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Shield AI', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
