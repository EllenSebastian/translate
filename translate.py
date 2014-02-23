# -*- coding: utf-8 -*-
#!/usr/bin/env python


adjTags = ["JJ","JJS","JJR"]
nounTags = ["NN","NNS"]
verbTags = ["VB","VBD","VBG","VBN","VBP","VBZ"]

import nltk
import pdb
import string
import re
from nltk import NgramModel
from nltk.probability import (ConditionalProbDist, ConditionalFreqDist, MLEProbDist, SimpleGoodTuringProbDist) 
from nltk.corpus import brown


preNounAdjectives = ["beau","beaux","belle","belles","bel","laid","laids","laide","laides",
"joli","jolie","jolis","jolies","jeune","jeunes","vieux","vieil","noubel","nouvelle",
"nouvelles","bon","bonne","bons","bonnes","mauvais","mauvaise","mauvaises","grand",
"grands","grande","grandes","petit","petits","petite","petites","gros","grosse","grosses"]
articles = ["a","the","an",]
sentence1 = "this part of the contribution of and this contribution must be in consistency with the reaction international coordinate"
sentence2 = "Mr. the president thank you many of your comprehension"
adjSentence = "The cat fourth is sleeping"
titles = ["Monsieur","Madame","Mademoiselle"]

def estimator(fdist,bins):
    # from http://nltk.googlecode.com/svn-/trunk/doc/api/nltk.model.ngram-pysrc.html
    return nltk.probability.SimpleGoodTuringProbDist(fdist) 

languageModel = NgramModel(3, brown.words(categories='news'), True,False,estimator)

# return a list of tupules of words and part of speech tags
# argument sentence is a STRING.
def POStag (sentence):
	postagged = nltk.pos_tag(sentence.split(" "))
	return postagged


def estimator(fdist,bins):
	# from http://nltk.googlecode.com/svn-/trunk/doc/api/nltk.model.ngram-pysrc.html
	return SimpleGoodTuringProbDist(fdist) 

def correct_with_LM(sentence,frenchSentence):
	#pdb.set_trace()
	pdb.set_trace()
	return sentence

# if adjectives are in the wrong order, correct them. 
# argument sentence is a STRING. 
def switchAdjectives (sentence,frenchSentence):
	frenchSentence = frenchSentence.split(" ")
	postagged = POStag(sentence)
	sentence = sentence.split(" ")
	for i in range(1,len(sentence)):
		if (postagged[i-1][1] in nounTags and (postagged[i][1] == "NNP" or postagged[i][1] in adjTags) and not frenchSentence[i] in preNounAdjectives):
			temp = sentence[i]
			sentence[i] = sentence[i-1]
			sentence[i-1] = temp
	return string.join(sentence)

# ugh this does not work currently. 
def removeArticles(sentence):
	postagged = POStag(sentence)
	sentence = re.sub("all of","all",sentence)
	# change "time of more" to "more time"  NOUN of ADJ
	# change "system of networking" to "networking system" , "market of capital" to "capital market" 
	# NOUN of NOUN (sometimes) 
	# change "of vERB" to "to verb"
	sentence = sentence.split(" ")

	for i in range(0,len(sentence)-2):
		if (i < len(sentence) -2 and postagged[i][1] in nounTags and sentence[i+1] == "of" and postagged[i+2][1] in adjTags):
			
			sentence[i+1] = sentence[i]
			sentence[i] = sentence[i+2]
			sentence[i+2] = ""
		if (sentence[i] == "of" and postagged[i+1][1] in verbTags):
			pdb.set_trace()
			sentence[i] = "to"
	return string.join(sentence)
#print POStag(sentence1)
#switchAdjectives(adjSentence)
