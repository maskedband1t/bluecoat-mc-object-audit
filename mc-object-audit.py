#!/usr/bin/env python 

import json, sys, requests, argparse, os 
from requests.auth import HTTPBasicAuth
from configparser import SafeConfigParser

conf_file_path = './config.ini'
api_headers = {"Content-Type":"application/json","Accept":"application/json"}

def get_config(conf_file_path): 
	'''
	Parses config.ini file for username, password variables.

	Input: conf_file_path - path to configurationfile
	Output: conf_dict - config dictionary
	'''

	conf_parser = SafeConfigParser()
	conf_parser.read(conf_file_path)
	
	conf_dict = {}

	conf_dict['username'] = conf_parser.get('config', 'username')
	conf_dict['password'] = conf_parser.get('config', 'password')
	conf_dict['hostname'] = conf_parser.get('config', 'hostname')
	conf_dict['port'] = conf_parser.get('config', 'port')

	return conf_dict

def get_mc_shared_objects(url_root, credentials):
	'''
	Gets list of MC shared objects

	Input: url_root (string) , credentials (HTTPBasicAuth object)
	Output: shared_object_arry - array of json objects representing shared objects
	'''

	api_path = url_root + '/policies?shared=true'
	response = requests.get(api_path, auth=creds, headers=api_headers )
	policies = json.loads(response.text)

	shared_object_array = []

	for policy in policies:
		if policy['contentType'] != 'cplf':
			shared_object_array.append(policy)

	return shared_object_array

def get_mc_policy_contents():
	pass

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="MC Object Reporter")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("--output", help="Path to output csv file")

	args = vars(parser.parse_args())

	config = get_config(conf_file_path)

	url_root = "https://" + config['hostname'] + ":" + config['port'] + '/api'
	creds = HTTPBasicAuth(config['username'], config['password'])

	policies = get_mc_shared_objects(url_root, creds)
	print(policies)





