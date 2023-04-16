from collections import defaultdict
import os
import requests
import datetime

# 设置时区为 UTC+0，防止 Debug 时时区不一致导致的问题 
os.environ['TZ'] = 'UTC'

# 从环境变量中获取 GitHub Personal Access Token
token = os.environ.get('TOKEN')

if not token:
    raise ValueError('No token provided')

# 设置 GitHub API 的请求头，包括 PAT 和 Accept 头部
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

# 定义 owner 和 repo 名称（可以从环境变量中获取）
owner = os.environ.get('OWNER')
repo = os.environ.get('REPO')

if not owner or not repo:
    raise ValueError('No owner or repo provided')

# 获取最近一周的日期
def get_week_dates():
    # utc+8
    today = datetime.datetime.now() + datetime.timedelta(hours=8)
    start = today - datetime.timedelta(days=today.weekday())
    end = start + datetime.timedelta(days=6)
    return [start + datetime.timedelta(days=i) for i in range((end - start).days + 1)]

WEEK_DATES = get_week_dates()
A_WEEK_AGO = (datetime.datetime.now() + datetime.timedelta(hours=8) - datetime.timedelta(days=7)).date()

def has_next_page(response):
    return response.links and 'next' in response.links

def handle_issues(issue, mappings=None, starred_issues=None):
    if not mappings:
        mappings = defaultdict(int)
    if not starred_issues:
        starred_issues = []

    if not issue['body']:
        return mappings, starred_issues

    created_date = datetime.datetime.strptime(
        issue['created_at'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
    date_path = created_date.strftime('%Y/%m/%d')
    mappings[date_path] += 1

    if created_date.date() >= A_WEEK_AGO:
        for label in issue['labels']:
            if label['name'] == "-Like":
                starred_issues.append({'url': issue['html_url'], 'title': issue['title']})
                break

    return mappings, starred_issues



# 发送请求获取所有 issue 列表
url = f'https://api.github.com/repos/{repo}/issues'
response = requests.get(url, headers=headers, params={
                        'state': 'open', 'creator': owner, 'page': 1})

mappings = None
starred_issues = None

while True:
    print(f'Current page: {response.url}')
    # 遍历 issue 列表
    for issue in response.json():
        mappings, starred_issues = handle_issues(issue, mappings, starred_issues)

    # 如果有下一页，继续遍历
    if has_next_page(response):
        response = requests.get(response.links['next']['url'], headers=headers)
    else:
        break

# mappings = defaultdict(<class 'int'>, {'2023/04/15': 5, '2023/04/14': 5, '2023/04/13': 2, '2023/02/03': 1, '2023/02/02': 1, '2023/02/01': 1, '2023/01/31': 1, '2023/01/30': 1, '2023/01/29': 1, '2023/01/28': 1})
# output
# # 本周记录
# |          | 4.10 | 4.11 | 4.12 | 4.13 | 4.14 | 4.15 | 4.16 |
# | -------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
# | 刷题量： | -    | -    | -    | 10   | 5    | -    | -    |


# 生成 markdown 表格
def generate_table(mappings):
    dates = WEEK_DATES
    total_count = sum([mappings.get(date.strftime('%Y/%m/%d'), 0) for date in dates])
    table = ['|          | {} |'.format(' | '.join([date.strftime('%m.%d') for date in dates]))]
    table.append('| :--------: | {} |'.format(' | '.join([':---:' for _ in dates])))
    table.append('| 刷题量 | {} |'.format(' | '.join([str(mappings.get(date.strftime('%Y/%m/%d'), '-')) for date in dates])))
    table.append('|        | {} |'.format(' | '.join([' ' for _ in range(len(dates)-2)] + [f'**总计：** | {total_count}'])))
    return table

def generate_starred_list(starred_issues):
    if not starred_issues:
        return 'No liked issues in the past week.'

    md_list = []
    for issue in starred_issues:
        md_list.append(f'- [{issue["title"]}]({issue["url"]})')

    return '\n'.join(md_list)

# 追加到 README.md 开头
tpl_path = './tpl/README_tpl.md'
plan_path = './components/plan.md'
todo_path = './components/todo.md'

with open(tpl_path, 'r', encoding='utf-8') as f:
    tpl = f.read()

with open(plan_path, 'r', encoding='utf-8') as f:
    plan = f.read()

with open(todo_path, 'r', encoding='utf-8') as f:
    todo = f.read()

starred = generate_starred_list(starred_issues)
weekly = '\n'.join(generate_table(mappings))

with open('./README.md', 'w', encoding='utf-8') as f:
    content = tpl
    content = content.replace('<!-- weekly -->', weekly)
    content = content.replace('<!-- plan -->', plan)
    content = content.replace('<!-- todo -->', todo)
    content = content.replace('<!-- starred -->', starred)
    f.write(content)


