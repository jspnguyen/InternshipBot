from bs4 import BeautifulSoup
from datetime import datetime
import requests, pytz

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
    table_data = table_data.replace("</tr>", "")
    table_data = table_data.replace("</tbody>", "")
    table_data = table_data.replace("</table>", "")
    table_data = table_data.replace("</td>", "")
    table_data = table_data.replace("\n", "")
    table_data = table_data.split("<tr>")
    
    return table_data

def locationClean(location_data: str) -> list:
    location_split = location_data.replace("<details><summary><strong>", "")
    location_split = location_split.replace("</details>", " ")
    location_split = location_split.replace("</strong></summary>", "/")
    location_split = location_split.replace("<br/>", "/")
    location_split = location_split.split("/")
    
    return location_split