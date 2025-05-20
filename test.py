import unittest
from app import app

class ProductScheduleRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_product_schedule_data(self):
        response = self.app.get('/api/product_schedule',query_string={'修理方式': '维修'})
        print(response.data)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        # Check if the response contains the expected keys
        self.assertIn('success', data)
        # Check if the success key is True
        self.assertTrue(data['success'])
        # Check if the response contains the expected data structure
        self.assertIn('stages_select', data)
        self.assertIn('count_stages_current', data)
        self.assertIn('stage_complete_ratio', data)
        print(data['stages_select'])
        print(data['count_stages_current'])
        print(data['stage_complete_ratio'])

if __name__ == '__main__':
    unittest.main()
