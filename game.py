import random, os, re

def create_lists(words, players):
	indices = range(len(words))
	lists = {}
	for player in players:
		lists[player] = list(indices)
		random.shuffle(lists[player])
	return lists

def random_teams(lists):
	a = dict([(x, lists[x]) for x in random.sample(lists.keys(), len(lists) / 2)])
	b = dict([(x, lists[x]) for x in lists.keys() if x not in a.keys()])
	return {'A':a, 'B':b}

def score_player(player_indices, actual_indices):
	score = 0
	player_index = 0
	for index in actual_indices:
		if index != player_indices[player_index]:
			continue
		score += 1
		player_index = (player_index + 1) % len(player_indices)
	return score

def get_next_word(player_indices, actual_indices):
	score = 0
	player_index = 0
	for index in actual_indices:
		if index != player_indices[player_index]:
			continue
		score += 1
		player_index = (player_index + 1) % len(player_indices)
	return player_indices[player_index]

def print_team(name, team, actual_indices, words):
	scores = map(lambda x: score_player(x, actual_indices), team.values())
	next_indices = map(lambda x: get_next_word(x, actual_indices), team.values())
	score = sum(scores)
	players = team.keys()
	print('\n\nTeam %s %i' %(name, score))
	for player, score, next_index in zip(players, scores, next_indices):
		print('\t%-12s %i (next: %2i %s)' %(player, score, next_index, words[next_index]))

def print_team_scores(teams, actual_indices, words):
	for name, team in teams.iteritems():
		print_team(name, team, actual_indices, words)

def print_word_list(words):
	print('Word List:')
	for i, word in enumerate(words):
		print('\t%2i %s' %(i, word))

def swap_player(teams, a_team, a_player, b_team, b_player):
	if a_team not in teams:
		raise Exception('Bad a_team: "%s"' %(a_team))
	if a_player not in teams[a_team]:
		raise Exception('Bad a_player: "%s"' %(a_player))

	if b_team not in teams:
		raise Exception('Bad b_team: "%s"' %(b_team))
	if b_player not in teams[b_team]:
		raise Exception('Bad b_player: "%s"' %(b_player))

	teams[a_team][b_player] = teams[b_team][b_player]
	teams[b_team][a_player] = teams[a_team][a_player]
	del teams[a_team][a_player]
	del teams[b_team][b_player]
	return 'Swapped %s and %s' %(a_player, b_player)

def handle_swap(teams, tokens):
	if len(tokens) != 2:
		raise Exception('Bad command: "%s"' %(' '.join(tokens)))
	return swap_player(teams, 'A', tokens[0], 'B', tokens[1])

def handle_word(actual_indices, words, tokens):
	if len(tokens) != 1:
		raise Exception('Bad command: "%s"' %(' '.join(tokens)))
	index = int(tokens[0])
	if index < 0 or index >= len(words):
		raise Exception('Bad index %i' %(index))
	actual_indices.append(index)
	return 'Added word %2i %s' %(index, words[index])

def handle_undo(actual_indices, words, tokens):
	if len(tokens) != 0:
		raise Exception('Bad command: "%s"' %(' '.join(tokens)))
	if len(actual_indices) == 0:
		raise Exception('Nothing to undo!')
	removed = actual_indices.pop()
	return 'Removed word %2i %s' %(removed, words[removed])

def handle_cmd(cmd, teams, words, actual_indices):
	tokens = cmd.split(' ')
	if len(tokens) == 0:
		raise Exception('Bad command: "%s"' %(cmd))
	action = tokens[0]
	tokens = tokens[1:]
	result = None
	if action == 'swap' or action == 's':
		result = handle_swap(teams, tokens)
	elif action == 'word' or action == 'w':
		result = handle_word(actual_indices, words, tokens)
	elif action == 'undo' or action == 'u':
		result = handle_undo(actual_indices, words, tokens)
	elif re.match('^[0-9]+$', cmd):
		result = handle_word(actual_indices, words, [cmd])
	else:
		raise Exception('Bad command: "%s"' %(cmd))
	return result

def print_recent_words(actual_indices, words, max_print):
	print('\nRecent words:')
	for i in xrange(max_print):
		index = len(actual_indices) - max_print + i
		if index >= 0 and index < len(actual_indices):
			print('\t' + words[actual_indices[index]])
	if len(actual_indices) == 0:
		print('\t<empty>')

def main(seed = None):
	if seed is not None:
		random.seed(seed)
	words = [x.strip() for x in file('words.txt')]
	players = [x.strip() for x in file('players.txt')]
	lists = create_lists(words, players)
	teams = random_teams(lists)
	actual_indices = []

	os.system('clear')
	while True:
		print_word_list(words)
		print_team_scores(teams, actual_indices, words)
		print_recent_words(actual_indices, words, 5)
		cmd = raw_input('Election2016$ ')
		try:
			os.system('clear')
			print('Command was "%s"' %(cmd))
			result = handle_cmd(cmd, teams, words, actual_indices)
			print result
			if result == 'Quit':
				break
		except Exception as e:
			print(e)

if __name__ == '__main__':
	main(seed = 1)
