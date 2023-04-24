import csv
import requests
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Check if weekly_contests.csv exists
if not os.path.exists("./weekly_contests.csv"):
    print("weekly_contests.csv not found. Please run contest.py and contest2csv.py first.")
    exit(1)

# Download ratings.txt
url = "https://raw.githubusercontent.com/zerotrac/leetcode_problem_rating/main/ratings.txt"
try:
    response = requests.get(url)
except requests.exceptions.RequestException as e:
    print(e)
    exit(1)

ratings_txt = response.text.splitlines()

# Process ratings.txt to create a dictionary with title_slug as key and rating as value
ratings = {}
for line in ratings_txt[1:]: # Skip the first line
    fields = line.split('\t')
    rating, title_slug = float(fields[0]), fields[4]
    ratings[title_slug] = rating

# Read weekly_contests.csv and extract title_slug from url
with open("./weekly_contests.csv", mode="r", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader)
    header.insert(3, "rating")
    

    # Write output to weekly_contests_with_rating.csv
    with open("./weekly_contests_with_rating.csv", mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        
        for row in reader:
            url = row[3]
            title_slug = url.split('/')[-2]
            rating = ratings.get(title_slug, -1)
            row.insert(3, rating)
            writer.writerow(row)

print("weekly_contests_with_rating.csv has been generated.")
