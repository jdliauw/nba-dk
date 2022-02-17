import requests
from bs4 import BeautifulSoup
import os
import shutil
import time

start = time.time()

def store_year_stats(year):
    # time.sleep(5)
    url = 'http://www.basketball-reference.com/leagues/NBA_' + year + '_totals.html'
    url_request = requests.get(url)
    html = url_request.text
    soup = BeautifulSoup(html, 'html.parser')
    stats_table = soup.find('table', {'class' : 'sortable  stats_table'}).find('tbody').findAll('tr')

    file_name = str(year) + '_nba_totals.csv'
    output = open(str(year) + '_nba_totals.csv', "w+") 
    output.write('PID,LAST,FIRST,POS,AGE,TEAM,GP,GS,MP,FGM,FGA,FG%,3PM,3PA,3P%,2PM,2PA,2P%,EFG%,FTM,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS\n')

    for row in stats_table:
        omit = 0
        for attribute in row.findAll('td'):
            if omit != 0:
                if omit == 1:
                    pid = attribute.find('a')['href']
                    pid = pid[pid.rfind('/') + 1 : pid.rfind('.')]
                    output.write(pid + ',')
                    name = attribute['csk']
                    last, first = name.split(',')
                    output.write(last + ',')
                    output.write(first + ',')
                    del first, last, name
                elif omit == 29:
                    output.write(str(attribute.string) + '\n')
                else:
                    output.write(str(attribute.string) + ',')
            omit = omit + 1
        
    output.close()

    if not os.path.exists('year_stats_files'):
        os.makedirs('year_stats_files')
    
    source = os.path.dirname(os.path.abspath(__file__))
    year_destination = source + "/year_stats_file"
    file_path = year_destination + '/' + file_name
    if os.path.exists(file_path):
        os.remove(file_path) # write over file
    shutil.move(file_name, year_destination)

def grab_player_urls(year):
    plurls = []
    url = 'http://www.basketball-reference.com/leagues/NBA_{0}_totals.html'.format(year)
    url_request = requests.get(url)
    html = url_request.text
    soup = BeautifulSoup(html, 'html.parser')
    a_tags = soup.find('table', {'class' : 'sortable  stats_table'}).find('tbody').findAll('a')
    
    for a_tag in a_tags:
        if 'players' in a_tag['href']:
            full_url = 'http://basketball-reference.com' + str(a_tag['href'])
            if full_url not in plurls:            
                plurls.append(full_url)

    return plurls

def grab_game_log_urls(player_url, year):

    glurl = []
    for i in range(0, len(player_url)):
        glurl.append(player_url[i][:-5] + '/gamelog/{0}/'.format(year))

    return glurl

    # time.sleep(3.5)
    # game_log_url = []
    # url_request = requests.get(player_url)
    # html = url_request.text
    # li_tags = BeautifulSoup(html, 'html.parser').findAll('li', {'class' : 'narrow'})
    # a_tags = BeautifulSoup(str(li_tags), 'html.parser').findAll('a')
    # del li_tags
    
    # for a_tag in a_tags:
    #     if 'gamelog' in a_tag['href'] and str(year) in a_tag['href']:
    #         full_url = 'http://basketball-reference.com' + str(a_tag['href'])

    #         if full_url not in game_log_url:            
    #             game_log_url.append(full_url)

    # return game_log_url

