import mysql.connector
from mysql.connector import errorcode
from getpass import getpass
from datetime import datetime
from tabulate import tabulate
import random
import csv
import hashlib
# MySQL connection setup
db_config = {
    'user': 'root',
    'password': 'nanu2004',
    'host': 'localhost',
    'database': 'atmdb'
}

try:
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Access denied. Check your username and password.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist. Create the database first.")
    else:
        print(err)
    exit(1)

# Function to authenticate administrators
def authenticate_admin(username, password):
    query = "SELECT * FROM admintable WHERE admin_username = %s AND admin_password = %s"
    cursor.execute(query, (username, password))
    admin = cursor.fetchone()
    return admin

# Function to reset PIN for administrators
def reset_admin_pin(admin):
    new_pin = input("Enter new 4-digit PIN: ")
    password = getpass("Confirm password: ")
    security_answer = input(f"Answer the security question: {admin['security_question']}\n")
    
    if password == admin['admin_password'] and security_answer.lower() == admin['security_answer'].lower():
        update_query = "UPDATE admintable SET pin = %s, login_flag = '1' WHERE admin_username = %s"
        cursor.execute(update_query, (new_pin, admin['admin_username']))
        cnx.commit()
        print("PIN reset successful.")
    else:
        print("Authentication failed. PIN reset canceled.")

def view_atm_status():
    query = "SELECT * FROM MachineTable"
    cursor.execute(query)
    machine_data = cursor.fetchall()

    if machine_data:
        headers = machine_data[0].keys()
        rows = [tuple(row.values()) for row in machine_data]
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
    else:
        print("No data found in MachineTable.")

# Function to print custtable in table form
def print_custtable():
    query = "SELECT Accno, Account_Holder_Name, User_Name, Account_Balance, DOB, Mobile_Number, Login_Flag FROM custtable"
    cursor.execute(query)
    cust_data = cursor.fetchall()

    if cust_data:
        headers = cust_data[0].keys()
        rows = [tuple(row.values()) for row in cust_data]
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
    else:
        print("No data found in custtable.")

# Function to add a new customer
def add_customer():
    # Get input from admin for all columns
    account_holder_name = input("Enter Account Holder Name: ")
    user_name = input("Enter User Name: ")
    password = getpass("Enter Password: ")
    dob = input("Enter Date of Birth (YYYY-MM-DD): ")
    mobile_number = input("Enter Mobile Number: ")
    account_balance = float(input("Enter Account Balance: "))  # Assume a float for the balance

    # Generate a random 4-digit PIN
    pin = str(random.randint(1000, 9999))

    # Get the last account number from the custtable
    last_account_query = "SELECT MAX(Accno) as last_account FROM custtable"
    cursor.execute(last_account_query)
    last_account_result = cursor.fetchone()
    last_account = last_account_result['last_account']

    # Assign an account number one greater than the previous last account number
    accno = str(int(last_account) + 1)

    # Insert new customer into custtable
    insert_query = """
        INSERT INTO custtable (Accno, Account_Holder_Name, User_name, Password, PIN, DOB, Mobile_Number, Account_Balance, Login_Flag)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '0')
    """
    data = (accno, account_holder_name, user_name, password, pin, dob, mobile_number, account_balance)
    
    try:
        cursor.execute(insert_query, data)
        cnx.commit()
        print("New customer added successfully.")

    except mysql.connector.Error as err:
        print(f"Error adding customer: {err}")

# Function to modify customer details
def modify_customer():
    print_custtable()  # Print custtable before modification

    # Get the account holder name to modify
    account_holder_name_to_modify = input("Enter the Account Holder Name to modify: ")

    # Get input from admin for the new values
    new_account_holder_name = input("Enter new Account Holder Name: ")
    new_user_name = input("Enter new User Name: ")
    # ... (Ask for other columns to modify)

    # Update the customer details in custtable
    update_query = "UPDATE custtable SET Account_Holder_Name = %s, User_Name = %s WHERE Account_Holder_Name = %s"
    data = (new_account_holder_name, new_user_name, account_holder_name_to_modify)

    try:
        cursor.execute(update_query, data)
        cnx.commit()
        print("Customer details modified successfully.")

    except mysql.connector.Error as err:
        print(f"Error modifying customer details: {err}")

# Function to delete a customer
def delete_customer():
    print_custtable()  # Print custtable before deletion

    # Get the account holder name to delete
    account_holder_name_to_delete = input("Enter the Account Holder Name to delete: ")

    # Delete the customer from custtable
    delete_query = "DELETE FROM custtable WHERE Account_Holder_Name = %s"
    
    try:
        cursor.execute(delete_query, (account_holder_name_to_delete,))
        cnx.commit()
        print("Customer deleted successfully.")

    except mysql.connector.Error as err:
        print(f"Error deleting customer: {err}")

