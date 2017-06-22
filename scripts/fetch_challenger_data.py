import sys
import json
import argparse
import common_tools as ct


"""
Basic workflow to get match endpoint data for 20 recent 
	ranked solo queue matches for all Challenger players in NA.
1. Get full list of Challenger players
2. Get 'account id' for each player by 'summoner name'
3. Get match list for each player by 'account id'
4. Get match endpoint data for each match by 'match id'
5. Get also match timeline data for each match by 'match_id', if available
"""


parser = argparse.ArgumentParser(description="Fetch match data using Riot API for Challenger ranked solo queue 5x5 games.")
parser.add_argument('-r', '--region', type=ct.check_region_name, dest='region', required=True, help='Specify region (e.g., NA, BR1, EUN1, KR, and OC1)')
args = parser.parse_args()


REGION = args.region
QUEUE_TYPE = "RANKED_SOLO_5x5"
NBR_GAMES = 20

USER_API_KEY = ct.get_api_key()

# Default rate limit, unless requested
# 500 requests every 10 minutes
MAX_REQUESTS_PER_MIN = 50
SLEEP_TIME = ct.get_sleep_time(MAX_REQUESTS_PER_MIN)

URL_PREFIX = ct.get_url_prefix(REGION)
URL_SUFFIX = ct.get_url_suffix(USER_API_KEY)

DATETIME = ct.get_formatted_date()

OUT_DIR = "data/"
OUT_FILE_ENDPOINTS = OUT_DIR + "-".join(["challengers", "endpoints", REGION, QUEUE_TYPE, DATETIME]) + ".json"
OUT_FILE_TIMELINES = OUT_DIR + "-".join(["challengers", "timelines", REGION, QUEUE_TYPE, DATETIME]) + ".json"


fh_endpoints = open(OUT_FILE_ENDPOINTS, 'w')
fh_timelines = open(OUT_FILE_TIMELINES, 'w')


league_list_dto = json.loads(ct.get_json_data(ct.get_challengers_by_queue(URL_PREFIX, URL_SUFFIX, QUEUE_TYPE), sleep_time=SLEEP_TIME))

for league_item_dto in league_list_dto["entries"]:
	player_id = league_item_dto["playerOrTeamId"]
	print "INFO: Getting data for player " + player_id
	
	summoner_dto = ct.get_json_data(ct.get_summoner_by_id(URL_PREFIX, URL_SUFFIX, player_id), sleep_time=SLEEP_TIME)
	if summoner_dto is None:
		continue
	else:
		summoner_dto = json.loads(summoner_dto)
	
	account_id = summoner_dto["accountId"]
	match_list_dto = ct.get_json_data(ct.get_match_list_by_account_id(URL_PREFIX, URL_SUFFIX, account_id), sleep_time=SLEEP_TIME)
	if match_list_dto is None:
		continue
	else:
		match_list_dto = json.loads(match_list_dto)
	
	for match_reference_dto in match_list_dto["matches"][:NBR_GAMES]:
		game_id = match_reference_dto["gameId"]
		queue = match_reference_dto["queue"]
		
		# Skip unless RANKED_SOLO_5x5 (queueType=4) or TEAM_BUILDER_RANKED_SOLO (queueType=420)
		if queue not in [4, 420]: continue
		
		match_dto = ct.get_json_data(ct.get_match_endpoint_by_match_id(URL_PREFIX, URL_SUFFIX, game_id), sleep_time=SLEEP_TIME)
		match_timeline_dto = ct.get_json_data(ct.get_match_timeline_by_match_id(URL_PREFIX, URL_SUFFIX, game_id), sleep_time=SLEEP_TIME)
		
		if match_dto is not None:
			fh_endpoints.write(match_dto + "\n")
		if match_timeline_dto is not None:
			fh_timelines.write(match_timeline_dto + "\n")


fh_endpoints.close()
fh_timelines.close()

