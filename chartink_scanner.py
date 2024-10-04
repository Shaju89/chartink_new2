import os
import sys
import yfinance as yf
import yaml
import json
import traceback
from urllib.parse import quote_plus
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timezone
from ChartInkCookie import update_chartink_cookie

url = 'https://chartink.com/screener/process'

script_dir = os.path.dirname(os.path.abspath(__file__))

# Join the script directory with the filename
config_path = os.path.join(script_dir, 'ChartInkCookie.yaml')

# Load the config using the full path

with open(config_path) as f:
    req_hdr = yaml.load(f, Loader=yaml.FullLoader)['Request']

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-csrf-token": req_hdr['x-csrf-token'],
    "x-requested-with": "XMLHttpRequest",
    "cookie": req_hdr['cookie']
  }

def get_post_response(url, data, hdr):
    # print(data)
    # print(hdr)
    urllib3.disable_warnings(InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    return http.request('POST', url, headers=hdr, body=data)

def get_url_encode(x):
    # print(x)
    return quote_plus(x).replace('%28','(').replace('%29',')').replace('%2A','*').replace('%2A','*').replace('%3A+','=')

def get_dow_change():
    # Fetch data for the Dow Jones Industrial Average
    dow = yf.Ticker("^DJI")
    
    # Get historical market data (last 2 days)
    hist = dow.history(period="5d")
    return round(((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100,3)

# Function to clear IntraDayCandles.json
def clear_intraday_candles():
    print('Clearing IntraDayCandles.json ...')
    data = {"candles": []}
    with open('./IntraDayCandles.json', 'w') as file:
        json.dump(data, file, indent=4)

# Function to update IntraDayCandles.json
def update_intraday_candles(response, action):
    # print(response)
    try:
        with open('./IntraDayCandles.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"candles": []}

    for entry in response:     
        # print(f"Entry: {entry}")   
        scrip = entry.get('nsecode')        
        name = entry.get('name')
        per_chg = entry.get('per_chg')
        close = entry.get('close')
        volume = entry.get('volume')
        if scrip and name and per_chg and close and volume:            
            data["candles"].append({
                "Scrip": scrip,
                "Action": action,
                "Name": name,
                "PerChg": per_chg,
                "Close": close,
                "Volume": volume
            })
    # print(f"Data: {data}")
    with open('./IntraDayCandles.json', 'w') as file:
        json.dump(data, file, indent=4)

result = {}

prev_ss_15m_red = lambda x:'scan_clause: ( {57960}'+'( [={0}] 15 minute close < [={0}] 15 minute open and( {0} day ago high - greatest(  {0} day ago open, {0} day ago close  ) ) >= abs( {0} day ago close - {0} day ago open ) * 2.5 and( least(  {0} day ago open, {0} day ago close  ) - {0} day ago low ) <= abs( {0} day ago open - {0} day ago close ) * 0.3 ) )'.format(x)
prev_hammer_15m_green = lambda x:'scan_clause: ( {57960}'+'( [={0}] 15 minute close > [={0}] 15 minute open and ( least(  {0} day ago open, {0} day ago close  ) - {0} day ago low ) >= abs( {0} day ago close - {0} day ago open ) * 2.5 and {0} day ago high - ( greatest( {0} day ago open, {0} day ago close  ) ) <= abs( {0} day ago open - {0} day ago close ) * 0.3 ) )'.format(x)

def run_scanner():
    clear_intraday_candles()
    with open('./ChartInkCookie.yaml') as fh:
        data = yaml.load(fh, Loader=yaml.Loader)
    time_now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    time_exp = data['Request']['exp_time']
    # Parse the given time string into a datetime object
    given_time_format = "%d-%m-%Y-%H:%M:%S"
    exp_time = datetime.strptime(time_exp, given_time_format)

    # Get the current GMT time and parse it into a datetime object
    current_gmt_time_str = datetime.now(timezone.utc).strftime(given_time_format)
    current_gmt_time = datetime.strptime(current_gmt_time_str, given_time_format)

    if exp_time <= current_gmt_time:
        print(f'{exp_time=}')
        print(f"{current_gmt_time=}")
        print('updating cookie ....')
        update_chartink_cookie()
    else:
        print("Cookie hasn't been expired yet")

    with open('./ChartInkCookie.yaml') as fh:
        data = yaml.load(fh, Loader=yaml.Loader)

    print("Chartink Scanner is running...")

    time_now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    time_exp = data['Request']['exp_time']

    try:
        response = get_post_response(url, get_url_encode(prev_ss_15m_red(1)), headers)
        resp_ss = json.loads(response.data)['data']
        update_intraday_candles(resp_ss, 'SELL')
    
        response = get_post_response(url, get_url_encode(prev_hammer_15m_green(1)), headers)
        resp_hamm = json.loads(response.data)['data']

        update_intraday_candles(resp_hamm, 'BUY')
        return "run_scanner : Success"
    except Exception as e:
        print(f"Error processing BUY data: {e}")
        return f"Run_scanner : Fail -> {str(e)}"

if __name__ == '__main__':
    try:                
        print(run_scanner())
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()