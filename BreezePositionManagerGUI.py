import tkinter as tk
import datetime
import json
from optimizerv2 import optimizer
from functools import partial

# import breeze_connect.config as temp

# temp.SECURITY_MASTER_URL


class BManagerGUI(tk.Tk):

    ERROR = "Error"
    SUCCESS = "Success"
    WARNING = "Warning"
    INFO = "Info"
    TITLE = ["TkDefaultFont",15]

    def __init__(self):
        super().__init__()
        self.option_add("*Font","Courier")
        self.title("Breeze Positions Manager")
        self.grid_rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)        

        self.frame_main = tk.Frame(self)
        self.frame_main.grid(sticky=tk.NSEW)

        # # Setup the Messages frame with the Scrollbar
        self.create_message_frame()

        self.establish_session()

        # # Setup the input frame
        self.create_positions_frame()

    def create_message_frame(self):
        title = tk.Label(self.frame_main,text="MESSAGES",background="dark turquoise",foreground="black",borderwidth=2,relief=tk.GROOVE,font=self.TITLE)
        title.grid(row=0,column=0,sticky=tk.NSEW)
        msg_out_frame = tk.Frame(self.frame_main)
        msg_out_frame.grid(row=1, column=0, pady=(5, 0), sticky=tk.NW)
        msg_out_frame.grid_rowconfigure(0, weight=1)
        msg_out_frame.grid_columnconfigure(0, weight=1)        
        msg_out_frame.grid_propagate(False)
        
        self.msg_canvas = tk.Canvas(msg_out_frame)
        self.msg_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        
        msg_vsb = tk.Scrollbar(msg_out_frame, orient=tk.VERTICAL, command=self.msg_canvas.yview)
        msg_vsb.grid(row=0, column=1, sticky=tk.NS)
        self.msg_canvas.configure(yscrollcommand=msg_vsb.set)

        self.msg_frame = tk.Frame(self.msg_canvas)
        self.msg_canvas.create_window((0,0), window=self.msg_frame, anchor=tk.SE)

        msg_out_frame.config(width=1200,height=100)        

    def create_positions_frame(self):
        self.iw_session_token = tk.StringVar()

        title = tk.Label(self.frame_main,text="POSITIONS",background="dark turquoise",foreground="black",borderwidth=2,relief=tk.GROOVE,font=self.TITLE)
        title.grid(row=2,column=0,sticky=tk.NSEW)
        position_out_frame = tk.Frame(self.frame_main)
        position_out_frame.grid(row=3, column=0, pady=(5, 0), sticky=tk.NW)
        position_out_frame.grid_rowconfigure(0, weight=1)
        position_out_frame.grid_columnconfigure(0, weight=1)        
        position_out_frame.grid_propagate(False)
        
        self.position_canvas = tk.Canvas(position_out_frame)
        self.position_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        
        position_vsb = tk.Scrollbar(position_out_frame, orient=tk.VERTICAL, command=self.position_canvas.yview)
        position_vsb.grid(row=0, column=1, sticky=tk.NS)
        self.position_canvas.configure(yscrollcommand=position_vsb.set)

        self.position_frame = tk.Frame(self.position_canvas)
        self.position_canvas.create_window((0,0), window=self.position_frame, anchor=tk.SE)

        position_out_frame.config(width=1200,height=100)

        positions = optimizer.get_positions()
        # print("Showing positions below")
        # print(json.dumps(positions,indent=4))

    def establish_session(self):
        frame = self.frame_main
        if optimizer.check_session() == 200:
            message = "Breeze Session Established"
            self.display_message(message,self.SUCCESS)
        else:
            message = "Breeze Session Failed. Get fresh token from https://api.icicidirect.com/apiuser/home"
            self.display_message(message,self.ERROR)

            iw_el = tk.Label(frame,text='Breeze Session Token')
            iw_el.grid(row=0,sticky=tk.E,columnspan=2)
            iw_ee = tk.Entry(frame,textvariable=self.iw_session_token)
            iw_ee.grid(row=0,column=2,sticky=tk.W)
            tk.Button(frame,text='Exit',height=2,command=self.quit).grid(row=9,column=1,sticky=tk.E)
            tk.Button(frame,text='Submit',height=2,command=self.input_submit).grid(row=9,column=2,sticky=tk.W)    

    def submit_token(self):
        if optimizer.reinitiate_session(self.iw_session_token.get()) != 200:
            message = "Breeze Initiation Failed @"+str(datetime.datetime.today())
            self.display_message(message,self.ERROR)                
        else:
            message = "Breeze Session Successfully Connected @"+str(datetime.datetime.today())+" : Please RESTART application"
            self.display_message(message,self.SUCCESS)            

    def populate_positions(self):
        frame = self.position_frame
        canvas = self.position_canvas
        
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))        

    def create_input_frame(self):
        # frame = self.input_frame

        title = tk.Label(self.frame_main,text="INPUT",background="dark turquoise",foreground="black",borderwidth=2,relief=tk.GROOVE,font=self.TITLE)
        title.grid(row=2,column=0,sticky=tk.NSEW)        
        frame = tk.Frame(self.frame_main)
        frame.grid(row=3, column=0, pady=(5, 0), sticky=tk.NW)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure([0,1,2,3], weight=1, minsize=300)

        self.iw_session_token = tk.StringVar()
        self.iw_actual_limit = tk.IntVar()
        self.iw_actual_limit.set(1)
        self.iw_limits = tk.IntVar()
        self.iw_stock_code = tk.StringVar()
        self.iw_lot_size = tk.IntVar()
        self.iw_expiry_date = tk.StringVar()
        self.iw_target_margin_ute = tk.IntVar()
        self.iw_otm_call_distance = tk.IntVar()
        self.iw_otm_put_distance = tk.IntVar()
        self.iw_top = tk.IntVar()

        if optimizer.check_session() == 200:
            message = "Breeze Session Established"
            self.display_message(message,self.SUCCESS)
        
            iw_scl = tk.Label(frame,text='Stock Code')
            iw_scl.grid(row=1,sticky=tk.E,columnspan=2)
            iw_sce = tk.Entry(frame,textvariable=self.iw_stock_code)
            iw_sce.grid(row=1,column=2,sticky=tk.W)

            iw_lsl = tk.Label(frame,text='Lot Size')
            iw_lsl.grid(row=2,sticky=tk.E,columnspan=2)
            iw_lse = tk.Entry(frame,textvariable=self.iw_lot_size)
            iw_lse.grid(row=2,column=2,sticky=tk.W)

            iw_edl = tk.Label(frame,text='Expiry Date (YYYY-MM-DD)')
            iw_edl.grid(row=3,sticky=tk.E,columnspan=2)
            iw_ede = tk.Entry(frame,textvariable=self.iw_expiry_date)
            iw_ede.grid(row=3,column=2,sticky=tk.W)

            iw_ll = tk.Label(frame,text='Limits (in lakhs)')
            iw_ll.grid(row=4,sticky=tk.E,columnspan=2)
            iw_le = tk.Entry(frame,textvariable=self.iw_limits,state='readonly',readonlybackground="dark gray")
            iw_le.grid(row=4,column=2,sticky=tk.W)
            tk.Checkbutton(frame,text='Use actual limits',variable=self.iw_actual_limit,command=partial(self.limit_toggle,frame)).grid(row=4,column=3,sticky=tk.W)
            
            iw_tml = tk.Label(frame,text='Targeted Margin Utilisation (%)')
            iw_tml.grid(row=5,sticky=tk.E,columnspan=2)
            iw_tme = tk.Entry(frame,textvariable=self.iw_target_margin_ute)
            iw_tme.grid(row=5,column=2,sticky=tk.W)

            iw_cel = tk.Label(frame,text='CE Strike Price distance (%) from Spot')
            iw_cel.grid(row=6,sticky=tk.E,columnspan=2)
            iw_cee = tk.Entry(frame,textvariable=self.iw_otm_call_distance)
            iw_cee.grid(row=6,column=2,sticky=tk.W)

            iw_pel = tk.Label(frame,text='PE Strike Price distance (%) from Spot')
            iw_pel.grid(row=7,sticky=tk.E,columnspan=2)
            iw_pee = tk.Entry(frame,textvariable=self.iw_otm_put_distance)
            iw_pee.grid(row=7,column=2,sticky=tk.W)

            iw_tl = tk.Label(frame,text='# of top options to analyse')
            iw_tl.grid(row=8,sticky=tk.E,columnspan=2)
            iw_te = tk.Entry(frame,textvariable=self.iw_top)
            iw_te.grid(row=8,column=2,sticky=tk.W)            
        else:
            message = "Breeze Session Failed. Get fresh token"
            self.display_message(message,self.ERROR)

            iw_el = tk.Label(frame,text='Breeze Session Token')
            iw_el.grid(row=0,sticky=tk.E,columnspan=2)
            iw_ee = tk.Entry(frame,textvariable=self.iw_session_token)
            iw_ee.grid(row=0,column=2,sticky=tk.W)

        tk.Button(frame,text='Exit',height=2,command=self.quit).grid(row=9,column=1,sticky=tk.E)
        tk.Button(frame,text='Submit',height=2,command=self.input_submit).grid(row=9,column=2,sticky=tk.W)
    
    def limit_toggle(self,frame):
        if self.iw_actual_limit.get() == 1:
            iw_le = tk.Entry(frame,textvariable=self.iw_limits,state='readonly',readonlybackground="dark gray")
            iw_le.grid(row=4,column=2,sticky=tk.W)
        else:
            iw_le = tk.Entry(frame,textvariable=self.iw_limits,state='normal',readonlybackground="dark gray")
            iw_le.grid(row=4,column=2,sticky=tk.W)

    def input_submit(self):
        if optimizer.check_session() == 400:
            if optimizer.reinitiate_session(self.iw_session_token.get()) != 200:
                message = "Breeze Initiation Failed @"+str(datetime.datetime.today())
                self.display_message(message,self.ERROR)                
            else:
                message = "Breeze Session Successfully Connected @"+str(datetime.datetime.today())+" : Please RESTART application"
                self.display_message(message,self.SUCCESS)
        else:
            parms = {}
            error = False
            try:
                parms['stock_code'] = self.iw_stock_code.get()
                parms['lot_size'] = self.iw_lot_size.get()
                parms['expiry_date'] = self.iw_expiry_date.get()
                parms['actual_limit'] = bool(self.iw_actual_limit.get())
                
                if self.iw_actual_limit.get() == 1:
                    parms['limits'] = 0
                else:
                    parms['limits'] = self.iw_limits.get() * 100000
                
                parms['target_margin_ute'] = self.iw_target_margin_ute.get()
                parms['otm_call_distance'] = self.iw_otm_call_distance.get()
                parms['otm_put_distance'] = self.iw_otm_put_distance.get()
                parms['top'] = self.iw_top.get()
            except:
                message = "Check and correct inputs"
                self.display_message(message,self.ERROR)
                error = True                

            ### Hard coding for testing
            # self.parms['stock_code'] = "CNXBAN"
            # self.parms['lot_size'] = 15
            # self.parms['expiry_date'] = "2024-10-01"
            # self.parms['actual_limit'] = False
            # self.parms['limits'] = 10000000
            # self.parms['target_margin_ute'] = 90
            # self.parms['otm_call_distance'] = 10
            # self.parms['otm_put_distance'] = 10
            # self.parms['top'] = 3

            try:
                if int(parms['target_margin_ute']) <=0 or int(parms['target_margin_ute']) > 100:
                    message = "Enter valid target margin utilisation (%) between 0 & 100"
                    self.display_message(message,self.ERROR)
                    error = True
            except:
                message = "Enter valid target margin utilisation (%) between 0 & 100"
                self.display_message(message,self.ERROR)
                error = True

            try:
                if int(parms['lot_size']) <=0:
                    message = "Enter valid lot size greater than 0"
                    self.display_message(message,self.ERROR)
                    error = True
            except:
                message = "Enter valid lot size greater than 0"
                self.display_message(message,self.ERROR)
                error = True

            try:
                if int(parms['otm_call_distance']) <=0 or int(parms['otm_call_distance']) > 30:
                    message = "Enter valid distance (%) from spot price for CE between 0 & 30"
                    self.display_message(message,self.ERROR)
                    error = True
            except:
                message = "Enter valid distance (%) from spot price for CE between 0 & 30"
                self.display_message(message,self.ERROR)
                error = True

            try:
                if int(parms['otm_put_distance']) <=0 or int(parms['otm_put_distance']) > 30:
                    message = "Enter valid distance (%) from spot price for PE between 0 & 30"
                    self.display_message(message,self.ERROR)
                    error = True
            except:
                message = "Enter valid distance (%) from spot price for PE between 0 & 30"
                self.display_message(message,self.ERROR)
                error = True

            try:
                if int(parms['top']) <=0 or int(parms['top']) > 10:
                    message = "Provide reasonable # of options (less than 10) to explore"
                    self.display_message(message,self.ERROR)
                    error = True
            except:
                message = "Provide reasonable # of options (less than 10) to explore"
                self.display_message(message,self.ERROR)
                error = True

            try:
                if datetime.date.fromisoformat(parms['expiry_date']) <= datetime.date.today():
                    message = "Provide today or future date"
                    self.display_message(message,self.ERROR)
                    error = True                    
            except:
                message = "Provide correct date in YYYY-MM-DD format"
                self.display_message(message,self.ERROR)
                error = True

            if error == False:
                # print("Input Parameters:")
                # print(json.dumps(parms,indent=4))
                response = optimizer.optimize(parms)

                if response['margin_situation']['Status'] == 200:
                    limits = response['margin_situation']['Success']['limits']
                    limits = f'₹{int(limits):,.0f}'
                    message = "Limits available for fresh trade = "+limits
                    self.display_message(message,self.SUCCESS)
                else:
                    message = response['margin_situation']['Error']
                    self.display_message(message,self.ERROR)

                if response['ce_options']['Status'] == 200:
                    message = "CE options fetched successfully"
                    self.display_message(message,self.SUCCESS)
                else:
                    message = response['ce_options']['Error']
                    self.display_message(message,self.ERROR)

                if response['pe_options']['Status'] == 200:
                    message = "PE options fetched successfully"
                    self.display_message(message,self.SUCCESS)
                else:
                    message = response['pe_options']['Error']
                    self.display_message(message,self.ERROR)

                # print("Optimised Results:")
                # print(json.dumps(response,indent=4))
                self.create_output_frame()                
                self.display_options(response)

    def create_output_frame(self):
        # # Setup the optimisation option output frame
        try:
            self.output_out_frame_title.destroy()
            self.output_out_frame_title = tk.Label(self.frame_main,text="OPTIMISED OPTIONS",background="dark turquoise",foreground="black",borderwidth=2,relief=tk.GROOVE,font=self.TITLE)
            self.output_out_frame_title.grid(row=4,column=0,sticky=tk.NSEW)
        except:
            self.output_out_frame_title = tk.Label(self.frame_main,text="OPTIMISED OPTIONS",background="dark turquoise",foreground="black",borderwidth=2,relief=tk.GROOVE,font=self.TITLE)
            self.output_out_frame_title.grid(row=4,column=0,sticky=tk.NSEW)
        
        try:
            self.output_out_frame.destroy()
            self.output_out_frame = tk.Frame(self.frame_main)
            self.output_out_frame.grid(row=5, column=0, pady=(5, 0), sticky=tk.NW)
            self.output_out_frame.grid_rowconfigure(0, weight=1)
            self.output_out_frame.grid_columnconfigure(0, weight=1)        
            self.output_out_frame.grid_propagate(False)
            self.output_canvas = tk.Canvas(self.output_out_frame)
            self.output_canvas.grid(row=0, column=0, sticky=tk.NSEW)
            out_vsb = tk.Scrollbar(self.output_out_frame, orient=tk.VERTICAL, command=self.output_canvas.yview)
            out_vsb.grid(row=0, column=1, sticky=tk.NS)
            self.output_canvas.configure(yscrollcommand=out_vsb.set)
            self.output_frame = tk.Frame(self.output_canvas)
            self.output_canvas.create_window((0,0), window=self.output_frame, anchor=tk.SE)
            self.output_out_frame.config(width=1200,height=100)            
        except:    
            self.output_out_frame = tk.Frame(self.frame_main)
            self.output_out_frame.grid(row=5, column=0, pady=(5, 0), sticky=tk.NW)
            self.output_out_frame.grid_rowconfigure(0, weight=1)
            self.output_out_frame.grid_columnconfigure(0, weight=1)        
            self.output_out_frame.grid_propagate(False)
            self.output_canvas = tk.Canvas(self.output_out_frame)
            self.output_canvas.grid(row=0, column=0, sticky=tk.NSEW)
            out_vsb = tk.Scrollbar(self.output_out_frame, orient=tk.VERTICAL, command=self.output_canvas.yview)
            out_vsb.grid(row=0, column=1, sticky=tk.NS)
            self.output_canvas.configure(yscrollcommand=out_vsb.set)
            self.output_frame = tk.Frame(self.output_canvas)
            self.output_canvas.create_window((0,0), window=self.output_frame, anchor=tk.SE)
            self.output_out_frame.config(width=1200,height=100)

        try:
            self.destroy_order_frame()
        except:
            None

    def display_options(self,data):
        frame = self.output_frame
        canvas = self.output_canvas

        # clear previous entries
        # for widget in frame.winfo_children():
        #     widget.destroy()

        selected_option = tk.StringVar(value=' ')
        if data['ce_options']['Status'] == 200:
            for i in data['ce_options']['Success']:
                d = datetime.datetime.strptime(i['expiry_date'], '%Y-%m-%d')
                d = datetime.date.strftime(d, "%d-%b-%y")
                premium = i['premium']
                premium = f'₹{int(premium):,.0f}'
                option = i['stock_code']+"-"+d+"-"+str(i['strike_price'])+"-CE | Qty = "+str(i['quantity'])+" | Premium = "+str(premium)+"        "
                print(option)                
                button = tk.Radiobutton(frame,height=1,text=option,justify=tk.LEFT,variable=selected_option,value=i,command=partial(self.confirm_order,i))
                button.grid(row=len(frame.grid_slaves()),sticky=tk.NW)

        if data['pe_options']['Status'] == 200:
            row=len(frame.grid_slaves())
            for i in data['pe_options']['Success']:
                d = datetime.datetime.strptime(i['expiry_date'], '%Y-%m-%d')
                d = datetime.date.strftime(d, "%d-%b-%y")
                premium = i['premium']
                premium = f'₹{int(premium):,.0f}'
                option = i['stock_code']+"-"+d+"-"+str(i['strike_price'])+"-PE | Qty = "+str(i['quantity'])+" | Premium = "+str(premium)
                print(option)
                button = tk.Radiobutton(frame,height=1,text=option,variable=selected_option,value=i,command=partial(self.confirm_order,i))
                button.grid(row=len(frame.grid_slaves())-row,column=1,sticky=tk.NW)

        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

    def create_order_frame(self):    
        # # Setup the order frame
        try:
            self.order_frame_title.destroy()
            self.order_frame_title = tk.Label(self.frame_main,text="CONFIRM ORDER",background="dark turquoise",foreground="black",borderwidth=2,relief=tk.GROOVE,font=self.TITLE)
            self.order_frame_title.grid(row=6,column=0,sticky=tk.NSEW)            
        except:
            self.order_frame_title = tk.Label(self.frame_main,text="CONFIRM ORDER",background="dark turquoise",foreground="black",borderwidth=2,relief=tk.GROOVE,font=self.TITLE)
            self.order_frame_title.grid(row=6,column=0,sticky=tk.NSEW)

        try:
            self.order_frame.destroy()
            self.order_frame = tk.Frame(self.frame_main)
            self.order_frame.grid(row=7, column=0, pady=(5, 0), sticky=tk.NW)
            self.order_frame.grid_rowconfigure(0, weight=1)
            self.order_frame.grid_columnconfigure([0,1,2,3], weight=1, minsize=300)            
        except:    
            self.order_frame = tk.Frame(self.frame_main)
            self.order_frame.grid(row=7, column=0, pady=(5, 0), sticky=tk.NW)
            self.order_frame.grid_rowconfigure(0, weight=1)
            self.order_frame.grid_columnconfigure([0,1,2,3], weight=1, minsize=300)

    def destroy_order_frame(self):
        self.order_frame_title.destroy()
        self.order_frame.destroy()

    def confirm_order(self,i):
        order = i

        self.create_order_frame()

        stock_code = order['stock_code']
        self.ow_stock_code = tk.StringVar(value=stock_code)
        ow_scl = tk.Label(self.order_frame,text='Stock Code')
        ow_scl.grid(row=1,sticky=tk.E,columnspan=2)
        ow_sce = tk.Entry(self.order_frame,textvariable=self.ow_stock_code,state='readonly',readonlybackground="dark gray")
        ow_sce.grid(row=1,column=2,sticky=tk.W)

        strike_price = order['strike_price']
        self.ow_strike_price = tk.StringVar(value=strike_price)
        ow_spl = tk.Label(self.order_frame,text='Strike Price')
        ow_spl.grid(row=2,sticky=tk.E,columnspan=2)
        ow_spe = tk.Entry(self.order_frame,textvariable=self.ow_strike_price,state='readonly',readonlybackground="dark gray")
        ow_spe.grid(row=2,column=2,sticky=tk.W)

        expiry_date = order['expiry_date']
        self.ow_expiry_date = tk.StringVar(value=expiry_date)
        ow_edl = tk.Label(self.order_frame,text='Expiry Date (YYYY-MM-DD)')
        ow_edl.grid(row=3,sticky=tk.E,columnspan=2)
        ow_ede = tk.Entry(self.order_frame,textvariable=self.ow_expiry_date,state='readonly',readonlybackground="dark gray")
        ow_ede.grid(row=3,column=2,sticky=tk.W)

        option = order['option']
        self.ow_option = tk.StringVar(value=option)
        ow_ol = tk.Label(self.order_frame,text='Option')
        ow_ol.grid(row=4,sticky=tk.E,columnspan=2)
        ow_oe = tk.Entry(self.order_frame,textvariable=self.ow_option,state='readonly',readonlybackground="dark gray")
        ow_oe.grid(row=4,column=2,sticky=tk.W)

        self.ow_action = tk.StringVar(value='SELL')
        ow_al = tk.Label(self.order_frame,text='Action')
        ow_al.grid(row=5,sticky=tk.E,columnspan=2)
        ow_ae = tk.Entry(self.order_frame,textvariable=self.ow_action,state='readonly',readonlybackground="dark gray")
        ow_ae.grid(row=5,column=2,sticky=tk.W)

        total_qty = order['quantity']
        self.ow_total_qty = tk.StringVar(value=total_qty)
        ow_tql = tk.Label(self.order_frame,text='Total Quantity')
        ow_tql.grid(row=6,sticky=tk.E,columnspan=2)
        ow_tqe = tk.Entry(self.order_frame,textvariable=self.ow_total_qty)
        ow_tqe.grid(row=6,column=2,sticky=tk.W)

        self.ow_order_tranche = tk.StringVar(value='900')
        ow_otl = tk.Label(self.order_frame,text='Order Tranche Size')
        ow_otl.grid(row=7,sticky=tk.E,columnspan=2)
        ow_ote = tk.Entry(self.order_frame,textvariable=self.ow_order_tranche)
        ow_ote.grid(row=7,column=2,sticky=tk.W)

        price = order['best_bid_price']
        self.ow_price = tk.StringVar(value=price)
        ow_pl = tk.Label(self.order_frame,text='Price')
        ow_pl.grid(row=8,sticky=tk.E,columnspan=2)
        ow_pe = tk.Entry(self.order_frame,textvariable=self.ow_price)
        ow_pe.grid(row=8,column=2,sticky=tk.W)

        tk.Button(self.order_frame,text='Exit',height=2,command=self.destroy_order_frame).grid(row=9,column=1,sticky=tk.E)
        tk.Button(self.order_frame,text='Order',height=2,command=self.fire_order).grid(row=9,column=2,sticky=tk.W)

    def fire_order(self):
        order = {}

        error = False
        try:        
            order['stock_code'] = self.ow_stock_code.get()
            order['strike_price'] = self.ow_strike_price.get()        
            order['expiry_date'] = self.ow_expiry_date.get()
            order['right'] = self.ow_option.get()
            order['action'] = self.ow_action.get()
            total_qty = self.ow_total_qty.get()
            tranche_size = self.ow_order_tranche.get()
            order['quantity'] = tranche_size
            order['order_type'] = "limit"
            order['price'] = self.ow_price.get()
        except:
            message = "Check and correct order inputs"
            self.display_message(message,self.ERROR)
            error = True            

        try:
            if int(total_qty) <=0:
                message = "Enter valid total order quantity"
                self.display_message(message,self.ERROR)
                error = True
        except:
            message = "Enter valid total order quantity"
            self.display_message(message,self.ERROR)
            error = True

        try:
            if int(tranche_size) <=0:
                message = "Enter valid tranche size"
                self.display_message(message,self.ERROR)
                error = True
        except:
            message = "Enter valid tranche size"
            self.display_message(message,self.ERROR)
            error = True

        try:
            if float(order['price']) <=0:
                message = "Enter valid price"
                self.display_message(message,self.ERROR)
                error = True
        except:
            message = "Enter valid price"
            self.display_message(message,self.ERROR)
            error = True

        if error == False:
            iterations = int(int(total_qty)/int(tranche_size))
            remainder = int(total_qty) % int(tranche_size)

            print('======================== Firing following orders ========================')
            # optim = optimizer()
            while iterations > 0:
                print(json.dumps(order,indent=4))
                response = optimizer.place_order(order)
                print(response)
                iterations -=1
                if response['Status'] == 200:
                    message = order['stock_code'] + "-" + order['expiry_date'] + "-" + order['strike_price'] + "-" + order['right'] + " | Qty = " + str(order['quantity']) + " | Price = " + order['price'] + " >> " + response['Success']['message'] + " : " + response['Success']['order_id']
                    self.display_message(message,self.SUCCESS)
                else:
                    message = response['Error'] + order['stock_code'] + "-" + order['expiry_date'] + "-" + order['strike_price'] + "-" + order['right'] + " | Qty = " + str(order['quantity']) + " | Price = " + order['price']
                    self.display_message(message,self.ERROR)

            if remainder > 0:
                order['quantity'] = remainder
                print(json.dumps(order,indent=4))            
                response = optimizer.place_order(order)
                print(response)            
                if response['Status'] == 200:
                    message = order['stock_code'] + "-" + order['expiry_date'] + "-" + order['strike_price'] + "-" + order['right'] + " | Qty = " + str(order['quantity']) + " | Price = " +order['price'] + " >> " + response['Success']['message'] + " : " + response['Success']['order_id']
                    self.display_message(message,self.SUCCESS)
                else:
                    message = response['Error'] + order['stock_code'] + "-" + order['expiry_date'] + "-" + order['strike_price'] + "-" + order['right'] + " | Qty = " + str(order['quantity']) + " | Price = " +order['price']
                    self.display_message(message,self.ERROR)

    def display_message(self,text,type):
        frame = self.msg_frame
        canvas = self.msg_canvas

        if type == self.SUCCESS:
            color = "Green"
        elif type == self.ERROR:
            color = "Red"
        elif type == self.WARNING:
            color = "Amber"
        elif type == self.INFO:
            color = None

        message = tk.Label(frame,text=text,background=color)
        message.grid(row=len(frame.grid_slaves()),column=0,sticky=tk.NW)
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

if __name__ == "__main__":
    window = BManagerGUI()
    window.mainloop()