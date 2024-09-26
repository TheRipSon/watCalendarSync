# schedule_fetcher.py

import requests
from bs4 import BeautifulSoup
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the InsecureRequestWarning from urllib3
warnings.simplefilter('ignore', InsecureRequestWarning)

def fetch_schedule(url):
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        blocks = soup.find_all('div', class_='block_nr')

        block_info = {}
        for block in blocks:
            block_id = f"block{block.find('span', class_='nr').text.strip()}"
            hr1 = block.find('span', class_='hr1').text.strip()
            hr2 = block.find('span', class_='hr2').text.strip()
            block_info[block_id] = (hr1, hr2)

        lessons = []
        lessons_div = soup.find_all('div', class_='lesson')

        for lesson in lessons_div:
            date = lesson.find('span', class_='date').text.strip()
            name = lesson.find('span', class_='name').text.strip()
            info = lesson.find('span', class_='info').text.strip()
            block_id = lesson.find('span', class_='block_id').text.strip()

            if block_id in block_info:
                start_time, end_time = block_info[block_id]
                lessons.append({
                    'summary': name,
                    'description': info,  # Optional
                    'location': None,  # Optional: None if no location
                    'start': {
                        'dateTime': f"{date.replace('_', '-') }T{start_time}:00",  # Corrected format
                        'timeZone': 'Europe/Warsaw',
                    },
                    'end': {
                        'dateTime': f"{date.replace('_', '-') }T{end_time}:00",  # Corrected format
                        'timeZone': 'Europe/Warsaw',
                    },
                })
                print("Formatted start time:", f"{date.replace('_', '-') }T{start_time}:00")
                print("Formatted end time:", f"{date.replace('_', '-') }T{end_time}:00")

            else:
                print(f"Block ID {block_id} not found in block information.")

        return lessons
    else:
        print(f"Failed to retrieve the schedule, status code: {response.status_code}")
        return []
    
def fetch_update_time(url):
    response = requests.get(url,verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    update_time_span = soup.find("span", class_="head_info")
    if update_time_span:
        update_time_text = update_time_span.get_text()
        print(update_time_text)
        update_time = update_time_text.split("i:")[1]
        return update_time
    return None