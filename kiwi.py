import time
from datetime import datetime, date

import requests
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException


class PriceInfo:
    def __init__(self, price, booking_token, dep_loc, arr_loc, flight_date):
        self.price = price
        self.booking_token = booking_token
        self.dep_loc = dep_loc
        self.arr_loc = arr_loc
        self.flight_date = flight_date


def get_cheapest_flights(dep_loc: str, arr_loc: str, dep_date: date = None) -> dict:
    """Returns the cheapest tickets for a range of dates based on locations"""
    url = 'https://api.skypicker.com/flights'
    payload = {
        'flyFrom': dep_loc,
        'to': arr_loc,
        'partner': 'picky',
        'curr': 'KZT'
    }
    prices_data = dict()

    if dep_date is None:
        date_from = datetime.today().strftime('%d/%m/%Y')
        date_to = (datetime.today() + relativedelta(months=1)).strftime('%d/%m/%Y')
        payload['dateFrom'] = date_from
        payload['dateTo'] = date_to
    else:
        payload['dateFrom'] = dep_date.strftime('%d/%m/%Y')
        payload['dateTo'] = dep_date.strftime('%d/%m/%Y')

    returned_json = get_response_json(url, payload)
    data_list = returned_json['data']

    for data in data_list:
        timestamp = data['dTimeUTC']
        curr_date = datetime.fromtimestamp(timestamp).date()
        curr_date_str = curr_date.strftime('%Y-%m-%d')

        if curr_date_str not in prices_data:
            prices_data[curr_date_str] = PriceInfo(data['price'], data['booking_token'], dep_loc, arr_loc, curr_date)

    return prices_data


def check_flight_ticket(booking_token: str, currency: str = 'KZT', passenger_num: int = 1) -> dict:
    """Returns information about the ticket, its validity and price change, i.e. verifies the ticket,
    waits until the ticket is checked(limit:5 min) as per API spec"""
    url = 'https://booking-api.skypicker.com/api/v0.1/check_flights'
    retry_timer, retry_limit = 5, 300
    payload = {
        'v': 2,
        'booking_token': booking_token,
        'bnum': 1,
        'pnum': passenger_num,
        'currency': currency
    }

    returned_json = get_response_json(url, payload)

    is_checked = returned_json['flights_checked']

    while not is_checked and retry_timer < retry_limit:
        time.sleep(retry_timer)
        returned_json = get_response_json(url, payload)
        is_checked = returned_json['flights_checked']
        retry_timer += 10

    return {
        'is_invalid': returned_json['flights_invalid'],
        'is_price_changed': returned_json['price_change'],
        'price': returned_json['tickets_price'],
        'orig_price': returned_json['orig_price'],
        'currency': returned_json['currency'],
        'conversion_price': returned_json['conversion']['amount']
    }


def get_response_json(url, payload):
    r = requests.get(url, params=payload)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return r.json()
