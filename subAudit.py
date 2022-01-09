#!/usr/bin/python3

try:
    import argparse
    import datetime
    import json
    import requests
    import time
    import jira.generate_card as jira
    from billing_api.billingauth import billing_user, billing_token
except (ModuleNotFoundError, ImportError) as module:
    quit(f'The following module needs to be installed:\n {module}\n Use "pip install $MODULE" then try again.\n')

display_add = 'SubAccount-add'
display_del = 'SubAccount-remove'
list_of_types = {'CDN': {'name': ['Akamai'], 'display': [display_add, display_del]},
                 'DDOS': {'name': ['ddos.premium', 'ddos.standard'], 'display': [display_add, display_del]},
                 'Load Balancers': {'name': ['LB.license'], 'display': [display_del]}}
jira_project = 'Network Team'
jira_type = 'Task'
jira_summary = 'Weekly Subaccount/Product check'


class Data(object):
    def __init__(self):
        """Set the variables."""
        self.date = 7
        self.url = 'https://api.example.com/Logging/info'
        self.params = {}
        self.types = list_of_types
        self.dictionary = {}

    def get_data(self):
        """Grab data from billing"""
        req = {'params': self.params}
        send = requests.post(self.url, auth=(billing_user, billing_token), data=json.dumps(req))
        send2 = send.json()
        return send2

    def set_params(self, msg_data):
        """Set Parameters to use towards get_data"""

        def date():
            """Default 7 days except when user provided alternate number."""
            today = datetime.date.today()
            d = str(today - datetime.timedelta(days=self.date))
            return d

        self.params = {
            'search': [
                {'data': date(),
                 'field': 'date',
                 'method': 'greater'
                 },
                {'data': 'SubAccount-',
                 'field': 'type',
                 'method': 'contains'
                 },
                {'data': msg_data,
                 'field': 'message',
                 'method': 'contains'}
            ],
            'order': 'asc',
            'page_size': '1000'
        }

    def pull_data(self):
        """Pull the data."""

        def update_dict(data, k):
            """Update Dictionary with data."""
            try:
                self.dictionary[k]
            except KeyError:
                self.dictionary[k] = {}
            count = len(self.dictionary[k]) + 1
            for i in data['items']:
                print(f'i = {i}')
                try:
                    self.dictionary[k][count].update(i)
                except (AttributeError, KeyError):
                    self.dictionary[k][count] = i
                count += 1
            return

        print(f'One moment as we gather data.')
        for key, value in self.types.items():
            for t in value['name']:
                self.set_params(t)
                update_dict(self.get_data(), key)
        return

    def report(self, display_only, days=None):
        pre_msg = 'Below are a list of sub-accounts recently created or terminated that the Network team supports at ' \
                  'some level.  Occasionally the Network team is gets missed in the creation or termination process.  ' \
                  'This weekly check is to help reduce the number of misses.\n\n* CDN = Akamai only\n* DDoS = Premium ' \
                  '(On site) mitigations\n* Load Balancer = Licensing only\n\nh3. Instructions:\n1. Grab account name ' \
                  'from billing.  Search Salesforce for account name and find product add/termination ticket.\n2. If ' \
                  'needed perform network portion of procedure.\n* CDN - [Akamai ' \
                  '|https://control.akamai.com/]\n* DDoS - [On site ' \
                  '|https://ddos.example.com]\n* LB License - [ License Manager ' \
                  '|https://license.example.com]\n\n3. Note Ticket/Jira and mark it done.\n\n'
        message = ''
        if days:
            self.date = int(days)
        self.pull_data()

        def sort(string, subtype):
            json_value = ''
            for key, value in string.items():
                if string[key]['type'] == subtype:
                    json_value += f'{json.dumps(value, sort_keys=True, indent=4)}\n'
            return f'{json_value}\n'

        for k1, v1 in self.dictionary.items():
            action_list = [action for action in self.types[k1]['display'] if (action in str(v1))]
            if action_list:
                message += f'\nh1. {k1}'
                for a in action_list:
                    if a is display_add:
                        message += f'\nh3. Additions:\n'
                        message += f'{{code:JSON}}\n {sort(v1, a)}{{code}}\n'
                    else:
                        message += f'\nh3. Terminations:\n'
                        message += f'{{code:JSON}}\n {sort(v1, a)}{{code}}\n'
        if message and display_only:
            print_msg = pre_msg + message
            print(print_msg)
        elif message:
            jira_desc = pre_msg + message
            print(f'Calling on Jira script...\n')
            jira.Issue(jira_project, jira_type, jira_summary, jira_desc).create()
        else:
            print(f'\n  No network product additions or terminations found.\n')


def main():
    start = time.perf_counter()
    parser = argparse.ArgumentParser(description="Script to review subaccount additions/deletions related to "
                                                 "networking services.")
    parser.add_argument('-d', '--days', metavar='<# of DAYS>', type=int, help='Number of days back to search.',
                        dest='days')
    parser.add_argument('-p', '--print', help='Print only, do not create Jira Card.',
                        action='store_true')
    args = parser.parse_args()
    Data().report(args.print, args.days)
    finish = time.perf_counter()
    print(f'\nReport completed in {round(finish - start, 2)} second(s)')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        quit('')
