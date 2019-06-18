#!/usr/bin/env python3

import json, sys, requests, argparse, os, csv 
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
	Output: shared_object_array - array of json objects representing shared objects
	'''

	api_path = url_root + '/policies?shared=true'
	response = requests.get(api_path, auth=credentials, headers=api_headers )
	policies = json.loads(response.text)

	shared_object_array = []

	for policy in policies:
		if (policy['contentType'] == 'CUSTOM_CATEGORY' or policy['contentType'] == 'IP_LIST' or policy['contentType'] == 'URL_LIST'):
			shared_object_array.append(policy)

	return shared_object_array

def get_mc_policy_contents(url_root, credentials, policy):
	'''
	Gets list of policy contents given a policy

	Input: url_root (string) , credentials (HTTPBasicAuth object) , policy - single shared object
	Output: content_list - multi-line string with object_type,object_name,object_description,url,url_description
	'''
	content_list = ''

	api_path = url_root + '/policies/' + policy['uuid'] + '/content'
	response = requests.get(api_path, auth=credentials, headers=api_headers )

	
	super_content = json.loads(response.text)
	internalJson = super_content['content']

	contentType = policy['contentType']
	name = policy['name']
	description = policy['description']
	url = ''
	url_description = ''

	contentCount = 0
	if(contentType != 'IP_LIST'):
		for url in internalJson['urls']:
			content_list = content_list + contentType + ',' + name + ',' + description + ','

			if len(internalJson['urls']) != 0:
				content_list += url['url'] + ','
				exists = False
				for field in url:
					if field == 'description':
						exists = True

				url_description = 'NULL'
				if exists:
					if url['description'] != '':
						url_description = url['description']
				content_list += url_description + '\n'
				
			else:
				content_list += "NULL,NULL\n"

	else:
		for ip in internalJson['ipAddresses']:
			content_list = content_list + contentType + ',' + name + ',' + description + ','

			if len(internalJson['ipAddresses']) != 0:
				content_list += ip['ipAddress'] + ','
				exists = False
				for field in ip:
					if field == 'description':
						exists = True

				url_description = 'NULL'
				if exists:
					if ip['description'] != '':
						url_description = ip['description']
				content_list += url_description + '\n'
				
			else:
				content_list += "NULL,NULL\n"
				
			
	return content_list

	


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="MC Object Reporter")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("--output", help="Path to output csv file")

	args = vars(parser.parse_args())

	config = get_config(conf_file_path)

	url_root = "https://" + config['hostname'] + ":" + config['port'] + '/api'
	creds = HTTPBasicAuth(config['username'], config['password'])

	policies = get_mc_shared_objects(url_root, creds)

	with open(args['output'], 'w') as csvfile:
		csvfile.write('object_type,object_name,object_description,url,url_description\n')

		for policy in policies:
			content_list = get_mc_policy_contents(url_root, creds, policy)
			csvfile.write(content_list)
			
	print("CSV Written.")
			
	

	






