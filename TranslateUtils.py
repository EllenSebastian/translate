def get_list_of_words(sentence, delims=",' ", remove=''):
  """Gets the sentence as a list of words, split at
    delims and with the characters in remove removed.
      
    NOTE: Assumes one-char delims and one-char removes.
  """
  result = [sentence]
  for delim in delims:
    result = _get_stripped_tokens(result, delim, remove)
  return result
  
def _get_stripped_tokens(strlist, delim, remove):
  result = []
  for str in strlist:
    tokens = str.split(delim)
    stripped_tokens = _stripped_words(tokens, remove)
    result.extend(stripped_tokens)
  return result
  
def _stripped_words(words, remove_chars):
  """Given a list of words and a string of characters to remove,
     returns the list of string with every one of the remove_chars
     removed.
  """
  result = []
  for word in words:
    word = _strip_chars(word, remove_chars)
    result.append(word)
  return result
    
def _strip_chars(word, chars_to_remove):
  """Given a word and list of chars, returns the word with
     every char in the list removed.
  """
  for char in chars_to_remove:
    word = word.replace(char, '')
  return word