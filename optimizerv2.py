import math
import copy
import datetime
from cred import cred
import json

class optimizer():

    connection = cred()    

    def __init__(self):
        super().__init__()

    def get_session():
        return optimizer.connection.get_session()

    def get_session_token():
        return optimizer.connection.get_session_token()

    def check_session():
        return optimizer.connection.check_session()

    def reinitiate_session(token):
        return optimizer.connection.reinitiate_session(token)    

    def optimize(parms):
        optimize_result = {}
        optimize_result['margin_situation'] = {}
        optimize_result['ce_options'] = {}
        optimize_result['pe_options'] = {}
        # margin_situation = {}
        stock_code = parms['stock_code']
        expiry_date = parms['expiry_date']+"T06:00:00.000Z"
        target_margin_ute = parms['target_margin_ute'] # Target % utilisation of margin; typically a good idea to limit to 80-90% to accommodate sudden margin shortfalls
        lot_size = parms['lot_size']
        otm_call_distance = parms['otm_call_distance'] # % distance from the spot; typically a good idea to stay 8-10% away from spot price for CE
        otm_put_distance = parms['otm_put_distance'] # % distance from the spot; typically a good idea to stay 10-15% away from spot price for PE
        top = parms['top'] # Number of highest payout CE / PE options to display
        actual_limit = parms['actual_limit'] # Whether to calculate actual limits available; NOTE: Breeze API doesn't provide upstreamed amount so inaccurate limits calculations
        
        # Calculate actual limits if parameters ask for actual calculations

        if actual_limit == True:
            # Getting free limits
            get_margin_result = optimizer.get_margin_situation(target_margin_ute)
            if get_margin_result['Status'] == 200:
                limits = get_margin_result['Success']['limits']
            else:
                limits = 0
            optimize_result['margin_situation'] = get_margin_result
        else:
            limits = parms['limits'] # Limits to consider if not actual_limit
            optimize_result['margin_situation']['Status'] = 400
            optimize_result['margin_situation']['Error'] = "Ignoring actual limits; using limits parameter"

        if limits <= 0:
            optimize_result['ce_options']['Status'] = 400
            optimize_result['ce_options']['Error'] = "Insufficient / Unknown limits to initiate any trades"
            optimize_result['pe_options']['Status'] = 400
            optimize_result['pe_options']['Error'] = "Insufficient / Unknown limits to initiate any trades"
        else:
            # Getting OTM CALL chain
            right = "CALL"
            otm_distance = otm_call_distance
            optimize_result['ce_options'] = optimizer.get_options(right,stock_code,lot_size,expiry_date,limits,otm_distance,top)

            # Getting OTM PUT chain
            right = "PUT"
            otm_distance = otm_put_distance
            optimize_result['pe_options'] = optimizer.get_options(right,stock_code,lot_size,expiry_date,limits,otm_distance,top)

        return optimize_result  

    def get_margin_situation(target_margin_ute):
        margin_situation = {}
        breeze = optimizer.get_session()
        margin = breeze.get_margin(exchange_code="NFO")
        # print(json.dumps(margin,indent=4))

        if margin['Status'] == 200:
            margin_situation['Status'] = 200
            margin_situation['Success'] = {}
            actual_margin_ute = 0
            for i in margin['Success']['limit_list']:
                actual_margin_ute =+ int(i["amount"])
            
            margin_situation['Success']['actual_margin_ute'] = actual_margin_ute
            margin_situation['Success']['cash_limit'] = margin['Success']['cash_limit']
            margin_situation['Success']['actual_margin_avl'] = margin['Success']['cash_limit'] + actual_margin_ute
            margin_situation['Success']['target_margin_free'] = margin['Success']['cash_limit'] * (100 - target_margin_ute) / 100
            margin_situation['Success']['limits'] = margin_situation['Success']['actual_margin_avl'] - margin_situation['Success']['target_margin_free']
        else:
            margin_situation['Status'] = margin['Status']
            margin_situation['Error'] = margin['Error']
        return margin_situation

    def get_options(right,stock_code,lot_size,expiry_date,limits,otm_distance,top):
        exchange_code = "NFO"
        product_type = "options"
        action = "sell"
        sorted_options = {}
        breeze = optimizer.get_session()
        options_chain = breeze.get_option_chain_quotes(stock_code=stock_code,
                            exchange_code=exchange_code,
                            product_type=product_type,
                            expiry_date=expiry_date,
                            right=right)

        if options_chain['Status'] == 200:
            # Calculating the premium that can be collected for every Liquid OTM CE option
            options = [{}] #unable to use sort function unless this is a list of dicts!
            for i in options_chain['Success']:
                if int(i["total_buy_qty"]) > 0 and ((right == "CALL" and int(i["strike_price"]) > int(float(i["spot_price"]) * (1 + otm_distance / 100))) or (right == "PUT" and int(i["strike_price"]) < int(float(i["spot_price"]) * (1 - otm_distance / 100))) ):
                    option_margin = breeze.margin_calculator([{"strike_price": int(i["strike_price"]),
                                                "quantity": lot_size,
                                                "product": product_type,
                                                "action": action,
                                                "expiry_date": expiry_date,
                                                "stock_code": stock_code,
                                                "right": right
                                                }],exchange_code = exchange_code)
                    temp = {}
                    temp["stock_code"] = stock_code
                    temp["strike_price"] = int(i["strike_price"])
                    temp["expiry_date"] = expiry_date.removesuffix("T06:00:00.000Z")
                    # print("Expiry date after stripping: "+temp['expiry_date'])
                    temp["option"] = right
                    temp["quantity"] = math.floor(limits / float(option_margin['Success']['span_margin_required'])) * lot_size
                    temp["best_bid_price"] = i["best_bid_price"]
                    temp["premium"] = int(temp["quantity"] * i["best_bid_price"])
                    options.append(copy.deepcopy(temp))

            # Sort the top call options by premium
            options.pop(0)
            options = sorted(options, key=lambda x: x["premium"], reverse=True)
            sorted_options['Success'] = options[:top]
            sorted_options['Status'] = 200
        else:
            sorted_options['Error'] = right+" : "+options_chain['Error']
            sorted_options['Status'] = options_chain['Status']

        return sorted_options   

    def get_positions():
        breeze = optimizer.get_session()
        positions = breeze.get_portfolio_positions()
        if positions['Status'] == 200:
            for i in positions['Success']:
                if i['action'] == "Sell":
                    i['current_profit'] = (float(i['average_price']) - float(i['ltp'])) * int(i['quantity'])
                    i['carry_profit'] = float(i['ltp']) * int(i['quantity'])
                else:
                    i['current_profit'] = (float(i['ltp']) - float(i['average_price'])) * int(i['quantity'])
                    i['carry_profit'] = - float(i['ltp']) * int(i['quantity'])
        else:
            positions['Error'] = positions['Error']
            positions['Status'] = positions['Status']            

        print(json.dumps(positions,indent=4))
        return positions

    def hedge_options(right,stock_code,lot_size,quantity,expiry_date,strike_price,top):
        exchange_code = "NFO"
        product_type = "options"
        sorted_hedges = {}
        breeze = optimizer.get_session()
        options_chain = breeze.get_option_chain_quotes(stock_code=stock_code,
                            exchange_code=exchange_code,
                            product_type=product_type,
                            expiry_date=expiry_date,
                            right=right)

        if options_chain['Status'] == 200:
            # Find the premium of ATM option by weeding out ITM options and illiquid options
            options = [{}] #unable to use sort function unless this is a list of dicts!            
            for i in options_chain['Success']:
                if int(i['total_sell_qty']) > 0 and int(i['strike_price']) < strike_price and int(i['strike_price']) > int(i['spot_price']):
                    i['spot_distance'] = int(i['strike_price']) - int(i['spot_price'])
                    temp = {}
                    temp['strike_price'] = int(i['strike_price'])
                    temp['best_offer_price'] = i['best_offer_price']                    
                    temp['spot_distance'] = i['spot_distance']
                    temp['strike_distance'] = strike_price - int(i['strike_price'])
                    options.append(copy.deepcopy(temp))
            options.pop(0)
            options = sorted(options, key=lambda x: x['spot_distance'], reverse=False)
            atm_strike = options[0]['strike_price']
            atm_premium = options[0]['best_offer_price']

            # Build an array of what is the premium ratio at various distances from the spot
            for i in options:
                i['premium_ratio'] = i['best_offer_price'] / atm_premium

            for i in options:
                for j in options:
                    if i['strike_distance'] == j['spot_distance']:
                        hedge_qty = quantity * j['premium_ratio']
                        i['hedge_qty'] = math.ceil(hedge_qty/lot_size) * lot_size
                        i['hedge_premium'] = i['hedge_qty'] * i['best_offer_price']
                        break # better option than using WHILE loop because theoretically we may have options at a strike distance that don't match with any spot distance in case any of the intermediate options are illiquid
            options = sorted(options, key=lambda x: x['hedge_premium'], reverse=False)
            sorted_hedges['Success'] = options[:top]
            sorted_hedges['Status'] = 200
        else:
            sorted_hedges['Error'] = right+" : "+options_chain['Error']
            sorted_hedges['Status'] = options_chain['Status']

        return sorted_hedges   
        
    def place_order(order):
        breeze = optimizer.get_session()
        response = breeze.place_order(stock_code=order['stock_code'],
                        action=order['action'],
                        strike_price=order['strike_price'],
                        right=order['right'],
                        price=order['price'],
                        expiry_date=order['expiry_date']+"T06:00:00.000Z",
                        validity="day",
                        order_type=order['order_type'],
                        quantity=order['quantity'],
                        validity_date=str(datetime.date.today())+"T06:00:00.000Z",
                        stoploss="",
                        disclosed_quantity="0",
                        exchange_code="NFO",
                        product="options")
        return response