def store_game_logs(player_gl_url, output):
    time.sleep(3.5)
    url_request = requests.get(player_gl_url)
    html = url_request.text
    soup = BeautifulSoup(html, 'html.parser')
    pid = player_gl_url[player_gl_url.rfind('players') + 10 : -14]
    gl_table = soup.find('table', {'class' : 'sortable  row_summable stats_table'}).find('tbody').findAll('tr')
    
    try:
        first, last = soup.find('h1').string.rsplit(' ',3)[0].split(' ',1)
    except:
        first = ''
        last = soup.find('h1').string.rsplit(' ',3)[0]

    season = str(int(player_gl_url[-5 : -1]) -1) + '-' + str(player_gl_url[-5 : -1])

    # with open(ofn, "a") as output:
    for row in gl_table: 
        glt_index = 0
        for attribute in row.findAll('td'):
            if glt_index == 0:
                hold = attribute.string
            elif glt_index == 1:
                if attribute.string == None:
                    glt_index = 0
                    break;
                else:
                    output.write(pid + ',' + first + ',' + last + ',' + season + ',' + hold + ',')
                    glt_index = glt_index + 1
                    continue;
            elif glt_index == 2:
                if attribute.string is not None:
                    year, month, day = attribute.string.split('-')
                    output.write(year + ',' + month + ',' + day + ',')
                else:
                    output.write('None, None, None,')
            elif glt_index == 3:
                if attribute.string is not None:
                    years = attribute.string.split('-')
                    days = float(years[1])/365.25
                    years = float(years[0]) + float(days)
                    output.write(str(years) + ',')
                else:
                    output.write('None,')
            elif glt_index == 5:
                if attribute.string == '@':
                    output.write('AWAY' + ',') 
                else:
                    output.write('HOME' + ',')
            elif glt_index == 7:            
                if attribute.string is not None:
                    if 'W' in attribute.string:
                        w = attribute.string[attribute.string.find('+') + 1 : attribute.string.rfind(')')]
                        output.write(w + ',')
                    else:
                        l = attribute.string[attribute.string.find('-') : attribute.string.rfind(')')]
                        output.write(l + ',')
                else:
                    output.write('None,')
            elif glt_index == 8:
                if attribute.string is not None:
                    if attribute.string == '1':
                        output.write('TRUE' + ',')
                    else:
                        output.write('FALSE' + ',')
                else:
                    output.write('None,')
            elif glt_index == 9:
                if attribute.string is not None:
                    mp = attribute.string.split(':')

                    if len(mp) == 3:
                        mp = float(mp[0]) + float(mp[1])/60 + float(mp[2])/360
                        output.write(str(mp) + ',')
                    else:
                        mp = float(mp[0]) + float(mp[1])/60
                        output.write(str(mp) + ',')
                else:
                    output.write('None,')
            elif glt_index == 29:
                output.write(str(attribute.string) +'\n')
                break;
            else:
                output.write(str(attribute.string) + ',')
            glt_index = glt_index + 1

def year_parse():
    
    years = []
    indices = []
    hold = []
    print('\nThis script pulls the game logs from basketball-reference.com for a given year or years and stores it as a csv in your current directory in the format: \"YEAR-YEAR_stats.csv\"\n')
    print('   + If you want to pull a single year, just type the year followed by \'enter\'\n   + If you want to pull from multiple years, separate each year by a space, then \'enter\'.')
    print('   + If you want to pull from an (inclusive) range of years, separate by the years by a \'-\' (ex: 1996-1997), then \'enter\'\n')

    selection = raw_input("   Year(s) selection: ")

    if ' ' not in selection and '-' not in selection:
        years.append(selection)

    elif ' ' in selection:
        years = selection.split(' ')

        flag = True
        i = 0

        while flag:

            if '-' in years[i]:
                hold = years[i].split('-')

                for j in range(int(hold[1])  + 1 - int(hold[0])):
                    hold.append(str(int(hold[0]) + j))

                hold.remove(hold[0])
                hold.remove(hold[0])                

                for k in range(0, len(hold)):
                    if(hold[k] not in years):
                        years.append(hold[k])
                years.remove(years[i])
                i = i - 1

            i = i + 1

            if i == len(years):
                flag = False

    else:
        years = selection.split('-')

        for i in range(int(years[1]) + 1 - int(years[0])):
            years.append(str(int(years[0]) + i))

        years.remove(years[0])
        years.remove(years[0])
           
    years.sort()

    return years

def run():

	years = year_parse()

	for year in years:
		ofn = '{0}-{1}_stats.csv'.format(str(int(year)-1), year)
		output = open(ofn, "w+")
		output.write('PID,FIRST,LAST,SEASON,GAME,YEAR,MONTH,DAY,AGE,TEAM,HOME/AWAY,OPP,RESULT,GS,MP,FGM,FGA,FG%,3PM,3PA,3P%,FTM,FTA,FT%,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS,GMSC,+/-\n')
		purls = grab_player_urls(year)
		glurls = grab_game_log_urls(purls, year)
		
		for i in range(0,len(glurls)):
			print(i)
			store_game_logs(glurls[i], output)

		output.close()

	print('\ntime elapsed:', time.time() - start, '\n')

if __name__ == '__main__':
    run()