import json
import _mysql
db=_mysql.connect(
	host="localhost",
	user="tom",
	passwd="",
	db="orb"
	)

gfilename=raw_input("name of goal file: ")
dfilename=raw_input("name of defense file: ")
gfile = open(gfilename,'r')
jsonI = gfile.read()
jsonAll = json.loads(jsonI)

for i in jsonAll:
	print i, jsonAll[i]
	if len(jsonAll[i]) == 4:
		db.query("delete from goal where team="+str(i))
		db.query("insert into goal values ("+str(i)+","+str(jsonAll[i][0])+","+str(jsonAll[i][1])+","+str(jsonAll[i][2])+","+str(jsonAll[i][3])+")")
	else:
		print "WHY:",i
		print len(jsonAll[i])
gfile.close()
dfile = open(dfilename,'r')
jsonI = dfile.read()
jsonAll = json.loads(jsonI)

for i in jsonAll:
	print i, jsonAll[i]
	if len(jsonAll[i]) == 9:
		db.query("delete from defense where team="+str(i))
		db.query("insert into defense values ("+str(i)+","+str(jsonAll[i][0])+","+str(jsonAll[i][1])+","+str(jsonAll[i][2])+","+str(jsonAll[i][3])+","+str(jsonAll[i][4])+","+str(jsonAll[i][5])+","+str(jsonAll[i][6])+","+str(jsonAll[i][7])+","+str(jsonAll[i][8])+")")
	else:
		print "WHY:",i
		print len(jsonAll[i])