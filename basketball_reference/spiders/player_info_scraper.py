import scraper

def get_player_urls():
  soup = scraper.get_soup()
  rows = soup.find("table", {"id": "per_game_stats"}).findAll("tr", {"class" : "full_table"})
  urls = []

  for row in rows:
    scrape_player_info(row.findAll("a")[0]["href"])

def scrape_player_info(url):
  soup = scraper.get_soup()
  div = soup.find("div", {"itemtype" : "https://schema.org/Person"})
  first, last = div.find("h1", {"itemprop": "name"}).text.split(" ", 1)
  feet, inches = div.find("span", {"itemprop" : "height"}).text.split("-", 1)
  lbs = div.find("span", {"itemprop" : "weight"}).text.replace("lb", "")
  birth_year, birth_month, birth_day = div.find("span", {"itemprop" : "birthDate"})["data-birth"].split("-", 2)
  birth_place = div.find("span", {"itemprop": "birthPlace"}).text
  birth_city = birth_place[birth_place.find("in\xa0") + 3 : birth_place.find(",")]
  birth_state = birth_place[birth_place.find(',') + 2 :]

  ps = div.findAll('p')
  for p in ps:
    ptext = p.text

    # position
    if "Position:" in ptext:
      shoots = a[a.rfind(' ') + 1 : -1]
      if "Point Guard" in ptext:
        position = 1
      elif "Shooting Guard" in ptext: 
        position = 2
      elif "Small Forward" in ptext:
        position = 3
      elif "Power Forward" in ptext:
        position = 4
      elif "Center" in ptext:
        position = 5
      else:
        logging.warning("Unknown position {}".format(ptext))
    
    if "High School:" in ptext:
      hs_city = ptext[ptext.find("in\n") + 5 : ptext.find(",")]
      hs_state = ptext[ptext.rfind(' ') + 1 : -1]

    if "Draft:" in ptext:
      pick = ptext[ptext.find("pick, ") + 6 : ptext.rfind("overall") - 3]
      draft_year = ptext[ptext.rfind(',') + 2 : ptext.rfind(',') + 6]

def scrape_player_college_stats():
  pass

def main():
  logging.basicConfig(filename='player_info_scraper.log',level=logging.DEBUG)
  # scraper.store_html("https://www.basketball-reference.com/players/a/allengr01.html")
  # get_player_urls()
  scrape_player_info("woah")

if __name__ == "__main__":
  main()