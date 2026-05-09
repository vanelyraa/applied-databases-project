# Imports
from neo4j import GraphDatabase
import mysql.connector
import time

# User inputs SQL and Neo4j credentials for connection
mysql_user = input("Enter MySQL username: ")
mysql_password = input("Enter MySQL password: ")

neo4j_user = input("Enter Neo4j username: ")
neo4j_password = input("Enter Neo4j password: ")

#Neo4j connection
#print("Connecting to Neo4j...") #Test print statement, testing DB connection in VM 
neo4j_driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=(neo4j_user, neo4j_password), max_connection_lifetime=1000)

# print("Neo4j connected") #Test print statement, testing DB connection in VM 

# MySQL connection
# print("Connecting to MySQL...") #Test print statement, testing DB connection in VM 
conn = mysql.connector.connect(
    host="localhost",
    user=mysql_user,
    password=mysql_password,
    database="appdbproj"
)
mysql_cursor = conn.cursor(dictionary=True)

# print("MySQL connected") #Test print statement, testing DB connection in VM 

# Running functions based on user menu choice and returning to main menu
def main():
    
    while True:
        display_menu()
    
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
        elif choice == "7":
            top_attendees()
        elif choice == "8":
            suggested_connections()
        elif choice == "9":
            connection_path()           
        elif choice == "x":
            break

        time.sleep(3) #3 seconds pause before returning to main menu

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

    # User print statements 
    print(f"Session Details For : {speaker_name}")
    print("----------------------------------------------")

    # Loop through result and print results or no found message
    if results:
        for result in results:
            print(result["speakerName"],"|", result["sessionTitle"],"|", result["roomName"])
    else:
        print("No speakers found of that name")

    return
    
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
        company = mysql_cursor.fetchone()

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
    while True:
        # Getting attendee IDs from user
        attendee_id = input("\nEnter Attendee ID : ")
        
        # Validating IDs as number
        if not attendee_id.isdigit():
            print("***ERROR *** Invalid attendee ID")
            continue

        attendee_id = int(attendee_id)
        
        # SQL query, find attendee by ID
        mysql_cursor.execute(
            "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
            (attendee_id,)
        )
        attendee = mysql_cursor.fetchone()

        # Attendee does not exist print statement
        if not attendee:
            print("***ERROR *** Attendee does not exist")
            continue

        attendee_name = attendee["attendeeName"]

        # Checking Neo4j connections query
        with neo4j_driver.session(database="attendeenetwork") as session:
            query = """
            MATCH (a:Attendee {AttendeeID: $id})
            OPTIONAL MATCH (a)-[:CONNECTED_TO]-(b:Attendee)
            RETURN b.AttendeeID AS id
            """

            #Running query and extracting connected Ids if any
            result = session.run(query, id=attendee_id)
            records = [r["id"] for r in result if r["id"] is not None]

        # Output to user
        print(f"Attendee Name: {attendee_name}")
        print("--------------------------------")

        #User doesn't exist in Neo4j
        if not records:
            print("No connections")
            return

        print("These attendees are connected:")
        
        #Looping through attendee ID and retrieving SQL attendee info if any
        for row in records:
            mysql_cursor.execute(
                "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
                (row,)
            )
            connection = mysql_cursor.fetchone()

            if connection:
                print(f"{row} | {connection['attendeeName']}")
        return

def add_connection():

    while True:

        # Getting attendees IDs from user
        attendee1 = input("Enter Attendee 1 ID: ")
        attendee2 = input("Enter Attendee 2 ID: ")

        # Validating IDs as number and print statement
        if not attendee1.isdigit() or not attendee2.isdigit():
            print("*** ERROR *** Attendee IDs must be numbers")
            continue

        # Same atendee ID check
        if attendee1 == attendee2:
            print("*** ERROR *** An attendee cannot connect to him/herself")
            continue

        # Checking if both attendees exist in MySQL
        mysql_cursor.execute("SELECT * FROM attendee WHERE attendeeID = %s", (attendee1,))
        id1= mysql_cursor.fetchone()
            
        mysql_cursor.execute("SELECT * FROM attendee WHERE attendeeID = %s", (attendee2,))
        id2= mysql_cursor.fetchone()

        if not id1 or not id2:
            print("*** ERROR *** One or both attendee IDs do not exist")
            continue
        
        # Running Neo4j session to check existing connections and create new connection if needed
        with neo4j_driver.session(database="attendeenetwork") as session:

            # Checking if connection exists
            connection_query = """
            MATCH (a:Attendee {AttendeeID: $id1})-[:CONNECTED_TO]-(b:Attendee {AttendeeID: $id2})
            RETURN b
            """

            # Running query with user inputs
            result = session.run(connection_query, id1=int(attendee1), id2=int(attendee2))
            records = list(result)

            # If records found, connection exists, print statement
            if records:
                print("***ERROR*** These attendees are already connected")
                continue

            # Creating missing nodes and adding connection
            creation_query = """
            MERGE (a:Attendee {AttendeeID: $id1})
            MERGE (b:Attendee {AttendeeID: $id2})
            CREATE (a)-[:CONNECTED_TO]->(b)
            """

            # Execute query with user inputs, converting user inputs to integer to match Neo4j id values stored
            session.run(creation_query, id1=int(attendee1), id2=int(attendee2))
            print(f"Attendee {attendee1} is now connected to Attendee {attendee2}")
    
        break
    
def view_rooms(): 
    # Executing SQL query and fetching results
    mysql_cursor.execute("select roomID, roomName, capacity from room")
    results = mysql_cursor.fetchall()   

    # Header print statement for user
    print("\nRoomID | RoomName | Capacity")

    # Looping through results and printing
    for result in results:
        print(result["roomID"],"|", result["roomName"],"|", result["capacity"])  

