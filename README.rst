
What it does
------------
- Stores log file data from multiple remote hosts to MongoDB
  - Creates processes that ssh to a remote host and run "tail --follow=name" on the log file
  - Parses the log file using Regular Expressions
  - Stores the data in MongoDB
- Queries MongoDB for interesting statistics
- Creates real-time plots in a web browser

Dependencies
------------
- MongoDB
- PyMongo
- Orbited
- Twisted
- stompservice

To use it
---------
- Copy settings.py.template to settings.py and edit it
- Start mongod
- Start orbited
- In first terminal, run "sourceexecutive.py"
- In second terminal, run "analyzerexecutive.py"

Problems / Limitations
----------------------
- Leaves "zombie" "tail --follow=name " processes
- Only works with my custom Nginx log file
