# applied-databases-project

# Applied Databases


## Table of Contents
 - [Project Purpose](#project-purpose)
 - [Project Structure](#project-structure)
 - [Setup Instructions](#setup-instructions)
 - [Project Results](#project-results)
 - [Implementation](#implementation)


## Project Purpose
This repository contains my project submissions for the Applied Databases module completed as part of the Higher Diploma in Science in Computing in Data Analytics at ATU.


## Project Structure

```text
APPLIED-DATABASES-PROJECT/
│
├── Database/
│   ├── appdbproj.sql
│   └── appdbprojNeo4j.txt
│
├── innovation.doc
├── main.py
├── README.md
└── requirements.txt
```


## Setup Instructions

1. Clone GitHub Repository  
<pre> git clone https://github.com/vanelyraa/applied-databases-project.git </pre>

2. Navigate to Project Directory  

3. Download and install Python 3.12  
[Python 3.12](https://www.python.org/downloads/release/python-31210/?utm_source=chatgpt.com)

4. Install Required Dependencies  
<pre> python pip install -r requirements.txt </pre>

5. Setup MySQL Database  
Open MySQL Workbench and run  
<pre> Database/appdbproj.sql </pre>

6. Setup Neo4j Database  
Download and install Neo4j Desktop  
[Neo4j Desktop](https://neo4j.com/download/?utm_source=chatgpt.com)
Create and start a local Neo4j instance  

Create database  
<pre> CREATE DATABASE attendeenetwork </pre>

Select database  
<pre> :use attendeenetwork </pre>

Run  
<pre> Database/appdbprojNeo4j.txt </pre>

7. Run Application  
<pre> python main.py </pre>

The application will request:  
MySQL username/password  
Neo4j username/password  


## Implementation
This project is a Conference Management System developed in Python using both MySQL and Neo4j databases.
The application allows users to:
- View conference speakers and sessions 
- View attendees by company 
- Add new attendees 
- Create attendee connections 
- View attendee connections 
- View conference rooms 
The project also includes Neo4j graph-based innovations:
- Top connected attendees 
- Suggested attendee connections 
- Shortest connection path between attendees 


MySQL not running in virtual machine, switch from Python 3.14 to 3.12: https://www.reddit.com/r/mysql/comments/1ocgznh/help_with_mysqlconnector_connection_issue_please/

** End **