def top_attendees():

    # Top attendee print statement
    print("\nTop 5 Connected Attendees")
    print("---------------------------")

    # Fetching number of connections, order by highest to lowest and returning top 5
    with neo4j_driver.session(database="attendeenetwork") as session:
        query = """
        MATCH (a:Attendee)
        OPTIONAL MATCH (a)-[:CONNECTED_TO]-(b)
        RETURN a.AttendeeID AS id, COUNT(b) AS connections
        ORDER BY connections DESC
        LIMIT 5
        """

        # Running query Neo4j query
        result = session.run(query)

        # Fetching top connected attendees in SQL and printing 
        for row in result:   
            mysql_cursor.execute(
                "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
                (row["id"],)            
            )
            # Fetching attendee returned by SQL query
            atendee = mysql_cursor.fetchone()
            print(f"{row['id']} | {atendee['attendeeName']} | {row['connections']}")

    return            

def suggested_connections():

    while True:
        attendee_id = input("\n Enter your ID: ")

        # Validating numeric input
        if not attendee_id.isdigit():
            print("*** ERROR *** Invalid attendee ID")
            continue

        attendee_id = int(attendee_id)

        # Executing SQL query to retrieve attendee name by ID
        mysql_cursor.execute(
            "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
            (attendee_id,)
        )
        attendee = mysql_cursor.fetchone()

        # If attendee id not found, print statement to user
        if not attendee:
            print("*** ERROR *** Attendee does not exist")
            continue #Let user try id input again

        print(f"\nSuggested Connections For {attendee['attendeeName']}")
        print("---------------------------------------")

        # Opening Neo4j session
        with neo4j_driver.session(database="attendeenetwork") as session:

            # Neo4j query, find attendee suggestions through mutual connections, excluding existing connections and own attendee
            query = """
            MATCH (a:Attendee {AttendeeID:$id})-[:CONNECTED_TO]-(connection)-[:CONNECTED_TO]-(newconnection)

            WHERE NOT (a)-[:CONNECTED_TO]-(newconnection)
            AND newconnection.AttendeeID <> $id

            RETURN newconnection.AttendeeID AS id
            """
            
            # Running query with user input
            result = session.run(query, id=attendee_id)

            # Converting Neo4j query results into a list
            records = list(result)

            # If no suggestion found, print statement to user
            if not records:
                print("No suggested connections found")
                return
            
            # Looping through suggested attendee IDs and retrieve attendee names from MySQL
            for row in records:
                mysql_cursor.execute(
                    "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
                    (row["id"],)
                )
                person = mysql_cursor.fetchone()

                print(
                    f"{row['id']} | "
                    f"{person['attendeeName']}"
                )
        return

def connection_path():

    while True:

        # Getting attendee IDs from user
        attendee1 = input("\n Enter First Attendee ID: ")
        attendee2 = input("Enter Second Attendee ID: ")

        # Validating IDs as numbers
        if not attendee1.isdigit() or not attendee2.isdigit():
            print("*** ERROR *** Attendee IDs must be numbers")
            continue

        # Same attendee validation
        if attendee1 == attendee2:
            print("*** ERROR *** Attendees must be different")
            continue

        # Checking if both attendees exist in MySQL
        mysql_cursor.execute(
            "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
            (attendee1,)
        )
        id1 = mysql_cursor.fetchone()

        mysql_cursor.execute(
            "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
            (attendee2,)
        )
        id2 = mysql_cursor.fetchone()

        # If one of both ids not found, print to user
        if not id1 or not id2:
            print("*** ERROR *** One or both attendee IDs do not exist")
            continue

        # Opening Neo4j session
        with neo4j_driver.session(database="attendeenetwork") as session:

            # Query verify shortest connection path between users    
            query = """
            MATCH p = shortestPath(
                (a:Attendee {AttendeeID:$id1})-[*]-(b:Attendee {AttendeeID:$id2})
            )
            RETURN p
            """

            # Running query with user inputs
            result = session.run(query, id1=int(attendee1), id2=int(attendee2))

            # Converting Neo4j query results into a list
            records = list(result)

            print("\nConnection Path")
            print("-----------------")

            # Id no path found, print statement to user
            if not records:
                print("No connection path found")
                return

            # Getting shortest path from Neo4j and store it in a variable
            path = records[0]["p"]

            # New list to store attendee ids from path
            connections = []

            # Extract attendee IDs from path and appending to connections list
            for node in path.nodes:
                connections.append(str(node["AttendeeID"]))

            # Printing shortest path ids with ->
            print(f"\n{' -> '.join(connections)}")

            # Looping through nodes and retrieve attendee names from SQL and printing results
            for row in path.nodes:

                mysql_cursor.execute(
                    "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
                    (row["AttendeeID"],)
                )

                person = mysql_cursor.fetchone()
                print(f"{row['AttendeeID']} | {person['attendeeName']}")

        return    

# Main menu
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
    print("7 - Top connected attendees")
    print("8 - Suggested Connections")
    print("9 - Find Connection Path")
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
# Neo4j session: https://neo4j.com/docs/python-manual/current/transactions/
# Order by and limit: https://stackoverflow.com/questions/58438626/neo4j-query-for-most-common-relationship
# Fetch one/all: https://www.geeksforgeeks.org/dbms/querying-data-from-a-database-using-fetchone-and-fetchall/
# New connection Neo4j: https://github.com/neo4j/neo4j/issues/9109
# Shortest path Neo4j:  https://neo4j.com/docs/cypher-manual/current/patterns/shortest-paths/
# Print path with arrow: https://stackoverflow.com/questions/12453580/how-to-concatenate-join-items-in-a-list-to-a-single-string
# Time sleep function: https://www.geeksforgeeks.org/python/sleep-in-python/