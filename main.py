import json
import re
import math
import os
import heapq
from pymongo import MongoClient
from nltk import PorterStemmer
from bs4 import BeautifulSoup
from tkinter import *


ps = PorterStemmer()
db = MongoClient().indexingdb

#open bookkeeping.json file and store its data into bookkeeping variable
with open("WEBPAGES_RAW/bookkeeping.json") as bookkeeping_content:
	bookkeeping = json.load(bookkeeping_content)

#-------------------------------------------------------------------------------------------

def user_input():
	#Window
	master = Tk()
	master.title("Search Engine")  #title for the html page
	master.geometry("540x300")     #sets the size for the page

	#Logo
	#path = "querio.png"
	path = "querioo.png"
	img = PhotoImage(file=path)
	panel = Label(master, image=img)
	panel.place(x=120,y=40)

	#Input Form
	query = Entry(master)
	query.place(x= 230, y = 180)

	#Mile stone 1 Button
	search_button_mile_1 = Button(master, text = "Search Mile 1", command=lambda q=query: print_query_info(query.get()))
	search_button_mile_1.place(x = 210, y = 220)

	#Mile stone 2 Button
	search_button_mile_2 = Button(master, text = "Search Mile 2", command=lambda q=query: search_engine(query.get()))
	search_button_mile_2.place(x =300, y = 220)

	master.mainloop()

#-------------------------------------------------------------------------------------------
#This function prints number of URLs retrieved for q and lists the first 20 URLS for it
def print_query_info(q):

	print('\nInverted Index has been loaded')
	print('-----------------------------------------------------------')
	print('Search query is: ', q)
	print('-----------------------------------------------------------')

	q_url = []
	term = ps.stem(q).lower()                           #converts the term to its base form and makes it lowercase
	p_content = db.index.find_one({'term': term})		#finding the term in our index and get its postings content
	url_keys = p_content['postings'].keys()				#save the key associate with each tf-idf in url_keys
	for key in url_keys:								#use the keys in url_keys to find urls in bookkeeping
		q_url.append(bookkeeping[key])				 	#searches bookkeeping.json for the key
	doc_counter = len(q_url)
	print("Number of URLs:	" + str(doc_counter) + "\n")	#print the number of URLs
	counter = 0
	if doc_counter <= 20:									#print the first 20 URLs
		for url in q_url:									#if the number of urls are
			print(url)										#less than 20
			print('-----------------------------------------------------------')
	else:
		while counter < 20:									#otherwise print the
			print(q_url[counter])							#the first 20 urls
			print('-----------------------------------------------------------')
			counter = counter + 1

#-------------------------------------------------------------------------------------------

def cosine_similarity(q):
	index = {}
	documents = set()
	for term in q:
		finder = db.index.find_one({'term': term})		#find term in db
		if finder:										#if we found the term
			#ex: index = {'Artificial' : {"WEBPAGES_RAW/0/0": 10,  "WEBPAGES_RAW/5/68": 15,  "WEBPAGES_RAW/1/22": 34, ...},
			#			 'Intellegence': {"WEBPAGES_RAW/0/41": 24, "WEBPAGES_RAW/15/19": 11, "WEBPAGES_RAW/25/22": 47, ...}}
			index[term] = finder['postings']
			#updates the documents set with itself and the union of the other
			#postings keys which are the weights
			documents.update(finder['postings'].keys())
	#ex: idf_of_term = [('Artificial', {'WEBPAGES_RAW/0/0': 10, 'WEBPAGES_RAW/5/68': 15, 'WEBPAGES_RAW/1/22': 34}),
	# ('Intellegence', {'WEBPAGES_RAW/0/41': 24, 'WEBPAGES_RAW/15/19': 11, 'WEBPAGES_RAW/25/22': 47}), ...]
	idf_of_term = sorted(index.items(), key=lambda x: len(x[1]))
	doc_filter = int(len(idf_of_term) * 3 / 4)
	for i in range(0, doc_filter):
		#Update doucments with the intersection of itself and the previous data
		#stored in it
		documents.intersection_update(idf_of_term[i][1].keys())

	doc_score = {}
	#ex: documnets = ['WEBPAGES_RAW/0/0', 'WEBPAGES_RAW/5/68', 'WEBPAGES_RAW/1/22', ...]
	for doc in list(documents):							#for each doc in documents list
		doc_score[doc] = {}								#makes dictionary in doc_score using documents as a key
		for term in index.keys():						#for each term in index
			if doc in index[term]:
				doc_score[doc][term] = index[term][doc]
			else:
				doc_score[doc][term] = 0

	score = {}
	for doc in doc_score:
		doc_length = 0
		for weight in doc_score[doc].values():
			doc_length += weight * weight

		doc_length = math.sqrt(doc_length)
		each_score = 0
		for term in doc_score[doc]:
			each_score += doc_score[doc][term]

		score[doc] = each_score / doc_length

	return [k for k, v in heapq.nlargest(10, score.items(), key=lambda x: x[1])]

