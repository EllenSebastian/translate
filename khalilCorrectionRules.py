import nltk

# return a list of tupules of words and part of speech tags
# argument sentence is a STRING.
def POStag (sentence):
	postagged = nltk.pos_tag(sentence.split(" "))
	return postagged

def _token_is_negative_prefix(token):
  return token == 'ne' or token == 'n'

def remove_double_negative(french_sentence):
  """In french, there are TWO negative words in a negative sentence.
  for example, 'je NE peux PAS'.  Both of those will translate to
  'not', changing te meaning of the sentence in direct translation.
  This function remove the 'NE' or 'n' to prevent this.
  """
  tokens = french_sentence.split(' ')
  result_tokens = []
  for i in xrange(len(tokens)):
    print token
    token = tokens[i]
    # If token is negative prefix and a token within three 3 spaces is
    # 'pas', then we are confident that this should be removed.
    if _token_is_negative_prefix(token) and 'pas' in tokens[i+1:i+5]:
      verb_index = i
      continue
    elif 'pas' == token:
      print '###### found pas'
      # Handles the different ordering, ie 'n'envisagerait même pas'
      # (not would consider not)
      # would have just become 'envisagerait même pas' (would consider not),
      # while we want
      # 'envisagerait même pas' (would not consider)
      result_tokens.insert(verb_index, token)
    else:
      result_tokens.append(token)
  return ' '.join(result_tokens)

# TODO: I'm not entirely convinced that this is wise.  
def alter_possessives(english_sentence):
  pass