import pandas as pd
import mysql.connector
from mysql.connector import errorcode
import mysql

# MySQL connection setup
db_config = {
    'user': 'root',
    'password': 'nanu2004',
    'host': 'localhost',
    'database': 'atmdb'
}

try:
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    # cursor.execute("DROP TABLE admintable")
    # cursor.execute("DROP TABLE custtable")
    cursor.execute("DROP TABLE dentable")
    cursor.execute("DROP TABLE machinetable")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Access denied. Check your username and password.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist. Create the database first.")
    else:
        print(err)
    exit(1)

#AdminData table creation
# Read the CSV file
csv_file_path = 'AdminData.csv'
df = pd.read_csv(csv_file_path)

# Define the table name
table_name = 'admintable'

# Define the table creation query
create_table_query = f"""
    CREATE TABLE {table_name} (
        admin_username VARCHAR(255),
        admin_password VARCHAR(255),
        security_question VARCHAR(255),
        security_answer VARCHAR(255),
        login_flag INT,
        pin INT,
        PRIMARY KEY (admin_username)
    )
"""

# Execute the table creation query
try:
    cursor.execute(create_table_query)
    print(f"Table '{table_name}' created successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

# Insert data into the table
for index, row in df.iterrows():
    insert_query = f"""
        INSERT INTO {table_name} 
        (admin_username, admin_password, security_question, security_answer, login_flag, pin) 
        VALUES 
        (%s, %s, %s, %s, %s, %s)
    """
    data = (row['admin username'], row['password'], row['security question'], row['answer'],
            row['login flag'], row['pin'])

    try:
        cursor.execute(insert_query, data)
        cnx.commit()

    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")

# CustomerData Table Creation
# Read the CSV file
csv_file_path = 'CustData.csv'
df = pd.read_csv(csv_file_path)

# Define the table name
table_name = 'CustTable'

# Define the table creation query
create_table_query = f"""
    CREATE TABLE {table_name} (
        Accno INT,
        Account_Holder_Name VARCHAR(255),
        User_Name VARCHAR(255),
        Password VARCHAR(255),
        Account_Balance INT,
        DOB VARCHAR(255),
        Mobile_Number VARCHAR(15),
        Login_Flag INT,
        PIN VARCHAR(64),
        PRIMARY KEY (Accno)
    )
"""

# Execute the table creation query
try:
    cursor.execute(create_table_query)
    print(f"Table '{table_name}' created successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

# Insert data into the table
for index, row in df.iterrows():
    insert_query = f"""
        INSERT INTO {table_name} 
        (Accno, Account_Holder_Name, User_Name, Password, Account_Balance, DOB, Mobile_Number, Login_Flag, PIN) 
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (
        row['Accno'], row['Account Holder Name'], row['user name'], row['password'],
        row['account balance'], row['DOB'], row['Mobile number'], row['login flag'], row['pin']
    )

    try:
        cursor.execute(insert_query, data)
        cnx.commit()

    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")

# MachineTable Creation
# Read the CSV file
csv_file_path = 'MachineData.csv'
df = pd.read_csv(csv_file_path)

# Define the table name
table_name = 'MachineTable'

# Define the table creation query
create_table_query = f"""
    CREATE TABLE {table_name} (
        MachineID INT,
        Location VARCHAR(255),
        MaintenanceSchedule VARCHAR(255),
        Status VARCHAR(255),
        CashBalance DECIMAL(10, 2),
        PRIMARY KEY (MachineID)
    )
"""

# Execute the table creation query
try:
    cursor.execute(create_table_query)
    print(f"Table '{table_name}' created successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

# Insert data into the table
for index, row in df.iterrows():
    insert_query = f"""
        INSERT INTO {table_name} 
        (MachineID, Location, MaintenanceSchedule, Status, CashBalance) 
        VALUES 
        (%s, %s, %s, %s, %s)
    """
    data = (
        row['MachineID'], row['Location'], row['MaintenanceSchedule'], row['Status'], row['CashBalance']
    )

    try:
        cursor.execute(insert_query, data)
        cnx.commit()

    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")

# DenominationTable Creation
# Read the CSV file
csv_file_path = 'DenData.csv'
df = pd.read_csv(csv_file_path)

# Define the table name
table_name = 'DenTable'

# Define the table creation query
create_table_query = f"""
    CREATE TABLE {table_name} (
        MachineID INT,
        Money_loaded INT,
        FOREIGN KEY (MachineID) REFERENCES MachineTable(MachineID)
    )
"""

# Execute the table creation query
try:
    cursor.execute(create_table_query)
    print(f"Table '{table_name}' created successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

# Insert data into the table
for index, row in df.iterrows():
    insert_query = f"""
        INSERT INTO {table_name} 
        (MachineID, Money_loaded) 
        VALUES 
        (%s, %s)
    """
    data = (
        int(row['MachineID']), int(row['Money_loaded']))

    try:
        cursor.execute(insert_query, data)
        cnx.commit()

    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
try:
    cnx = mysql.connector.connect(
        user='root',
        password='nanu2004',
        host='localhost',
        database='atmdb'
    )

    cursor = cnx.cursor()

    # Define the structure of the transaction_table
    transaction_table_definition = (
        "CREATE TABLE transaction_table ("
        "  TID INT AUTO_INCREMENT PRIMARY KEY,"
        "  Accno INT NOT NULL,"
        "  trans_amt DECIMAL(10, 2) NOT NULL,"
        "  transaction_type CHAR(1) NOT NULL,"
        "  amount DECIMAL(10, 2) NOT NULL,"
        "  transaction_time_stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "  FOREIGN KEY (Accno) REFERENCES CustTable(Accno)"
        ")"
    )

    # Create the transaction_table
    cursor.execute(transaction_table_definition)

    print("Transaction table created successfully.")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Access denied. Check your username and password.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist.")
    else:
        print(err)
cursor.close()
cnx.close()