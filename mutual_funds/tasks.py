from core.celery_config import app
from mutual_funds.models import MutualFunds, PriceData
from utils.common_utils import get_data, get_isin_list, fetch_price_list, get_isin
from utils.constant import ISIN_URL
from mutual_funds.views import AddIsin, Visualizer


@app.task
def fetch_isin():
    """
    fetch isin and save it database
    :return:None
    """
    print('Started fetching ISIN list.....')
    response = get_data(ISIN_URL)
    if response:
        isin_list = get_isin_list(response)
        AddIsin.save_isin(isin_list)
        print('Created new ISIN ')
    else:
        print('Response Timeout {}'.format(ISIN_URL))


@app.task()
def fetch_price_data():
    """
    fetch the price list and store to database
    if price list already available fetch only last one
    :return: None
    """
    print('Fetching price Data ')
    isin_list = MutualFunds.objects.all().values_list('isin')
    for isin in isin_list:
        isin_number = isin[0]
        validate = PriceData.objects.filter(fk_mutual_fund__isin=isin_number)
        response = fetch_price_list(isin_number)
        if response and validate:
            print('Fetching latest price for {}'.format(isin_number))
            """
                created based assumption:
                If price list already available then it need to update
                only the latest single date.
                Hope Price list api will update one price data in 24 hours.
            """
            # fetch only the last and save to price list
            isin_obj = get_isin(isin_number)
            price_list = response['price_list'][-1]
            if isin_obj:
                data = {
                    'fk_mutual_fund': isin_obj,
                    'date': price_list[0],
                    'price': price_list[1]
                }
                try:
                    PriceData.objects.create(**data)
                except Exception as e:
                    print(e)
                    continue
        elif response:
            print('Fetching Complete price data'.format(isin_number))
            # if price list not available
            mutual_fund_name = response['name']
            price_list = response['price_list']
            Visualizer.save_price(price_list, isin_number, mutual_fund_name)

        else:
            # if response is 400
            print('failed response {}'.format(isin_number))
            continue


