from collections import defaultdict
import os
import requests
import datetime

from utils.dotenv_loader import load_env

# 设置时区为 UTC+0，防止 Debug 时时区不一致导致的问题 
os.environ['TZ'] = 'UTC'

load_env()

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

def handle_issues(issue, mappings=None, starred_issues=None, review_issues=None):
    if not mappings:
        mappings = defaultdict(int)
    if not starred_issues:
        starred_issues = []
    if not review_issues:
        review_issues = defaultdict(int)

    if not issue['body']:
        return mappings, starred_issues, review_issues

    created_date = datetime.datetime.strptime(
        issue['created_at'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
    updated_date = datetime.datetime.strptime(
        issue['updated_at'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
    created_date_path = created_date.strftime('%Y/%m/%d')
    updated_date_path = updated_date.strftime('%Y/%m/%d')
    mappings[created_date_path] += 1

    review_flag = False
    like_flag = False
    if created_date.date() >= A_WEEK_AGO:
        for label in issue['labels']:
            if label['name'] == "-Like":
                like_flag = True
            elif label['name'] == "-Review":
                review_issues[updated_date_path] += 1
                review_flag = True

    elif updated_date.date() >= A_WEEK_AGO:
        for label in issue['labels']:
            if label['name'] == "-Review":
                review_issues[updated_date_path] += 1
                break
        
    if like_flag:
        starred_issues.append({'url': issue['html_url'], 'title': issue['title'], 'reviewed': review_flag})

    return mappings, starred_issues, review_issues



# 发送请求获取所有 issue 列表
url = f'https://api.github.com/repos/{repo}/issues'
response = requests.get(url, headers=headers, params={
                        'state': 'open', 'creator': owner, 'page': 1})

mappings = None
starred_issues = None
review_issues = None

while True:
    print(f'Current page: {response.url}')
    # 遍历 issue 列表
    for issue in response.json():
        mappings, starred_issues, review_issues = handle_issues(issue, mappings, starred_issues, review_issues)

    # 如果有下一页，继续遍历
    if has_next_page(response):
        response = requests.get(response.links['next']['url'], headers=headers)
    else:
        break

def count_streak_days(mappings):
    streak = 0
    today = datetime.datetime.now() + datetime.timedelta(hours=8)
    date = today.date()
    # 如果今天还没有刷题，先从昨天开始统计
    if date.strftime('%Y/%m/%d') not in mappings:
        date -= datetime.timedelta(days=1)
    while date.strftime('%Y/%m/%d') in mappings:
        streak += 1
        date -= datetime.timedelta(days=1)
    return streak

streak = count_streak_days(mappings)

# 生成 markdown 表格
def generate_table(mappings, review_issues, streak):
    dates = WEEK_DATES
    total_count = sum([mappings.get(date.strftime('%Y/%m/%d'), 0) for date in dates])
    table = ['|          | {} |'.format(' | '.join([date.strftime('%m.%d') for date in dates]))]
    table.append('| :--------: | {} |'.format(' | '.join([':---:' for _ in dates])))
    table.append('| 刷题量 | {} |'.format(' | '.join([str(mappings.get(date.strftime('%Y/%m/%d'), '-')) for date in dates])))
    table.append('| 复习量 | {} |'.format(' | '.join([str(review_issues.get(date.strftime('%Y/%m/%d'), '-')) for date in dates])))
    table.append('|        | {} |'.format(' | '.join([' ' for _ in range(len(dates)-6)] + [f'**本周复习** | {sum(review_issues.values())}', f'**本周刷题** | {total_count}', f'**连续打卡** | {streak}'])))
    return table

def generate_starred_list(starred_issues):
    if not starred_issues:
        return 'No liked issues in the past week.'

    md_list = []
    for issue in starred_issues:
        if issue['reviewed']:
            md_list.append(f'- [x] [{issue["title"]}]({issue["url"]})')
        else:
            md_list.append(f'- [ ] [{issue["title"]}]({issue["url"]})')

    return '\n'.join(md_list)

# 追加到 README.md 开头
tpl_path = './tpl/README_tpl.md'
plan_path = './components/plan.md'
todo_path = './components/todo.md'
resources_path = './components/resources.md'

with open(tpl_path, 'r', encoding='utf-8') as f:
    tpl = f.read()

with open(plan_path, 'r', encoding='utf-8') as f:
    plan = f.read()

with open(todo_path, 'r', encoding='utf-8') as f:
    todo = f.read()

with open(resources_path, 'r', encoding='utf-8') as f:
    resources = f.read()

starred = generate_starred_list(starred_issues)
weekly = '\n'.join(generate_table(mappings, review_issues, streak))

with open('./README.md', 'w', encoding='utf-8') as f:
    content = tpl
    content = content.replace('<!-- weekly -->', weekly)
    content = content.replace('<!-- plan -->', plan)
    content = content.replace('<!-- todo -->', todo)
    content = content.replace('<!-- starred -->', starred)
    content = content.replace('<!-- resources -->', resources)
    f.write(content)


