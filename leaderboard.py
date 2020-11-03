import json
import argparse
import sys
import requests
import time
import re


class RequestAPI:
    """
    RequestAPI object designed to send requests to the Diabotical API leaderboard
    with different behavior depending on received parameters.
    Method to use: RequestApi.perform() which takes all the required parameters from the constructor.
    Other methods are protected.
    """
    def __init__(self, **kwargs):
        """
        Constructor of the RequestAPI class. Setting up parameters (checks if available. sets defaults).
        Setting up the API leaderboard URL.
        :param kwargs: arguments received from the parser. <Mode> is required argument, <count>, <user_id> and <country>
        are optional.
        """
        # Setting up game mode. Checks of the mode itself should be performed in parser.
        try:
            self.mode: str = kwargs['mode']
        except KeyError as arg_err:
            arg_err.__str__ = "Invalid arguments received from the parser!"
            raise

        # Setting up count. Checks of the count itself should be performed in parser.
        try:
            self.count: int = kwargs['count']
        except KeyError as arg_err:
            arg_err.__str__ = "Invalid arguments received from the parser!"
            raise

        if self.count is None:
            self.count = 20

        # Setting up user_id. Checks of the user_id itself should be performed in parser.
        try:
            self.user_id: str = kwargs['user_id']
        except KeyError as arg_err:
            arg_err.__str__ = "Invalid arguments received from the parser!"
            raise

        # Setting up country. Checks of the country itself should be performed in parser.
        try:
            self.country: str = kwargs['country']
        except KeyError as arg_err:
            arg_err.__str__ = "Invalid arguments received from the parser!"
            raise

        # Setting up API URL.
        self.url: str = 'https://www.diabotical.com/api/v0/stats/leaderboard'

    def _perform_request(self) -> list:
        """
        Protected method for requesting the API and checking the result of the request.
        The API standard output is 1 page of 20 entries, so multiple requests can be made depending on requested
        quantity of entries (<count> argument).
        :return: a list of dictionaries, containing requested amount of user's entries.
        """
        result: list = []
        pars: dict = {'mode': f'{self.mode}', 'offset': 0}
        pages: int = self.count // 20
        if self.count % 20 > 1:
            pages += 1

        def connect_to_api(url, parameters) -> list:
            """
            Built-in function to actually connect to API. Performs connect, check if the response body
            has required information.
            :param url: url to request
            :param parameters: dictionary with the parameters of the request.
            :return: a list of dictionaries, containing 20 user's entries from the requested page.
            """
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
                data: list = response.json()["leaderboard"]
            except (ValueError, KeyError) as data_err:
                data_err.__str__ = "Bad response, unable to decode."
                raise
            return data

        # Single request (count 20 or less)
        if pages < 2:
            result = connect_to_api(self.url, pars)

        # Multiple requests (count more than 20)
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

    @staticmethod
    def _default_request(u_list: list) -> json:
        """
        Task point #1. Takes a list of the <count> users and returns it as json object without "user_id" field.
        :param u_list: list of the users received from the API request.
        :return: json object with user entries.
        """
        for entry in u_list:
            del entry['user_id']
        output = u_list

        return json.dumps(output, indent=4)

    def _search_by_userid(self, u_list: list) -> json:
        """
        Task point #2. Takes a list of the <count> users and searches it for the specific user with the <user_id>
        parameter.
        :param u_list: list of the users received from the API request.
        :return: json object with requested user's entry (without "user_id") or the info string if user is not found.
        """

        users_unfiltered: list = u_list
        u_id: str = self.user_id

        def user_filter(entry: dict) -> bool:
            """
            Filter function for searching the user in the list received from API.
            :param entry: user's entry
            :return: True if the user is found, False otherwise.
            """
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

    def _count_users_by_country(self, u_list: list) -> json:
        """
        Task point #3. Searches in the user's list for the users from a specific country with the <country> parameter.
        Ignores users without country information.
        :param u_list: list of the users received from the API request.
        :return: json obj with the number of players of a given country within requested amount of user's or with
        the information string if there are no users from the requested country.
        """

        users_unfiltered: list = u_list
        country: str = self.country

        def country_filter(entry: dict) -> bool:
            """
            Filter function for the country searching.
            :param entry: user's entry
            :return: True if the user is from the requested country, False otherwise
            """
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
        """
        Requests information of the <count> users. Passes the information received to the specific method depending
        on the args <user_id> or <country> (or absence of those).
        :return: json object with the result of the specific method's work.
        """
        try:
            users_list: list = self._perform_request()
        except Exception:
            raise

        if self.user_id:
            result = self._search_by_userid(users_list)
        elif self.country:
            result = self._count_users_by_country(users_list)
        else:
            result = self._default_request(users_list)
        return result


class LeaderboardParser:
    """
    A parser for the command line arguments. Parses and checks arguments received.
    """
    def __init__(self):
        """
        A constructor. Specifying the arguments in conformity with the task.
        Restrictions for the arguments are established due to leaderboard properties
        (there are 500 entries in every mode) and user's actual properties (<user_id> and <country> format).
        Arguments <user-id> and <country> are mutually exclusive.
        """
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
        """
        Performs parsing and checks.
        :return: A dictionary with arguments.
        """
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
        if arguments.user_id is not None:
            user_id_format = r'[a-z0-9]{32}'
            if not re.match(user_id_format, arguments.user_id):
                self.parser.error('Incorrect user_id format. Id must consist of 32 lowercase letters or digits.')

        # checking country
        if arguments.country is not None:
            country_format = r'[a-z]{2}'
            if not re.match(country_format, arguments.country):
                self.parser.error('Incorrect country format. Country must consist of two lowercase letters.')

        return arguments.__dict__


if __name__ == "__main__":
    ldbrd = LeaderboardParser()
    ldbrd_args = ldbrd.parse_args()
    try:
        rqst = RequestAPI(**ldbrd_args)
        information = rqst.perform()
        print(information)
    except Exception as error:
        print(error.__str__)
