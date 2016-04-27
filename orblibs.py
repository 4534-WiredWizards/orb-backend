import os
import pickle
import requests

def getTeams():
	if os.path.isfile("./teams.pickle"):
		print 'existing data found, loading'
		f = open("./teams.pickle","r")
		obj = pickle.load(f);
		f.close()
		return obj

	teamsDict = {}
	print 'pulling data for all teams'
	x = 0
	while requests.get('http://www.thebluealliance.com/api/v2/teams/'+str(x)+'?X-TBA-App-Id=frc4534:auto-scouting:3').json() != []:
		page = requests.get('http://www.thebluealliance.com/api/v2/teams/'+str(x)+'?X-TBA-App-Id=frc4534:auto-scouting:3').json()
		for team in page:
			teamsDict[str(team['team_number'])] = team
#            print "loaded team " + str(team['team_number'])
		x += 1
	f = open("./teams.pickle","w")
	pickle.dump(teamsDict,f)
	f.close()
	return teamsDict

def getEventTeams():
	if os.path.isfile("./eventteams.pickle"):
		print 'existing data found, loading'
		f = open("./eventteams.pickle","r")
		obj = pickle.load(f);
		f.close()
		print 'done'
		return obj

	print 'pulling data for events'
	allEvents = requests.get('http://www.thebluealliance.com/api/v2/events/2016?X-TBA-App-Id=frc4534:auto-scouting:3').json()
	eventTeams = {}
	eventMatches = {}
	eventTeamsNumbers = {}
	for event in allEvents:
		print "getting event " + event['key']
		eventTeams[event['key']] = requests.get('http://www.thebluealliance.com/api/v2/event/'+event['key']+'/teams?X-TBA-App-Id=frc4534:auto-scouting:3').json()
		eventTeamsNumbers[event['key']] = []
		for team in eventTeams[event['key']]:
			eventTeamsNumbers[event['key']].append(team['team_number']) 
		eventMatches[event['key']] = requests.get('http://www.thebluealliance.com/api/v2/event/'+event['key']+'/matches?X-TBA-App-Id=frc4534:auto-scouting:3').json()
	eventCodeList = []
	for i in eventTeams:
		eventCodeList.append(i)
	f = open("./eventteams.pickle","w")
	pickle.dump((eventTeams, eventMatches, eventTeamsNumbers),f)
	f.close()
	return (eventTeams, eventMatches, eventTeamsNumbers)
