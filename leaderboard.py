import json
import argparse
import sys
import requests
import time
import re


class RequestAPI:
    def __init__(self, **kwargs):

        # Setting up game mode. Checks of the mode itself should be performed in parser.
        try:
            self.mode = kwargs['mode']
        except KeyError:
            raise KeyError("Invalid arguments received from the parser!")

        # Setting up count. Checks of the count itself should be performed in parser.
        try:
            self.count = kwargs['count']
        except KeyError:
            raise KeyError("Invalid arguments received from the parser!")

        if self.count is None:
            self.count = 20

        # Setting up user_id. Checks of the user_id itself should be performed in parser.
        try:
            self.user_id = kwargs['user_id']
        except KeyError:
            raise KeyError("Invalid arguments received from the parser!")

        # Setting up country. Checks of the country itself should be performed in parser.
        try:
            self.country = kwargs['country']
        except KeyError:
            raise KeyError("Invalid arguments received from the parser!")

        self.url = 'https://www.diabotical.com/api/v0/stats/leaderboard'

        # self.logpath = "./leaderboard_logs"

    def _perform_request(self) -> json:
        result = []
        pars = {'mode': f'{self.mode}', 'offset': 0}
        pages = self.count // 20
        if self.count % 20 > 1:
            pages += 1

        def connect_to_api(url, parameters):

            try:
                response = requests.get(url, timeout=2, params=parameters)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                e.__str__ = f'Unexpected response. Code {response.status_code}'
                raise
            except requests.exceptions.RequestException as err:
                err.__str__ = 'Unable to connect to server.'
                raise

            try:
                data = response.json()["leaderboard"]
            except (ValueError, KeyError):
                return "Bad response, unable to decode."
            return data

        if pages < 2:
            result = connect_to_api(self.url, pars)

        else:
            for i in range(pages):
                pars['offset'] = i * 20
                chunk = connect_to_api(self.url, pars)
                # a pause to avoid code 429 (happens at large count value with sleep less than 0.2 sec)
                time.sleep(0.2)
                result += chunk

        # Checks if there is proper user's entries in the result list:
        if not result:
            raise ValueError("No data received from server with given parameters!")
        # Checks if there is required fields in the very first entry of the result list assuming that the rest of
        # entries have the same structure.
        if 'user_id' not in result[0] or 'country' not in result[0]:
            raise KeyError("Invalid data received from server with given parameters!")

        return result[0:self.count]

    def _default_request(self) -> json:
        try:
            result = self._perform_request()
        except Exception as err:
            return err.__str__
        for entry in result:
            del entry['user_id']
        output = result

        return json.dumps(output, indent=4)

    def _search_by_userid(self) -> json:
        try:
            users_unfiltered = self._perform_request()
        except Exception as err:
            return err.__str__
        u_id = self.user_id

        def user_filter(entry: dict) -> bool:
            if entry['user_id'] == u_id:
                return True
            else:
                return False

        users_filtered = filter(user_filter, users_unfiltered)
        try:
            result = next(users_filtered)
        except StopIteration:
            output = "No such user found!"
            return json.dumps(output)

        del result['user_id']
        output = result

        return json.dumps(output, indent=4)

    def _count_users_by_country(self) -> json:
        try:
            users_unfiltered: list = self._perform_request()
        except Exception as err:
            return err.__str__

        country: str = self.country

        def country_filter(entry: dict) -> bool:
            if entry['country'] == country:
                return True
            else:
                return False

        users_filtered = filter(country_filter, users_unfiltered)
        result = []
        for f_entry in users_filtered:
            result.append(f_entry)

        if result:
            output = len(result)
        else:
            output = "No users of such country!"

        return json.dumps(output)

    def perform(self):
        if self.user_id:
            result = self._search_by_userid()
        elif self.country:
            result = self._count_users_by_country()
        else:
            result = self._default_request()
        return result


class Leaderboard:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Parameters: [-mode <MODE>], -- count <N>, --user_id, "
                                                          "<USER_id>, --country <COUNTRY>")
        self.parser.add_argument('--mode', action='store', type=str, required=True,
                                 help='Game mode. Available options: r_macguffin, r_wo, r_rocket_arena_2, '
                                      'r_shaft_arena_1, r_ca_2, r_ca_1.')
        self.parser.add_argument('--count', action='store', type=int, required=False,
                                 help='Number of entries to display or to search within from 1 to 500. Defaults to 20.')
        self.id_or_country = self.parser.add_mutually_exclusive_group(required=False)
        self.id_or_country.add_argument('--user_id', action='store', type=str,
                                        help='User id to search within given range. Usually consists of 32 letters or '
                                             'digits.')
        self.id_or_country.add_argument('--country', action='store', type=str,
                                        help='Country selection to display the number of users of such country within '
                                             'given range of users. Consists of two lowercase letters')

    def parse_args(self):
        arguments = self.parser.parse_args(sys.argv[1:])

        # checking mode
        if arguments.mode not in ['r_macguffin', 'r_wo', 'r_rocket_arena_2', 'r_shaft_arena_1', 'r_ca_2', 'r_ca_1']:
            self.parser.error(
                'Incorrect mode! Modes available: r_macguffin, r_wo, r_rocket_arena_2, r_shaft_arena_1, r_ca_2, r_ca_1')
        # checking count
        if arguments.count is not None:
            if arguments.count < 1 or arguments.count > 500:
                self.parser.error('Count must be from 1 to 500!')

        # checking user_id
        user_id_format = r'[a-z0-9]{32}'
        if not re.match(user_id_format, arguments.user_id):
            self.parser.error('Incorrect user_id format. Id must consist of 32 lowercase letters or digits.')

        # checking country
        country_format = r'[a-z]{2}'
        if not re.match(country_format, arguments.user_id):
            self.parser.error('Incorrect country format. Country must consist of two lowercase letters.')

        return arguments.__dict__


if __name__ == "__main__":
    # r = RequestAPI()
    # print(r.default_request())
    # print(r.count_users_by_country("ru"))
    # print(r.search_by_userid('b325363ffe6d46c8840c951b334cc09c'))

    ldbrd = Leaderboard()
    ldbrd_args = ldbrd.parse_args()
    rqst = RequestAPI(**ldbrd_args)
    # rqst = RequestAPI(mode='r_macguffin', count=42, user_id=None, country='de')
    # rqst = RequestAPI(mode='r_macguffin', count=500, user_id='b325363ffe6d46c8840c951b334cc09c', country=None)
    a = rqst.perform()
    print(a)

