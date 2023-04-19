# Prepare

## 图床

1. 创建图床分支（如 pics）：

   ```bash
   git checkout --orphan pics
   # 删除所有文件
   git rm -rf .
   # 创建 README.md
   echo "# 图床" > README.md
   # 提交
   git commit -m "init"
   # 推送到远程
   git push origin pics
   ```
2. 创建 CF Worker，将其部署到 Cloudflare Workers，加速访问。（可选）

   创建 CF Worker [脚本](scripts/cf-worker.js)，绑定域名（官方的三级域名已被墙），然后填写到 PicGo 的自定义域名中。

3. 配置 PicGo，将图床设置为 GitHub

   ```
   设定仓库名: winterggg/github-issues-leetcode
   设定分支名: pics
   设定Token: ***
   设定存储路径: images/
   设定自定义域名: https://pics.winterg.site/
   ```
