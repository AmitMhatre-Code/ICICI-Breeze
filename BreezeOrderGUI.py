import tkinter as tk
import datetime
import json
from optimizer import optimizer

class BOrder(tk.Tk):

    ERROR = "Error"
    SUCCESS = "Success"
    WARNING = "Warning"
    INFO = "Info"
    TITLE = ["TkDefaultFont",15]

    def __init__(self):
        super().__init__()
        self.option_add("*Font","Courier")
        self.title("Breeze Order")
        self.grid_rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)        

        frame_main = tk.Frame(self)
        frame_main.grid(sticky=tk.NSEW)

        # # Setup the Messages frame with the Scrollbar
        title = tk.Label(frame_main,text="MESSAGES",background="dark turquoise",foreground="black",borderwidth=2,relief=tk.GROOVE,font=self.TITLE)
        title.grid(row=0,column=0,sticky=tk.NSEW)
        msg_out_frame = tk.Frame(frame_main)
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

        # # Setup the order frame
        title = tk.Label(frame_main,text="PLACE ORDER",background="dark turquoise",foreground="black",borderwidth=2,relief=tk.GROOVE,font=self.TITLE)
        title.grid(row=2,column=0,sticky=tk.NSEW)        
        self.order_frame = tk.Frame(frame_main)
        self.order_frame.grid(row=3, column=0, pady=(5, 0), sticky=tk.NW)
        self.order_frame.grid_rowconfigure(0, weight=1)
        self.order_frame.grid_columnconfigure([0,1,2,3], weight=1, minsize=300)

        self.create_order_widget()

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

    def create_order_widget(self):
        frame = self.order_frame

        if optimizer.check_session() == 200:
            self.ow_stock_code = tk.StringVar()
            self.ow_strike_price = tk.StringVar()
            self.ow_expiry_date = tk.StringVar()
            self.ow_option = tk.StringVar(value=' ')
            self.ow_action = tk.StringVar(value=' ')
            self.ow_total_qty = tk.IntVar()
            self.ow_order_tranche = tk.IntVar()
            self.ow_price = tk.StringVar()

            message = "Breeze Session Established"
            self.display_message(message,self.SUCCESS)
            ow_scl = tk.Label(frame,text='Stock Code')
            ow_scl.grid(row=1,sticky=tk.E,columnspan=2)
            ow_sce = tk.Entry(frame,textvariable=self.ow_stock_code)
            ow_sce.grid(row=1,column=2,sticky=tk.W)

            ow_spl = tk.Label(frame,text='Strike Price')
            ow_spl.grid(row=2,sticky=tk.E,columnspan=2)
            ow_spe = tk.Entry(frame,textvariable=self.ow_strike_price)
            ow_spe.grid(row=2,column=2,sticky=tk.W)

            ow_edl = tk.Label(frame,text='Expiry Date (YYYY-MM-DD)')
            ow_edl.grid(row=3,sticky=tk.E,columnspan=2)
            ow_ede = tk.Entry(frame,textvariable=self.ow_expiry_date)
            ow_ede.grid(row=3,column=2,sticky=tk.W)

            ow_oe = tk.Radiobutton(frame,height=1,text="PUT",justify=tk.LEFT,variable=self.ow_option,value="PUT")            
            ow_oe.grid(row=4,column=2,sticky=tk.W)
            ow_oe = tk.Radiobutton(frame,height=1,text="CALL",justify=tk.LEFT,variable=self.ow_option,value="CALL")            
            ow_oe.grid(row=4,column=2,sticky=tk.E)     

            ow_ae = tk.Radiobutton(frame,height=1,text="BUY",justify=tk.LEFT,variable=self.ow_action,value="BUY")            
            ow_ae.grid(row=5,column=2,sticky=tk.W)
            ow_ae = tk.Radiobutton(frame,height=1,text="SELL",justify=tk.LEFT,variable=self.ow_action,value="SELL")            
            ow_ae.grid(row=5,column=2,sticky=tk.E)    

            ow_tql = tk.Label(frame,text='Total Quantity')
            ow_tql.grid(row=6,sticky=tk.E,columnspan=2)
            ow_tqe = tk.Entry(frame,textvariable=self.ow_total_qty)
            ow_tqe.grid(row=6,column=2,sticky=tk.W)

            ow_otl = tk.Label(frame,text='Order Tranche Size')
            ow_otl.grid(row=7,sticky=tk.E,columnspan=2)
            ow_ote = tk.Entry(frame,textvariable=self.ow_order_tranche)
            ow_ote.grid(row=7,column=2,sticky=tk.W)

            ow_pl = tk.Label(frame,text='Price')
            ow_pl.grid(row=8,sticky=tk.E,columnspan=2)
            ow_pe = tk.Entry(frame,textvariable=self.ow_price)
            ow_pe.grid(row=8,column=2,sticky=tk.W)

            tk.Button(frame,text='Exit',height=2,command=self.quit).grid(row=9,column=1,sticky=tk.E)
            tk.Button(frame,text='Order',height=2,command=self.fire_order).grid(row=9,column=2,sticky=tk.W)
        else:
            message = "Breeze Session Failed. Get fresh token"
            self.display_message(message,self.ERROR)

            self.iw_session_token = tk.IntVar()
            iw_el = tk.Label(frame,text='Breeze Session Token')
            iw_el.grid(row=0,sticky=tk.E,columnspan=2)
            iw_ee = tk.Entry(frame,textvariable=self.iw_session_token)
            iw_ee.grid(row=0,column=2,sticky=tk.W)            

            tk.Button(frame,text='Exit',height=2,command=self.quit).grid(row=9,column=1,sticky=tk.E)
            tk.Button(frame,text='Connect',height=2,command=self.connect).grid(row=9,column=2,sticky=tk.W)            

    def connect(self):
        if optimizer.check_session() == 400:
            if optimizer.reinitiate_session(self.iw_session_token.get()) != 200:
                message = "Breeze Initiation Failed @"+str(datetime.datetime.today())
                self.display_message(message,self.ERROR)                
            else:
                message = "Breeze Session Successfully Connected @"+str(datetime.datetime.today())+" : Please RESTART application"
                self.display_message(message,self.SUCCESS)

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
            if datetime.date.fromisoformat(order['expiry_date']) <= datetime.date.today():
                message = "Provide today or future date"
                self.display_message(message,self.ERROR)
                error = True                    
        except:
            message = "Provide correct date in YYYY-MM-DD format"
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
                # print(response)
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
                # print(response)            
                if response['Status'] == 200:
                    message = order['stock_code'] + "-" + order['expiry_date'] + "-" + order['strike_price'] + "-" + order['right'] + " | Qty = " + str(order['quantity']) + " | Price = " +order['price'] + " >> " + response['Success']['message'] + " : " + response['Success']['order_id']
                    self.display_message(message,self.SUCCESS)
                else:
                    message = response['Error'] + order['stock_code'] + "-" + order['expiry_date'] + "-" + order['strike_price'] + "-" + order['right'] + " | Qty = " + str(order['quantity']) + " | Price = " +order['price']
                    self.display_message(message,self.ERROR)

if __name__ == "__main__":
    window = BOrder()
    window.mainloop()