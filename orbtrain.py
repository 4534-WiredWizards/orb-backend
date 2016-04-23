import theano
import numpy
from pylearn2 import datasets
from pylearn2.models import mlp
from pylearn2.termination_criteria.__init__ import EpochCounter
from pylearn2.training_algorithms import sgd
import thread
import time
import requests
import logging
logging.getLogger("pylearn2").setLevel(logging.WARNING)

epochsMode=5000
def evaluateTeam(eventCodeList,teamNumber):
	print "###   saving example dataset for team #"+str(teamNumber)
	roboDataset = [[[],[]],[[],[]]]
	reattempts = 10
	brokenRequest = False
	for event in eventCodeList:
		r = []
		print "requesting matches at",event,"for team",teamNumber
		rStr = 'http://www.thebluealliance.com/api/v2/team/frc' + str(teamNumber) + '/event/'+event+'/matches?X-TBA-App-Id=frc4534:auto-scouting:2'
		try:
			r = requests.get(rStr)
		except:
			print "first match event request for team",teamNumber,"failed, beginning reattempts",r
			time.sleep(2)
			while r == [] and reattempts > 0:
				try:
					r = requests.get(rStr)
				except:
					pass
				time.sleep(2)
				reattempts -= 1
				print reattempts,"more attempts to request matches at",event,"for team",teamNumber
			if r == []:
				brokenRequest = True
		if brokenRequest:
			print "broken request, team",teamNumber,", event:",event,". internet disconnected/unreachable?"
		if brokenRequest == False:
			for i in r.json():
				try:
					stringMatchData = [[],[]]
					numMatchData = [[],[]]
					if "frc"+str(teamNumber) in i['alliances']['blue']['teams']:
						alliance = 'blue'
					elif "frc"+str(teamNumber) in i['alliances']['red']['teams']:
						alliance = 'red'
					else:
						alliance = 'team is not in match alliances...'
					stringMatchData[0].append('E_LowBar')
					stringMatchData[0].append(i['score_breakdown'][alliance]['position2'])
					stringMatchData[0].append(i['score_breakdown'][alliance]['position3'])
					stringMatchData[0].append(i['score_breakdown'][alliance]['position4'])
					stringMatchData[0].append(i['score_breakdown'][alliance]['position5'])
					stringMatchData[1].append(i['score_breakdown'][alliance]['position1crossings'])
					stringMatchData[1].append(i['score_breakdown'][alliance]['position2crossings'])
					stringMatchData[1].append(i['score_breakdown'][alliance]['position3crossings'])
					stringMatchData[1].append(i['score_breakdown'][alliance]['position4crossings'])
					stringMatchData[1].append(i['score_breakdown'][alliance]['position5crossings'])
					incompleteMatchDataError = False
					for j in stringMatchData[0]:
						if j == 'E_LowBar':
							numMatchData[0].append(0)
						elif j == 'A_Portcullis':
							numMatchData[0].append(1)
						elif j == 'A_ChevalDeFrise':
							numMatchData[0].append(2)
						elif j == 'B_Moat':
							numMatchData[0].append(3)
						elif j == 'B_Ramparts':
							numMatchData[0].append(4)
						elif j == 'C_Drawbridge':
							numMatchData[0].append(5)
						elif j == 'C_SallyPort':
							numMatchData[0].append(6)
						elif j == 'D_RockWall':
							numMatchData[0].append(7)
						elif j == 'D_RoughTerrain':
							numMatchData[0].append(8)
						else:
							incompleteMatchDataError = True
					for j in stringMatchData[1]:
						numMatchData[1].append(j)
					if incompleteMatchDataError == False:
						for j in numMatchData[0]:
							roboDataset[0][0].append([j])
						for j in numMatchData[1]:
							roboDataset[0][1].append([j])
						#roboDataset[0][0].append(numMatchData[0])
						#roboDataset[0][1].append(numMatchData[1])

					roboDataset[1][1].append([i['score_breakdown'][alliance]['autoBouldersLow'],i['score_breakdown'][alliance]['autoBouldersHigh'],i['score_breakdown'][alliance]['teleopBouldersLow'], i['score_breakdown'][alliance]['teleopBouldersHigh']])
					roboDataset[1][0].append([0])
				except:
					print "exception in event "+event+", team "+str(teamNumber) + ", match #" + str(i['match_number'])
					pass

	hidden_layer_1 = mlp.Tanh(layer_name='hidden1', dim=16, irange=.1, init_bias=1.)
	hidden_layer_2 = mlp.Tanh(layer_name='hidden2', dim=8, irange=.1, init_bias=1.)
	output_layer = mlp.Linear(layer_name='output', dim=4, irange=.1, init_bias=1.)
	layers = [hidden_layer_1, hidden_layer_2, output_layer]
	trainer = sgd.SGD(learning_rate=.05, batch_size=10, termination_criterion=EpochCounter(epochsMode))
	ann = mlp.MLP(layers, nvis=1)
	roboDataset[1][0] = numpy.array(roboDataset[1][0])
	roboDataset[1][1] = numpy.array(roboDataset[1][1])
	try:
		ds = datasets.DenseDesignMatrix(X=roboDataset[1][0],y=roboDataset[1][1])
	except IndexError:
		print "IndexError in dataset creation for team",teamNumber,",","length of dataset=",len(roboDataset[1])
	ret = [[],[]]
	start = time.time()
	if len(roboDataset[1][1]) > 4: ## only here to train for teams with enough matches to get _anywhere_ within reasonably reliable net results
		print "Scoring team",teamNumber,"in goals"
		trainer.setup(ann,ds)
		print "training for <=",epochsMode,"epochs (team",teamNumber,")"
		while True:
			trainer.train(dataset=ds)
			ann.monitor.report_epoch()
			if not trainer.continue_learning(ann):
				break
		print "network training time:",int(time.time() - start),"seconds for team",teamNumber
		inputs = numpy.array([[0]])
		for i in ann.fprop(theano.shared(inputs, name='inputs')).eval()[0]:
			ret[0].append(i)
			
	hidden_layer_1 = mlp.Tanh(layer_name='hidden1', dim=16, irange=.1, init_bias=1.)
	hidden_layer_2 = mlp.Tanh(layer_name='hidden2', dim=8, irange=.1, init_bias=1.)
	output_layer = mlp.Linear(layer_name='output', dim=1, irange=.1, init_bias=1.)
	layers = [hidden_layer_1, hidden_layer_2, output_layer]
	trainer = sgd.SGD(learning_rate=.05, batch_size=10, termination_criterion=EpochCounter(epochsMode))
	ann = mlp.MLP(layers, nvis=1)
	roboDataset[0][0] = numpy.array(roboDataset[0][0])
	roboDataset[0][1] = numpy.array(roboDataset[0][1])
	try:
		ds = datasets.DenseDesignMatrix(X=roboDataset[0][0],y=roboDataset[0][1])
	except IndexError:
		print "IndexError in dataset creation for team",teamNumber,",","length of dataset=",len(roboDataset[0][1])
	start = time.time()
	if len(roboDataset[0][1]) > 4: ## only here to train for teams with enough matches to get _anywhere_ within reasonably reliable net results
		print "Scoring team",teamNumber,"in defenses"
		trainer.setup(ann,ds)
		print "training for <=",epochsMode,"epochs (team",teamNumber,")"
		while True:
			trainer.train(dataset=ds)
			ann.monitor.report_epoch()
			if not trainer.continue_learning(ann):
				break
		print "network training time:",int(time.time() - start),"seconds for team",teamNumber
		# inputs = numpy.array([[0]])
		inputs = [[0],[1],[2],[3],[4],[5],[6],[7],[8]]
		for i in inputs:
			ret[1].append(ann.fprop(theano.shared(numpy.array([i]), name='inputs')).eval()[0][0])
		# for i in ann.fprop(theano.shared(inputs, name='inputs')).eval()[0]:
		#     ret.append(i)
	return ret