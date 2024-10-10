#!/usr/bin/env python3

# chashao - porkbun dynamic dns client
# made with <3 by moth.monster

# SPDX-License-Identifier: MIT-0

import requests, json, shelve
import tomllib as toml

# import config from toml
global config
with open("config.toml", "rb") as f:
	config = toml.load(f)

def getIP(): # get ipv4 ∨ ipv6 addresses, all in a nice tidy array
	ping6 = json.loads(requests.post(config["endpoint"] + '/ping/', data = json.dumps(config["keys"])).text)
	if config["verbose"] == True:
		print(ping6)
	if config["v6only"] == True:
		ip = ip = {"v6": ping6["yourIp"]}
		return ip
	else:
		ping4 = json.loads(requests.post(config["endpointv4"] + '/ping/', data = json.dumps(config["keys"])).text)
		if config["verbose"] == True:
			print(ping4)
		if ping4["yourIp"] == ping6["yourIp"]:
			ip = {"v4": ping4["yourIp"]}
			return ip 
		else:
			ip = {"v4": ping4["yourIp"], "v6": ping6["yourIp"]}
			return ip
	
def getRecords(domain): # grab all the records so we know which ones to delete to make room for our record. Also checks to make sure we've got the right domain
	records=json.loads(requests.post(config["endpoint"] + '/dns/retrieve/' + domain, data = json.dumps(config["keys"])).text)
	if records["status"]=="ERROR":
		print('Error getting domain. Check to make sure you specified the correct domain, and that API access has been switched on for this domain.')
		exit(1)
	return(records)

def delRecords(): # delete old records
	for i in getRecords(config["domain"]["root"])["records"]:
		if i["name"]==fqdn and (i["type"] == 'A' or i["type"] == 'AAAA' or i["type"] == 'ALIAS' or i["type"] == 'CNAME'):
			requests.post(config["endpoint"] + '/dns/delete/' + config["domain"]["root"] + '/' + i["id"], data = json.dumps(config["keys"])).text

if not config["domain"]["sub"] == "": # format things properly
	fqdn = config["domain"]["sub"] + '.' + config["domain"]["root"]
else:
	fqdn = config["domain"]["root"]

ip = getIP()

with shelve.open("cache") as cache: # caching to avoid redundant work
	try:
		cache["ip"]
	except KeyError:
		if config["verbose"] == True:
			cache["ip"] = "DUMMY" # add dummy value to prevent error in next comparison
			print("Cache empty!")
	if cache["ip"] == ip:
		if config["verbose"] == True:
			print("IP has not changed. Nothing needs to be done.")
	else:
		cache["ip"] = ip # update cached value
		if config["verbose"] == True:
			print("IP has changed.")
		if not config["dryrun"]:
			delRecords()
		# add A record if needed
		try:
			ip["v4"]
		except KeyError:
			pass
		else:
			if config["dryrun"]:
				print("A " + fqdn + " " + ip["v4"] + " " + str(config["ttl"]))
			else:
				record4 = config["keys"].copy()
				record4.update({'name': config["domain"]["sub"], 'type': 'A', 'content': ip["v4"], 'ttl': config["ttl"]})
				requests.post(config["endpoint"] + '/dns/create/'+ config["domain"]["root"], data = json.dumps(record4)).text
		# add AAAA record if needed
		try:
			ip["v6"]
		except KeyError:
			pass
		else:
			if config["dryrun"]:
				print("AAAA " + fqdn + " " + ip["v6"] + " " + str(config["ttl"]))
			else:
				record6 = config["keys"].copy()
				record6.update({'name': config["domain"]["sub"], 'type': 'AAAA', 'content': ip["v6"], 'ttl': config["ttl"]})
				requests.post(config["endpoint"] + '/dns/create/'+ config["domain"]["root"], data = json.dumps(record6)).text