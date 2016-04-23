import requests
from flask import Flask, request, make_response
from flask.ext.mysql import MySQL
import json
import orbtrain
import thread

mysql = MySQL()
app = Flask(__name__)
app.debug = True
app.config['MYSQL_DATABASE_USER'] = 'tom'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'orb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

x = 0
teamsDict = {}
print 'pulling data for all teams'
while requests.get('http://www.thebluealliance.com/api/v2/teams/'+str(x)+'?X-TBA-App-Id=frc4534:auto-scouting:3').json() != []:
	page = requests.get('http://www.thebluealliance.com/api/v2/teams/'+str(x)+'?X-TBA-App-Id=frc4534:auto-scouting:3').json()
	for team in page:
		teamsDict[str(team['team_number'])] = team
	x += 1
print 'pulling data for events'
allEvents = requests.get('http://www.thebluealliance.com/api/v2/events/2016?X-TBA-App-Id=frc4534:auto-scouting:3').json()
eventTeams = {}
for event in allEvents:
	eventTeams[event['key']] = requests.get('http://www.thebluealliance.com/api/v2/event/'+event['key']+'/teams?X-TBA-App-Id=frc4534:auto-scouting:3').json()
eventCodeList = []
for i in eventTeams:
	eventCodeList.append(i)







# missingTeams = []
# dbTeams = []
# cursor.execute('select team from goal')
# data = cursor.fetchall()
# for i in data:
# 	dbTeams.append(i[0])
# for i in teamsDict:
# 	if int(i) not in dbTeams:
# 		print "missing team from goal db...",i
# 		missingTeams.append(int(i))
# goalMissingTeams = []
# for i in missingTeams:
# 	for j in eventTeams:
# 		for k in eventTeams[j]:
# 			if (i == k['team_number']) and (i not in goalMissingTeams):
# 				goalMissingTeams.append(i)
# 				print i


# missingTeams = []
# dbTeams = []
# cursor.execute('select team from defense')
# data = cursor.fetchall()
# for i in data:
# 	dbTeams.append(i[0])
# for i in teamsDict:
# 	if int(i) not in dbTeams:
# 		print "missing team from defense db...",i
# 		missingTeams.append(int(i))
# defenseMissingTeams = []
# for i in missingTeams:
# 	for j in eventTeams:
# 		for k in eventTeams[j]:
# 			if (i == k['team_number']) and (i not in defenseMissingTeams):
# 				defenseMissingTeams.append(i)
# 				print i

# for i in defenseMissingTeams:
# 	if i not in goalMissingTeams:
# 		goalMissingTeams.append(i)
# missingTeams = goalMissingTeams
# missingTeams = sorted(missingTeams)
# print missingTeams

# index = 0
# for i in missingTeams:
# 	print i
# 	print index,"/",len(missingTeams)
# 	missingTeamEvents = []
# 	for j in eventTeams:
# 		for k in eventTeams[j]:
# 			if i == k['team_number']:
# 				missingTeamEvents.append(j)
# 				print j
# 	missingTeamRatings = orbtrain.evaluateTeam(missingTeamEvents,i)
# 	print missingTeamRatings
# 	if missingTeamRatings != [[],[]]:
# 		cursor.execute("select * from goal where team="+str(i))
# 		data = cursor.fetchone()
# 		print data
# 		print cursor.execute("delete from goal where team="+str(i))
# 		print cursor.execute("insert into goal values ("+str(i)+","+str(missingTeamRatings[0][0])+","+str(missingTeamRatings[0][1])+","+str(missingTeamRatings[0][2])+","+str(missingTeamRatings[0][3])+")")
# 		cursor.execute("select * from goal where team="+str(i))
# 		data = cursor.fetchone()
# 		print data
# 		print cursor.execute("delete from defense where team="+str(i))
# 		print cursor.execute("insert into defense values ("+str(i)+","+str(missingTeamRatings[1][0])+","+str(missingTeamRatings[1][1])+","+str(missingTeamRatings[1][2])+","+str(missingTeamRatings[1][3])+","+str(missingTeamRatings[1][4])+","+str(missingTeamRatings[1][5])+","+str(missingTeamRatings[1][6])+","+str(missingTeamRatings[1][7])+","+str(missingTeamRatings[1][8])+")")
# 		conn.commit()
# 		print "altered database values in goal and defense tables for team",i
# 	index += 1





def addResultsToDatabase(ret,teamNumber):
	print ret
	cursor.execute("delete from goal where team="+str(teamNumber))
	cursor.execute("insert into goal values ("+str(teamNumber)+","+str(ret[0][0])+","+str(ret[0][1])+","+str(ret[0][2])+","+str(ret[0][3])+")")
 	cursor.execute("delete from defense where team="+str(teamNumber))
 	cursor.execute("insert into defense values ("+str(teamNumber)+","+str(ret[1][0])+","+str(ret[1][1])+","+str(ret[1][2])+","+str(ret[1][3])+","+str(ret[1][4])+","+str(ret[1][5])+","+str(ret[1][6])+","+str(ret[1][7])+","+str(ret[1][8])+")")
 	conn.commit()
 	print "altered database values in goal and defense tables for team",teamNumber


