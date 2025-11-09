# ---------------------------------------------------------
# RAILWAY RESERVATION SYSTEM PROJECT
# Developed by: Nitin P.
# Class: 12
# Description:
# Python + MySQL project for booking, checking, and cancelling
# train tickets. Includes distance-based fares, multiple
# passenger support, and SQL-style table display for all tickets.
# ---------------------------------------------------------

import mysql.connector

# ---------------------------------------------------------
# DATABASE CONNECTION SETUP
# ---------------------------------------------------------
mycon = mysql.connector.connect(host='localhost', user='root', passwd='12345')
cursor = mycon.cursor()
mycon.autocommit = True

cursor.execute("CREATE DATABASE IF NOT EXISTS railway")
cursor.execute("USE railway")

# main ticket table
cursor.execute("""
CREATE TABLE IF NOT EXISTS railway(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phno VARCHAR(15),
    age INT(4),
    gender VARCHAR(20),
    from_f VARCHAR(100),
    to_t VARCHAR(100),
    date_d VARCHAR(20),
    train_no VARCHAR(10),
    train_name VARCHAR(100),
    class VARCHAR(20),
    total_cost FLOAT(10,2)
)
""")

# user accounts table
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_accounts(
    fname VARCHAR(100),
    lname VARCHAR(100),
    user_name VARCHAR(100),
    password VARCHAR(100) PRIMARY KEY,
    phno VARCHAR(15),
    gender VARCHAR(50),
    dob VARCHAR(50),
    age VARCHAR(4)
)
""")

# ---------------------------------------------------------
# SIGN IN / SIGN UP FUNCTIONS
# ---------------------------------------------------------
def signup():
    print("\n\t\t--- SIGN UP ---")
    fname = input("First Name: ")
    lname = input("Last Name: ")
    user_name = input("Username: ")
    password = input("Password: ")
    confirm = input("Re-enter Password: ")
    phno = input("Phone Number: ")
    print("M = Male | F = Female | N = Not to mention")
    gender_input = input("Enter Gender: ").lower()
    gender_map = {'m': 'Male', 'f': 'Female', 'n': 'Not to mention'}
    gender = gender_map.get(gender_input, 'Not to mention')
    dob = input("Date of Birth (DD/MM/YYYY): ")
    age = input("Age: ")

    if password != confirm:
        print("Passwords do not match.")
        return

    cursor.execute("INSERT INTO user_accounts VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                   (fname, lname, user_name, password, phno, gender, dob, age))
    print("\nAccount created successfully!")
    user_menu()


def signin():
    print("\n\t\t--- SIGN IN ---")
    user = input("Username: ")
    pwd = input("Password: ")
    
    # FIXED: Check both username and password in the query
    cursor.execute("SELECT * FROM user_accounts WHERE user_name=%s AND password=%s", (user, pwd))
    data = cursor.fetchone()
    
    if data:
        print("Login successful!")
        user_menu()
    else:
        print("Invalid credentials or account not found.")


# ---------------------------------------------------------
# BOOKING FUNCTION
# ---------------------------------------------------------
def ticket_booking():
    print("\n\t\t--- TICKET BOOKING ---")

    routes = [
        {"no": "11020", "name": "Konark Express", "from": "Chennai", "to": "Mumbai", "distance": 1250},
        {"no": "12301", "name": "Rajdhani Express", "from": "Delhi", "to": "Kolkata", "distance": 1500},
        {"no": "12025", "name": "Shatabdi Express", "from": "Bangalore", "to": "Hyderabad", "distance": 570},
        {"no": "16507", "name": "Jodhpur Express", "from": "Pune", "to": "Jaipur", "distance": 1100},
        {"no": "12621", "name": "Tamil Nadu Express", "from": "Chennai", "to": "Delhi", "distance": 2180}
    ]

    print("\nAvailable Routes:\n")
    for i, r in enumerate(routes, 1):
        print(f"{i}. {r['from']} -> {r['to']} | Train No: {r['no']} | Name: {r['name']} | Distance: {r['distance']} km")

    try:
        route_choice = int(input("\nChoose Route (1-5): "))
        if not (1 <= route_choice <= len(routes)):
            print("Invalid route.")
            return
    except ValueError:
        print("Invalid input.")
        return

    route = routes[route_choice - 1]

    classes = {
        "1": ("Sleeper", 0.75),
        "2": ("3rd AC", 1.25),
        "3": ("2nd AC", 1.75),
        "4": ("1st AC", 2.5)
    }

    print("\nAvailable Classes and Approx Prices:")
    for key, val in classes.items():
        price = route["distance"] * val[1]
        print(f"{key}. {val[0]} - ₹{price:.2f}")

    class_choice = input("Select Class (1-4): ")
    if class_choice not in classes:
        print("Invalid class.")
        return

    train_class, multiplier = classes[class_choice]
    cost_per_ticket = route["distance"] * multiplier

    try:
        tickets = int(input("Enter number of tickets: "))
        if tickets <= 0:
            print("Invalid ticket number.")
            return
    except ValueError:
        print("Invalid input.")
        return

    total_cost = cost_per_ticket * tickets
    print(f"\nTotal fare for {tickets} ticket(s): ₹{total_cost:.2f}")

    confirm = input("Confirm booking? (Y/N): ").upper()
    if confirm != 'Y':
        print("Booking cancelled.")
        return

    phno = input("Contact Phone Number for booking: ")
    date = input("Date of Journey (DD/MM/YYYY): ")

    # Input details for all passengers
    passenger_list = []
    for i in range(1, tickets+1):
        print(f"\nPassenger {i} details:")
        name = input("Name: ")
        age = int(input("Age: "))
        gender = input("Gender (M/F/N): ").upper()
        gender_map = {'M': 'Male', 'F': 'Female', 'N': 'Not to mention'}
        gender = gender_map.get(gender, 'Not to mention')
        passenger_list.append((name, phno, age, gender, route["from"], route["to"], date, route["no"], route["name"], train_class, cost_per_ticket))

    # Save all passengers to DB
    for p in passenger_list:
        cursor.execute("""
        INSERT INTO railway (name, phno, age, gender, from_f, to_t, date_d, train_no, train_name, class, total_cost)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, p)

    print("\n--- BOOKING CONFIRMED ---")
    print(f"Train: {route['name']} ({route['no']}) | Class: {train_class} | Date: {date}")
    print(f"Number of Passengers: {tickets}")
    print(f"Total Cost: ₹{total_cost:.2f}")
    print("---------------------------")


