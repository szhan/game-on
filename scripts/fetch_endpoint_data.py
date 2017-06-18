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

api_cmd = ct.get_challengers_by_queue(URL_PREFIX, URL_SUFFIX, QUEUE_TYPE)
list_challengers = ct.get_json_by_request(api_cmd)

# Decode into dict, and extract player names, and wins and losses per player
league_list_dto = json.loads(list_challengers)	# LeagueListDTO
for league_item_dto in league_list_dto["entries"][:3]:
	""" Iterate through list of LeagueItemDTO. """
	player_id = league_item_dto["playerOrTeamId"]
	summoner_dto = json.loads(ct.get_json_by_request(ct.get_summoner_by_id(URL_PREFIX, URL_SUFFIX, player_id)))
	account_id = summoner_dto["accountId"]
	match_list_dto = json.loads(ct.get_json_by_request(ct.get_match_list_by_account_id(URL_PREFIX, URL_SUFFIX, account_id, recent=True)))
	
	for match_reference_dto in match_list_dto["matches"]:
		print "\t".join([
				str(account_id),
				str(match_reference_dto["gameId"]),
				str(match_reference_dto["lane"]),
				str(match_reference_dto["champion"]),
				str(match_reference_dto["role"])
				])

