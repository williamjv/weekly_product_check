try:
    import json
    import yaml
    from atlassian import Jira
except (ModuleNotFoundError, ImportError) as module:
    quit(f'The following module needs to be installed:\n {module}\n Use "pip install $MODULE" then try again.\n')


class Issue:
    def __init__(self, project, issue_type, summary, description):
        self.p = project
        self.t = issue_type
        self.s = summary
        self.d = description

    def create(self):
        credentials = yaml.load(open('./jira/credentials.yml'))
        jira = Jira(
            url=credentials['database']['hostname'],
            username=credentials['database']['username'],
            password=credentials['database']['password'],
            cloud=True)
        fields = {"project": {"key": self.p},
                  "issuetype": {"name": self.t},
                  "summary": self.s,
                  "description": self.d
                  }

        print(jira.issue_create(fields))
