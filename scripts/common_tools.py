import argparse
import json
import math
import time
import pycurl
from datetime import date
from StringIO import StringIO


""" Game constants """
VALID_LEAGUE_NAMES = [	'CHALLENGER',
			'MASTER'
			]

VALID_REGION_NAMES = [	'BR1', 'EUN1', 'EUW1',
			'JP1', 'KR', 'LA1',
			'LA2', 'NA1', 'OC1',
			'TR1', 'RU', 'PBE1'
			]

VALID_QUEUE_TYPES = [	'RANKED_SOLO_5x5',		# queueType = 4
			'TEAM_BUILDER_RANKED_SOLO',	# queueType = 420
			'RANKED_TEAM_5x5'		# queueType = 42
			]


""" Simple utilities """
def get_api_key ():
	""" The file containing the API key is assumed to be in the main directory. """
	api_key_file = "API_KEY"
	
	key = None
	with open(api_key_file) as file:
		key = file.read().rstrip()
	
	return key


def check_league_name(league_name):
	""" Check if league name is valid. """
	if league_name not in VALID_LEAGUE_NAMES:
		msg1 = "ERROR: League name is invalid!\n"
		msg2 = "ERROR: Use one of the following values: " + ", ".join(VALID_LEAGUE_NAME)
		raise ArgumentTypeError(msg1 + msg2)
	else:
		return league_name


def check_region_name(region_name):
	""" Check if region name is valid. """
	if region_name not in VALID_REGION_NAMES:
		msg1 = "ERROR: Region name is invalid!\n"
		msg2 = "ERROR: Use one of the following values: " + ", ".join(VALID_REGION_NAMES)
		raise argparse.ArgumentTypeError(msg1 + msg2)
	else:
		return region_name


def check_queue_type(queue_type):
	""" Check if queue type is valid. """
	if queue_type not in VALID_QUEUE_TYPES:
		msg1 = "ERROR: Queue type is invalid!\n"
		msg2 = "ERROR: Use one of the following values: " + ", ".join(VALID_QUEUE_TYPES)
		raise argparse.ArgumentTypeError(msg1 + msg2)
	else:
		return queue_type


def get_sleep_time(max_requests_per_min, time_gap=2):
	""" Compute sleep time between requests in seconds. """
	return math.ceil(max_requests_per_min / 60.0) + time_gap


def get_formatted_date():
	""" Get current date YYYY-MM-DD as string. """
	return date.today().strftime("%Y_%m_%d")


""" Thin wrappers around Riot API (v3) """
def get_url_prefix(region_name):
	""" Create URL prefix, which is the Riot Game API website. """
	return "https://" + region_name + ".api.riotgames.com/lol"


def get_url_suffix(user_api_key):
	""" Create URL suffix for appending API key. """
	return "?api_key=" + user_api_key


def get_challengers_by_queue(url_prefix, url_suffix, queue_type):
	""" Use League v3 API call, and return LeagueListDTO. """
	return url_prefix + "/league/v3/challengerleagues/by-queue/" + queue_type + url_suffix


def get_masters_by_queue(url_prefix, url_suffix, queue_type):
	""" Use League v3 API call, and return LeagueListDTO. """
	return url_prefix + "/league/v3/masterleagues/by-queue/" + queue_type + url_suffix


def get_summoner_by_name(url_prefix, url_suffix, summoner_name):
	"""
	Use Summoner v3 API call, and return SummonerDTO. 
	Contents include 'name', 'id', and 'accountId', but see Riot API doc.
	WARNING: Use 'get_summoner_by_id' instead, because it is safer due to inconsistent encoding.
	"""
	return url_prefix + "/summoner/v3/summoners/by-name/" + summoner_name + url_suffix


def get_summoner_by_id(url_prefix, url_suffix, summoner_id):
	""" Use Summoner v3 API call, and return SummonerDTO. """
	return url_prefix + "/summoner/v3/summoners/" + str(summoner_id) + url_suffix


