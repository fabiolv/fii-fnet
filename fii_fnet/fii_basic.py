from flask.wrappers import Response
import requests
import unicodedata
from flask import jsonify, Blueprint
from bs4 import BeautifulSoup
from kora.selenium import wd

# Builds the Blueprint for fii_basic
fii_basic = Blueprint('fii_basic', __name__)

@fii_basic.route('/testkora/<id>')
def kora(id):
    url = F'http://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={id}&cvm=true'

    wd.get(url)

    print(f'Document id {id}')
    print(url)
    print(wd.page_source)

    return wd.page_source

def get_data_from_web(ticker):
    url = f'https://www.fundsexplorer.com.br/funds/{ticker}'

    # Get the html
    html = requests.get(url)

    return html

def error_out(status_code: int, msg: str):
    out = dict()

    out['status_code'] = status_code
    out['msg'] = msg
    out['error'] = True
    out['data'] = {}

    resp = jsonify(out)
    resp.status_code = status_code

    return resp

@fii_basic.route('/fiis/<ticker>')
def get_fii_info(ticker: str):
    param_ticker = ticker.upper()

    fii = {
        'ticker': '',
        'name': '',
        'cnpj': ''
    }

    out = {
        'status_code': 0,
        'msg': None,
        'error': None,
        'data': {},
    }

    if param_ticker == '':
        out['status_code'] = 400
        out['msg'] = 'Ticker not provided'
        out['error'] = True
        resp = jsonify(out)
        resp.status_code = 400
        return resp
        
    html = get_data_from_web(param_ticker)

    if html.status_code != 200:
        return error_out(html.status_code, f'Error while retrieveing the ticker {param_ticker}')

    # Create the BS4 object from the HTML
    parser = 'html.parser'
    soup = BeautifulSoup(html.content, parser)

    # Use CSS selector to the the DIV with ID basic-infos
    basic_div = soup.select_one('#basic-infos')
    if basic_div is None:
        return error_out(400, f'Error while retrieving the basic info of the ticker {param_ticker} from {html.url}')

    # Look for the name of the FII
    name_span = basic_div.find('span', text='Razão Social')
    # The next element will be the description one
    name_span_value = name_span.find_next('span', {'class': 'description'}).get_text().strip()
    # Remove the special chars from the FII name
    # TODO: Need to find a better way to do it...
    name_span_value = unicodedata.normalize('NFKD', name_span_value).encode('ASCII', 'ignore').decode('UTF-8')
    
    # Look for the span with text CNPJ
    cnpj_span = basic_div.find('span', text='CNPJ')
    cnpj_span_value = cnpj_span.find_next('span', {'class': 'description'}).get_text().strip()

    fii['ticker'] = param_ticker.upper()
    fii['name'] = name_span_value.upper()
    fii['cnpj'] = cnpj_span_value

    out['status_code'] = 200
    out['msg'] = 'ok'
    out['error'] = False
    out['data'] = fii

    # print(unicodedata.normalize('NFKD', name_span_value).encode('ASCII', 'ignore').decode('UTF-8'))

    resp = jsonify(out)
    resp.status_code = 200
    return resp

@fii_basic.route('/quote/<ticker>')
def quote(ticker):
    if ticker == '':
        return jsonify({'msg': 'Ticker not provided'})
    
    url = f'https://yfstocks.herokuapp.com/quote/{ticker}?format=JSON&debug=1'
    resp = requests.get(url)
    return resp.json()

@fii_basic.route('/fiis')
def root():
    print('Request for /fiis')
    return jsonify({'msg': 'Usage /fiis/<TICKER>'})