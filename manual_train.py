import orbtrain
import orblibs
import requests
import sys

eventTeams = orblibs.getEventTeams()
args = sys.argv
args.pop(0)

for team in args:

    print "======== " + team + " ========"
    teamEvents = []
    for j in eventTeams:
        for k in eventTeams[j]:
            if int(team) == k['team_number']:
                teamEvents.append(j)
    
    print orbtrain.evaluateTeam(teamEvents,team)
    print "======================"
