# CanvasScrape


This is a small python script that I wrote mostly for personal use. It uses Mechanize to scrape my school's Canvas account and if there are any new announcements by the professor for any class, texts it to my number using the Twilio API. I used sqlite3 to maintain a database of announcements, each with a unique id, which I used to check whether the announcement was new.
