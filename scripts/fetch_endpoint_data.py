import json
import common_tools as ct


"""
Basic workflow to get match endpoint data for 20 recent 
	ranked solo queue matches for all Challenger players in NA.
1. Get full list of Challenger players
2. Get 'account id' for each player by 'summoner name'
3. Get match list for each player by 'account id'
4. Get match endpoint data for each match by 'match id'
"""


REGION = "na1"	# e.g., "na", "eun1", "euw1", "br"
QUEUE_TYPE = "RANKED_SOLO_5x5"

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


league_list_dto = json.loads(ct.get_json_by_request(ct.get_challengers_by_queue(URL_PREFIX, URL_SUFFIX, QUEUE_TYPE), SLEEP_TIME))

for league_item_dto in league_list_dto["entries"]:
	player_id = league_item_dto["playerOrTeamId"]
	print "INFO: Getting data for player " + player_id
	
	summoner_dto = json.loads(ct.get_json_by_request(ct.get_summoner_by_id(URL_PREFIX, URL_SUFFIX, player_id), SLEEP_TIME))
	account_id = summoner_dto["accountId"]
	match_list_dto = json.loads(ct.get_json_by_request(ct.get_match_list_by_account_id(URL_PREFIX, URL_SUFFIX, account_id, recent=True), SLEEP_TIME))
	
	for match_reference_dto in match_list_dto["matches"]:
		game_id = match_reference_dto["gameId"]
		
		match_dto = ct.get_json_by_request(ct.get_match_endpoint_by_match_id(URL_PREFIX, URL_SUFFIX, game_id), SLEEP_TIME)
		match_timeline_dto = ct.get_json_by_request(ct.get_match_timeline_by_match_id(URL_PREFIX, URL_SUFFIX, game_id), SLEEP_TIME)		
		
		if match_dto is not None:
			fh_endpoints.write(match_dto)
		if match_timeline_dto is not None:
			fh_timelines.write(match_timeline_dto)


fh_endpoints.close()
fh_timelines.close()

