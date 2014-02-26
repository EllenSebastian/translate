# -*- coding: utf-8 -*-
#!/usr/bin/env python
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import FrenchStemmer
import codecs
import sys
import re
import pdb
from correctionRules import * 
import TranslateUtils

class DirectTranslate:
  """Word-by-word direct translator.
  
  Usage:
  translator = DirectTranslate(translation_dict)
  for sentence in file:
    print translator.translate(sentence, delims=",' ", remove='')
  """
  def __init__(self, translation_dict, lemmatized=False):
    self.english_lemmatizer = WordNetLemmatizer()
    self.french_stemmer = FrenchStemmer()
    if not lemmatized:
      stemmed_dict = self._get_lemmatized_dict(translation_dict)
    self.stemmed_dict = stemmed_dict
    self.translation_dict = translation_dict
    
  def _get_lemmatized_dict(self, dict):
    result = {}
    for french_word, english_translation_list in dict.iteritems():
      french_stem = self.french_stemmer.stem(french_word)
      english_translations = [
        self.english_lemmatizer.lemmatize(word) for word in english_translation_list
      ]
      # NOTE: This may or may not be the best stragetgy.  If two distinct
      # French words in the initial dict have the same stem,
      # it appends the two lists of translations.
      # TODO: Reconsider.
      # TODO: Consider removing duplicates from this new list.  But need to preserve order.
      if french_stem not in result:
        result[french_stem] = english_translations
      else:
        result[french_stem].extend(english_translations)
    return result

  # TODO: Could this go in TranslationUtils?
  def _tokenize_punctuation(self,sentence):
  	sentence = re.sub(","," ,", sentence)
  	sentence = re.sub(";"," ;", sentence)
  	sentence = re.sub("\?"," ?", sentence)
  	sentence = re.sub("\."," .", sentence)
  	sentence = re.sub("\xab"," \" ", sentence)
  	sentence = re.sub("\xbb"," \" ", sentence)
  	sentence = re.sub("n'","ne ", sentence)
  	sentence = re.sub("l'","le ", sentence)
  	sentence = re.sub("d'","de ", sentence)
  	sentence = re.sub("qu'","que ", sentence)
  	return sentence
  def _untokenize_punctuation(self,sentence):
  	sentence = re.sub("[ ]+,",",", sentence)
  	sentence = re.sub("[ ]+;",";", sentence)
  	sentence = re.sub("[ ]+\?","?", sentence)
  	sentence = re.sub("[ ]+\.",".", sentence)
  	sentence = re.sub("[ ]+\"," ,"\"", sentence)
  	return sentence
  	
  def _get_preprocessed_sentence(self, french_sentence):
    """Apply any preprossing rules here.
    Args:
      french_sentence: string; the sentence in french
    
    Returns:
      The sentence with all preprocessing rules applied.
    """
    french_sentence = unicode(french_sentence)
    french_sentence = remove_double_negative(french_sentence)
    french_sentence = changeParceQue(french_sentence)
#    french_sentence = add_plural_tags(french_sentence)
#    print 'Pre:',french_sentence
    return french_sentence

  # TODO: Add code to keep commas.  Translate them into a word.
  def translate(self, sentence, delims=" ", remove=''):
    sentence = self._get_preprocessed_sentence(sentence)
    sentence = self._tokenize_punctuation(sentence)
    tokens = self._get_list_of_words(sentence, delims, remove)
    translated_list = []
    for token in tokens:
      stemmed_token = self.french_stemmer.stem(token).lower()
      if stemmed_token in self.stemmed_dict:
        possible_translations = self.stemmed_dict[stemmed_token]
        if possible_translations:
          # Use first translation in the list
          translation = get_best_translation(possible_translations, translated_list)
          translated_list.append(translation)
      elif token in self.translation_dict:
        possible_translations = self.translation_dict[token]
        if possible_translations:
          # Use first translation in the list
          translation = get_best_translation(possible_translations, translated_list)
          translated_list.append(translation)
      else:
      	translated_list.append(token)
    translated_sentence = ' '.join(translated_list)
    translated_sentence = translated_sentence[0].upper() + translated_sentence[1:]
    
    translated_sentence = self._get_postprocessed_sentence(translated_sentence, sentence)

    translated_sentence = self._untokenize_punctuation(translated_sentence)
    return translated_sentence
    
  def _get_postprocessed_sentence(self, english_sentence, french_sentence):
    """Apply any postproccessing rules here.
    Args: 
      english_sentence: string; an english sentence
    
    Returns:
      The sentence with all postprocessing rules applied.
    """ 
    result = deBetweenVerbs(english_sentence, french_sentence)
    result = switchAdjectives(result, french_sentence)
    result = removeArticles(result)
    
    result = make_plural_nouns(result)
    # Remove any double spaces, make sure we call this last.
    result = re.sub('  ', ' ', result)
