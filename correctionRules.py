# -*- coding: utf-8 -*-
#!/usr/bin/env python


adjTags = ["JJ","JJS","JJR"]
nounTags = ["NN","NNS"]
verbTags = ["VB","VBD","VBG","VBN","VBP","VBZ"]

import nltk
#import pdb
import math
import string
import re
from nltk import NgramModel
from nltk.probability import (LaplaceProbDist, ConditionalProbDist, ConditionalFreqDist, MLEProbDist, SimpleGoodTuringProbDist) 
from nltk.corpus import brown
import TranslateUtils


preNounAdjectives = ["beau","beaux","belle","belles","bel","laid","laids","laide","laides",
"joli","jolie","jolis","jolies","jeune","jeunes","vieux","vieil","noubel","nouvelle",
"nouvelles","bon","bonne","bons","bonnes","mauvais","mauvaise","mauvaises","grand",
"grands","grande","grandes","petit","petits","petite","petites","gros","grosse","grosses"]
articles = ["a","the","an",]
sentence1 = "this part of the contribution of and this contribution must be in consistency with the reaction international coordinate"
sentence2 = "Mr. the president thank you many of your comprehension"
adjSentence = "The cat fourth is sleeping"
titles = ["Mr.","Mrs.","Miss", "President"]


estimator = lambda fdist, bins: LaplaceProbDist(fdist,max(1,fdist.B()))  # laplace smoothing

trigramLM = NgramModel(3, brown.words(categories='news'), True,False,estimator)
bigramLM = NgramModel(2, brown.words(categories='news'), True,False,estimator)
unigramLM = NgramModel(1, brown.words(categories='news'), True,False,estimator)

# return a list of tupules of words and part of speech tags
# argument sentence is a STRING.
def POStag (sentence):
	postagged = nltk.pos_tag(sentence.split(" "))
	return postagged




# return the best translation of possible_translations based on 
# the position in the list combined with the laplace language-model probability of the word.
# probability is determined by:
#   P(word) = languageModelProbability/log(positionInList+2)
def get_best_translation(possible_translations,translated_list):
	translation_probs = []
	if (len(possible_translations) == 1):
		return possible_translations[0]
	if (len(translated_list) == 0): # use unigram
		for i in range(len(possible_translations)-1):
			logFactor = math.log(i+2)
			translation_probs.append(unigramLM.prob(possible_translations[i],translated_list) / logFactor)

	elif (len(translated_list )== 1): # use bigram
		for i in range(len(possible_translations)-1):
			logFactor = math.log(i+2)
			translation_probs.append(bigramLM.prob(possible_translations[i],translated_list) / logFactor)
	else: #use trigram
		for i in range(len(possible_translations)-1):#
			logFactor = math.log(i+2)
			translation_probs.append(trigramLM.prob(possible_translations[i],translated_list) / logFactor)

	#if ( translation_probs.index(max(translation_probs)) != 0):
	#	pdb.set_trace()
	toReturn = possible_translations[translation_probs.index(max(translation_probs))]
	return toReturn


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
	# get rid of WHOSE a 
	sentence = sentence.split(" ")
#	pdb.set_trace()
	for i in range(0,len(sentence)-2):
		if (i < len(sentence) -2 and postagged[i][1] in nounTags and sentence[i+1] == "of" and postagged[i+2][1] in adjTags):
#			print "    switching " + ' '.join(sentence[i:i+3]) + " ->  " + sentence[i+2] + " " + sentence[i]
			sentence[i+1] = sentence[i]
			sentence[i] = sentence[i+2]
			sentence[i+2] = ""
		if ("DT" in postagged[i][1] and (sentence[i+1] == "the")):
#			print "     switching " + ' '.join(sentence[i:i+3]) + " -> " + sentence[i] + " " + sentence[i+2]
			sentence[i+1] = "" 
		if (sentence[i] == "of" and postagged[i+1][1] in verbTags + adjTags):
#			print "     switching  of " + sentence[i+1] + " --> to " + sentence[i+1]
			sentence[i] = "to"
		if (sentence[i] in titles and sentence[i+1] == "the"):
			sentence[i+1] = ""
	return string.join(sentence)
#print POStag(sentence1)
#switchAdjectives(adjSentence)

#this method will actually have to check for verb phrases
def deBetweenVerbs(sentence, frenchSentence):
	frenchSentence = frenchSentence.split(" ")
	postagged = POStag(sentence)
	sentence = sentence.split(" ")
	for i in range(0, len(sentence) - 3):
		if (postagged[i][1] in verbTags and postagged[i + 1][0] == 'de' and postagged[i + 2][1] in verbTags):
			sentence[i + 1] = "to";

	return ' '.join(sentence)

def changeParceQue(frenchSentence):
	frenchSentence = frenchSentence.split(" ")
	for i in range(0, len(frenchSentence) - 2):
		if frenchSentence[i].lower() == "parce" and frenchSentence[i + 1] == 'que':
			frenchSentence.pop(i + 1);
	return ' '.join(frenchSentence)

def _token_is_negative_prefix(token):
  return token == 'ne' or token == 'n' or token == "n'"

def remove_double_negative(french_sentence):
  """In french, there are TWO negative words in a negative sentence.
  for example, 'je NE peux PAS'.  Both of those will translate to
  'not', changing te meaning of the sentence in direct translation.
  This function remove the 'NE' or 'n' to prevent this.
  """
  # TODO: Substantially messes up with 'envisagerait', because it's tranlation is two words.
  # we should get 'would not consider'; we instead get 'would consider not'
  tokens = TranslateUtils.get_list_of_words(french_sentence)
  result_tokens = []
  for i in xrange(len(tokens)):
    token = tokens[i]
    # If token is negative prefix and a token within three 3 spaces is
    # 'pas', then we are confident that this should be removed.
    if _token_is_negative_prefix(token) and 'pas' in tokens[i+1:i+6]:
      continue
    else:
      result_tokens.append(token)
  return ' '.join(result_tokens)