# ---------------------------------------------------------
# TICKET CHECKING / CANCELLING / ACCOUNT FUNCTIONS
# ---------------------------------------------------------
def ticket_checking():
    print("\n\t\t--- CHECK BOOKED TICKET ---")
    phno = input("Enter your Phone Number: ")
    cursor.execute("SELECT * FROM railway WHERE phno=%s", (phno,))
    data = cursor.fetchall()
    if not data:
        print("No ticket found for this number.")
        return

    print("\n--- Ticket Details ---")
    headers = ['ID', 'Name', 'Phone', 'Age', 'Gender', 'From', 'To', 'Date', 'Train No', 'Train Name', 'Class', 'Cost']
    for row in data:
        for h, val in zip(headers, row):
            print(f"{h}: {val}")
        print("----------------------------")


def ticket_cancelling():
    print("\n\t\t--- CANCEL TICKET ---")
    phno = input("Enter Phone Number: ")
    cursor.execute("SELECT * FROM railway WHERE phno=%s", (phno,))
    data = cursor.fetchall()
    if not data:
        print("No ticket found.")
        return
    cursor.execute("DELETE FROM railway WHERE phno=%s", (phno,))
    print("Ticket(s) cancelled successfully.")


def display_account_details():
    print("\n\t\t--- ACCOUNT DETAILS ---")
    user = input("Username: ")
    pwd = input("Password: ")
    cursor.execute("SELECT fname, lname, phno, gender, dob, age FROM user_accounts WHERE user_name=%s AND password=%s", (user, pwd))
    data = cursor.fetchone()
    if not data:
        print("No account found.")
        return
    print("\n--- Your Account Info ---")
    labels = ['First Name', 'Last Name', 'Phone', 'Gender', 'DOB', 'Age']
    for i in range(len(labels)):
        print(f"{labels[i]}: {data[i]}")


