# -*- coding: utf-8 -*-
#!/usr/bin/env python


"""Tag	Meaning	Examples
ADJ	adjective	new, good, high, special, big, local
ADV	adverb	really, already, still, early, now
CNJ	conjunction	and, or, but, if, while, although
DET	determiner	the, a, some, most, every, no
EX	existential	there, there's
FW	foreign word	dolce, ersatz, esprit, quo, maitre
MOD	modal verb	will, can, would, may, must, should
N	noun	year, home, costs, time, education
NP	proper noun	Alison, Africa, April, Washington
NUM	number	twenty-four, fourth, 1991, 14:24
PRO	pronoun	he, their, her, its, my, I, us
P	preposition	on, of, at, with, by, into, under
TO	the word to	to
UH	interjection	ah, bang, ha, whee, hmpf, oops
V	verb	is, has, get, do, make, see, run
VD	past tense	said, took, told, made, asked
VG	present participle	making, going, playing, working
VN	past participle	given, taken, begun, sung
WH	wh determiner	who, which, when, what, where, how"""
adjTags = ["JJ","JJS","JJR"]
nounTags = ["NN","NNS"]
import nltk
import pdb
import string
preNounAdjectives = ["beau","beaux","belle","belles","bel","laid","laids","laide","laides",
"joli","jolie","jolis","jolies","jeune","jeunes","vieux","vieil","noubel","nouvelle","nouvelles","bon","bonne","bons","bonnes","mauvais",
"mauvaise","mauvaises","grand","grands","grande","grandes","petit","petits","petite","petites","gros","grosse","grosses"]

sentence1 = "this part of the contribution of and this contribution must be in consistency with the reaction international coordinate"
sentence2 = "Mr. the president thank you many of your comprehension"
adjSentence = "The cat fourth is sleeping"

# return a list of tupules of words and part of speech tags
# argument sentence is a STRING.
def POStag (sentence):
	postagged = nltk.pos_tag(sentence.split(" "))
	return postagged


# argument sentence is a STRING. 
def switchAdjectives (sentence):
	postagged = POStag(sentence)
	sentence = sentence.split(" " )
	for i in range(1,len(sentence)):
		if (postagged[i-1][1] in nounTags and postagged[i][1] in adjTags):
			temp = sentence[i]
			sentence[i] = sentence[i-1]
			sentence[i-1] = temp
	return string.join(sentence)

print POStag(sentence1)
switchAdjectives(adjSentence)
