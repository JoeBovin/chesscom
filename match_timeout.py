from codecs import open
from datetime import date
import os.path
import requests
import time

Team = 'team-France'
Id = '1111856'
threshold = 25

def get(url):
    return requests.get(url).json()

def filter_team_members(team):
	for player in team['players']:
		if player['timeout_percent'] > threshold:
			print('@%s (elo: %d, timeout: %.2f)' % (player['username'], player["rating"], player["timeout_percent"]))

def filter_match_members(teamName):
	match = get('https://api.chess.com/pub/match/' + Id)
	team1 = match['teams']['team1']
	team2 = match['teams']['team2']
	if team1['name'] == teamName:
		filter_team_members(team1)
	elif team2['name'] == teamName:
		filter_team_members(team2)
	else:
		print('This match is not for your team %s (%s or %s)' % (teamName, match['teams']['team1']['name'], match['teams']['team2']['name']))

def main():
	team = get('https://api.chess.com/pub/club/' + Team)
	if 'name' in team:
		teamName = team['name']
		filter_match_members(teamName)

if __name__ == '__main__':
    main()
