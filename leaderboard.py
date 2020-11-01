import json

import requests
import logging


# FORMAT = '%(asctime) - %(message)'
# logging.basicConfig(filename='leaderboard.log', filemode='w', format=FORMAT, level=0)


class RequestAPI:
    def __init__(self, mode='r_macguffin'):  # переделать на kwargs
        self.pars = {'mode': f'{mode}', 'offset': 0}
        self.url = 'https://www.diabotical.com/api/v0/stats/leaderboard'
        self.logpath = "./leaderboard_logs"

    def _perform_request(self):
        response = requests.get(self.url, params=self.pars)
        # logging.debug(msg=f"Performing request to {self.url} with parameters {self.pars}")
        return response.json()

    def default_request(self):
        result = self._perform_request()
        for entry in result['leaderboard']:
            entry.pop('user_id')
        print(json.dumps(result['leaderboard'], indent=4))

    def search_by_userid(self, user_id: str = ''):
        users_unfiltered = self._perform_request()

        def user_filter(entry: dict) -> bool:
            if entry['user_id'] == user_id:
                return True
            else:
                return False

        users_filtered = filter(user_filter, users_unfiltered['leaderboard'])
        try:
            result = next(users_filtered)
        except StopIteration:
            print("No such user found!")
            return

        result.pop('user_id')
        print(json.dumps(result, indent=4))

    def count_users_by_country(self, country: str = ''):
        users_unfiltered = self._perform_request()

        def country_filter(entry: dict) -> bool:
            if entry['country'] == country:
                return True
            else:
                return False

        users_filtered = filter(country_filter, users_unfiltered['leaderboard'])
        result = []
        for f_entry in users_filtered:
            result.append(f_entry)

        if result:
            output = len(result)
        else:
            output = "No users of such country!"

        print(json.dumps(output))


if __name__ == "__main__":
    r = RequestAPI()
    # r.default_request()
    # r.count_users_by_country("ru")
    # r.search_by_userid('b325363ffe6d46c8840c951b334cc09c')