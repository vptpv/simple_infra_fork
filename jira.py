import json
from atlassian import Jira as JiraLib


class Jira:
    def __init__(self):
        file = open('temp/jira_bot.json', 'r')
        user_data = json.loads(file.read())
        file.close()

        self.jira = JiraLib(
            url=user_data['url'],
            username=user_data['username'],
            password=user_data['password']
        )

    def hot_zip(self):
        jql = 'key = VKENG-3623'
        data = self.jira.jql(jql)
        issue_links = data.get('issues')[0].get('fields').get('issuelinks')
        tasks = ['VKENG-3623']
        for i in issue_links:
            # print(i.get('type')['inward'], end = '\t')
            for ii in i.keys():
                if ii[-5:] == 'Issue':
                    # print(i.get(ii)['key'], end = '\t')
                    # print(i.get(ii)['fields']['summary'])
                    tasks.append(i.get(ii)['key'])
        return tasks
