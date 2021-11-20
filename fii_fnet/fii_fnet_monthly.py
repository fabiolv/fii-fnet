# import unicodedata
# from kora.selenium import wd
# from bs4 import BeautifulSoup
# import json
from datetime import datetime
from flask.wrappers import Response
from urllib.parse import urlencode, quote_plus
import requests
from flask import Blueprint, jsonify, request
import html

# Builds the Blueprint for fii_fnet_monthly
fii_fnet_monthly = Blueprint('fii_fnet_monthly', __name__)

def search_fnet_monthly_report(cnpj:str, period:str) -> dict:
    """
        Uses the FNET API to search for the documents published by a fund.
        It returns the HTML that is returned by the WebDriver
    """
    # API parameters
    type = 1 #tipoFundo
    category = 6 #idCategoriaDocumento
    doc_type = 40 #idTipoDocumento
    doc_subtype = 0 #idEspecieDocumento
    status = 'A' #situacao
    cnpj = cnpj #cnpj

    # The date must be urlencoded so the API filter works
    month = period[0:2]
    year = period[2:]
    period_encode_key = {"dataReferencia": F"{month}/{year}"}
    period_encoded = urlencode(period_encode_key, quote_via=quote_plus) #dataReferencia

    # Base URL
    # example https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=22&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&tipoFundo=1&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&situacao=A&cnpj=37087810000137&dataReferencia=06%2F2021&_=1628987139815
    # 2021-11-20 - Using the HTTP URL instead of the HTTPS so we don't need to use Kora/Selenium to call the API
    base_url = (f'http://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=22'
        f'&s=0&l=10'
        f'&tipoFundo={type}'
        f'&idCategoriaDocumento={category}'
        f'&idTipoDocumento={doc_type}'
        f'&idEspecieDocumento={doc_subtype}'
        f'&situacao={status}'
        f'&cnpj={cnpj}'
        f'&{period_encoded}')

    resp = requests.get(base_url)
    # wd.get(base_url)

    # data = wd.page_source
    data = resp.json()
    print(base_url)
    print(data)  

    return data

# def parse_html(html: str) -> dict:
#     """Using BeautifulSoup, parses the HTML returned from Kora and creates a dict"""
#     soup = BeautifulSoup(html, 'html.parser')

#     print('parse html...')

#     data = json.loads(soup.text)
#     print(data)

#     return data

def get_fnet_doc_content(id:str) -> str:
    """Searches for the doc in FNET using the id and return the page HTML"""

    headers = {
        'Accept': 'text/html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    }

    url = f'http://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={id}&cvm=true'

    # wd.get(url)
    # html = wd.page_source

    resp = requests.get(url, headers=headers)
    html_text = resp.text

    # Using the html unescape instead of the normalize function to convert the non-standard chars
    # html = unicodedata.normalize('NFKD', html).encode('ASCII', 'ignore').decode('UTF-8')
    html_text = html.unescape(html_text)

    return html_text

@fii_fnet_monthly.route("/monthlyreports")
def get_monthly_report_root():
    return "Usage /monthlyreports/CNPJ?period=MMYYYY"

@fii_fnet_monthly.route("/monthlyreports/<cnpj>")
def get_monthly_report(cnpj: str) -> Response:
    """
    Receives the CNPJ of a fund and the URL query parameter period=MMYYY
    Returns a JSON with the HTML of the monthly report of the fund.
    """
    
    default_period = f'{str(datetime.now().month).zfill(2)}{datetime.now().year}'
    period = request.args.get('period', default=default_period, type=str)

    print(period)
    print(cnpj)

    if len(period) != 6:
        out = {
            'status_code': 400,
            'msg': f'Invalid period (MMYYYY) provided: {period}',
            'error': True,
            'data': [],
        }
        resp = jsonify(out)
        resp.status_code = 400
        return resp

    docs = search_fnet_monthly_report(cnpj, period)

    # docs = parse_html(html_docs)

    if docs["recordsFiltered"] != 1 or docs["recordsTotal"] == 0:
        out = {
            'status_code': 404,
            'msg': f"Could not get the monthly report for {cnpj} on {period}. FNET API returned: recordsTotal: {docs['recordsTotal']}, recordsFiltered: {docs['recordsFiltered']}",
            'error': True,
            'data': {},
        }
        resp = jsonify(out)
        resp.status_code = 404
        return resp

    doc_id = docs["data"][0]["id"]
    doc_html = get_fnet_doc_content(doc_id)

    data = {
        "cnpj": cnpj,
        "period": period,
        "doc": doc_id,
        "html": doc_html
    }
    out = {
        'status_code': 200,
        'msg': "ok",
        'error': False,
        'data': data,
    }

    resp = jsonify(out)
    resp.status_code = 200

    return resp
