from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests, pytz, re

pst = pytz.timezone('America/Los_Angeles')

def githubData(page_data: requests.models.Response, timeframe: int) -> list:
    return_list = []
    
    search_dates = []
    now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pst)

    if timeframe == 1:
        for i in range(7):
            date = now - timedelta(days=i)
            formatted_date = date.strftime("%b %d")
            search_dates.append(formatted_date)
    else:
        search_dates.append(now.strftime("%b %d"))
    
    result = BeautifulSoup(page_data.text, 'lxml')
    table_data = str(result.find("table"))

    table_data = githubClean(table_data)

    prev_company_name = ""
    
    for entry in table_data:
        job_data = entry.split("<td>")
        if job_data[-1] in search_dates:
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
                
            try:
                app_link = link_split[1]
            except: 
                app_link = "LOCKED"
            date_posted = job_data[5]
            
            if "href" in job_data[1]:
                match = re.search(r'rel="nofollow">(.*?)</a>', job_data[1])
                company_name = match.group(1)
                prev_company_name = company_name
            elif "↳" in job_data[1]:
                company_name = prev_company_name
            else:
                company_name = job_data[1]
                prev_company_name = company_name
            
            return_list.append([role_title, location_title, app_link, date_posted, company_name])
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