#Author name: Liyema Kota
#Date: 6/03/2023
#Description: The following code will be used to start and run the server, which will be the one that communicates with the database and send information to the client

import socket 
import mysql.connector
from datetime import date
import time

class Server:
    #Initializes the server class
    def __init__(self, port, listen = 50, timeout = 10, buf = 4096, queueSize = 10):
        self.port = port
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen = listen
        self.timeout = timeout
        self.bufsize = buf
        self.counter = 0
    #Function is called when the server sends data to the client
    def send(self, connection, string):
        connection.send(bytes(string,encoding="ascii"))
    #Function is called when the server receives data from the client
    def recv(self, connection):
        self.counter += 1
        print(f"Recieved: {self.counter}")
        return str(connection.recv(self.bufsize), encoding="ascii")
    #Function is called when a certain item or customer is to be checked in the database
    def check_exists(self,table, value, column ,my_db):
        mycur = my_db.cursor()
        value = (value,)
        sql = f"SELECT * FROM {table} WHERE {column} = %s;"
        mycur.execute(sql,value)
        myresult = mycur.fetchall()
        if myresult == []:
            print("Empty set")
            mycur.close()
            return False
        else:
            print(f"Person/item exists: {myresult}")
            mycur.close()
            return True
    #Function is called when the client tries to register a customer
    def server_customer_register(self,connection, my_db):
        print("Registering customer")
        print("Waiting for name")
        name = self.recv(connection)
        name_check = self.check_exists("customers", name, "fname", my_db)
        if name_check == True:
            message = "CUSTOMER EXISTS"
            print(message)
            self.send(connection,message)
            
        elif name_check == False:
            message = "PROCEED"
            self.send(connection,message)
            surname = self.recv(connection) #Receive the surname from the client
            address = self.recv(connection) #Receive the address from the client
            phone_no = self.recv(connection) #Receive the phone number from the client
            phone_no_check = self.check_exists("customers", phone_no,"phone", my_db) #Checks if phone number exists

            #Asks the client to keep sending phone numbers until it gets one that doesnt already exists in the database 
            while phone_no_check == True:
                message = "Phone number already exists"
                self.send(connection, message)
                phone_no = self.recv(connection)
                phone_no_check = self.check_exists("customers", phone_no,"phone", my_db)
            message = "PROCEED"
            self.send(connection,message)
            #Inputting customer details into database
            mycur = my_db.cursor()
            sql = "INSERT INTO customers (fname, sname, address, phone) VALUES (%s, %s, %s, %s);"
            info = [(name, surname, address, phone_no),]
            mycur.executemany(sql, info)
            my_db.commit()
            #print("Customer successfully registered")


            #Checking if all details are correct 
            print(f"===============================================")
            print("CUSTOMER DETAILS")
            print(f"Name: {name}")
            print(f"Surname: {surname}")
            print(f"Address: {address}")
            print(f"Phone number: {phone_no}")
            print("==================================================")     
    #Function is called when the client tries to register an item
    def server_item_register(self, connection, my_db):
        #print("Registering item")
        item_name = self.recv(connection) #Recieve item name from client
        name_check = self.check_exists("items", item_name, "iname", my_db)
        if name_check == True:
            message = "ITEM EXISTS"
            print(message)
            self.send(connection,message) #Send confirmation status to the client
        elif name_check == False:
            message = "PROCEED"
            self.send(connection,message) #Send confirmation to the client
            descrip = self.recv(connection) #Receive the description from the client
            price = float(self.recv(connection)) #Receive the price from the client
            count = int(self.recv(connection)) #Receive the amount from the client
            
            #Inputting customer details into database
            mycur = my_db.cursor()
            sql = "INSERT INTO items (iname, descrip, price, count) VALUES (%s, %s, %s, %s);"
            info = [(item_name, descrip, price, count),]
            mycur.executemany(sql, info)
            my_db.commit()
            #print("Item successfully registered")


            #Checking if all details are correct 
            #print(f"===============================================")
            #print("ITEM DETAILS")
            #print(f"Item name: {item_name}")
            #print(f"Description: {descrip}")
            #print(f"Price: R{price}")
            #print(f"Count: {count}")
            #print("==================================================")     
    #Function is called when the server needs customer details from the database  
    def get_customer(self,customer_name, my_db):
        mycur = my_db.cursor()
        sql = "SELECT * FROM customers WHERE fname = %s"
        name =(customer_name,) 
        mycur.execute(sql,name)
        my_result = mycur.fetchall()
        return my_result[0]
    #Function is called when the server needs item details from the database  
    def get_item(self,item_name, my_db):
        mycur = my_db.cursor()
        sql = "SELECT * FROM items WHERE iname = %s"
        name =(item_name,) 
        mycur.execute(sql,name)
        my_result = mycur.fetchall()
        item = []
        for x in my_result[0]:
            x = str(x)
            item.append(x)
        item = ",".join(item)
        return item
    #Function is called when the server needs to updated the remaining item amount in the database
    def update_item_amount(self, item_name,remaining_amount, my_db):
        #print("Update amount function called")
        mycur = my_db.cursor()
        sql = f"UPDATE items SET count = {remaining_amount} WHERE iname = %s"
        values = (item_name,)
        mycur.execute(sql,values)
        my_db.commit()
    #Function is called when the client tries to buy an item
    def server_buy(self, connection, my_db):
        customer_name = self.recv(connection) #Receive customer name from the client to check if it is registered
        customer_check = self.check_exists("customers", customer_name, "fname", my_db)
        if customer_check == False:
            while customer_check == False:
                customer_status = "Customer not registered" 
                self.send(connection,customer_status) #Send registration status to client
                customer_name = self.recv(connection) #Receive new name from client 
                customer_check = self.check_exists("customers", customer_name, "fname", my_db)
        if customer_check == True:
            customer_status = "Customer registered"
            self.send(connection, customer_status) #Send registration status to client
            customer = self.get_customer(customer_name, my_db)
            #print(f"Customer: {customer}")
            customer_surname = customer[2]
            customer_id = customer[0]
            invoice_id = self.server_create_invoice(my_db, customer_id)
            invoice = open(f"{invoice_id}.txt", "w")
            invoice.write("================INVOICE================\n")
            invoice.write(f"Customer name: {customer_name}\n")
            invoice.write(f"Customer surname: {customer_surname}\n")
            invoice.write(f"Invoice number: {invoice_id}\n")
            invoice.write("=======================================\n")
            invoice.write("ITEMS\n")
            invoice.write("=======================================\n")
            #print(f"invoice id: {invoice_id}")
            self.send(connection, invoice_id) #Send invoice ID to client
            self.send(connection, customer_surname) #Send customer surname to client
            totalPrice = 0
            
            while True:
                item_name = self.recv(connection) #Recieve name of item from client
                if item_name == "xxx" or item_name == 0:
                    break
                #print(f"Item name: {item_name}")
                check_item = self.check_exists("items", item_name, "iname", my_db)
                #print(f"check_item: {check_item}")
                if check_item == False:
                    while check_item == False:
                        #print("ITEM DOESNT EXIST")
                        item_status = "ITEM DOESN'T EXIST"
                        self.send(connection, item_status) #Send status of the item to the client
                        item_name = self.recv(connection) #Recieve new item name from the server
                        check_item = self.check_exists("items", item_name, "iname", my_db)
                if check_item == True:
                    item_status = "ITEM EXISTS"
                    self.send(connection, item_status)  #Send status of the item to the client
                    item = self.get_item(item_name, my_db)
                    self.send(connection, item) #Send item info to client
                    print(f"Item info: {item}")
                    item_id, item_name, item_descr, item_price, item_amount = item.split(",")
                    item_price = float(item_price)
                    item_amount = int(item_amount)
                    if item_amount > 0:
                        invoice.write(f"{item_name}\n")
                        invoice.write(f"{item_descr}\n")
                        invoice.write("+++++++++++++++++++++++++++++++++++++++\n")
                        print("==================================")
                        print(f"Item name: {item_name}")
                        print(f"Item description: {item_descr}")
                        print(f"Item price: R{item_price}")
                        print(f"Max amount: {item_amount}")
                        print("==================================")
                        bought_amount = int(self.recv(connection)) #Receive the amount bought from client
                        invoice.write(f"R{item_price} X {bought_amount}\n")
                        invoice.write(f"---------------------\n")
                        subTotal = item_price * float(bought_amount)
                        totalPrice = round(totalPrice + subTotal, 2)
                        invoice.write(f"R{round(subTotal,2)}\n")
                        invoice.write("=======================================\n")
                        #print(f"Bought amount: {bought_amount}")
                        remaining_amount = int(item_amount) - bought_amount
                        self.update_item_amount(item_name, remaining_amount, my_db)
            #print(f"Total amount: R{totalPrice}")
            invoice.write(f"Total: R{round(float(totalPrice),2)}\n")
            invoice.write("=======================================\n")
            invoice.close()
            self.server_update_invoice(invoice_id, totalPrice, my_db)
    #Function creates an invoice
    def server_create_invoice(self, my_db, customer_id):
        #Create an invoice entry into invoices table
        mycur = my_db.cursor()
        dateBought = date.today()
        sql = "INSERT INTO invoices (custID, dateBought, totalPrice) VALUES (%s, %s, '0')"
        values = (customer_id, dateBought,)
        mycur.execute(sql, values)
        my_db.commit()
        mycur.close()
        #Return invoice id
        mycur = my_db.cursor()
        last_row_sql = "SELECT invoiceID FROM invoices ORDER BY invoiceID DESC LIMIT 1"
        mycur.execute(last_row_sql,)
        result = mycur.fetchall()
        invoice_id = str(result[0][0])
        mycur.close()
        return invoice_id
    #function updates invoice
    def server_update_invoice(self, invoice_id, amountPaid, my_db):
        print("Update invoice function called")
        my_cur = my_db.cursor()
        update_invoice_sql = f"UPDATE invoices SET totalPrice = {amountPaid} WHERE invoiceID = %s"
        values = (invoice_id,)
        my_cur.execute(update_invoice_sql, values,)
        my_db.commit()
        my_cur.close()
    #Function gets invoice
    def server_get_invoice(self, connection,my_db):
        print("Server get invoice called")
        invoice_id = self.recv(connection) #Recieve invoice_id from client
        invoice_check = self.check_exists("invoices", invoice_id, "invoiceID",my_db)
        if invoice_check == False:
            while invoice_check == False:
                print(f"Invoice check: {invoice_check}")
                message = "Invoice doesnt exist"
                self.send(connection, message) #Send invoice status to client
                invoice_id = self.recv(connection) #Recieve invoice_id from client
                print("Made it here")
                invoice_check = self.check_exists("invoices", invoice_id, "invoiceID",my_db)
        message = "PROCEED"
        self.send(connection, message)

        invoice = open(f"{invoice_id}.txt", "r")
        for rec in invoice:
            print(rec.strip())
            self.send(connection,rec)
        message = "End of invoice"
        self.send(connection,message)
        invoice.close()

    def run(self):
        print("Server started...")
        self.soc.bind(('', self.port))
        self.soc.listen(self.listen)
        print("Waiting for connection")
        connection, address = self.soc.accept()#Recieve connection from client
            
        #while True:
        print("Waiting for instruction")
        message = ''
        while message == '':
            message = self.recv(connection) #Receive instruction from client
            print(f"Message in while loop: {message}")
            
        print("Client connected")
        
        my_db = mysql.connector.connect(
            user = "yourUserName",
            password = "yourPassword",
            host = "localhost",
            database = "network_store"
            )
        
        print(f"Message: {message}")
        if message == "Customer Register":
            self.server_customer_register(connection, my_db)
        elif message == "Item Register":
            self.server_item_register(connection, my_db)
        elif message == "Buy Item":
            self.server_buy(connection, my_db)
        elif message == "Get Invoice":
            self.server_get_invoice(connection,my_db)
        elif message == "Quit":
            quit()
        else:
            print("{message} is an invalid instruction")
        self.__init__(8081)
        self.run()
while True:
    print("Initializing server...")
    server = Server(8081, listen = 100)
    server.run()
    print("Server re-ran")