import re
import urllib3
import subprocess
import json
import yaml
from bs4 import BeautifulSoup
from datetime import datetime, timezone

def update_chartink_cookie():
    hdr =  {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"97\", \"Chromium\";v=\"97\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

    http = urllib3.PoolManager()
        
    resp1=http.request('GET', 'https://chartink.com/login', headers=hdr)

    soup = BeautifulSoup(resp1.data, 'lxml')

    csrfToken = soup.find('meta', attrs = {'name':'csrf-token'}).attrs['content']

    print(csrfToken)

    # print(datetime.today)
    # print(resp1.getheader('Set-Cookie'))
    #print('\n')
    cookies = re.search(r'(XSRF-TOKEN=.*?);.*(ci_session=.*?);.*expires=(.*?);',resp1.headers.get('Set-Cookie',''))
    print(cookies.group(1))
    print('\n')
    print(cookies.group(2))
    print('\n')
    time_exp =cookies.group(3).split(', ')[1]
    print(time_exp)
    input_time_format = "%d %b %Y %H:%M:%S %Z"
    time_obj = datetime.strptime(time_exp, input_time_format)

    # Format the datetime object into the desired format
    output_time_format = "%d-%m-%Y-%H:%M:%S"
    output_time_str = time_obj.strftime(output_time_format)

    print(output_time_str)
    with open('./ChartInkCookie.yaml') as fh:
        data = yaml.load(fh,Loader=yaml.Loader)
        
    print(data['Request'])
    data['Request']['cookie'] = '; '.join([cookies.group(1),cookies.group(2)])
    data['Request']['x-csrf-token'] = csrfToken
    data['Request']['exp_time'] = output_time_str
    print(data['Request'])

    with open('./ChartInkCookie.yaml', 'w') as fh:
        yaml.dump(data, fh)

if __name__ == "__main__":
    update_chartink_cookie()