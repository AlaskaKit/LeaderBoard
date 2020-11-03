import unittest
from leaderboard import RequestAPI


class TestRequestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # один раз пнри запуске
        pass

    def setUp(self):
        # перед каждым тестом, мб очистка значений
        pass

    def test_perform_request(self):
        pass


    @classmethod
    def tearDownClass(cls):
        # мб убрать тестовые логи
        pass


if __name__ == '__main__':
    unittest.main()
