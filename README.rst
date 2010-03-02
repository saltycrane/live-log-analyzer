
What it does (part 1)
---------------------
- Creates processes that ssh to a remote host and run "tail -f" on the log file
- Parses the log file using Regular Expressions
- Stores the data in MongoDB

What it does (part 2)
---------------------
- Queries MongoDB and prints statistics in real-time

Example results::

         Stats over the last             1 min             5 min            15 min
    ------------------------------------------------------------------------------
              Total requests               560              2823              7842
        Cache HIT (media: 0)    32.7% (64/196)   33.9% (339/999)  31.6% (926/2927)
        Cache HIT (media: 1)   96.7% (354/366) 95.5% (1731/1813) 95.9% (4667/4869)
        Cache UPDATING (all)     0.00% (0/563)    0.11% (3/2826)    0.10% (8/7845)
           Cache STALE (all)     0.00% (0/563)    0.00% (0/2826)    0.00% (0/7845)
                 domain1.com               233              1434              3871
                 domain2.com                26                99               271
                 domain3.com                24               122               373
                 domain4.net               276              1146              3238
         Upstream 4xx status                 3                10                43
         Upstream 5xx status                 0                 1                 1
           Avg response time             0.976             2.012             1.710

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