def get_match_list_by_account_id(url_prefix, url_suffix, account_id, recent=False):
	"""
	Use Match v3 API call, and return MatchlistDto, which contains a list of MatchReferenceDto.
	This return the full match history available, and data for each match is accessed via MatchReferenceDto.	
	Contents include 'matches' (list of MatchReferenceDto) and 'totalGames'.
	
	MatchReferenceDto contains 'lane', 'gameId', 'champion', 'role', but see Riot API doc.
	
	If recent set to True, then only data for the last 20 matches played are retrieved.
	"""
	if recent:
		return url_prefix + "/match/v3/matchlists/by-account/" + str(account_id) + "/recent" + url_suffix
	else:
		return url_prefix + "/match/v3/matchlists/by-account/" + str(account_id) + url_suffix


def get_match_endpoint_by_match_id(url_prefix, url_suffix, match_id):
	"""
	Use Match v3 API call, and return MatchDto, which contains multiple types of data:
	(1) ParticipantIdentityDto -> PlayerDto, (2) TeamStatsDto, and (3) ParticipantDto, and more.
	"""
	return url_prefix + "/match/v3/matches/" + str(match_id) + url_suffix


def get_match_timeline_by_match_id(url_prefix, url_suffix, match_id):
	"""
	Use Match v3 API call, and return MatchTimelineDto, which contains multiple types of data:
	(1) MatchFrameDto, (2) MatchParticipantFrameDto, (3) MatchEventDto, and more.
	"""
	return url_prefix + "/match/v3/timelines/by-match/" + str(match_id) + url_suffix


def get_json_data(api_cmd, max_attempts=5, sleep_time=3):
	""" 
	Send request to Riot API server, and handle response, retrying requests up to 'max_attempts' times.
	Decode returned JSON string, and retry if JSON string is invalid up to 'max_attempts' times.
	"""
	json_str = None		# Encoded
	json_data = None	# Decoded
	
	nbr_attempts = 0
	
	buffer = StringIO()
	c = pycurl.Curl()
	
	while True:
		c.setopt(c.URL, api_cmd)
		c.setopt(c.WRITEDATA, buffer)
		c.perform()
		
		""" Retry until successful. Not entirely sure if 0 is really the expected response... """
		resp_code = c.getinfo(c.RESPONSE_CODE)
		
		if resp_code == 200:
			""" Success! Do something with response body. """
			try:
				json_str = buffer.getvalue()
				json_data = json.loads(json_str)
				break
			except ValueError as e:
				print "ERROR: Problematic JSON string... Retry..."
		elif resp_code == 400:
			print "ERROR: Bad request with code " + str(resp_code) + ". Skipping..."
			break
		elif resp_code == 403:
			print "ERROR: Rate limit exceeded! Check with Riot! Skipping..."
			break
		elif resp_code == 429:
			"""
			Service could have been temporarily unavailable. Retry...
			TODO: Figure out if sleep time can be informed by 'Retry-After' in response header.
			"""
		elif resp_code in [500, 503]:
			print "ERROR: Riot API server is down or unable to fulfill request. Retry..."
		else:
			print "ERROR: Unrecognized HTTP response code " + str(resp_code) + ". Retry..."
		
		nbr_attempts += 1
		if nbr_attempts >= max_attempts:
			break
		
		# Sleep before next attempt
		time.sleep(sleep_time)
	
	c.close()
	
	# Sleep before next API call
	time.sleep(sleep_time)
	
	return [json_data, json_str]


""" Display game constants """
if __name__ == "__main__":
	print "The following game constants are supported:\n"
	
	print "List of valid league names:"
	print "\n".join(VALID_LEAGUE_NAMES) + "\n"
	
	print "List of valid region names:"
	print "\n".join(VALID_REGION_NAMES) + "\n"
	
	print "List of valid queue types:"
	print "\n".join(VALID_QUEUE_TYPES) + "\n"


