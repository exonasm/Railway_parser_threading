import csv
import requests
from random import choice
import concurrent.futures

from bs4 import BeautifulSoup

URL = 'https://www.alta.ru'
proxies = open('proxies').read().split('\n')
user_agent_list = open('user_agent_list.txt').read().split('\n')

container = []


def get_html(url):
	
	proxy = {'http': 'http://' + choice(proxies)}
	user_agent = {'User-agent': choice(user_agent_list)}

	r = requests.get(url, headers=user_agent, proxies=proxy)
	return r.content


def get_railway_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    railways = soup.find_all('a', class_='pRailway_item')
    return railways


def get_station_list(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    stations = soup.find_all('a', class_='pRailway_item')
    return stations


def get_page_info(station_url):
    html = get_html(URL + station_url)
    soup = BeautifulSoup(html,'html.parser')
    info_location = soup.find_all('div', class_='pRailway_row')
    country = info_location[0].find('div', 'pRailway_column-left').text.split()[-1]
    station = info_location[3].find_all('div', 'pRailway_column-left')[-1].text.split()[-1]
    code = info_location[3].find_all('div', 'pRailway_column-left')[0].text.split()[-1]
    latitude = info_location[2].find('div', class_='pRailway_column-right').find_all('div')[0].text.split()[-1]
    longitude = info_location[2].find('div', class_='pRailway_column-right').find_all('div')[-1].text.split()[-1]
    coordinates = latitude + ', ' + longitude
    data = {
        'country': country,
        'station': station,
        'code': code,
        'coordinates': coordinates,
    }
    return data


def data_cumulator(data):
    container.append([
         data['country'],
         data['station'],
         data['code'],
         data['coordinates']
    ])


def csv_writer(data):
    with open('data.csv', 'wa') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer( (data['country'],
                     data['station'],
                     data['code'],
                     data['coordinates']) )


def getting_all_done(precise_railway):

	url = URL + precise_railway['href']
	stations = get_station_list(url)

	for station in stations:
		station_url = station['href']
		info = get_page_info(station_url)
        # csv_writer(info)
		print(info)


def main():
	html = get_html(URL + '/railway/')
	railways = get_railway_list(html)

#	for precise_railway in railways:
#	 	getting_all_done(precise_railway)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(railways)) as executor:
        executor.map(getting_all_done, railways)
    	

if __name__ == '__main__':
    main()
