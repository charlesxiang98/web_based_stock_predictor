# coding:utf-8

def get_stock_symbols():
    symbol_file = open("stock_symbols.txt", "r")
    symbol = symbol_file.read().split(',')
    return symbol

def get_api_key():
    with open('api_key.txt', 'r') as f2:
        api_key = f2.readlines()
        api_key = ','.join(api_key).replace(' ','')
        return api_key

if __name__ == '__main__':
    print(get_stock_symbols())
    print(get_api_key())
