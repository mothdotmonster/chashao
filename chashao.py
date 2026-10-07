#!/usr/bin/env python3

# chashao - porkbun dynamic dns client
# made with <3 by moth.monster

# SPDX-License-Identifier: MIT-0

import requests, json, shelve, logging, datetime
import tomllib as toml

# import config from toml
global config
with open("config.toml", "rb") as f:
	config = toml.load(f)

logging.basicConfig(
	level=logging.INFO,
	handlers=[
		logging.StreamHandler()
	]
)
log = logging.getLogger()
log.setLevel(logging.WARNING)
if config["verbose"] == True:
	log.setLevel(logging.INFO)
elif config["verbose"] == "debug":
	log.setLevel(logging.DEBUG)

def getIP(): # get ipv4 ∨ ipv6 addresses, all in a nice tidy array
	ping6 = json.loads(requests.post(config["endpoint"] + '/ping/', data = json.dumps(config["keys"])).text)
	log.debug(ping6)
	if config["v6only"] == True:
		ip = ip = {"v6": ping6["yourIp"]}
		return ip
	else:
		ping4 = json.loads(requests.post(config["endpointv4"] + '/ping/', data = json.dumps(config["keys"])).text)
		log.debug(ping4)
		if ping4["yourIp"] == ping6["yourIp"]:
			ip = {"v4": ping4["yourIp"]}
			return ip 
		else:
			ip = {"v4": ping4["yourIp"], "v6": ping6["yourIp"]}
			return ip

ip = getIP()
log.info(ip)

with shelve.open("chashao.cache") as cache: # caching to avoid redundant work
	try:
		cache["ip"]
	except KeyError:
		cache["ip"] = "DUMMY" # add dummy value to prevent error in next comparison
		log.info("Cache empty!")
	if cache["ip"] == ip and config["cache"]:
		log.info("IP has not changed. Nothing needs to be done.")
	else:
		cache["ip"] = ip # update cached value
		if not config["cache"]:
			log.info("Caching is disabled. Updating records.")
		else:
			log.info("IP has changed. Updating records.")
		if config["dryrun"]:
			log.info("Dry run enabled. Nothing will actually be done.")
		# add A record if needed
		try:
			ip["v4"]
		except KeyError:
			log.info("no ipv4")
		else:
			log.info("updating ipv4")
			record4 = config["keys"].copy()
			record4.update({'content': ip["v4"], 'ttl': config["ttl"], 'notes': "chashao " + str(datetime.datetime.now())})
			if not config["dryrun"]:
				try:
					r = requests.post(config["endpoint"] + '/dns/editByNameType/' + config["domain"]["root"] + "/A/" + config["domain"]["sub"], data = json.dumps(record4)).text
					r = json.loads(r)["code"]
				except KeyError:
					log.debug("no error code. This is a good thing!")
				except requests.exceptions.RequestException:
					log.info("Something went wrong, nullifying cache.")
					cache["ip"] = "DUMMY"
				else:
					if r["code"] == "EDIT_ERROR_NO_DNS_RECORD_MATCHES_THAT_NAME_AND_TYPE":
						log.info("No record for ipv4, make one from scratch")
						record4.update({'name': config["domain"]["sub"], 'type': 'A'})
						requests.post(config["endpoint"] + '/dns/create/'+ config["domain"]["root"], data = json.dumps(record4)).text
			else:
				log.info(record4)

		# add AAAA record if needed
		try:
			ip["v6"]
		except KeyError:
			log.info("no ipv6")
		else:
			log.info("updating ipv6")
			record6 = config["keys"].copy()
			record6.update({'content': ip["v6"], 'ttl': config["ttl"], 'notes': "chashao " + str(datetime.datetime.now())})
			if not config["dryrun"]:
				try:
					r = requests.post(config["endpoint"] + '/dns/editByNameType/' + config["domain"]["root"] + "/AAAA/" + config["domain"]["sub"], data = json.dumps(record6)).text
					r = json.loads(r)["code"]
				except KeyError:
					log.debug("no error code. This is a good thing!")
				except requests.exceptions.RequestException:
					log.info("Something went wrong, nullifying cache.")
					cache["ip"] = "DUMMY"
				else:
					if r["code"] == "EDIT_ERROR_NO_DNS_RECORD_MATCHES_THAT_NAME_AND_TYPE":
						log.info("No record for ipv6, make one from scratch")
						record6.update({'name': config["domain"]["sub"], 'type': 'AAAA'})
						requests.post(config["endpoint"] + '/dns/create/'+ config["domain"]["root"], data = json.dumps(record6)).text
			else:
				log.info(record6)			