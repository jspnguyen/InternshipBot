from bs4 import BeautifulSoup
from datetime import datetime
import requests, pytz, re

pst = pytz.timezone('America/Los_Angeles')

def githubData(page_data: requests.models.Response) -> list:
    return_list = []
    
    now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pst)
    current_date = now.strftime("%b %d")
    
    result = BeautifulSoup(page_data.text, 'lxml')
    table_data = str(result.find("table"))

    table_data = githubClean(table_data)

    for entry in table_data:
        job_data = entry.split("<td>")
        if job_data[-1] == current_date:
            link_split = job_data[4].split('"')
            
            location_split = locationClean(job_data[3])
            
            role_title = job_data[2]
            if len(location_split) == 1:
                location_title = location_split[0]
            else:
                location_string = ""
                for i in range(1, len(location_split)):
                    if i == len(location_split) - 1:
                        location_string += location_split[i]
                    else:
                        location_string += location_split[i] + ", "
                location_title = location_string
            app_link = link_split[1]
            date_posted = job_data[5]
            
            return_list.append([role_title, location_title, app_link, date_posted])
    return return_list

def githubClean(table_data: str) -> list:
    pattern = re.compile(r"</(tr|tbody|table|td)>")
    
    clean_data = pattern.sub("", table_data)
    
    table_data_clean = [row.strip() for row in clean_data.split("<tr>") if row]
    
    return table_data_clean

def locationClean(location_data: str) -> list:
    tags_to_remove = re.compile(r"<details><summary><strong>|</strong></summary>|</details>")
    tags_to_replace_with_slash = re.compile(r"<br/>")

    clean_data = tags_to_remove.sub("", location_data)
    clean_data = tags_to_replace_with_slash.sub("/", clean_data)

    location_split = list(filter(None, clean_data.split('/')))

    location_split = [element.strip() for element in location_split]

    return location_split