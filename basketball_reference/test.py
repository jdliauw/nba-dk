from requests_html import HTMLSession
from bs4 import BeautifulSoup

def run():
	session = HTMLSession()
	response = session.get("https://www.basketball-reference.com/leagues/NBA_2019.html")
	print(response.html)
	print("hello")

if __name__ == "__main__":
	run()
