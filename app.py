import requests, json, sys


class Updater:
    markers = 'ABCDEFGHIJKLMNOPQRST'

    def __init__(self):
        self.__input = self.__load_input() # input is products with prices from json (data.json must be inside the same location with .exe)
        self.__guid = '67a07fb6-8266-4247-b974-de89d6bd1020' #key for symfonia
        self.__host = 'http://192.168.70.70:80/api' # host of symfonia


    def __load_input(self):
        with open('data.json', encoding='utf-8') as file: 
            return json.loads(file.read()) #load data from data.json


    def __load_prices(self):
        res = requests.get(f'{self.__host}/Prices/SalePriceTypes', headers={ 
            'Authorization': 'Session {' + self.__session + '}' 
        }) #load prices list from static endpoint
        if res.status_code >= 400: 
            raise Exception('Server of Symfonia is not responsing currently. Might be unavailable right now. Try again later.')
        return json.loads(res.text)
    

    def login(self): # login is using guid key to obtain a authorization, and then new session is opening
        res = requests.get(f'{self.__host}/Sessions/OpenNewSession?deviceName=test', headers={ 
            'Authorization': 'Application {' + self.__guid + '}' 
        })
        self.__session = res.text.replace('"', '')
        if '{' in self.__session: # symfonia is unavailable right now
            print("User's limit is exceeded. Try later.")
            sys.exit()
        else: 
            print('\n' + self.__session + '\n')
        return self
    

    def logout(self): # for tweaking working for this program is necessery to close a session with session key
        requests.get(f'{self.__host}/Sessions/CloseSession', headers={ 
            'Authorization': 'Session {' + self.__session + '}' 
        })
        return self
    

    def run(self): # essential engine of program
        errors = list()
        static_prices = self.__load_prices() # load prices from endpoint
        for i in self.__input:
            code = i['Kod']
            total = { "SalePrices": [] } # data for this instance is a dict which will be transfering to json as input data for product
            prices = [(key, float(i[key][:-3])) for key in i if key != 'Kod' and key != 'Nazwa']
            for price in prices:
                suitable_static_price = static_prices[Updater.markers.index(price[0])]
                total['SalePrices'].append({ # final instance of each price
                    "Value": price[1], #value
                    "PriceParameter": 2, #idk what is that but without this that had no worked
                    "Type": suitable_static_price['Type'], # required data from "static" prices
                    "Kind": suitable_static_price['Kind'] # as above
                })
            res = requests.put(f'{self.__host}/ProductPrices/Update?productCode={code}', data=json.dumps(total), headers={
                'Authorization': 'Session {' + self.__session + '}', 
                'Content-Type': 'application/json'
            })
            if res.status_code < 400:
                print(f"{code} updated")
            else:
                print(f"{code} not updated")
                errors.append(i)
        print("ERRORS WITH:")
        for i in errors:
            print(i['Kod'])
        return self



if __name__ == '__main__':
    Updater().login().run().logout() #run program
