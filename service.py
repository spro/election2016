from game import *
import somata

words = [x.strip() for x in file('words.txt')]
players = [x.strip() for x in file('players.txt')]
lists = create_lists(words, players)
teams = random_teams(lists)
actual_indices = []

def getWords(cb): cb(words)
def getPlayers(cb): cb(players)
def getTeams(cb): cb(teams)
def getPlayed(cb): cb(map(lambda x: words[x], actual_indices))

def getScore(team, player, cb):
    response = score_player(teams[team][player], actual_indices)
    cb(response)

def _getScores():
    team_scores = {}
    for name, team in teams.iteritems():
        scores = map(lambda x: score_player(x, actual_indices), team.values())
        next_indices = map(lambda x: get_next_word(x, actual_indices), team.values())
        score = sum(scores)
        players = team.keys()
        print('\n\nTeam %s %i' %(name, score))
        team_scores[name] = {}
        for player, score, next_index in zip(players, scores, next_indices):
            print('\t%-12s %i (next: %2i %s)' %(player, score, next_index, words[next_index]))
            team_scores[name][player] = {'score': score, 'next': words[next_index]}
    return team_scores

def getScores(cb):
    cb(_getScores())

def doSwap(name1, name2, cb):
    response = swap_player(teams, 'A', name1, 'B', name2)
    getScores(cb)

def doWord(index, cb):
    index = int(index)
    actual_indices.append(index)
    scores = _getScores()
    cb({'scores': scores, 'played': map(lambda x: words[x], actual_indices)})

def doUndo(cb):
    removed = actual_indices.pop()
    print('Removed word %2i %s' %(removed, words[removed]))
    scores = _getScores()
    cb({'scores': scores, 'played': map(lambda x: words[x], actual_indices)})

commands = {
    'score': getScore,
    'scores': getScores,
    'words': getWords,
    'players': getPlayers,
    'teams': getTeams,
    'played': getPlayed,
    'swap': doSwap,
    'word': doWord,
    'undo': doUndo
}

test = somata.Service('election2016', commands, {'bind_port': 5555, 'heartbeat': 0})
