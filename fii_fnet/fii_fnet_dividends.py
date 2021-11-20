# import unicodedata
# from kora.selenium import wd
# from bs4 import BeautifulSoup
from datetime import datetime
from calendar import monthrange
from flask.wrappers import Response
from urllib.parse import urlencode, quote_plus
from flask import Blueprint, jsonify, request
import html
import requests

# Get the list of documents from FNET
# Return the HTML in a JSON

# Builds the Blueprint for fii_fnet_dividend
fii_fnet_dividend = Blueprint('fii_fnet_dividend', __name__)

def search_fnet_dividends_report(cnpj:str, period:str) -> dict:
    """
        Uses the FNET API to search for the documents published by a fund.
        It returns the HTML that is returned by the WebDriver
    """
    # API parameters
    type = 1 #tipoFundo
    category = 14 #idCategoriaDocumento
    doc_type = 41 #idTipoDocumento
    doc_subtype = 0 #idEspecieDocumento
    status = 'A' #situacao
    cnpj = cnpj #cnpj

    # The date must be urlencoded so the API filter works
    month = period[0:2]
    year = period[2:]
    last_day = monthrange(int(year), int(month))[1]
    period_encode_key = {"dataInicial": F"01/{month}/{year}", "dataFinal": F"{last_day}/{month}/{year}"}
    period_encoded = urlencode(period_encode_key, quote_via=quote_plus) #dataReferencia

    #https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=4&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&tipoFundo=1&idCategoriaDocumento=14&idTipoDocumento=41&idEspecieDocumento=0&situacao=A&cnpj=11664201000100&dataReferencia=07%2F2021
    #https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=22&s=0&l=10&tipoFundo=1&idCategoriaDocumento=14&idTipoDocumento=41&idEspecieDocumento=0&situacao=A&cnpj=11664201000100&dataReferencia=07%2F2021


    # Base URL
    # example https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=22&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&tipoFundo=1&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&situacao=A&cnpj=37087810000137&dataReferencia=06%2F2021&_=1628987139815
    base_url = (f'http://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=22'
        f'&s=0&l=24'
        f'&tipoFundo={type}'
        f'&idCategoriaDocumento={category}'
        f'&idTipoDocumento={doc_type}'
        f'&idEspecieDocumento={doc_subtype}'
        f'&situacao={status}'
        f'&cnpj={cnpj}'
        f'&{period_encoded}')
    print(base_url)

    # wd.get(base_url)
    # data = wd.page_source

    resp = requests.get(base_url)
    data = resp.json()
    # print(data)  

    return data

def get_fnet_doc_content(id:str) -> str:
    """Searches for the doc in FNET using the id and return the page HTML"""

    url = f'http://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={id}&cvm=true'

    headers = {
        'Accept': 'text/html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    }
    # wd.get(url)
    # html = wd.page_source

    resp = requests.get(url, headers=headers)
    # html = unicodedata.normalize('NFKD', html).encode('ASCII', 'ignore').decode('UTF-8')

    # Using html unescape instead of the normalize function to replace the special chars in the page
    html_text = html.unescape(resp.text)
    return html_text

@fii_fnet_dividend.route("/dividends")
def get_dividend_report_root():
    return "Usage /dividendss/CNPJ?period=MMYYYY"

@fii_fnet_dividend.route("/dividends/<cnpj>")
def get_dividend_report(cnpj: str) -> Response:
    """
    Receives the CNPJ of a fund and the URL query parameter period=MMYYY
    Returns a JSON with ALL the dividends docs found for the fund given and their HTMLs
    """

    default_period = F"{str(datetime.now().month).zfill(2)}{datetime.now().year}"
    period = request.args.get('period', default=default_period, type=str)

    print(period)
    print(cnpj)

    if len(period) != 6:
        out = {
            'status_code': 400,
            'msg': F'Invalid period (MMYYYY) provided: {period}',
            'error': True,
            'data': [],
        }
        resp = jsonify(out)
        resp.status_code = 400
        return resp

    docs = search_fnet_dividends_report(cnpj, period)

    if docs["recordsTotal"] == 0:
        out = {
            'status_code': 404,
            'msg': f'Could not find any monthly report for {cnpj} on {period}',
            'error': True,
            'recordsTotal': docs['recordsTotal'],
            'data': [],
        }
        resp = jsonify(out)
        resp.status_code = 404
        return resp

    # docs_content is a list of jsons with the ID and the html content of each document found
    docs_content = [ 
        {
            'doc_id': doc['id'],
            'html': get_fnet_doc_content(doc['id']),
        }
        for doc in docs['data']
    ]

    data = {
        'cnpj': cnpj,
        'period': period,
        'docs': docs_content,
    }

    out = {
        'status_code': 200,
        'msg': 'ok',
        'error': False,
        'recordsTotal': docs['recordsTotal'],
        'data': data,
    }

    resp = jsonify(out)
    resp.status_code = 200

    return resp