# Function to check if transtable exists
def is_transtable_exists():
    try:
        cursor.execute("SELECT 1 FROM transtable LIMIT 1")
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_NO_SUCH_TABLE:
            return False
        else:
            return False

# Function to export transaction logs from transtable to a CSV file
def export_transaction_logs():
    if not is_transtable_exists():
        print("No transaction logs exist")
        return None

    select_query = "SELECT * FROM transtable"
    if cursor.execute(select_query).rowcount():
        transaction_logs = cursor.fetchall()

    if transaction_logs:
        file_name = "transaction_logs.csv"
        with open(file_name, 'w', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=transaction_logs[0].keys())
            csv_writer.writeheader()

            for log in transaction_logs:
                # Convert timestamp to a readable format
                log['Date_Time'] = log['Date_Time'].strftime("%Y-%m-%d %H:%M:%S")
                csv_writer.writerow(log)

        print(f"Transaction logs exported to {file_name} successfully.")
    else:
        print("No transaction logs found.")

def view_machine_table():
    query = "SELECT * FROM MachineTable"
    cursor.execute(query)
    machine_data = cursor.fetchall()

    if machine_data:
        headers = machine_data[0].keys()
        rows = [tuple(row.values()) for row in machine_data]
        print("\nMachineTable:")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
    else:
        print("No data found in MachineTable.")

# Administrator Dashboard
def admin_dashboard(admin):
    while True:
        print("\nAdmin Dashboard (XYZ Bank ATM)")
        print("1. Reset PIN")
        print("2. View ATM Status")
        print("3. Manage Users")
        print("4. Cash Management")
        print("5. Transaction Logs")
        print("6. Exit")
        
        option = input("Enter option: ")
        
        if option == '1':
            reset_admin_pin(admin)
        elif option == '2':
            print("Viewing ATM Status...")
            view_atm_status()
        elif option == '3':
            print("Managing Users...")
            print_custtable()  # Print custtable before entering the submenu
            # Submenu for managing users
            print("\nManage Users Submenu:")
            print("1. Add Customer")
            print("2. Modify Customer Details")
            print("3. Delete Customer")
            print("4. Back to Main Menu")

            manage_users_option = input("Enter option: ")

            if manage_users_option == '1':
                add_customer()
            elif manage_users_option == '2':
                modify_customer()
            elif manage_users_option == '3':
                delete_customer()
            elif manage_users_option == '4':
                continue  # Go back to the main menu
            else:
                print("Invalid option. Please try again.")
        elif option == '4':
            print("Cash Management...")
            view_machine_table()
            mid = input("Enter the machine ID you want to manage: ")
            while True:
                
                print("\nCash Management Operations:")
                print("1. Load Cash")
                print("2. Dispense Cash (Sample Withdrawal)")
                print("3. Empty Cash Cassettes")
                print("4. Back to Main Menu")
                ch=input("Your choice: ")
                if ch=='1':
                    print("Cash Loading")
                    # Cash loading algo
                elif ch=='2':
                    print("Withdrawl Sample")
                    # Sample withdrawl algo
                elif ch=='3':
                    print("Emptying cash casettes")
                elif ch=='4':
                    print("Exitting!!")
                    break
                else:
                    print("Invalid choice!!")
        elif option == '5':
            print("Viewing Transaction Logs...")
            export_transaction_logs();
        elif option == '6':
            print("Exiting Admin Dashboard.")
            break
        else:
            print("Invalid option. Please try again.")
# Function to authenticate the account holder
def authenticate_user(accno, pin):
    query = "SELECT * FROM CustTable WHERE Accno = %s"
    cursor.execute(query, (accno,))
    user_data = cursor.fetchone()

    if user_data:
        if user_data['Login_Flag'] == 0:
            # First-time login, ask to change PIN and set security question
            mobile_number = input("Enter your mobile number for security: ")

            if mobile_number == user_data['Mobile_Number']:
                new_pin = input("Enter your new 4-digit PIN: ")
                
                # Update PIN, security question, and set LoginFlag to 1
                update_query = "UPDATE CustTable SET PIN = %s, Login_Flag = 1 WHERE Accno = %s"
                cursor.execute(update_query, (hashlib.sha256(new_pin.encode()).hexdigest(), accno))
                cursor.execute("ALTER TABLE CustTable MODIFY COLUMN PIN VARCHAR(64)");
                cnx.commit()

                print("PIN and security question set. You can now log in with your new PIN.")
                return False
            else:
                print("Invalid mobile number. First-time login failed.")
                return False
        else:
            # Subsequent login, ask for PIN
            entered_pin = input("Enter your PIN: ")
            if hashlib.sha256(entered_pin.encode()).hexdigest() == user_data['PIN']:
                return True
            else:
                print("Incorrect PIN. Login failed.")
                return False
    else:
        print("Account not found. Login failed.")
        return False

