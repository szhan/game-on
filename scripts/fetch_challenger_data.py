import json
import argparse
import common_tools as ct


"""
Basic workflow to get match data for Challenger players.
1. Get list of Challenger players
2. Get 'account id' for each player by 'summoner name'
3. Get match list for each player by 'account id'
4. Get match endpoint data for each match by 'match id'
5. Get also match timeline data for each match by 'match_id', if available
6. Dump summoner, match list, endpoint, and timeline data into separate files
"""


parser = argparse.ArgumentParser(description="Fetch match data using Riot API for Challenger games.")
parser.add_argument('-r', '--region', type=ct.check_region_name, dest='region', required=True, help='Specify region (e.g., NA1, BR1, EUN1, KR, and OC1)')
parser.add_argument('-q', '--queue-type', type=str, dest='queue_type', default='RANKED_SOLO_5x5', help='Specify queue type (default = RANKED_SOLO_5x5)')
parser.add_argument('-m', '--max-requests-per-min', type=int, dest='max_requests_per_min', default=40, help='Specify max request per minute (default = 40 sec)')
parser.add_argument('-n', '--nbr-players', type=int, dest='nbr_players', default=100, help='Specify number of players to get data for (default = 100)')
parser.add_argument('-g', '--nbr-games', type=int, dest='nbr_games', default=20, help='Specify number of recent games to get data for (default = 20)')
parser.add_argument('-o', '--output-dir', type=str, dest='out_dir', default="data/", help='Provide path to output directory (default = data/)')
parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='Switch on debug mode')
args = parser.parse_args()


REGION = args.region
QUEUE_TYPE = args.queue_type
NBR_PLAYERS = args.nbr_players
NBR_GAMES = args.nbr_games
OUT_DIR = args.out_dir
DEBUG = args.debug

MAX_REQUESTS_PER_MIN = args.max_requests_per_min
SLEEP_TIME = ct.get_sleep_time(MAX_REQUESTS_PER_MIN)

USER_API_KEY = ct.get_api_key()
DATETIME = ct.get_formatted_date()

URL_PREFIX = ct.get_url_prefix(REGION)
URL_SUFFIX = ct.get_url_suffix(USER_API_KEY)

def get_file_name(data_type):
	return OUT_DIR + "-".join(["challengers", data_type, REGION, QUEUE_TYPE, DATETIME]) + ".json"


OUT_FILE_SUMMONERS = get_file_name("summoners")
OUT_FILE_MATCHLIST = get_file_name("matchlist")
OUT_FILE_ENDPOINTS = get_file_name("endpoints")
OUT_FILE_TIMELINES = get_file_name("timelines")

fh_summoners = open(OUT_FILE_SUMMONERS, 'w')
fh_matchlist = open(OUT_FILE_MATCHLIST, 'w')
fh_endpoints = open(OUT_FILE_ENDPOINTS, 'w')
fh_timelines = open(OUT_FILE_TIMELINES, 'w')


cmd_get_league_list_dto = ct.get_challengers_by_queue(URL_PREFIX, URL_SUFFIX, QUEUE_TYPE)
[league_list_dto, league_list_str] = ct.get_json_data(cmd_get_league_list_dto, sleep_time=SLEEP_TIME)

for league_item_dto in league_list_dto["entries"][:NBR_PLAYERS]:
	player_id = league_item_dto["playerOrTeamId"]
	print "INFO: Getting data for player " + player_id
	
	""" Extract accountId from SummonerDTO for querying match history. """
	account_id = None
	
	cmd_get_summoner_dto = ct.get_summoner_by_id(URL_PREFIX, URL_SUFFIX, player_id)
	if DEBUG: print "DEBUG: " + cmd_get_summoner_dto
	
	[summoner_dto, summoner_str] = ct.get_json_data(cmd_get_summoner_dto, sleep_time=SLEEP_TIME)
	if summoner_dto is None:
		continue
	else:
		account_id = summoner_dto["accountId"]
	
	matches = None
	
	cmd_get_match_list_dto = ct.get_match_list_by_account_id(URL_PREFIX, URL_SUFFIX, account_id)
	if DEBUG: print "DEBUG: " + cmd_get_match_list_dto
	
	[match_list_dto, match_list_str] = ct.get_json_data(cmd_get_match_list_dto, sleep_time=SLEEP_TIME)
	if match_list_dto is None:
		continue
	else:
		matches = match_list_dto["matches"]
	
	""" Store SummonerDTO and MatchListDTO separately. """
	fh_summoners.write(str(account_id) + "\t" + summoner_str + "\n")
	fh_matchlist.write(str(account_id) + "\t" + match_list_str + "\n")
	
	""" Get match endpoint and timeline data for NBR_GAMES games. """
	for match_reference_dto in matches[:NBR_GAMES]:
		game_id = match_reference_dto["gameId"]
		queue = match_reference_dto["queue"]
		
		# Skip unless RANKED_SOLO_5x5 (queueType=4) or TEAM_BUILDER_RANKED_SOLO (queueType=420)
		# TODO: Allow for other queue types
		if queue not in [4, 420]: continue
		
		cmd_get_match_dto = ct.get_match_endpoint_by_match_id(URL_PREFIX, URL_SUFFIX, game_id)
		if DEBUG: print "DEBUG: " + cmd_get_match_dto
		[match_dto, match_str] = ct.get_json_data(cmd_get_match_dto, sleep_time=SLEEP_TIME)
		
		cmd_get_match_timeline_dto = ct.get_match_timeline_by_match_id(URL_PREFIX, URL_SUFFIX, game_id)
		if DEBUG: print "DEBUG: " + cmd_get_match_timeline_dto
		[match_timeline_dto, match_timeline_str] = ct.get_json_data(cmd_get_match_timeline_dto, sleep_time=SLEEP_TIME)
		
		if match_dto is not None and match_timeline_dto is not None:
			fh_endpoints.write(str(game_id) + "\t" + match_str + "\n")
			fh_timelines.write(str(game_id) + "\t" + match_timeline_str + "\n")
	

fh_summoners.close()
fh_matchlist.close()
fh_endpoints.close()
fh_timelines.close()

