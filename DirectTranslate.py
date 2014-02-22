#!/usr/bin/env python

class DirectTranslate:
  """Word-by-word direct translator.
  
  Usage:
  translator = DirectTranslate(translation_dict)
  for sentence in file:
    print translator.translate(sentence, delims=",' ", remove='')
  """

  def __init__(self, translation_dict):
    self.translation_dict = translation_dict
    
  def translate(self, sentence, delims=",' ", remove=''):
    tokens = self._get_list_of_words(sentence, delims, remove)
    translated_list = []
    for token in tokens:
      if token in self.translation_dict:
        possible_translations = self.translation_dict[token]
        if possible_translations:
          # Use first translation in the list
          translation = possible_translations[0]
          translated_list.append(translation)
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
  'a': ['1', 'dsfsfd'],
  'b': ['2', 'lakjdf'],
  'c': ['3', 'asdfsd'],
  'none': None,
}

# Test it out    
def main():
  input = 'a b\'c none, b'
  translator = DirectTranslate(test_dict)
  print translator.translate(input)

if __name__ == '__main__':
  main()