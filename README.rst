
What it does (part 1)
---------------------
- Creates processes that ssh to a remote host and run "tail --follow=name" on the log file
- Parses the log file using Regular Expressions
- Stores the data in MongoDB

What it does (part 2)
---------------------
- Queries MongoDB and prints statistics in real-time

Example results::

    Stats over the last                1 min               5 min              15 min
    --------------------------------------------------------------------------------
    Requests per minute                                                             
      Total req/min                      734                 535                 699
      asdf.com                           413                 276                 370
      asdf1.com                           25                  27                  27
      asdf2.com                           13                  13                  21
      asdf3.net                          277                 216                 276
    Cache status (%)                                                                
      HIT (media: 0)         49.8% (120/241)     49.7% (380/764)   47.5% (1588/3344)
      UPDATING (all)           0.00% (0/734)      0.00% (0/2676)    0.25% (26/10482)
      STALE (all)              0.00% (0/734)      0.00% (0/2676)     0.00% (0/10482)
    Upstream HTTP status (N)                                                            
      4xx status                           6                  16                  59
      5xx status                           0                   0                   0
    Avg upstream response time (secs)                                                            
      10.111.111.130:80           1.602 (66)         1.760 (173)         2.244 (804)
      10.111.111.241:80           0.593 (37)         0.891 (116)         1.057 (453)
      10.111.111.209:80           0.733 (23)          0.998 (98)         1.056 (462)
    Error logs (N)                                                                  
      Nginx error count                    0                   0                   0
      PHP error count                      0                   0                   2

Dependencies
------------
- MongoDB
- PyMongo

To use it
---------
- Start mongod
- Copy settings.py.template to settings.py and edit it
- In first terminal, run "python source.py"
- In second terminal, run "python executive.py"

Problems / Limitations
----------------------
- Leaves "zombie" "tail --follow=name " processes
- Only works with my custom Nginx log file

Plans
-----
- Add a web UI using Orbited, MorbidQ, js.io, Twisted, etc.
