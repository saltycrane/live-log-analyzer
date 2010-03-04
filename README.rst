
What it does (part 1)
---------------------
- Creates processes that ssh to a remote host and run "tail -f" on the log file
- Parses the log file using Regular Expressions
- Stores the data in MongoDB

What it does (part 2)
---------------------
- Queries MongoDB and prints statistics in real-time

Example results::

    Stats over the last                1 min               5 min              15 min
    --------------------------------------------------------------------------------
    Requests (N)                                                                    
      Total requests                    1154                5906               18061
      asdf.com                           647                3356               10185
      asdf1.com                           26                 119                 426
      asdf2.com                           37                 175                 471
      asdf3.net                          441                2225                6885
    Cache status (%)                                                                
      HIT (media: 0)         50.6% (164/324)    52.6% (861/1638)   54.5% (2705/4961)
      UPDATING (all)          0.00% (0/1180)      0.03% (2/5932)    0.06% (11/18087)
      STALE (all)             0.00% (0/1191)      0.00% (0/5943)     0.00% (0/18098)
    Upstream HTTP status (N)                                                            
      4xx status                          10                  28                  79
      5xx status                           0                   0                   0
    Avg upstream response time (secs)                                                            
      10.111.111.130:80           1.858 (50)         2.156 (228)         1.676 (748)
      10.111.111.241:80           1.150 (54)         1.303 (281)         1.261 (737)
      10.111.111.209:80           1.165 (46)         1.041 (235)         1.060 (726)
    Error logs (N)                                                                  
      Nginx error count                    0                   0                   0
      PHP error count                      0                   1                   2

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
- Leaves "zombie" "tail -f " processes
- Only works with my custom Nginx log file
