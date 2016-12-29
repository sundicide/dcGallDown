import sqlite3

con = sqlite3.connect("DCcrawlerDB")
cur = con.cursor()
#url= 'http://gall.dcinside.com/mgallery/board/view/?id=twicemina&no=359322&page=1&exception_mode=recommend'
cur.execute("SELECT * FROM urls")
#cur.execute("SELECT COUNT(*) FROM urls WHERE url='%s' and state=1"% url)
#ret = cur.fetchone()
#print(ret)
for i,r in enumerate(cur):
    print(i, r)