@app.route('/')
def index():
	return json.dumps(['Project Orb.'])

# Returns a list of teams at event identified by eventcode.
@app.route('/list/<eventcode>/')
def teamsAtEvent(eventcode):
	try:
		return json.dumps(eventTeams[eventcode])
	except:
		return json.dumps({})

# Returns a basic JSON object about that team. 
@app.route('/team/<number>/')
def teamObject(number):
	try:
		return json.dumps(teamsDict[number])
	except:
		return json.dumps({})

# Returns the entire defense skill lineup for that team. 
@app.route('/team/<number>/defense/')
def databaseDefense(number):
	try:
		cursor.execute("select * from defense where team="+str(number))
		data = cursor.fetchone()
		return json.dumps(data)
	except:
		return json.dumps({})

# Returns the defense skill for that team on defense X. 
@app.route('/team/<number>/defense/<defensenumber>/')
def databaseDefenseNumber(number, defensenumber):
	try:
		cursor.execute("select "+str(defensenumber)+" from defense where team="+str(number))
		data = cursor.fetchone()
		return json.dumps(data)
	except:
		return json.dumps({})

# Gets a team's skill at a low/high goal in auto/teleop.
@app.route('/team/<number>/goals/')
def databaseGoals(number):
	try:
		cursor.execute("select * from goal where team="+str(number))
		data = cursor.fetchone()
		return json.dumps(data)
	except:
		return json.dumps({})

# Gets a team's skill at a low goal in auto/teleop.
@app.route('/team/<number>/goals/low/')
def databaseGoalsLow(number):
	try:
		cursor.execute("select autolow, teleoplow from goal where team="+str(number))
		data = cursor.fetchone()
		return json.dumps(data)
	except:
		return json.dumps({})

# Gets a team's skill at a high goal in auto/teleop.
@app.route('/team/<number>/goals/high/')
def databaseGoalsHigh(number):
	try:
		cursor.execute("select autohigh, teleophigh from goal where team="+str(number))
		data = cursor.fetchone()
		return json.dumps(data)
	except:
		return json.dumps({})

# Returns the team's score for rankings.
@app.route('/team/<number>/score/')
def teamScore(number):
	try:
		cursor.execute('select * from goal where team='+str(number))
		teamGoal = cursor.fetchone()
		cursor.execute('select * from defense where team='+str(number))
		teamDefense = cursor.fetchone()
		teamGoalSum = teamGoal[1]+teamGoal[2]+teamGoal[3]+teamGoal[4]
		teamDefenseSum = teamDefense[1]+teamDefense[2]+teamDefense[3]+teamDefense[4]+teamDefense[5]+teamDefense[6]+teamDefense[7]+teamDefense[8]+teamDefense[9]
		return json.dumps(teamDefenseSum + teamGoalSum)
	except:
		return json.dumps({})
# Returns the public prediction table? of matches for an event.
@app.route('/predictions/<eventcode>')
def eventPredictions(eventcode):
	return teamScore(eventcode)
# # Parameters: (eventcode, matchidentifier) - Calculates result of a match by comparing teams' scores, and ranking alliance scores, returns result.
# @app.route('/work/match/')
# def ():

# # Parameters: (eventcode, matchidentifier) - Calculates the optimal defense selection for both alliances, returns result. 
# @app.route('/work/defense/')
# def ():

# Endpoint has alternate authentication, it is a webhook for TheBlueAlliance. Upcoming match notifications come here. Match prediction is evaluated and stored in a public display. 
@app.route('/work/match/upcoming/', methods=['POST','GET'])
def upcoming():
	if request.method == 'POST':
		notification = request.get_json()
		if notification['message_type'] == 'ping':
			print 'ping'
		if notification['message_type'] == 'verification':
			print notification['message_data']["verification_key"]
		return "ok"


def threadTeamsTrain(matchTeams,eventTeams):
	for i in matchTeams:
		teamEvents = []
		for j in eventTeams:
			for k in eventTeams[j]:
				if int(i) == k['team_number']:
					teamEvents.append(j)
		addResultsToDatabase(orbtrain.evaluateTeam(teamEvents,i),i)
# # Endpoint has alternate authentication, it is a webhook for TheBlueAlliance. Match score notifications come here, are entered into the database, and those teams are retrained. Match prediction is validated and updated in the display.
@app.route('/work/match/score', methods=['POST','GET'])
def score():
	if request.method == 'POST':
		notification = request.get_json()
		if notification['message_type'] == 'ping':
			print 'ping'
		if notification['message_type'] == 'verification':
			print notification['message_data']["verification_key"]
		if notification['message_type'] == 'match_score':
			matchTeams = []
			print notification['message_data']['match']['alliances']['blue']['teams']
			print notification['message_data']['match']['alliances']['red']['teams']
			for i in notification['message_data']['match']['alliances']['red']['teams']:
				matchTeams.append(i[3:])
			for i in notification['message_data']['match']['alliances']['blue']['teams']:
				matchTeams.append(i[3:])
			thread.start_new_thread(threadTeamsTrain, (matchTeams, eventTeams))
		return "ok"


if __name__ == '__main__':
    app.run(threaded=False)
