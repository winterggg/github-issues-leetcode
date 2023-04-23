import requests
import json
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

url = "https://leetcode.cn/graphql"
headers = {
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://leetcode.cn',
    'Referer': 'https://leetcode.cn/contest/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'x-csrftoken': 'kNlLM7y44Eagk88wE26f7YKjRcQOzPsAXnn1AekJrX3YzYLKnGVTobzNvumA9oZ0',
}

contests = []
page_num = 1
page_size = 10

while True:
    variables = {
        "pageNum": page_num,
        "pageSize": page_size
    }
    query = """
    query contestHistory($pageNum: Int!, $pageSize: Int) {
        contestHistory(pageNum: $pageNum, pageSize: $pageSize) {
            totalNum
            contests {
                title
                titleSlug
            }
        }
    }
    """
    payload = {
        "operationName": "contestHistory",
        "variables": variables,
        "query": query
    }
    response = requests.post(url, headers=headers, json=payload)
    data = json.loads(response.text)

    contest_list = data["data"]["contestHistory"]["contests"]
    total_num = data["data"]["contestHistory"]["totalNum"]

    for contest in contest_list:
        title_slug = contest["titleSlug"]
        title = contest["title"]
        link = f"https://leetcode.cn/contest/api/ranking/api/ranking/{title_slug}"
        contests.append({"title": title, "link": link})

    if len(contests) >= total_num:
        break

    page_num += 1

# save contests to file
with open("./contests.json", "w", encoding="utf-8") as f:
    json.dump(contests, f, ensure_ascii=False, indent=4)



