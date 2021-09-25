'''

Anton Wang wrote it.
wangad AT connect.hku.hk

'''

import os
import numpy as np
import urllib.request
import xml.etree.ElementTree as ET
import argparse

web_path0 = "https://data.binance.vision/"
data_info_path = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix="

parser = argparse.ArgumentParser(description='Used to download binance public data from '+web_path0)
parser.add_argument('--spot_or_futures', default='spot', type=str,
                        help='to download spot or future, input \'spot\' for spot and \'futures\' for future')
parser.add_argument('--coin_m_or_usdt_m_for_future', default='um', type=str,
                        help='coin-margined: cm, usdt-margined: um')
parser.add_argument('--data_type', default='klines', type=str,
                        help='data_type: klines, trades, aggTrades, ...')
parser.add_argument('--crypto_type', default='BTC', type=str,
                        help='crypto_type')
parser.add_argument('--delta_time', default="1m", type=str,
                        help='resolution of the crypto data')
parser.add_argument('--output_path', default="data", type=str,
                        help='path to save the data')
args = parser.parse_args()

assert args.spot_or_future == "spot" or args.spot_or_future == "futures"
assert args.coin_m_or_usdt_m_for_future == "cm" or args.coin_m_or_usdt_m_for_future == "um"

def getResponse(url):
    operUrl = urllib.request.urlopen(url)
    if(operUrl.getcode()==200):
        data = operUrl.read()
    else:
        print("Error receiving data", operUrl.getcode())
    return data

if args.spot_or_future == "spot":
    path = "data/" + args.spot_or_future + "/daily/"
else:
    path = "data/" + args.spot_or_future + "/" + args.coin_m_or_usdt_m_for_future + "/daily/"

print("show all data type in "+path)
print("--------------------------------------------------")
response = getResponse(data_info_path+path)
things_from_the_webpage = ET.fromstring(response)
for i in things_from_the_webpage.iter():
    if "Prefix" in i.tag and i.text is not None:
        print(i.text)
print("--------------------------------------------------")

if args.spot_or_future == "spot":
    path = "data/" + args.spot_or_future + "/daily/" + args.data_type + "/"
else:
    path = "data/" + args.spot_or_future + "/" + args.coin_m_or_usdt_m_for_future + "/daily/" + args.data_type + "/"

print("show all crypto type in "+path)
print("--------------------------------------------------")
response = getResponse(data_info_path+path)
things_from_the_webpage = ET.fromstring(response)
for i in things_from_the_webpage.iter():
    if "Prefix" in i.tag and i.text is not None:
        print(i.text)
print("--------------------------------------------------")

def get_all_related_symbols(path, symbol):
    info = getResponse(data_info_path+path)
    info_tree = ET.fromstring(info)
    related_symbols = []
    for item in info_tree.iter():
        if "Prefix" in item.tag and \
        item.text is not None and \
        item.text.split("/")[-2] != path.split("/")[-2] and \
        symbol in item.text.split("/")[-2]:
            related_symbols.append(item.text.split("/")[-2])
    
    return related_symbols

related_symbols = get_all_related_symbols(path, args.crypto_type)

for related_symbol in related_symbols:
    if args.spot_or_future == "spot":
        path = "data/" + args.spot_or_future + "/daily/" + args.data_type + "/" + related_symbol + "/"
    else:
        path = "data/" + args.spot_or_future + "/" + args.coin_m_or_usdt_m_for_future + "/daily/" + args.data_type + "/" + related_symbol + "/"

    print("show all delta time for "+str(related_symbol))
    print("--------------------------------------------------")
    response = getResponse(data_info_path+path)
    things_from_the_webpage = ET.fromstring(response)
    for i in things_from_the_webpage.iter():
        if "Prefix" in i.tag and i.text is not None:
            print(i.text)
    print("--------------------------------------------------")

    if args.spot_or_future == "spot":
        path = "data/" + args.spot_or_future + "/daily/" + args.data_type + "/" + related_symbol + "/" + args.delta_time + "/"
    else:
        path = "data/" + args.spot_or_future + "/" + args.coin_m_or_usdt_m_for_future + "/daily/" + args.data_type + "/" + related_symbol + "/" + args.delta_time + "/"
        
    print("in "+path)
    response = getResponse(data_info_path+path)
    things_from_the_webpage = ET.fromstring(response)
    flag = False
    for i in things_from_the_webpage.iter():
        if "Key" in i.tag and i.text.split(".")[-1] == "zip":
            print(i.text)
            flag = True
            break

    if flag:
        print("download")
        if not os.path.exists(args.output_path+"/"+path):
            os.makedirs(args.output_path+"/"+path)
        for i in things_from_the_webpage.iter():
            if "Key" in i.tag and i.text.split(".")[-1] == "zip":
                string = "wget "+web_path0+i.text+" -P "+args.output_path+"/"+path
                print(string)
                os.system(string)
    else:
        print("no data")
