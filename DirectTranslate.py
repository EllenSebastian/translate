# -*- coding: utf-8 -*-
#!/usr/bin/env python
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import FrenchStemmer

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
      translation_dict = self._get_lemmatized_dict(translation_dict)
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
    
  def translate(self, sentence, delims=",' ", remove=''):
    tokens = self._get_list_of_words(sentence, delims, remove)
    translated_list = []
    for token in tokens:
      token = self.french_stemmer.stem(token).lower()
      if token in self.translation_dict:
        possible_translations = self.translation_dict[token]
        if possible_translations:
          # Use first translation in the list
          translation = possible_translations[0]
          translated_list.append(translation)
      else:
        print 'MISSING WORD:', token
    return ' '.join(translated_list)
    
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


test_dict = {
	u"ce": ["this", "it", "that"],
	u"n'est": ["is"],
	u"qu'une": ["a"],
	u"partie": ["part", "portion", "party", "section", "match", "round", "proportion", "stroke", "slice", "stretch", "game", "parcel", "hand"],
	u"de": ["of", "to", "from", "by", "out of", "off", "at", "with", "than"],
	u"la": ["the", "her", "it", "lah", "la", "A"],
	u"contribution": ["contribution", "donation", "input"],
	u"l'UE": ["EU"],
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
	u"compréhension": ["comprehension", "connotation", "grasp", "hold", "ken"]
}

test_inputs = [
 u"Ce n'est qu'une partie de la contribution de l'UE, et cette contribution doit être en cohérence avec la réaction internationale coordonnée.",
 u"Monsieur le Président, merci beaucoup de votre compréhension."
]
# Test it out    
def main():
  translator = DirectTranslate(test_dict, lemmatized=False)
  for input in test_inputs:
    print translator.translate(input, remove='.,')

if __name__ == '__main__':
  main()