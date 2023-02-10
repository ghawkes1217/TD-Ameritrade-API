import time
import requests
from datetime import date, datetime, timezone
import json




#Create global variables holding your refresh token and customer id and account number:
r_tok = #*enter your refresh token*
c_id= #*enter your customer id, followed by the string '@AMER.OAUTHAP'*
a_num=#*enter your account number*

#Create a global variable holding your temporary access token.  Access token expires after 30 minutes 
def access_token():
    resp = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                         headers={'Content-Type': 'application/x-www-form-urlencoded'},
                         data={'grant_type': 'refresh_token',
                               'refresh_token': r_tok,
                               'client_id': c_id})
    x=resp.json()
    token=x['access_token']
    return(token)
a_tok=access_token()
#Comment the line above out once you have generated your access token.
#The access token will last 30 minutes and TD Ameritrade asks that 
#you not generate more access tokens than necessary.





#Check the stocks that you currently own   
#Returns a list of triples of the form: [ticker-symbol, number of shares you own, current share price]    
def get_positions():
    url='https://api.tdameritrade.com/v1/accounts/'+a_num

    btoken = 'Bearer ' + a_tok
    auth={'Authorization':btoken}
    what={'fields':'positions'}
    positions=requests.get(url,headers=auth,params=what).json()
    positions=positions['securitiesAccount']['positions']
    STK=[]
    for k in range(0,len(positions)):
        stock=positions[k]
        symbol=stock['instrument']['symbol']
        amount=stock['longQuantity']
        value=stock['marketValue']
        STK.append([symbol,amount,value]) 
    STK.sort(key=lambda y: y[0])
    return(STK)

#Check the orders you have placed recently
#Returns information on the orders that you have placed within the last timedelta minutes
#Output format is a list with elements of the form [order_id, [TICKER, shares, price, buy/sell]]
def get_orders(timedelta):
    your_orders=[]
    url='https://api.tdameritrade.com/v1/accounts/'+a_num
    btoken = 'Bearer ' + a_tok
    auth={'Authorization':btoken}
    what={'fields':'orders'}
    orders=requests.get(url,headers=auth,params=what).json()
    orders=orders['securitiesAccount']['orderStrategies']
    for k in range(0,len(orders)):
        order=orders[k]
        if order['orderStrategyType']=='SINGLE':
            timestring=order['enteredTime']
            timeclean=datetime.strptime(timestring[0:10]+' '+timestring[11:19],"%Y-%m-%d %H:%M:%S")
            epochtime=datetime.timestamp(timeclean)
            nowtime=datetime.timestamp(datetime.utcnow())
            if nowtime-epochtime<timedelta*60:
                ID=order['orderId']
                P=order['price']
                S=order['orderLegCollection'][0]['instrument']['symbol']
                Q=order['orderLegCollection'][0]['quantity']
                A=order['orderLegCollection'][0]['instruction']
                Y=[ID,[S,Q,P,A]]
                your_orders.append(Y)
    return(your_orders)    


#Check price history for one stock
#Retrieves historical stock prices over last 2 months (can be adjusted) for a given ticker symbol
#Input is 'TICKER' output is a chronological list [datetime, open, close, high, low] for each day in the time period
def history(stock):
    prices=[]
    url = 'https://api.tdameritrade.com/v1/marketdata/'+stock+'/pricehistory'
    info = {}
    info.update({'apikey': c_id})
    info.update({'period': 2})
    info.update({'periodType': "month"})
    info.update({'frequency': 1})
    info.update({'frequencyType': 'daily'})
    info.update({'endDate': 9991290400000})
    Ca=requests.get(url, params=info).json()
    prices=[stock]
    if 'candles' in Ca:
        Can=Ca['candles']
        for i in range(0,len(Can)):
            prices.append([Can[i]['datetime'],Can[i]['open'],Can[i]['close'],Can[i]['high'],Can[i]['low']])
    return(prices)
    
    
#Get information on a list of stocks
#Input is a list of ticker symbols
#Output is a dictionary object containing detailed information on each stock
#The key for each entry in the dictionary is the ticker symbol itself
def quote(list):
    syms=''
    for i in range(0,len(list)):
        syms+=list[i]
        syms+=','
    url = 'https://api.tdameritrade.com/v1/marketdata/quotes'
    stuff={'apikey': c_id}
    stuff.update({'symbol' : syms})
    btoken = 'Bearer ' + a_tok
    auth={}
    auth.update({'Content-Type':'application/json'})
    auth.update({'Authorization':btoken})
    return requests.get(url, params=stuff, headers=auth).json() 
    
    
    
#Get the details including status of a specific order.    
#Returns details of an order.  Input is 11-digit order ID.  Output is dictionary 
def order(order_id):
    dub=[]
    url='https://api.tdameritrade.com/v1/accounts/'+a_num+'/orders/'
    url+=str(order_id)
    btoken = 'Bearer ' + a_tok
    auth={'Authorization':btoken}
    what={'fields':'orders'}
    order_details=requests.get(url,headers=auth).json()
    return(order_details)


#Cancels an open order.  
#Input is the order ID.
def cancel(orderID):
    OrderID=str(orderID)
    url='https://api.tdameritrade.com/v1/accounts/'+a_num+'/orders/'+OrderID
    btoken = 'Bearer ' + a_tok
    auth={}
    auth.update({'Content-Type':'application/json'})
    auth.update({'Authorization':btoken})
    resp=requests.delete(url,headers=auth)
    return(resp)

