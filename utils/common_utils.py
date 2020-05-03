import json
import requests
from json import JSONDecodeError
from datetime import datetime

from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from requests.adapters import HTTPAdapter

from mutual_funds.models import MutualFunds
from utils.constant import PRICE_FETCH_URL


def get_data(url):
    """
    fetch the data from given url
    :param url: url to get result
    :return: response text
    """
    try:
        requests.adapters.DEFAULT_RETRIES = 5
        response = requests.get(url)

    except Exception as e:
        return False

    else:
        return response.text


def get_isin_list(data):
    """
    Get the response data and return the isin list
    :param data:(text, json) data
    :return: (list) ISIN list
    """
    if isinstance(data, str):
        return data.split('\r\n')
    try:
        json_data = json.loads(data)
        return json_data
    except ValueError:
        raise Exception('Except text/JSON data')


def verify_response(data):
    """
    verify json response of the price list data
    :param data: (json) price list or error
    :return: date and price list
    """
    try:
        return json.loads(data)
    except JSONDecodeError:
        return False


def unix_date_convert(data):
    """
    convet the unix date time to human readable
    :param data: (list)
    :return: datetime object
    """
    return datetime.fromtimestamp(data)


def fetch_price_list(isin):
    """
    Fetch the price list for given isin

    :param isin: (str) unique isin number
    :return: date and price
    """
    isin_url = PRICE_FETCH_URL + str(isin)
    result = get_data(isin_url)
    # Hope API returns JSON every-time so no validation
    is_success = verify_response(result)
    response = is_success['pfwresponse']
    if response['status_code'] == 200:
        fund_info = response['result']['fundinfo']
        price_list = fund_info['graph_data_for_amfi']
        name = fund_info['legal_name']
        return {'price_list': price_list, 'name': name}

    return False


def get_isin(isin):
    """
    helper method to get isn from db
    :param isin: (int) isin number
    :return: Mutual fund object
    """
    try:
        return MutualFunds.objects.get(isin=isin)
    except ObjectDoesNotExist:
        return False


def verify_mutual_fund_name(isin_obj, name):
    """

    :param isin_obj:  Mutual_Fund object
    :param name: (str) Mutual fund Name
    :return: True
    """

    if not isinstance(isin_obj, MutualFunds):
        return

    if name != isin_obj.name:
        isin_obj.name = name
        isin_obj.save()
        return True


def create_json_serialize(queryset, encoder=DjangoJSONEncoder):
    """
    Serialize the django queryset for chart
    :param queryset: django queryset
    :param encoder: type of json encoder
    :return: json object
    """
    if isinstance(queryset, QuerySet):

        data = [{'x': query['date'].date().strftime('%d-%m-%Y'), 'y': query['price']} for query in queryset]
        # cls to serialize the django datetime object
        return json.dumps(data, cls=DjangoJSONEncoder)

    return json.dumps(False)
