
What it does
------------
- Stores log file data from multiple remote hosts to MongoDB

  - Creates processes that ssh to a remote host and run "tail --follow=name" on the log file
  - Parses the log file using Regular Expressions
  - Stores the data in MongoDB

- Queries MongoDB for interesting statistics e.g.:

  - Requests/mintute
  - Cache hit rate
  - Count of HTTP 500 statuses
  - Average upstream response time
  - MySQL questions/second

- Creates real-time plots in a web browser

Dependencies
------------
- MongoDB
- PyMongo
- Orbited
- Twisted
- stompservice
- flot
- a few more in pip-requirements.txt

To use it
---------
- Copy settings_template.py to settings.py and edit it
- Start mongod
- Start orbited
- In first terminal, run "sourceexecutive.py"
- In second terminal, run "analyzerexecutive.py"

Problems / Limitations
----------------------
- Leaves "mysqladmin extended" processes running on remote host
- The bulk of this is set up for my custom Nginx log file (but it is easy to
  write your own custom sources, parsers, and analyzers.
