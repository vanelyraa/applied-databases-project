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
    print("Test")
    
def view_attendees_by_company():
    print("Test")

def add_attendee():
    print("Test")

def view_connections():
    print("Test")

def add_connection():
    print("Test")

def view_rooms(): 
    mysql_cursor.execute("select roomID, roomName, capacity from room")
    results = mysql_cursor.fetchall()   
    print("\nRoomID | RoomName | Capacity")

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