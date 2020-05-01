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
		self.status = ''

Team = 'team-France'
GameIdsList = ['5987', '5986', '5984', '6292', '6291', '6255', '6456', '6455', '6454', '6315', '6316', '6314', '6597', '6596', '6594', '6760', '6759', '6757' , '7308', '7310', '7312', '8966', '9052', '9053']

TeamMembers = []
Players = []
NonTeamMembers = []
ClosedAccount = []

def collect_team_members():
	members = get('https://api.chess.com/pub/club/' + Team + '/members')
	for player in members['weekly']:
		TeamMembers.append(player['username'])
	for player in members['monthly']:
		TeamMembers.append(player['username'])
	for player in members['all_time']:
		TeamMembers.append(player['username'])

def add_player(PlayerList, newplayer):
	inlist = False
	for player in PlayerList:
		if player.name == newplayer.name:
			player.num_games += newplayer.num_games
			player.won_games += newplayer.won_games
			inlist = True
	if inlist == False:
		PlayerList.append(newplayer)


def collect_all_players_from_one_match(url, team):
	if len(team) > 0:
		for player in team:
			if 'stats' in player:
				username = player['username']
				newPlayer = Player(username)
				newPlayer.won_games += get(player['board'])['board_scores'][newPlayer.name]
				newPlayer.num_games += 2
				if username in TeamMembers:
					add_player(Players, newPlayer)
				else:
					add_player(NonTeamMembers, newPlayer)
	else:
		print('Match %s is not played or not published in live API yet' % (url))



def collect_all_players_from_one_url(url, teamName):
	match = get(url)
	if 'teams' in match:
		teams = get(url)['teams']
		if teams['team1']['name'] == teamName:
			collect_all_players_from_one_match(url, teams['team1']['players'])
		elif teams['team2']['name'] == teamName:
			collect_all_players_from_one_match(url, teams['team2']['players'])
		else:
			print('Problem with match id %s: %s or %s are not %s' % (url, teams['team1']['name'], teams['team2']['name'], teamName))
	else:
		print('url %s is not a valid match' %(url))

def collect_all_players_from_all_urls(teamName):
	for id in GameIdsList:
		url = 'https://api.chess.com/pub/match/live/' + id
		print('fetching url %s' % (url))
		collect_all_players_from_one_url(url, teamName)

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
	size = len(NonTeamMembers)
	print('Players that left your team : ', size)
	for player in NonTeamMembers:
		profile = get('https://api.chess.com/pub/player/'+player.name)
		status = profile['status']
		if status.startswith('closed'):
			player.status = status
			ClosedAccount.append(player)
		else:
			print('@%s : %.1f/%d' % (player.name, player.won_games, player.num_games))
	print('Closed Account (not necessarily fairplay) :')
	for player in ClosedAccount:
		print('@%s (%s)' % (player.name, player.status))

def main():
	team = get('https://api.chess.com/pub/club/' + Team)
	if 'name' in team:
		TeamName = team['name']
		collect_team_members()
		collect_all_players_from_all_urls(TeamName)
		calculate_win_percent()
		size = len(Players)
		print('Number of player : ', size)
		print_players_per_wins()
		#print_players_per_win_percent()
		print_players_that_left()
	else:
		print('Unknow team')

if __name__ == '__main__':
	main()
