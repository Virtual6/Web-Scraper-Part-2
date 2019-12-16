import json
import re
import math
import os
import heapq
from pymongo import MongoClient
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup

ps = PorterStemmer()
stop_words = ['ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there',
			  'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they',
			  'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into',
			  'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who',
			  'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are',
			  'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her',
			  'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above',
			  'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any',
			  'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does',
			  'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can',
			  'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where',
			  'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't',
			  'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how',
			  'further', 'was', 'here', 'than']


#-------------------------------------------------------------------------------

def build_index():
	#open bookkeeping.json file and store its data into bookkeeping variable
	with open("WEBPAGES_RAW/bookkeeping.json") as bookkeeping_content:
		bookkeeping = json.load(bookkeeping_content)

	doc_count = 0 											#variable to count the documents
	matrix = {}												#dictionary that stores tf
	for document_id_weight in bookkeeping:                  #ex: 0/0
		path = "WEBPAGES_RAW/" + document_id_weight		    #path for the extracted HTML source code of a particular URL
		with open(path, 'r', encoding='UTF8') as content:
			doc_count = doc_count + 1
			soup = BeautifulSoup(content, "html.parser")	#parsing HTML and handling broken HTML
			# remove all script and style elements
			for script in soup(["script", "style", "link", "meta"]):
				script.extract()    #get rid of the script and style tages

			#extracting all the text from the page and return a list of all the matches in text list
			text = re.findall(r'\w+', soup.get_text())

			#storing the tf of each word in matrix
			for word in text:
				word = ps.stem(word).lower()
				if word in stop_words:    #if the word is in stop_words ignore it
					continue
				if len(word) >= 20:        #if word len is more that 20, skip it
					continue
				if word in matrix:
					if document_id_weight in matrix[word]:
						matrix[word][document_id_weight] += 1
				else:
					matrix[word] = {document_id_weight: 1}

			#finds the words in title in document and increases its tf by 500
			title = soup.title   #ex: <title>UCI Machine Learning Repository</title>
			if title and title.string:
				title = title.string  #ex: "UCI Machine Learning Repository"
				title_token = re.findall(r'\w+', title) #ex: ['UCI', 'Machine', 'Learning', 'Repository']
				for word in title_token:
					word = ps.stem(word).lower() #ex: ['uci', 'machin', 'learn', 'repositori']
					if word in stop_words:
						continue
					if word in matrix:
						if document_id_weight in matrix[word]:
							matrix[word][document_id_weight_weight] += 10


			#finds the words in bold in document and increases its tf by 2
			bold = soup.bold
			if bold and bold.string:
				bold = bold.string
				title_token = re.findall(r'\w+', bold)
				for word in title_token:
					word = ps.stem(word).lower()
					if word in stop_words:
						continue
					if word in matrix:
						if document_id_weight in matrix[word]:
							matrix[word][document_id_weight] += 2

			#finds the words in strong in document and increases its tf by 1
			strong = soup.strong
			if strong and strong.string:
				strong = strong.string
				strong_token = re.findall(r'\w+', strong)
				for word in strong_token:
					word = ps.stem(word).lower()
					if word in stop_words:
						continue
					if word in matrix:
						if document_id_weight in matrix[word]:
							matrix[word][document_id_weight] += 1

			#finds the words in h1 in document and increases its tf by 1
			heading_1 = soup.h1
			if heading_1 and heading_1.string:
				heading_1 = heading_1.string
				heading_token = re.findall(r"\w+", heading_1)
				for word in heading_token:
					word = ps.stem(word).lower()
					if word in stop_words:
						continue
					if word in matrix:
						if document_id_weight in matrix[word]:
							matrix[word][document_id_weight] += 9

			#finds the words in h1 in document and increases its tf by 1
			heading_2 = soup.h2
			if heading_2 and heading_2.string:
				heading_2 = heading_2.string
				heading_token = re.findall(r"\w+", heading_2)
				for word in heading_token:
					word = ps.stem(word).lower()
					if word in stop_words:
						continue
					if word in matrix:
						if document_id_weight in matrix[word]:
							matrix[word][document_id_weight] += 8

			#finds the words in h3 in document and increases its tf by 1
			heading_3 = soup.h3
			if heading_3 and heading_3.string:
				heading_3 = heading_3.string
				heading_token = re.findall(r"\w+", heading_3)
				for word in heading_token:
					word = ps.stem(word).lower()
					if word in stop_words:
						continue
					if word in matrix:
						if document_id_weight in matrix[word]:
							matrix[word][document_id_weight] += 7

			#finds the words in h4 in document and increases its tf by 1
			heading_4 = soup.h4
			if heading_4 and heading_4.string:
				heading_4 = heading_4.string
				heading_token = re.findall(r"\w+", heading_4)
				for word in heading_token:
					word = ps.stem(word).lower()
					if word in stop_words:
						continue
					if word in matrix:
						if document_id_weight in matrix[word]:
							matrix[word][document_id_weight] += 6

			#finds the words in h5 in document and increases its tf by 1
			heading_5 = soup.h5
			if heading_5 and heading_5.string:
				heading_5 = heading_5.string
				heading_token = re.findall(r"\w+", heading_5)
				for word in heading_token:
					word = ps.stem(word).lower()
					if word in stop_words:
						continue
					if word in matrix:
						if document_id_weight in matrix[word]:
							matrix[word][document_id_weight] += 5

			#finds the words in h6 in document and increases its tf by 1
			heading_6 = soup.h6
			if heading_6 and heading_6.string:
				heading_6 = heading_6.string
				heading_token = re.findall(r"\w+", heading_6)
				for word in heading_token:
					word = ps.stem(word).lower()
					if word in stop_words:
						continue
					if word in matrix:
						if document_id_weight in matrix[word]:
							matrix[word][document_id_weight] += 4

	calculate_tf_idf(index, doc_count)

#-------------------------------------------------------------------------------

def calculate_tf_idf(matrix, doc_count):

	db = MongoClient().indexingdb						#creating database and name it indexing db
	num_of_terms = {'num_of_docs': doc_count}			#creating a dictionary for number of documents
	insert_db = [num_of_terms]                          
	count = 1
	for term in matrix:
	    if count > 2000: #for every 2000 items in the list we add it to the database reset the list to avoid memory error
	        add_to_db = db.index.insert_many(insert_db)
	        count = 0    #reset the count
	        insert_db = []  #empty the list that updates the database
	    idf = math.log10(doc_count/float(len(matrix[term])))				#calculating idf
	    for doc in matrix[term]:
	        matrix[term][doc] = (1 + math.log10(matrix[term][doc])) * idf	#calculating tf-idf
		#ex: [{"term": "uci", "postings": {"WEBPAGES_RAW/0/0": 40}}, {"term": "science", "postings": {"WEBPAGES_RAW/2/15": 15}} ]
	    insert_db.append({"term": term, "postings": matrix[term]}) #append the new calculated tf_idf of the terms to the list
	    count += 1    #increment the counter
	if insert_db:
	    add_too_db = db.index.insert_many(insert_db)

#------------------------------------------------------------------------------