#    print 'Post:', result
    return result
  
  def _get_list_of_words(self, sentence, delims, remove):
    """Gets the sentence as a list of words, split at
      delims and with the characters in remove removed.
      
      NOTE: Assumes one-char delims and one-char removes.
    """
    result = [sentence]
    for delim in delims:
      result = self._get_stripped_tokens(result, delim, remove)
    return result
        
  def _get_stripped_tokens(self, strlist, delim, remove):
    result = []
    for str in strlist:
      tokens = str.split(delim)
      stripped_tokens = self._stripped_words(tokens, remove)
      result.extend(stripped_tokens)
    return result
  
  def _stripped_words(self, words, remove_chars):
    """Given a list of words and a string of characters to remove,
       returns the list of string with every one of the remove_chars
       removed."""
    result = []
    for word in words:
      word = self._strip_chars(word, remove_chars)
      result.append(word)
    return result
    
  def _strip_chars(self, word, chars_to_remove):
    """Given a word and list of chars, returns the word with
       every char in the list removed.
    """
    for char in chars_to_remove:
      word = word.replace(char, '')
    return word

vocab = {
  # Punctuation
  u",":[","],
  u".":["."],
  u";":[","],
  u"?":["?"],
  u"«":["\""],
  u"»":["\""],
  
  u"ce": ["this", "it", "that"],
  u"est": ["is"],
  u"une": ["one", "a", "an"],
  u"qu": ["that", "than", "which", "whether"],
  u"partie": ["part", "portion", "party", "section", "match", "round", "proportion", "stroke", "slice", "stretch", "game", "parcel", "hand"],
  u"de": ["of", "to", "from", "by", "out of", "off", "at", "with", "than"],
  u"la": ["the", "her", "it", "lah", "la", "A"],
  u"contribution": ["contribution", "donation", "input"],
  u"UE": ["EU"],
  u"et": ["and"],
  u"cette": ["this", "that"],
  u"doit": ["must"],
  u"être": ["be", "exist"],
  u"en": ["in", "into", "to", "at", "during", "of", "thereof"],
  u"cohérence": ["consistency"],
  u"avec": ["with", "to", "along with", "together with", "along"],
  u"réaction": ["reaction", "response", "feedback"],
  u"internationale": ["international"],
  u"coordonnée": ["coordinate"],
  u"Monsieur": ["Mr.", "sir", "monsieur", "mister", "gent", "master"],
  u"le": ["the", "it", "him"],
  u"Président": ["president", "chief executive", "chairman", "chancellor", "chief", "foreman", "moderator"],
  u"merci": ["thank you", "thank"],
  u"beaucoup": ["many", "much", "a lot", "far", "plenty", "so much", "widely", "a great many", "a great deal"],
  u"votre": ["your"],
  u"compréhension": ["comprehension", "connotation", "consideration", "grasp", "hold", "ken"],
  u"réalité": ["reality", "fact", "actuality", "case"],
  u"tout": ["all", "any", "every", "entire", "most important", "very", "in all", "all up", "whole", "anything"],
  u"un": ["a", "an", "one"],
  u"système": ["system", "method", "framework", "shape", "setup"],
  u"d’organes": ["bodies", "organs"],
  u"juridiques": ["legal", "juridicial", "jural", "statutory"],
  u"constitutionnels": ["constitutional"],
  u"dont": ["whose"],
  u"médiateur": ["mediator", "intermediary", "go-between", "troubleshooter", "arbitrator", "conciliator"],
  u"a": ["has"],
  u"été": ["summer", "summertime"],
  u"mis": ["placed"],
  u"sur": ["on", "about", "to", "over", "at", "onto", "with", "across", "before", "upon", "after", "against", "along"],
  u"pied": ["foot", "base", "leg", "bottom"],
  u"Pologne": ["Poland"],
  u"pour": ["for", "to", "of", "towards", "toward"],
  u"protéger": ["protect", "safeguard", "cover", "insure", "cushion", "fence", "guard", "defend", "shelter", "keep", "ensure", "patronize", "conserve", "vindicate"],
  u"liberté": ["freedom", "liberty", "license", "unrestraint"],
  u"garantir": ["ensure", "guarantee", "secure", "assure", "insure", "underwrite", "warrant", "indemnify", "avouch", "ark", "vouch for", "preserve", "back"],
  u"respect": ["respect", "regard", "deference", "fulfillment", "obeisance", "abidance", "reverence"],
  u"législation": ["legislation"],
  u"européenne": ["European"],
  u"par": ["by", "per", "through", "out of", "on", "via", "to", "par"],
  u"contre": ["against", "versus", "anti"],
  u"je": ["I"],
  u"ne": ["not"],
  u"peux": ["can", "may"],
  u"pas": ["not", "step", "footstep", "tread", "pace", "move", "pitch", "foot", "gauge", "gage", "steps"],
  u"accepter": ["accept", "take", "take on", "agree", "approve", "bear", "accede", "buy", "sell"],
  u"amendement": ["amendment"],
  u"3": ["3"],
  u"parce": ["because"],
  u"que": ["that", "than", "whether", "which", "what", "whom", "how"],
  u"grand-mère": ["grandmother", "grandma", "granny", "grannie"],
  u"allemande": ["German"],
  u"est": ["is", "east", "eastern"],
  u"diabétique": ["diabetic"],
  u"tous": ["all", "every", "everything"],
  u"les": ["<PLURAL>the</PLURAL>", "<PLURAL>them</PLURAL>"],
  u"européen": ["European"],
  u"doivent-ils": ["must they", "should they"],
  u"cesser": ["stop", "cease", "discontinue", "leave off", "come off", "desist"],
  u"manger": ["eat", "run through", "drink", "feed", "mouth", "meal", "manage", "make"],
  u"du": ["of", "the", "from"],
  u"sucre": ["sugar"],
  u"demande": ["request", "demand", "application", "claim", "requistion", "offer", "instance", "counterclaim", "bid", "desire"],
  u"donc": ["therefore", "thus", "whereof", "consequently"],
  u"une": ["a", "an", "one"],
  u"fois": ["times", "time"],
  u"plus": ["more", "most", "further", "any", "plus"],
  u"aux": ["<PLURAL>to</PLURAL>"],
  u"député": ["deputy", "member of parliament", "congressman", "representative", "burgess", "delegate"],
  u"parlement": ["parliament", "house"],
  u"lorsqu": ["when"],
  u"ils": ["they", "those"], 
  u"appel": ["call", "claim", "appeal", "calling", "plea", "summons", "roll call", "address"],
  u"nominal": ["nominal", "titular"],
  u"demain": ["tomorrow"],
  u"se": ["themselves", "himself", "herself"],
  u"prononcer": ["pronounce", "say", "enunciate", "sound", "adjudge", "utter"],
  u"faveur": ["favor", "favour"],
  u"droit": ["right", "sraight", "upright", "righteous", "upstading", "single-breasted", "law", "duty", "title", "fee", "due"],
  u"Assemblée": ["assembly"],
  u"à": ["to", "in", "at", "with", "upon", "by"],
  u"régir": ["govern", "administer", "steward"],
  u"ses": ["<PLURAL>its</PLURAL>", "<PLURAL>his</PLURAL>", "<PLURAL>her</PLURAL>"],
  u"propres": ["own", "clean", "fair", "cleanly", "neat", "immaculate", "tidy", "proper", "taut", "potty-trained"],
  u"affaires": ["business", "affairs", "things", "stuff", "trading", "clothes", "belongings", "transaction", "traps", "gear", "commerce", "kit"],
  u"ces": ["<PLURAL>these</PLURAL>", "<PLURAL>this</PLURAL>", "<PLURAL>that</PLURAL>"],
  u"auditions": ["hearings"],
  u"ont": ["have", "get", "own", "possess", "stock", "hold"],
  u"réussite": ["success", "achievement", "patience", "go"],
  u"retentissante": ["resounding", "ringing", "thundering", "plangent", "ringed"],
  u"partant": ["thus", "consequently", "runner", "starter"],
  u"citoyens": ["people"],
  u"Union": ["Union"],
  u"proposer": ["propose", "offer", "suggest", "move", "nominate", "hold out", "propound", "slate"],
  u"on": ["one"],
  u"vote": ["vote", "voting", "polling", "poll"],
  u"version": ["version", "translation"],
  u"espagnole": ["Spanish"],
  u"texte": ["text", "terms", "script", "wording", "work"],
  u"supprimant": ["removing"],
  u"Presidencia": ["Presidencia"],
  u"británica": [u"británica"],
  u"nous": ["we", "us"],
  u"devons": ["must"],
  u"clairement": ["clearly", "distinctly", "plainly", "patently", "plain", "fairly"],
  u"signaler": ["report", "point out", "signalize", "mention", "notify to", "flag"],
  u"au": ["of", "the"],
  u"gouvernement": ["government", "administration", "ministry"],
  u"bulgare": ["Bulgarian"],
  u"envisagerait": ["would consider"],
  u"moi-même": ["myself"],
  u"voter": ["vote", "cast a vote", "poll"],
  u"traité": ["treaty", "treatise", "processed", "accord", "pact", "convention", "disquisition"],
  u"adhésion": ["membership"],
  u"d": ["of", "the"],
  u"si": ["if", "whether", "so", "such", "that", "as"],
  u"exemple": ["example", "instance", "pattern", "sample", "type", "model", "exemplar", "epitome", "foretype", "specimen", "word"],
  u"article": ["article"],
  u"157": ["157"],
  u"code": ["code", "statute-book"],
  u"pénal": ["penal"],
  u"qui": ["which", "that", "who", "whom"],
  u"établit": ["establish", "develop", "found", "plant", "induct", "initiate", "put up", "set up in", "ascertain", "draw", "nail down"],
  u"discrimination": ["discrimination"],
  u"inacceptable": ["unacceptable", "inadmissable", "intolerable"],
  u"citoyenne": ["citizen", "burgher", "freeman"],
  u"homosexuel": ["homosexual", "gay", "queer"],
  u"Bulgarie": ["Bulgaria"],
  u"devait": ["was"],
  u"maintenir": ["maintain", "sustain", "retain", "steady", "protect", "fence", "screen", "hold firm", "uphold", "preserve", "prop", "hold tight", "cradle", "fend"],
  u"honorable": ["honorable", "honourable", "respectable", "creditable", "reputable", "decent"],
  u"parlementaire": ["parliamentary", "parliamentarian"],
  u"ai": ["have"],
  u"n": ["not"],
  u"aucune": ["no"],
  u"peine": ["penalty", "sentence:", "trouble", "sorrow", "grief", "infirmity", "pain", "bitterness", "ache", "forfeit", "gruel", "heartache", "pains"],
  u"vous": ["you", "ye", "you all"],
  u"répondre": ["answer", "respond", "reply", "speak", "answer back", "write back", "field", "rejoin"],
  u"car": ["car", "bus", "motor"],
  u"me": ["me", "myself"],
  u"suis": ["am"],
  u"moi": ["me", "I", "ego", "us"],
  u"permis": ["allowed", "permitted", "permit", "license", "allowable", "permissable", "order"],
  u"citer": ["quote", "cite", "mention", "name", "adduce", "bear witness", "summon to appear"],
  u"également": ["also", "likewise", "equally", "evenly"],
  u"importance": ["the importance"],
  u"problème": ["problem", "issue", "trouble", "headache", "question", "kink", "nodus", "snag"],
  u"rapport": ["report", "ratio", "relation", "respect", "connection", "reference", "record", "bearing", "affinity", "proceedings", "communication", "relevancy"],
  u"élargissement": ["enlargement"],
  u"l": ["the"],
  u"ailleurs": ["somewhere else"],
  u"cours": ["course", "price", "path", "run", "race", "rate", "lecture", "lesson", "school", "session", "period", "tenor", "tide", "quotation", "tuition"],
  u"des": ["<PLURAL>of</PLURAL>"],
  u"deux": ["two", "deuce"],
  u"prochain": ["next", "upcoming", "forthcoming"],
  u"décennie": ["decade", "decennary", "decennium"],
  u"augmentation": ["increase", "gain", "rise", "boost", "growth", "increment", "advance", "augmentation", "augment", "raise", "enhancement", "accession", "build-up", "expansion", "surge", "swell"],
  u"fort": ["strong", "hard", "stout", "large", "heavy", "great", "big", "loud", "broad", "intense", "fierce", "potent"],
  u"rejets": ["releases"],
  u"produiront": ["produce", "generate", "cause", "manufacture", "output", "grow", "turn out", "crank out", "put forth", "issue", "bring forward", "carry"],
  u"dans": ["in", "into", "within", "on", "during", "inside", "along", "aboard"],
  u"pays": ["country", "nation", "land", "home", "soil"],
  u"voie": ["way", "path", "track", "course", "route", "road", "lane"],
  u"développement": ["development", "developing", "growth", "improvement", "processing", "outgrowth", "upgrowth", "expansion"],
  u'lieu': ['place', 'lieu', 'room', 'scene', 'venue', 'locale', 'locus', 'locality'],
  u'quoi': ['what', 'which'],
  # TODO: Consider the phrase 'bien sûr', and possibly others like it.
  u'bien': ['well', 'good', 'OK', 'very', 'all right', 'rightly', 'kindly', 'nicely', 'greatly'], # TRUNCATED DUE TO NUMBER OF TRANSLATIONS
  u'sûr': ['sure', 'safe', 'secure', 'certain', 'reliable', 'dependable', 'clear', 'sound', 'steady', 'trusty', 'confident'], 
  u'mêlez': ['mix', 'mingle', 'shuffle', 'mix up'],
  u'affaires': ['business', 'affairs', 'things', 'stuff', 'trading', 'clothes', 'belongings', 'transaction', 'traps', 'gear', 'commerce', 'kit'],
  u'Caucase': ['Caucasus'],
  u'Sud': ['south'],
  u'mer': ['sea', 'blue', 'water'],
  u'Noire': ['black'],
  u'régimes': ['scheme', 'diet', 'government', 'regimen'],
  u'sont': ['be', 'exist'],
  u'particulièrement': ['particularly', 'especially', 'specially', 'notably', 'peculiarly', 'extra'],
  u'stables': ['stable', 'steady', 'firm', 'constant', 'enduring', 'stabile'],
  u'souhaitent': ['wish', 'hope', 'wish for', 'like', 'greet'],
  # TODO: Reconsider hyphenation.  I think it's probably best to keep it hyphenated, but
  # it's something to think about.  Also check this on the stemmer.
  u'peut-être': ['perhaps', 'maybe', 'possibly', 'perchance', 'probably', 'supposedly'],
  u'ingérence': ['interference', 'intrusion'],
  u'situation': ['situation', 'location', 'position', 'status', 'place', 'post', 'circumstance', 'context', 'pass'],
  u'Tchétchénie' : ['Chechnya'],
  u'mauvaise': ['bad', 'ill', 'poor', 'evil', 'faulty', 'black', 'common', 'coarse', 'leaden', 'nasty', 'shabby', 'unpleasant', 'paltry', 'perverse', 'failing', 'villanous', 'fiendish'],
  u'considère': ['considered', 'well-respected'],
  u'système': ['system', 'method', 'framework', 'shape', 'setup'],
  u'réseaux': ['network', 'grid' 'web', 'connection', 'connexion', 'net', 'mesh'],
  u'déterminant': ['determining', 'decisive'], # NOTE: FROM WORDREFERENCE INSTEAD
  u'échange': ['exchange', 'interchange', 'swap', 'reciprocation', 'swop', 'barter', 'truck'],
  u'informations': ['information', 'data', 'news'],
  u'connaissances': ['knowledge', 'knowing', 'cognition', 'expertise', 'reading', 'acquaintance', 'familiarity', 'information', 'science', 'cognizance', 'ken', 'lore'],
  u'réalisation': ['realization', 'achievement', 'implementation', 'attainment', 'accomplishment', 'execution', 'production', 'making', 'direction', 'consummation', 'attainability', 'enforcement', 'implementing', 'fulfillment', 'filmmaking'],
  u'projet': ['project', 'plan', 'design', 'idea', 'scheme', 'schema', 'blueprint', 'venture', 'business', 'topic'],
  u'commun': ['join', 'common', 'mutual', 'shared', 'communal', 'common-or-garden', 'normal', 'rife'],
  u'entre': ['between', 'among', 'in between', 'betwixt', 'amongst'],
  u'diverses': ['various', 'diverse', 'miscellaneous', 'several', 'varied', 'variant', 'manifold', 'varicoloured', 'varicolored', 'sundry', 'multifarious'],
  u'zone': ['area', 'zone', 'region', 'box', 'belt', 'pool'],
  u'union': ['union', 'unity', 'association', 'conjunction'],
  u'rappelle': ['recall', 'remind', 'remember', 'call back', 'withdraw', 'call to mind', 'bring back', 'call again', 'admonish'],
  u'ailleurs': ['somewhere else'],
  u'pouvoir': ['power', 'can', 'authority', 'authorization', 'agency', 'command', 'rule', 'proxy', 'may', 'might'],
  u'réalisé': ['achieve', 'realize', 'carry out', 'accomplish', 'execute', 'attain', 'actualize', 'fulfill'], # TRUNCATED DUE TO NUMBER OF TRANSLATIONS
  u'pleinement': ['fully', 'wholly'],
  u'exploiter': ['exploit', 'operate', 'harness', 'tap', 'work', 'follow up', 'capitalize on', 'utilize', 'quarry', 'milk', 'mine', 'avail'],
  u'autres': ['other', 'remainder'],
  u'instrument': ['instrument', 'tool', 'appliance', 'cradle', 'implement'],
  u'qui': ['which', 'that', 'who', 'whom'],
  u'existent': ['exist', 'be', 'be there', 'dwell'],
  u'déjà': ['already', 'previously', 'ever', 'yet'],
  u'comme': ['as', 'like', 'such as', 'since', 'as though', 'like this', 'like that', 'per'],
  u'carrefours': ['crossroads', 'intersection', 'junction', 'turning'],
  u'pense': ['think', 'suppose', 'guess', 'imagine', 'reckon', 'reflect', 'ruminate', 'conceive', 'realize', 'fancy', 'figure', 'wonder', 'say'],
  u'difficile': ['difficult', 'hard', 'tough', 'knotty', 'uneasy', 'laboured', 'labored', 'arduous', 'awkward', 'sticky', 'painful', 'unmanageable'], # TRUNCATED DUE TO NUMBER OF TRANSLATIONS
  u'surestimer': ['overestimate', 'overvalue'],
  u'importance': ['importance', 'significance', 'weight', 'prominence', 'worth', 'account', 'prominency', 'pith', 'standing', 'matter', 'largeness'], # TRUNCATED DUE TO NUMBER OF TRANSLATIONS
  u'marché': ['market', 'market place', 'mart', 'emporium', 'bargain'],
  u'capitaux': ['capital', 'fund']
}

# Test it out    
def main(args):
  translator = DirectTranslate(vocab, lemmatized=False)
  with codecs.open(args[0], 'r', 'utf-8') as f:
    for line in f:
      print line[:-1] # Remove newline
      print translator.translate(line, remove=u'\n')
      print
      print

if __name__ == '__main__':
  main(sys.argv[1:])
