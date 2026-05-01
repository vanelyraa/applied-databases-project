# Imports
from neo4j import GraphDatabase
import mysql.connector

#Neo4j connection
neo4j_driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "12345678"), max_connection_lifetime=1000)

#MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0205",
    database="appdbproj"
)
mysql_cursor = conn.cursor(dictionary=True)


def main():
    
    display_menu()

    while True:
        choice = input("Choice: ")

        if choice == "1":
            view_speakers()
        elif choice == "2":
            view_attendees_by_company()
        elif choice == "3":
            add_attendee()
        elif choice == "4":
            view_connections()
        elif choice == "5":
            add_connection()
        elif choice == "6":            
            view_rooms()            
        elif choice == "x":
            break
        else: 
            display_menu()

def view_speakers():
    # User input message
    speaker_name = input("\nEnter speaker name: ")

    #SQL query
    sql = """
    select ss.speakerName, ss.sessionTitle, rm.roomName
    from session ss
    inner join room rm
        on ss.roomID = rm.roomID
    where ss.speakerName like %s
    """

    # Running query with partial string match
    mysql_cursor.execute(sql,(f"%{speaker_name}%",))
    
    # Fetching and storing rows returned by query 
    results = mysql_cursor.fetchall()

    print(f"Session Details For : {speaker_name}")
    print("----------------------------------------------")

    # Loop through result and print results or no found message
    if results:
        for result in results:
            print(result["speakerName"],"|", result["sessionTitle"],"|", result["roomName"])
    else:
        print("No speakers found of that name")

    
def view_attendees_by_company():
    # Asking user to enter a valid company ID until one has been entered
    while True:
        company_id = input("Enter Company ID: ")

        # Validating positive numbers
        if not company_id.isdigit() or int(company_id) <= 0:
            continue

        # Checking if company exists block
        # Execute query,fecth results, if no results found, print message to user
        mysql_cursor.execute(
            "SELECT companyName FROM company WHERE companyID = %s",
            (company_id,)
        )
        company = mysql_cursor.fetchall()

        if not company:
            print(f"Company with ID {company_id} doesn't exist")
            return

        #If company exists, print company name
        company_name = company["companyName"]
        print(f"\n{company_name} Attendees")
        
        # Query to fetch attendees + sessions + rooms
        sql = """
        SELECT 
            a.attendeeName,
            a.attendeeDOB,
            s.sessionTitle,
            s.speakerName,
            s.sessionDate,
            r.roomName
        FROM attendee a
        INNER JOIN registration reg ON a.attendeeID = reg.attendeeID
        INNER JOIN session s ON reg.sessionID = s.sessionID
        INNER JOIN room r ON s.roomID = r.roomID
        WHERE a.attendeeCompanyID = %s
        """

        # Executing query and fetching results
        mysql_cursor.execute(sql, (company_id,))
        results = mysql_cursor.fetchall()

        # No atendees print statement
        if not results:
            print(f"No attendees found for {company_name}")
            return

        # Printing results if found
        for row in results:
            print(
                row["attendeeName"], "|",
                row["attendeeDOB"], "|",
                row["sessionTitle"], "|",
                row["speakerName"], "|",
                row["sessionDate"], "|",
                row["roomName"]
            )
        return

def add_attendee():

    print("\nAdd New Attendee")
    print("------------------")
    
    #Try/Except block for error handling
    try:
        # Getting atendee info from user input 
        attendee_id = input("Attendee ID: ")
        name = input("Name: ")
        dob = input("DOB: ")
        gender = input("Gender: ")
        company_id = input("Company ID: ")

        # Checking duplicated attendee ID
        mysql_cursor.execute(
            "SELECT * FROM attendee WHERE attendeeID = %s",
            (attendee_id,)
        )
        if mysql_cursor.fetchall():
            print(f"*** ERROR *** Attendee ID: {attendee_id} already exists")
            return

        # Checking valid gender 
        if gender not in ["Male", "Female"]:
            print("*** ERROR *** Gender must be Male/Female")
            return
       
        # Checking existing company ID
        mysql_cursor.execute(
            "SELECT * FROM company WHERE companyID = %s",
            (company_id,)
        )
        if not mysql_cursor.fetchall():
            print(f"*** ERROR *** Company ID: {company_id} does not exist")
            return

        # Add new attendee query
        sql = """
        INSERT INTO attendee (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
        VALUES (%s, %s, %s, %s, %s)
        """

        #Executing insert query with user input and committing changes
        mysql_cursor.execute(sql, (attendee_id, name, dob, gender, company_id))
        conn.commit()

        print("Attendee successfully added")

    # Other errors handling
    except Exception as e:
        print("*** ERROR ***", e)

def view_connections():
    print("Test")

def add_connection():
    print("Test")

def view_rooms(): 
    # Executing query and fetching results
    mysql_cursor.execute("select roomID, roomName, capacity from room")
    results = mysql_cursor.fetchall()   

    # Header print statement for user
    print("\nRoomID | RoomName | Capacity")

    # Looping through results and printing
    for result in results:
        print(result["roomID"],"|", result["roomName"],"|", result["capacity"])  

def display_menu():
    
    print("\nConference Management")
    print("---------------------\n")
    print("MENU")
    print("====")
    print("1 - View Speakers & Sessions")
    print("2 - View Attendees by Company")
    print("3 - Add New Attendee")
    print("4 - View Connected Attendees")
    print("5 - Add Attendee Connection")
    print("6 - View Rooms")
    print("x - Exit")


if __name__== "__main__":
    main()


# dictionary=True: https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursordict.html
# SQL command block: https://www.geeksforgeeks.org/python/sql-using-python/
# Return results from substring: https://chatgpt.com/share/69ecddd4-d850-83eb-9a32-e1dd66bc1b15
# User input error handling: https://dev.to/fosres/week-4-sql-injection-audit-challenge-le7
# Try/Except code block: https://medium.com/@icodewithben/data-validation-in-python-range-type-presence-and-form-aaefe8835a86
# Error message conditions 3.1.4.1: https://stackoverflow.com/questions/19382396/print-if-mysql-returns-no-results
# Validade integer: https://stackoverflow.com/questions/16335771/shorter-way-to-check-if-a-string-is-not-isdigit