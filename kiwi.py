import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import requests
from fastapi import HTTPException


def get_cheapest_flights(fly_from: str, fly_to: str, dep_date: date = None) -> dict:
    """Returns the cheapest tickets for a range of dates based on locations"""
    url_flights = 'https://api.skypicker.com/flights'
    currency = 'KZT'

    payload = {'flyFrom': fly_from, 'to': fly_to, 'partner': 'picky', 'curr': currency}

    if dep_date is None:
        date_from = datetime.today().strftime('%d/%m/%Y')
        date_to = (datetime.today() + relativedelta(months=1)).strftime('%d/%m/%Y')
        payload['dateFrom'] = date_from
        payload['dateTo'] = date_to
    else:
        payload['dateFrom'] = dep_date.strftime('%d/%m/%Y')
        payload['dateTo'] = dep_date.strftime('%d/%m/%Y')

    r = requests.get(url_flights, params=payload)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    returned_json = r.json()
    data_list = returned_json['data']
    prices_dict = dict()
    for data in data_list:
        curr_price = data['price']
        timestamp = data['dTimeUTC']
        booking_token = data['booking_token']
        curr_date = datetime.fromtimestamp(timestamp).date()
        curr_date_str = curr_date.strftime('%Y-%m-%d')
        if curr_date_str not in prices_dict:
            prices_dict[curr_date_str] = (curr_price, booking_token, fly_from, fly_to, curr_date)

    return prices_dict


def check_flight_ticket(booking_token: str, currency: str = 'KZT', passenger_num: int = 1) -> dict:
    """Returns information about the ticket, its validity and price change, i.e. verifies the ticket
    waits until the ticket is checked(limit:5 min) as per API"""
    url = 'https://booking-api.skypicker.com/api/v0.1/check_flights'
    baggage_num = 1
    retry_timer = 5
    retry_limit = 300
    payload = {'v': 2, 'booking_token': booking_token, 'bnum': baggage_num, 'pnum': passenger_num, 'currency': currency}

    r = requests.get(url, params=payload)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    returned_json = r.json()
    is_checked = returned_json['flights_checked']
    is_invalid = returned_json['flights_invalid']

    while not is_checked and retry_timer < retry_limit:
        time.sleep(retry_timer)
        r = requests.get(url, params=payload)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        is_invalid = r.json()['flights_invalid']
        is_checked = r.json()['flights_checked']
        retry_timer += 10
    is_price_changed = returned_json['price_change']
    price = returned_json['tickets_price']
    orig_price = returned_json['orig_price']
    conversion_price = returned_json['conversion']['amount']
    currency = returned_json['currency']
    dict_ticket = {'is_invalid': is_invalid, 'is_price_changed': is_price_changed, 'price': price,
                   'orig_price': orig_price, 'currency': currency, 'conversion_price': conversion_price}
    return dict_ticket


get_cheapest_flights('TSE', 'ALA', datetime.strptime('Dec 25 2019', '%b %d %Y').date())
