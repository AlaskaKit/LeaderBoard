import json
import unittest
from leaderboard import *


class TestRequestAPI(unittest.TestCase):

    def setUp(self) -> None:
        self.request_object = RequestAPI(mode='r_macguffin', count=2, user_id=None, country=None)

        self.users_list = [{"user_id": "b325363ffe6d46c8840c951b334cc09c", "name": "enesy", "country": "dk",
                            "match_type": 2, "rating": "2246", "rank_tier": 40, "rank_position": 1, "match_count": 48,
                            "match_wins": 42},
                           {"user_id": "aee1fba486c54d1d8600b3c82c9264d7", "name": "Cookk1", "country": "",
                            "match_type": 2, "rating": "2216", "rank_tier": 40, "rank_position": 2, "match_count": 34,
                            "match_wins": 30}]

        self.output_users_list = [{"name": "enesy", "country": "dk", "match_type": 2, "rating": "2246", "rank_tier": 40,
                                   "rank_position": 1, "match_count": 48, "match_wins": 42},
                                  {"name": "Cookk1", "country": "", "match_type": 2, "rating": "2216", "rank_tier": 40,
                                   "rank_position": 2, "match_count": 34, "match_wins": 30}]

        correct_leaderboard = json.dumps({"leaderboard": [
            {"user_id": "b325363ffe6d46c8840c951b334cc09c", "name": "enesy", "country": "dk",
             "match_type": 2, "rating": "2246", "rank_tier": 40, "rank_position": 1, "match_count": 48,
             "match_wins": 42},
            {"user_id": "aee1fba486c54d1d8600b3c82c9264d7", "name": "Cookk1", "country": "",
             "match_type": 2, "rating": "2216", "rank_tier": 40, "rank_position": 2, "match_count": 34,
             "match_wins": 30}]})

        incorrect_leaderboard = json.dumps({"leaderboard": [
            {"user_id": "b325363ffe6d46c8840c951b334cc09c", "name": "enesy", "country": "dk",
             "match_type": 2, "rating": "2246", "rank_tier": 40, "rank_position": 1, "match_count": 48,
             "match_wins": 42},
            {"user_id": "aee1fba486c54d1d8600b3c82c9264d7", "name": "Cookk1", "country": "",
             "match_type": 2, "rating": "2216", "rank_tier": 40, "rank_position": 2, "match_count": 34,
             "match_wins": 30}]})

        empty_leaderboard = json.dumps({"leaderboard": []})

        not_a_leaderboard = json.dumps({"i don't know what i am": [42]})
        not_a_json = "I'm a string'"

    def test_parse_args(self):
        pass

    def test_perform_request(self):
        pass

    def test_default_request(self):
        case = self.request_object._default_request(self.users_list)
        sample = json.dumps(self.output_users_list, indent=4)
        self.assertSequenceEqual(case, sample)

    def test_user_search1(self):
        self.request_object.user_id = "b325363ffe6d46c8840c951b334cc09c"
        case = self.request_object._search_by_userid(self.users_list)
        sample = json.dumps(self.output_users_list[0], indent=4)
        self.assertSequenceEqual(case, sample)

    def test_user_search2(self):
        self.request_object.user_id = "aaaaa63ffe6d46c8840c951b334cc09c"
        case = self.request_object._search_by_userid(self.users_list)
        sample = json.dumps("No such user found!")
        self.assertSequenceEqual(case, sample)

    def test_country_search1(self):
        self.request_object.country = "dk"
        case = self.request_object._count_users_by_country(self.users_list)
        sample = json.dumps(1)
        self.assertSequenceEqual(case, sample)

    def test_country_search2(self):
        self.request_object.country = "ru"
        case = self.request_object._count_users_by_country(self.users_list)
        sample = json.dumps("No users of such country!")
        self.assertSequenceEqual(case, sample)


if __name__ == '__main__':
    unittest.main()
