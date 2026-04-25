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
mysql_cursor = conn.cursor()


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
    

def view_attendees_by_company():


def add_attendee():


def view_connections():


def add_connection():


def view_rooms():
    
    
def display_menu():
    
    print("\nConference Management\n")
    print("\n---------------------\n\n")
    print("\nMENU\n")
    print("\n====\n")
    print("1 - View Speakers & Sessions")
    print("2 - View Attendees by Company")
    print("3 - Add New Attendee")
    print("4 - View Connected Attendees")
    print("5 - Add Attendee Connection")
    print("6 - View Rooms")
    print("x - Exit")


if__name__== "__main__":
    main()