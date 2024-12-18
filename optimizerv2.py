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
                if int(i['total_sell_qty']) > 0 and ((right == "Call" and int(i['strike_price']) <= int(strike_price) and int(i['strike_price']) > round(float(i['spot_price']))) or (right == "Put" and int(i['strike_price']) >= int(strike_price) and int(i['strike_price']) < round(float(i['spot_price'])))):
                    i['spot_distance'] = int(i['strike_price']) - round(float(i['spot_price']))
                    temp = {}
                    temp['stock_code'] = i['stock_code']
                    temp['expiry_date'] = i['expiry_date']
                    temp['right'] = i['right']
                    temp['action'] = "Buy"
                    temp['strike_price'] = int(i['strike_price'])
                    temp['best_offer_price'] = i['best_offer_price']
                    temp['ltp'] = i['ltp']
                    temp['spot_distance'] = i['spot_distance']
                    temp['strike_distance'] = int(strike_price) - int(i['strike_price'])
                    options.append(copy.deepcopy(temp))
            options.pop(0) # to remove the first empty entry was was necessary to declare options as an array of dicts
            options = sorted(options, key=lambda x: x['spot_distance'], reverse=True)
            atm_index = len(options) - 1
            atm_strike = options[atm_index]['strike_price']
            atm_premium = options[atm_index]['best_offer_price']
            print("atm_strike : ",atm_strike)
            print("atm_premium : ",atm_premium)

            # Build an array of the premium ratio at various distances from the spot
            for i in options:
                i['premium_ratio'] = i['best_offer_price'] / atm_premium
            
            # print(json.dumps(options,indent=4))
            for i in options:
                index = 0
                prev_distance = abs(options[0]['spot_distance'] - options[0]['strike_distance']) # this is the theoretically the largest difference that can exist for all the options between ATM Strike and Position Strike
                # Difference between spot distance (at top of i array) & strike distance (for current j array) will keep reducing as we go through j array. The moment it starts increasing again is where the spot distance of j array is closest to strike distance of i array and has the premium ratio we can use. And we can break out of the j array at that point
                for j in options:
                    distance = abs(j['spot_distance'] - i['strike_distance'])
                    # if i['strike_price'] == 61000:
                    #     print("index : ",index)
                    #     print("i strike : ",i['strike_price'])
                    #     print("i strike_distance : ",i['strike_distance'])
                    #     print("i spot_distance : ",i['spot_distance'])
                    #     print("j strike : ",j['strike_price'])
                    #     print("j strike_distance : ",j['strike_distance'])
                    #     print("j spot_distance : ",j['spot_distance'])
                    #     print("prev_distance : ",prev_distance)
                    #     print("distance : ",distance)
                    if distance > prev_distance:
                        # print("Picking up strike price : ", options[index-1]['strike_price'])
                        # print("Picking up premium ratio : ", options[index-1]['premium_ratio'])                        
                        hedge_qty = float(quantity) * options[index-1]['premium_ratio']
                        i['quantity'] = math.ceil(hedge_qty/lot_size) * lot_size
                        i['hedge_premium'] = i['quantity'] * i['best_offer_price']
                        # print("Calculated hedge_qty : ",i['hedge_qty'])
                        # print("Calculated hedge_premium : ",i['hedge_premium'])
                        break
                    else:
                        prev_distance = distance
                    index +=1                   

            print(json.dumps(options,indent=4))
            options.pop(0) #remove the option that represents the very position we want to hedge because the above would have calculated the hedge_premium for all options except the very option we are hedging for
            options = sorted(options, key=lambda x: x['hedge_premium'], reverse=False)
            sorted_hedges['Success'] = options[:top]
            sorted_hedges['Status'] = 200
        else:
            sorted_hedges['Error'] = right+" : "+options_chain['Error']
            sorted_hedges['Status'] = options_chain['Status']

        return sorted_hedges   

    def get_quote(stock_code,exchange_code,expiry_date,product_type,right,strike_price):
        breeze = optimizer.get_session()
        # quote = breeze.get_quotes(stock_code,exchange_code,expiry_date,product_type,right,strike_price)
        quote = breeze.get_option_chain_quotes(stock_code,exchange_code,expiry_date,product_type,right,strike_price)
        return quote

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