# Function to set a new PIN for the account holder
def set_pin(accno, new_pin):
    mobile_number = input("Enter your mobile number for security: ")

    query = "SELECT * FROM CustTable WHERE Accno = %s AND Mobile_Number = %s"
    cursor.execute(query, (accno, mobile_number))
    user_data = cursor.fetchone()

    if user_data:
        update_query = "UPDATE CustTable SET PIN = %s WHERE Accno = %s"
        cursor.execute(update_query, (hashlib.sha256(new_pin.encode()).hexdigest(), accno))
        cnx.commit()
        print("PIN successfully set.")
    else:
        print("Invalid mobile number. PIN set failed.")

# Function to perform a transaction (Deposit/Withdrawal)
def perform_transaction(accno, trans_amt, transaction_type):
    query = "SELECT * FROM CustTable WHERE Accno = %s"
    cursor.execute(query, (accno,))
    user_data = cursor.fetchone()

    if user_data:
        # Validate PIN
        entered_pin = input("Enter your PIN: ")
        if hashlib.sha256(entered_pin.encode()).hexdigest() == user_data['PIN']:
            # Process the transaction and update account balance
            new_balance = user_data['Account_Balance'] + trans_amt if transaction_type == 'D' else user_data['Account_Balance'] - trans_amt
            update_query = "UPDATE CustTable SET Account_Balance = %s WHERE Accno = %s"
            cursor.execute(update_query, (new_balance, accno))
            cnx.commit()

            # Record the transaction in the account_transactions table
            insert_query = "INSERT INTO transaction_table (Accno, trans_amt, transaction_type, amount, transaction_time_stamp) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (accno, trans_amt, transaction_type, new_balance, datetime.now()))
            cnx.commit()

            print("Transaction successful.")
        else:
            print("Incorrect PIN. Transaction failed.")
    else:
        print("Account not found. Transaction failed.")

# Function to view the statement of last ten transactions
def view_transaction_history(accno):
    query = "SELECT * FROM transaction_table WHERE Accno = %s ORDER BY Transaction_Time_Stamp DESC LIMIT 10"
    cursor.execute(query, (accno,))
    transaction_history = cursor.fetchall()

    if transaction_history:
        headers = transaction_history[0].keys()
        rows = [tuple(row.values()) for row in transaction_history]
        print("\nTransaction History:")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
    else:
        print("No transaction history found.")
#User Dashboard Function
def user_dashboard():
    accno = input("Enter your Account Number: ")

    if authenticate_user(accno, None):
        while True:
            print("\nUser Dashboard (XYZ Bank ATM)")
            print("1. Check Balance")
            print("2. Withdraw Cash")
            print("3. Deposit Funds")
            print("4. Change PIN")
            print("5. View Transaction History")
            print("6. Exit")

            choice = input("Please enter your choice: ")

            if choice == '1':
                query = "SELECT Account_Balance FROM CustTable WHERE Accno = %s"
                cursor.execute(query, (accno,))
                balance = cursor.fetchone()['Account_Balance']
                print(f"Your current balance: {balance}")
            elif choice == '2':
                withdrawal_amount = float(input("Enter the withdrawal amount: "))
                perform_transaction(accno, withdrawal_amount, 'W')
            elif choice == '3':
                deposit_amount = float(input("Enter the deposit amount: "))
                perform_transaction(accno, deposit_amount, 'D')
            elif choice == '4':
                new_pin = input("Enter your new 4-digit PIN: ")
                set_pin(accno, new_pin)
            elif choice == '5':
                view_transaction_history(accno)
            elif choice == '6':
                print("Exiting User Dashboard.")
                break
            else:
                print("Invalid choice. Please try again.")


# Main program
def main():
    while True:
        print("Welcome to XYZ Bank")
        print("\nChoose the dashboard you want to access:")
        print("1. Admin\n")
        print("2. Customer\n")
        print("3. Exit\n")
        ch=input("Your choice: ")
        if ch=='1':
            print("Welcome to admin dashboard\n")
            username = input("Enter username: ")
            password = getpass("Enter password: ")

            admin = authenticate_admin(username, password)

            if admin:
                print(f"Welcome, {admin['admin_username']}!")
                if(admin['login_flag']==0):
                    print("You have to reset your pin first!")
                    reset_admin_pin(admin)
                admin_dashboard(admin)
            else:
                print("Authentication failed. Invalid username or password.")
        elif ch=='2':
            print("Welcome to customer dashboard!\n")
            user_dashboard()
        elif ch=='3':
            print("Thank You for using our ATM!")
            break
        else:
            print("Invalid choice, try again!!")
if __name__ == "__main__":
    main()

# Close the database connection
cursor.close()
cnx.close()