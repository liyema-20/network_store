#Author name: Liyema Kota
#Date: 6/03/2023
#Description: The following code will be used by the user to send and request information from the server.

import socket
import time
import re

class Client:
    #Initialize the class
    def __init__(self, host, port, bufsize = 1024, timeout = 100):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.timeout = timeout
    #Function called when connection to server
    def connect(self):
        self.client.connect((self.host, self.port))
        print("Connection Opened")
    #Function called when closing the connection
    def close(self):
        self.client.close()
        print("Connection Closed")
    #Function called when client receives data from server
    def recv(self):
        return str(self.client.recv(self.bufsize), encoding="ascii")
    #Function called when client sends data to the server
    def send(self, string):
        return str(self.client.send(bytes(string, "ascii")))
    #Function called when client tries to register
    def client_customer_register(self):
        name = str(input("Name: "))
        self.send(name)
        client_confirmation_message = self.recv()

        if client_confirmation_message == "CUSTOMER EXISTS":
            print("Customer already registered")
            #self.customer_register_menu()
        elif client_confirmation_message == "PROCEED":
            surname = input("Surname: ")
            self.send(surname)
            address = input("Address: ")
            self.send(address)
            phone_no = input("Phone number: ")
            pattern = "^[0][0-9]{9}$"
            checked = re.search(pattern, phone_no)
            while checked == None:
                phone_no = input("Please enter 10 digit phone number begininning with 0: ")
                pattern = "^0[0-9]{9}$"
                checked = re.search(pattern, phone_no)
            self.send(phone_no)
            print("Waiting for phone confirmation")
            message = self.recv()

            while message == "Phone number already exists":
                print("Phone number already exists")
                phone_no = input("Phone number: ")
                self.send(phone_no)
                #print("Waiting for phone confirmation")
                message = self.recv()
            print("Customer successfully registered")
            #self.customer_register_menu()
    #Function called when client tries to register an item
    def client_item_register(self):
        item_name = str(input("Item name: "))
        self.send(item_name) #Send item name to server
        confirmation_message = self.recv() #Recieve confirmation status from server

        if confirmation_message == "ITEM EXISTS":
            print("Item already registered")
            #self.item_register_menu() 
        elif confirmation_message == "PROCEED":
            descrip = input("Description: ")
            self.send(descrip)
            price = input("Price: ")
            self.send(price)
            count = input("Amount of item: ")
            self.send(count)
            print("Item successfully registered")
    #Client called when client buys items
    def client_buy(self):
        customer_name = input("Name of customer: ")
        self.send(customer_name)# Sending name of customer to server to check if customer is registered
        customer_check = self.recv() #Receieving status of customers registration status
        #print(f"Register check: {customer_check}")
        if customer_check == "Customer not registered":
            while customer_check == "Customer not registered": #Keep requesting a customer name until a registered customer is entered
                print("Customer not registered")
                customer_name = input("Name of customer: ")
                self.send(customer_name) # Sending new name of customer to server to check if customer is registered
                customer_check = self.recv() #Receieving status of customers registration status
        if customer_check == "Customer registered":
            #print("Customer is registered")
            invoice_id = self.recv() #Recieve the invoice id from the server
            customer_surname = self.recv() #Recieve the customers surname from the server
            totalPrice = 0
        print("Enter items you would like to purchase. Enter xxx when done")
        item_name = input("Item name: ")
        while item_name != "xxx":
            self.send(item_name) #Send the name of the item to the server to check if it exists
            item_check = self.recv() #Recieve registration status of the item
            
            if item_check == "ITEM DOESN'T EXIST": #If the item doesnt exist keep requesting items until one that exists is entered
                while item_check == "ITEM DOESN'T EXIST":
                    print("Item doesn't exist")
                    item_name = input("Item name: ")
                    self.send(item_name) #Send the name of the item to the server to check if it exists
                    item_check = self.recv() #Recieve registration status of the item
            if item_check == "ITEM EXISTS":
                #print(f"Item check 2: {item_check}")
                item = self.recv() #Receive item info from server
                item_id, item_name ,item_descr, item_price, max_amount = item.split(",")
                item_price = float(item_price)
                max_amount = int(max_amount)
                print(f"item_descr: {item_descr}")
                print(f"item_price: {item_price}")
                print(f"Max amount: {max_amount}")
                

            if max_amount == 0:
                print("Item out of stock")
                amount = 0
            elif max_amount > 0:
                amount = int(input("Amount: "))     #Get the amount of required items
                while amount > max_amount:
                    print("Not enough in stock")
                    amount = int(input("Amount: "))
                self.send(str(amount))   #Send the purchased amount to the server
                
            item_name = input("Item name: ")
        self.send(item_name)
        #print("Made it here")
        invoice = open(f"{invoice_id}.txt","r")
        print(invoice.read())
        invoice.close()
    #Function called when client wants their invoice
    def client_get_invoice(self):
        invoice_id = input("Please input invoice id: ")
        self.send(str(invoice_id)) #Send invoice id to server
        #print("Waiting for confirmation status")
        invoice_confirmation = self.recv() #Receive invoice status from server
        #print(f"Confirmation status: {invoice_confirmation}")
        if invoice_confirmation == "Invoice doesnt exist":
            while invoice_confirmation == "Invoice doesnt exist":
                print("Invoice id doesn't exist")
                invoice_id = input("Please input invoice id: ")
                self.send(str(invoice_id)) #Send invoice id to server
                invoice_confirmation = self.recv() #Receive invoice status from server
        data = ''
        n = 0
        while data != "End of invoice":
            data = self.recv()
            if data == "End of invoice":
                break
            else:
                if n == 20:
                    break
                print(data.strip())
                n += 1    
            
    def customer_register_menu(self):
        print("=========================================================")
        print("|1. Register Another customer                           |")
        print("|2. Return to main menu                                 |")
        print("|3. Exit program                                        |")
        print("=========================================================")
        choice = input("Choice: ")
        if choice == "1":
            message = "Customer Register"
            self.send(message)
            self.client_customer_register()
        elif choice == "2":
            self.main_menu()
        elif choice == "3":
            message = "Quit"
            self.send(message)
            print("Thank you for using the program")
            quit()
        else:
            print("INVALID CHOICE!")
            self.customer_register_menu() 
    #Main menu displays the application options
    def main_menu(self):
        print("===========================================")
        print("|               NETWORK STORE              |")
        print("===========================================") 
        print("|1. Register customer                      |")
        print("|2. Register Item                          |")
        print("===========================================") 
        print("|3. Buy Items                              |")
        print("|4. Request Invoice                        |")
        print("===========================================") 
        print("|x. Exit                                   |")
        print("===========================================")
        choice = str(input("Choice: "))
        if choice == "1":
            message = "Customer Register"
            self.send(message)
            self.client_customer_register()
        elif choice == "2":
            message = "Item Register"
            self.send(message)
            self.client_item_register()
        elif choice == "3":
            message = "Buy Item"
            self.send(message)
            self.client_buy() 
        elif choice == "4":
            message = "Get Invoice"
            self.send(message)
            self.client_get_invoice()
            print("Invoice function completed")   
        elif choice == "x":
            message = "Quit"
            self.send(message)
            print("Thank you for using the program")
            quit()
        else:
            print("Invalid choice")
            self.main_menu()
        time.sleep(1)
        self.__init__('localhost', 8081)
        self.connect()
        self.main_menu()
    def item_register_menu(self):
        print("=========================================================")
        print("|1. Register Another Item                               |")
        print("|2. Return to main menu                                 |")
        print("|3. Exit program                                        |")
        print("=========================================================")
        choice = input("Choice: ")
        
        if choice == "1":
            message = "Item Register"
            self.send(message)
            self.client_item_register()
        elif choice == "2":
            self.main_menu()
        elif choice == "3":
            message = "Quit"
            self.send(message)
            print("Thank you for using the program")
            quit()
        else:
            print("INVALID CHOICE")
            self.item_register_menu()



while True:
    client = Client('localhost', 8081)
    client.connect()
    client.main_menu()

