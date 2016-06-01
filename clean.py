from __future__  import print_function
from argparse    import ArgumentParser
from collections import defaultdict
import os
import sys
import blessings
import json
import shutil

term   = blessings.Terminal()

g = {}
g['PATH']   = os.path.dirname(os.path.abspath(__file__))
g['PREFIX'] = 'clean_'
g['DEBUG']  = False

def parse_args():
	parser = ArgumentParser(description="Clean CLI")
	
	parser.add_argument('directory', help='Full path to directory')
	parser.add_argument('-r', '--rules', default=os.path.join(g['PATH'], 'rules.json'), 
						help='Full path to rules file. Default rules used otherwise')
	parser.add_argument('-p', '--prefix', default=g['PREFIX'], help='Clean folder name prefix')
	parser.add_argument('-d', '--debug', default=g['DEBUG'], help='Test run', action='store_true')

	args = parser.parse_args()

	g['PREFIX'], g['DEBUG'] = args.prefix, args.debug

	if not os.path.exists(args.directory):
		print (term.red, 'Invalid directory path', term.normal)

	if args.rules != None and not os.path.exists(args.rules):
		print (term.red, 'Invalid rules path', term.normal)

	rules = args.rules if args.rules else os.path.join(g['PATH'], 'rules.json')

	return args.directory, rules

def parse_rules(pth):
	with open(pth, 'r') as f:
		return json.load(f)

def get_files(dir):
	listdir = os.listdir(dir)
	files   = [f for f in listdir if os.path.isfile(os.path.join(dir, f))]
	return dir, files

def categorize_files(files, cat_func=lambda f: f.rsplit('.', 1)[-1]):
	dct = defaultdict(list)
	for f in files: dct[cat_func(f)].append(f)
	return dct

def ignore_files(data, rules):
	for format in rules['ignore']:
		if format in data: del data[format]
	return data

def delete_files(data, rules, dir):
	for format in rules['delete']:
		for f in data.get(format, []):
			fp = os.path.join(dir, f)
			print (term.dim, 'Deleting', fp, term.normal)
			if not g['DEBUG']: os.remove(fp)
	return data

def categorize_clean_files(data, rules):
	dct = defaultdict(list)
	for folder, formats in rules['clean'].items():
		for format in formats:
			dct[folder].extend(data.get(format, []))
	return dct

def make_folders(rules, cln_files, dir):
	for folder in rules['clean'].keys():
		if not cln_files.get(folder, False): continue
		pth = os.path.join(dir, g['PREFIX']+folder)
		if os.path.exists(pth):
			print (term.dim, 'folder exists:', g['PREFIX']+folder)
		else:
			print (term.bold, 'mkdir:', g['PREFIX']+folder)
			if not g['DEBUG']: os.mkdir(pth)

def move_clean_files(cat_data, dir):
	for folder, files in cat_data.items():
		folder_pth = os.path.join(dir, g['PREFIX']+folder)
		for file_ in files:
			file_pth = os.path.join(dir, file_)
			print (term.green, 'moving', file_, 'to', folder, term.normal)
			file_pth_new = os.path.join(folder_pth, file_)
			if not g['DEBUG']: shutil.move(file_pth, file_pth_new)

def clean(directory, rules_path):
	rules     = parse_rules(rules_path)
	_, files  = get_files(directory)
	cat_files = categorize_files(files)
	cat_files = ignore_files(cat_files, rules)
	cat_files = delete_files(cat_files, rules, directory)
	cln_files = categorize_clean_files(cat_files, rules)

	make_folders(rules, cln_files, directory)
	move_clean_files(cln_files, directory)

if __name__ == '__main__':
	clean(*parse_args())
