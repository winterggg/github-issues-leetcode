import json
import requests
import csv
import time
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load contests data
with open("./contests.json", "r", encoding="utf-8") as f:
    contests = json.load(f)

# # find { "title": "第 189 场周赛" } index
# for i, v in enumerate(contests):
#     if v['title'] == '第 189 场周赛':
#         print(i)
#         break

# Define headers for the CSV file
headers = ["contest", "title", "english_title", "url"]

# Check if progress.txt exists, and read the last saved index
try:
    with open("./progress.txt", "r") as progress_file:
        last_saved_index = int(progress_file.read().strip())
# File does not exist, or cannot be converted to int
except (FileNotFoundError, ValueError):
    last_saved_index = 0

# Open a new CSV file with append mode
with open("./weekly_contests.csv", "a", newline='', encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)

    # Write the header row only if starting from the beginning
    if last_saved_index == 0:
        csv_writer.writerow(headers)

    # Loop through each contest, from the last saved index
    for index, contest in enumerate(contests[last_saved_index:], start=last_saved_index):
        contest_title = contest["title"]
        contest_link = contest["link"]

        success = False
        while not success:
            try:
                # Send a GET request to the contest API URL
                response = requests.get(contest_link)
                response_data = response.json()

                # Extract questions from the response data
                questions = response_data["questions"]

                # Loop through each question and write to the CSV file
                for question in questions:
                    title = question["title"]
                    english_title = question["english_title"]
                    title_slug = question["title_slug"]

                    # Create the question URL
                    url = f"https://leetcode.cn/problems/{title_slug}/"

                    # Write the data to the CSV file
                    csv_writer.writerow([contest_title, title, english_title, url])

                success = True
                print(f"Processed contest {contest_title}")

            except Exception as e:
                print(f"Error: {e}, retrying in 60 seconds...")
                time.sleep(60)

        # Save the next contest index as the last saved index
        with open("progress.txt", "w") as progress_file:
            progress_file.write(str(index + 1))

print("All contests processed successfully.")
