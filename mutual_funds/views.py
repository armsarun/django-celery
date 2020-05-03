import json

from django.db import transaction
from django.shortcuts import render
from django.views import View

from mutual_funds.models import MutualFunds, PriceData
from utils.common_utils import (
    get_data,
    get_isin_list,
    unix_date_convert,
    fetch_price_list,
    get_isin,
    verify_mutual_fund_name,
    create_json_serialize)


def index(request):
    """
    list all mutual funds .
    """
    mutual_funds = MutualFunds.objects.all()
    context = {'mutual_funds': mutual_funds}

    return render(request, 'mutual_funds/index.html', context)


class AddIsin(View):
    """
    Add new isin

    Upload single isin id

    or bulk upload from csv
    """

    def get(self, request):
        return render(request, 'mutual_funds/add_isin.html')

    def post(self, request):
        context = {}
        form_type = request.POST.get('type')
        if form_type == 'save':
            isin_number = request.POST.get('isin')
            if isin_number:
                # simply get the
                obj, created = MutualFunds.objects.get_or_create(isin=isin_number)
                obj.isin = isin_number
                obj.save()
                context['message'] = '{} uploaded successfully'.format(isin_number)
            else:
                context['message'] = "ISIN field is mandatory"
        else:
            url = request.POST.get('url')
            if url:
                response = get_data(url)
                if response:
                    isin_list = get_isin_list(response)
                    AddIsin.save_isin(isin_list)
                    message = 'upload successful'
                    context['message'] = message
                else:
                    context['message'] = 'Validate the URL again'
            else:
                context['message'] = 'URL field is mandatory'

        return render(request, 'mutual_funds/add_isin.html', context)

    @staticmethod
    def save_isin(isin_list):
        create_record_list = [MutualFunds(isin=isin) for isin in isin_list]
        with transaction.atomic():
            # integrity errors will be ignored and insert only unique isin numbers
            MutualFunds.objects.bulk_create(create_record_list, ignore_conflicts=True)


class Visualizer(View):
    """
    Visualize the given isin
    """

    def get(self, request, *args, **kwargs):

        isin_number = kwargs['isin']

        context = {'isin': json.dumps(isin_number)}

        isin_obj = get_isin(isin_number)
        price_list = PriceData.objects.filter(fk_mutual_fund=isin_obj).values('price', 'date').order_by('-date')

        if not price_list:
            # fetch price and save if it doesn't have
            response = fetch_price_list(isin_number)
            if response:
                mutual_fund_name = response['name']

                price_list = response['price_list']

                # update price data
                update_price = Visualizer.save_price(price_list, isin_number, mutual_fund_name)

                if update_price:
                    price_list = PriceData.objects.filter(fk_mutual_fund=isin_obj).values('price', 'date').order_by('-date')
                    context['data'] = create_json_serialize(price_list)
                else:
                    context['message'] = "{} doesn't have price data".format(isin_number)
            else:
                context['message'] = 'Unable to fetch price list. Please try again'
        else:

            context['data'] = create_json_serialize(price_list)

        return render(request, 'mutual_funds/visualizer.html', context)

    @staticmethod
    def save_price(datalist, isin, name):
        """
        Get the datalist and update the price
        :param datalist: (list) price and date(unix format)
        :param isin: (str) isin number
        :param name: (str) Mutual fund name
        :return: True
        """

        # Check ISIN exist
        isin_obj = get_isin(isin)

        if isin_obj:
            # update mutual_fund name
            verify_mutual_fund_name(isin_obj, name)
            price_data_list = []
            for data in datalist:
                try:
                    date_time = unix_date_convert(data[0] / 1000)
                except ValueError:
                    continue
                price_data = {
                    'fk_mutual_fund': isin_obj,
                    'date': date_time,
                    'price': data[1]
                }
                price_data_list.append(PriceData(**price_data))

            with transaction.atomic():
                PriceData.objects.bulk_create(price_data_list, ignore_conflicts=True)
            return True
        return False