# ---------------------------------------------------------
# VIEW ALL TICKETS (SQL-style table)
# ---------------------------------------------------------
def display_all_tickets():
    print("\n\t\t--- ALL BOOKED TICKETS ---")
    cursor.execute("SELECT * FROM railway")
    rows = cursor.fetchall()
    if not rows:
        print("No tickets booked yet.")
        return

    headers = ["ID", "Name", "Phone", "Age", "Gender", "From", "To", "Date", "Train No", "Train Name", "Class", "Cost"]

    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        max_len = len(header)
        for row in rows:
            max_len = max(max_len, len(str(row[i])))
        col_widths.append(max_len + 2)

    border = "+" + "+".join("-" * w for w in col_widths) + "+"
    print(border)
    header_row = "|"
    for i, header in enumerate(headers):
        header_row += f"{header:^{col_widths[i]}}|"
    print(header_row)
    print(border)

    for row in rows:
        row_str = "|"
        for i, item in enumerate(row):
            row_str += f"{str(item):^{col_widths[i]}}|"
        print(row_str)
    print(border)


# ---------------------------------------------------------
# TICKET BILL
# ---------------------------------------------------------
def ticket_bill():
    print("\n\t\t--- TICKET BILL ---")
    phno = input("Enter Contact Phone Number: ")
    cursor.execute("SELECT * FROM railway WHERE phno=%s", (phno,))
    data = cursor.fetchall()
    if not data:
        print("No tickets found for this number.")
        return

    print("\n======= TICKET BILL =======")
    print(f"Phone Number: {phno}")
    print(f"Train: {data[0][9]} ({data[0][8]})")
    print(f"From: {data[0][5]}  To: {data[0][6]}")
    print(f"Class: {data[0][10]}")
    print(f"Date of Journey: {data[0][7]}")
    print("\nPassengers:")
    print("----------------------------")
    total_amount = 0
    for i, row in enumerate(data, 1):
        print(f"{i}. {row[1]} | Age: {row[3]} | Gender: {row[4]} | Cost: ₹{row[11]:.2f}")
        total_amount += row[11]
    print("----------------------------")
    print(f"Total Amount Payable: ₹{total_amount:.2f}")
    print("============================")


# ---------------------------------------------------------
# MAIN USER MENU
# ---------------------------------------------------------
def user_menu():
    while True:
        print("\n\t\t--- MAIN MENU ---")
        print("1. Ticket Booking")
        print("2. Check Ticket")
        print("3. Cancel Ticket")
        print("4. Account Details")
        print("5. View All Tickets")
        print("6. Ticket Bill")
        print("7. Logout")

        try:
            ch = int(input("Enter choice: "))
        except ValueError:
            print("Enter valid number.")
            continue

        if ch == 1:
            ticket_booking()
        elif ch == 2:
            ticket_checking()
        elif ch == 3:
            ticket_cancelling()
        elif ch == 4:
            display_account_details()
        elif ch == 5:
            display_all_tickets()
        elif ch == 6:
            ticket_bill()
        elif ch == 7:
            print("Logged out successfully.")
            break
        else:
            print("Invalid option.")


# ---------------------------------------------------------
# MAIN PROGRAM STARTS
# ---------------------------------------------------------
while True:
    print("\n---------------------------")
    print("WELCOME TO RAILWAY RESERVATION SYSTEM")
    print("---------------------------")
    print("1. Sign In")
    print("2. Sign Up")
    print("3. Exit")

    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("Enter a valid number.")
        continue

    if choice == 1:
        signin()
    elif choice == 2:
        signup()
    elif choice == 3:
        print("Thank you for using the Railway Reservation System!")
        break
    else:
        print("Invalid input.")
