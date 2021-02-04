# -*- coding: utf-8 -*-

"""
calculate-integrative-complexity.py

This version shows conditional entropy using different dimensions of source information.
"""

import sys, re, os, math, nltk
from classes_suffFirst import *

def usage():
	print (
#########################################################
# USAGE INSTRUCTIONS: calculate-integrative-complexity.py
#########################################################
)

def main():

	vcFreqs = {
		"ICØ": 235,
		"ICL": 379,
		"ICN1": 2,
		"ICN2": 243,
		"ICNG": 213
	}
	sumLexes = 0
	for vc in ["ICØ", "ICL", "ICN1", "ICN2", "ICNG"]:
		sumLexes += vcFreqs[vc]

	mpsFreqs = {
		"IMP.PFV": 298,
		"PST.PFV": 1950,
		"PRS": 1529,
		"IMP.IPFV": 285,
		"PST.IPFV": 836,
		"FUT": 135,
		"CHAR": 1006,
		"NMLZ": 837,
		"MV": 2823
	}
	sumTokens = 0
	for mps in ["IMP.PFV", "PST.PFV", "PRS", "IMP.IPFV", "PST.IPFV", "FUT", "CHAR", "NMLZ", "MV"]:
		sumTokens += mpsFreqs[mps]

	input = open('pitjantjatjara-verb-infl.txt', 'r')
	output = open('integrative-complexity_suffFirst.txt', 'w')
	output.write("NOTE: ALL AVERAGES ARE WEIGHTED BY IC FREQUENCY ACROSS LEXICAL TYPES, AND MPS FREQUENCY ACROSS CORPUS TOKENS.\nWEIGHTED AVERAGES APPEAR AT THE BOTTOM OF THIS OUTPUT.\n\n")

	inputLines = input.readlines()

	# These are unordered sets for collecting all the cell objects
	cells = []
	cellDict = {} # the lookup keys for these are "vc.mps"

	for line in inputLines:
		line = re.sub('[\n\r]*', '', line) #chomp
		line = re.sub('\s*$', '', line) #chomp trailing space too
		#print line

		# only process the lines that start with VC numbers
		if not re.search('^IC', line):
			continue

		fields = line.split('\t')
		vc = fields.pop(0)

		for mps in ["IMP.PFV", "PST.PFV", "PRS", "IMP.IPFV", "PST.IPFV", "FUT", "CHAR", "NMLZ", "MV"]:
			
			#print fields
			form = fields.pop(0)
			form = form.replace('\"', '') # get rid of any quote marks added by Excel

			(pros, aug, suff) = form.split('-')

			cell = Cell(mps, vc, form, pros, aug, suff)
			cells.append(cell)
			cellDict['.'.join([vc, mps])] = cell

	# For each cell , find out how predictive other MPS values are given this cell
	for sourceCell in cells:
		#output.write("###############\nTarget cell:") 
		#output.write(str(targetCell))
		#output.write("\n")

		#sourceCellAggrEnt 
		weightedAvSourceCellEnt = {
			'cueless': 0,
			'suff': 0,
			'augSuff': 0,
			'prosAugSuff': 0
		}

		# get the set of cells from the same VC as the target (but not including self). these will be used as "sources" for testing conditional predictability
		targetCells = [cell for cell in cells if ((cell.vc == sourceCell.vc) and not (cell is sourceCell))] 

		# this will be used for probability weighting of entropy below
		sumTargetFreqs = 0
		for t in targetCells:
			sumTargetFreqs += mpsFreqs[t.mps]
		
		# for each source cell, calculate how well it predicts the target
		for targetCell in targetCells:

			#probWeighting = 1 / len(targetCells) # use this if you want to treat all MPS as equiprobable
			probWeighting = mpsFreqs[targetCell.mps] / sumTargetFreqs

			# get the equivalent cells from all the vc's that have the same (available) cues as the sourceCell for the source MPS
			for cue in ('cueless', 'suff', 'augSuff', 'prosAugSuff'):
				sourceAnalogues = [cell for cell in cells if (cell.cues[cue] == sourceCell.cues[cue] and cell.mps == sourceCell.mps)] 

				# then get all the forms implied by these analogues

				# if there is only one VC where this MPS takes this form, then we know that the entropy will be 0, because there is only one possibility
				if len(sourceAnalogues)==1:
					entropy = 0
				else:
					impliedExponences = [] #this list is where we will store all the target cells from the analogous sources
					for analog in sourceAnalogues:
						#print "VC that matches this source:" + str(analogousCell)
						lookupString = '.'.join([analog.vc, targetCell.mps])
						impliedCell = cellDict[lookupString] #look up the implied cell
						#print "\tand its implied cell:" + str(impliedCell)
						# this version added each IC's exponence once
						#impliedExponences.append(impliedCell.cues['augSuff'])
						# this for-loop means that the exponences set is a frequency distribution based on dictionary frequencies of inflection classes
						impliedExponences.extend([impliedCell.cues['augSuff'] for n in range(vcFreqs[analog.vc])])

					# calculate entropy of impliedExponences set
					entropy = getEntropy(impliedExponences)
					#output.write('\t'.join([str(sourceCell), str(targetCell), str(entropy), '\n']))
					weightedAvSourceCellEnt[cue] += (entropy * probWeighting)

		#avSourceCellEnt = {}
		for cue in ('cueless', 'suff', 'augSuff', 'prosAugSuff'):
			#avSourceCellEnt[cue] = sourceCellAggrEnt[cue] / len(targetCells)
			sourceCell.avgEnt[cue] = weightedAvSourceCellEnt[cue]

	systemWeightedAvEnt = {
		'cueless': 0,
		'suff': 0,
		'augSuff': 0,
		'prosAugSuff': 0
	}
	prevCue = 'cueless'
	avEntropies = {} # entropies[cue][mps] = 0
	for cue in ('cueless', 'suff', 'augSuff', 'prosAugSuff'):
		output.write("============\nCue: "+cue+"\n\n")
		avEntropies[cue] = {}
		for mps in ["IMP.PFV", "PST.PFV", "PRS", "IMP.IPFV", "PST.IPFV", "FUT", "CHAR", "NMLZ", "MV"]:
			mpsWeighting = mpsFreqs[mps] / sumTokens
			# mpsWeighting = 1 / 9 # if you want to treat MPSs as equiprobable
			mpsWeightedAvEnt = {
				'cueless': 0,
				'suff': 0,
				'augSuff': 0,
				'prosAugSuff': 0
				}
			for vc in ["ICØ", "ICL", "ICN1", "ICN2", "ICNG"]:
				vcWeighting = vcFreqs[vc] / sumLexes
				# vcWeighting = 1 / 5 # if you treat VCs as equiprobable
				output.write(vc+"\t"+mps+"\t")
				cell = cellDict[".".join([vc, mps])]
				output.write(cell.form+"\t")
				output.write(str(cell.avgEnt[cue])+"\n")
				mpsWeightedAvEnt[cue] += cell.avgEnt[cue] * vcWeighting
				avEntropies[cue][mps] = mpsWeightedAvEnt[cue] # store in dictionary for comparison after next cue is added
			contr = avEntropies[prevCue][mps] - mpsWeightedAvEnt[cue]
			output.write("Av entropy with "+cue+" ")
			output.write('\t'.join([str(mps), str(mpsWeightedAvEnt[cue]), "\n"]))
			output.write("Av info contributed ")
			output.write('\t'.join([str(mps), str(contr), "\n"]))
			output.write("\n")
			systemWeightedAvEnt[cue] += mpsWeightedAvEnt[cue] * mpsWeighting
		output.write("System average entropy with "+cue+": "+str(systemWeightedAvEnt[cue])+"\n")
		output.write("\n\n")
		prevCue = cue

# looks through a set of items, and calculates their entropy
def getEntropy(items):
	#print items
	freqdist = nltk.FreqDist(items)
	probs = [freqdist.freq(l) for l in nltk.FreqDist(items)]
	return -sum([p * math.log(p,2) for p in probs])

if __name__ == "__main__":
	main()
