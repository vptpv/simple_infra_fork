import requests, json
from atlassian import Jira
from pprint import pprint

def hot_zip():
    file = open('temp/jira_bot.json', 'r')
    user_data = json.loads(file.read())
    file.close()

    jira = Jira(
        url = user_data['url'],
        username = user_data['username'],
        password = user_data['password'])

    JQL = 'key = VKENG-3623'
    data = jira.jql(JQL)
    issuelinks = data.get('issues')[0].get('fields').get('issuelinks')
    tasks = ['VKENG-3623']
    for i in issuelinks:
        # print(i.get('type')['inward'], end = '\t')
        for ii in i.keys():
            if ii[-5:] == 'Issue':
                # print(i.get(ii)['key'], end = '\t')
                # print(i.get(ii)['fields']['summary'])
                tasks.append(i.get(ii)['key'])
    return tasks