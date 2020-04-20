from codecs import open
from datetime import date
import os.path
import requests
import time

def get(url):
    return requests.get(url).json()

class Player(object):
	def __init__(self, name):
		self.name = name
		self.num_games = 0
		self.won_games = 0
		self.win_percent = 0

TeamName = "Team France"
TeamUrl = 'https://api.chess.com/pub/club/team-France'
GameIdsList = ['5987', '5986', '5984', '6292', '6291', '6255', '6456', '6455', '6454', '6315', '6316', '6314', '6597', '6596', '6594', '6760', '6759', '6757' , '7308', '7310', '7312']
TeamMembers = []
NonTeamMembers = []
Players = []

def collect_team_members():
	for player in get(TeamUrl + '/members')['weekly']:
		TeamMembers.append(player['username'])
	for player in get(TeamUrl + '/members')['monthly']:
		TeamMembers.append(player['username'])
	for player in get(TeamUrl + '/members')['all_time']:
		TeamMembers.append(player['username'])

def add_player(newplayer):
	inlist = False
	for player in Players:
		if player.name == newplayer.name:
			player.num_games += newplayer.num_games
			player.won_games += newplayer.won_games
			inlist = True
	if inlist == False:
		Players.append(newplayer)


def collect_all_players_from_one_match(team):
	for player in team:
		if 'stats' in player:
			username = player['username']
			if username in TeamMembers:
				newPlayer = Player(username)
				newPlayer.won_games += get(player['board'])['board_scores'][newPlayer.name]
				newPlayer.num_games += 2
				add_player(newPlayer)
			else:
				NonTeamMembers.append(username)



def collect_all_players_from_one_url(url):
	teams = get(url)['teams']
	if teams['team1']['name'] == TeamName:
		collect_all_players_from_one_match(teams['team1']['players'])
	elif teams['team2']['name'] == TeamName:
		collect_all_players_from_one_match(teams['team2']['players'])
	else:
		print('Problem with match id %d' % (url))

def collect_all_players_from_all_urls():
	for id in GameIdsList:
		collect_all_players_from_one_url('https://api.chess.com/pub/match/live/' + id)

def calculate_win_percent():
	for player in Players:
		player.win_percent = (player.won_games*100.0) / player.num_games

def print_players_per_wins():
	print('Players sorted by points earned')
	Players.sort(key=lambda x: x.won_games, reverse=True)
	for player in Players:
		print('@%s : %.1f/%d (perf %.1f)' % (player.name, player.won_games, player.num_games, player.win_percent))
	print('\n')

def print_players_per_win_percent():
	print('Players sorted by winning percentage')
	Players.sort(key=lambda x: x.win_percent, reverse=True)
	for player in Players:
		print('@%s : %.1f/%d (perf %.1f)' % (player.name, player.won_games, player.num_games, player.win_percent))
	print('\n')

def print_players_that_left():
	ntm = list(set(NonTeamMembers)) # make sure to print unique entries
	size = len(ntm)
	print('Players that left your team', size)
	for player in ntm:
		print('@%s' % (player))
	print('\n')

def main():
	collect_team_members()
	collect_all_players_from_all_urls()
	calculate_win_percent()
	size = len(Players)
	print('Number of player', size)
	print_players_per_wins()
	print_players_per_win_percent()
	print_players_that_left()

if __name__ == '__main__':
	main()