#-------------------------------------------------------------------------------------------
def search_engine(q):
	input = set()
	temp = {}
	result_key = []
	result_url = []
	doc_num = 0

	#get the input query, split it, stem it and store it into the input list
	original_input = q.split()  #ex: Artificial Intellegence
	for term in original_input:
		input.add(ps.stem(term))
	input = list(input)         #ex: ['Artificial', 'Intellegence']

	#Checks if the query is one word, and finds the related URLS
	#else if there are more than one word, it passes them to the cosine_similarity
	#function to find the related urls
	if len(input) == 1:														#if the input query cantains only one term
		finder = db.index.find_one({'term': input[0]})
		if finder:
			#ex: temp = {"WEBPAGES_RAW/0/0": 40, "WEBPAGES_RAW/5/68": 15, "WEBPAGES_RAW/1/22": 34, ...}
			temp = dict(zip(finder['postings'].keys(), finder['postings'].values()))				#make a dict for postings
			#ex: sorted_keys = ["WEBPAGES_RAW/0/0", "WEBPAGES_RAW/1/22", "WEBPAGES_RAW/5/68"]
			sorted_keys = [x[0] for x in sorted(temp.items(), key=lambda x: x[1], reverse=True)]	#sort the file numbers by tf-idf
			doc_num = len(sorted_keys)
			if(len(sorted_keys) <= 10):										#store the first 10 keys into the result_key
				result_key = sorted_keys;
				doc_num = len(sorted_keys)
			else:
				result_key = sorted_keys[:10]          #if the number of documents are more than 10
													   #only print the first 10
	else:											   #if the input query cantains more than one term
		sorted_keys = cosine_similarity(input)		   #compute the cosine cosine similarity
		doc_num = len(sorted_keys)
		result_key = sorted_keys[:10]

	counter = 1;
	print("\n" + str(doc_num) + " results\n")
	for key in result_key:
		print(str(counter) + ") " + bookkeeping[key] + "\n")
		counter = counter + 1;
		path = "WEBPAGES_RAW/" + key										#path for the extracted HTML source code of a particular URL
		with open(path, 'r', encoding='UTF8') as content:					#read the web content
			soup = BeautifulSoup(content, "html.parser")					#parsing HTML and handling broken HTML
			lines = re.split('\\.|\\s{2,}|\\n', soup.get_text())			#split the txt content by the lines
			description = ''												#create empty string
			for line in lines:												#for each line in lines list
				if len(re.findall("[\\w']+", line)) >= 500:					#if line's length is more than 500, skip it
					continue
				if any((' ' + term in line.lower() for term in input)):		#if there is searched term in the line
					if len(re.findall("[\\w']+", description)) >= 100:		#if the lines length is more that 100, skip it
						break
					description += line + '... '							#else, add it to description
		print("\t" + description + "\n\n")									#print description


#-------------------------------------------------------------------------------------------

# Main
user_input()
