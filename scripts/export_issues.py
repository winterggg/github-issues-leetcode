import os
import requests
import datetime
import frontmatter  # pip install python-frontmatter
# import re

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
owner = os.environ.get('OWNER')
repo = os.environ.get('REPO')

if not owner or not repo:
    raise ValueError('No owner or repo provided')


def has_next_page(response):
    return response.links and 'next' in response.links


def handle_issues(base_path, headers, issue):
    # 如果没有 issue body，跳过
    if not issue['body']:
        return

    # 解析 issue 数据，生成 front-matter 并写入 markdown 文件
    title = issue['title']
    issue_number = issue['number']
    # utc+8
    created_date = datetime.datetime.strptime(
        issue['created_at'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
    updated_date = datetime.datetime.strptime(
        issue['updated_at'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
    tags = [label['name'] for label in issue['labels']]

    fm = frontmatter.Post('')
    fm['title'] = title
    fm['created_at'] = created_date
    fm['updated_at'] = updated_date
    fm['tags'] = tags
    fm['issue_number'] = issue_number

    # 生成 markdown 文件
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    # safe_title_for_filename = re.sub(r'[\/\\":|*?<>]', '_', title)
    # filename = f'{base_path}/{safe_title_for_filename}.md'
    filename = f'{base_path}/{issue_number}.md'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(fm))
        f.write('\n\n')
        f.write(issue['body'])

    # 打印生成的文件名和 issue 标题
    print(f'File generated: {filename} ({title})')


# 发送请求获取所有 issue 列表
url = f'https://api.github.com/repos/{repo}/issues'
response = requests.get(url, headers=headers, params={
                        'state': 'open', 'creator': owner, 'page': 1})

# 清空 markdowns 目录
if os.path.exists(base_path):
    for file in os.listdir(base_path):
        os.remove(os.path.join(base_path, file))

while True:
    print(f'Current page: {response.url}')
    # 遍历 issue 列表
    for issue in response.json():
        handle_issues(base_path, headers, issue)

    # 如果有下一页，继续遍历
    if has_next_page(response):
        response = requests.get(response.links['next']['url'], headers=headers)
    else:
        break