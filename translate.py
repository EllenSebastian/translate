# -*- coding: utf-8 -*-
#!/usr/bin/env python
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import FrenchStemmer
import codecs
import sys
import re
import pdb
import translation_dictionary
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
    #self.french_stemmer = FrenchStemmer()
    if not lemmatized:
      stemmed_dict = self._get_lemmatized_dict(translation_dict)
    self.stemmed_dict = stemmed_dict
    self.translation_dict = translation_dict
    
  def _get_lemmatized_dict(self, dict):
    result = {}
    for french_word, english_translation_list in dict.iteritems():
      french_stem = french_word #self.french_stemmer.stem(french_word)
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
      stemmed_token = token.lower()#self.french_stemmer.stem(token).lower()
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
    # result = deBetweenVerbs(english_sentence, french_sentence)
    result = switchAdjectives(english_sentence, french_sentence)
    result = make_plural_nouns(result)
    result = removeArticles(result)

    # Remove any double spaces, make sure we call this last.
    result = re.sub('  ', ' ', result)
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

# Test it out    
def main(args):
  translator = DirectTranslate(translation_dictionary.vocab, lemmatized=False)
  with codecs.open(args[0], 'r', 'utf-8') as f:
    for line in f:
      print line[:-1] # Remove newline
      print translator.translate(line, remove=u'\n')
      print
      print

if __name__ == '__main__':
  main(sys.argv[1:])
