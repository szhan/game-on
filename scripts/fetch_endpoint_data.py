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
obj = json.loads(list_challengers)	# LeagueListDTO
for entry in obj["entries"]:
	""" Iterate through list of LeagueItemDTO. """
	print "\t".join([
			entry["playerOrTeamName"],
			str(entry["playerOrTeamId"]),
			str(entry["wins"]),
			str(entry["losses"]),
			str(entry["leaguePoints"])
			])

