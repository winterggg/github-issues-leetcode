import os
import requests
import datetime
import frontmatter # pip install python-frontmatter
import re

# 从环境变量中获取 GitHub Personal Access Token
token = os.environ.get('TOKEN')
base_path = os.environ.get('LC_EXPORT_PATH') or './markdowns'

if not token:
    raise ValueError('No token provided')

# 设置 GitHub API 的请求头，包括 PAT 和 Accept 头部
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

# 定义 owner 和 repo 名称（可以从环境变量中获取）
owner = os.environ.get('OWNER') # "winterggg"
repo = os.environ.get('REPO') # "winterggg/test_actions"

if not owner or not repo:
    raise ValueError('No owner or repo provided')

# 发送请求获取所有 issue 列表
url = f'https://api.github.com/repos/{repo}/issues'
params = {'state': 'all'}  # 获取所有状态的 issue
response = requests.get(url, headers=headers, params=params)

# 定义筛选条件
author = owner

# 遍历 issue 列表，筛选作者为 owner 的 issue
for issue in response.json():
    if issue['user']['login'] == author:
        # 获取 issue 的详细信息
        url = issue['url']
        response = requests.get(url, headers=headers)
        issue_data = response.json()

        # 解析 issue 数据，生成 front-matter 并写入 markdown 文件
        title = issue_data['title']
        # utc-8
        created_date = datetime.datetime.strptime(issue_data['created_at'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
        updated_date = datetime.datetime.strptime(issue_data['updated_at'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
        tags = [label['name'] for label in issue_data['labels']]

        fm = frontmatter.Post('')
        fm['title'] = title
        fm['created_at'] = created_date
        fm['updated_at'] = updated_date
        fm['tags'] = tags

        # 生成 markdown 文件
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        safe_title_for_filename = re.sub(r'[\/\\":|*?<>]', '_', title)
        filename = f'{base_path}/{safe_title_for_filename}.md'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(fm))
            f.write('\n\n')
            f.write(issue_data['body'])

        # 打印生成的文件名和 issue 标题
        print(f'File generated: {filename} ({title})')