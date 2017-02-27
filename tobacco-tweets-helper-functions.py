
'''
few helping functions for collecting preprocessing tweets
'''

from difflib import SequenceMatcher
import re

def strip_urls(tweet):
	modified_tweet = tweet[:]
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet)
	for u in urls:
		modified_tweet = tweet.replace(u, "")
	return modified_tweet.strip()


def pop_quasi_duplicates(l1, l2):
    pairs = []
    for i in range(len(l1)):
        if len(l1)> i+51:
            max_range = i+51
        else:
            max_range = len(l1)
        for j in range(i+1, max_range):
            if SequenceMatcher(None, l1[i], l1[j]).ratio()> 0.8:
                pairs.append([i, j])
    return pairs


def find_near_duplicates(di):
	similars = []
	keys = sorted(di.keys())
	for i in range(len(keys)-20):
		i_sim = [keys[i]]
		for  j in range(1, 20):
			if SequenceMatcher(None, keys[i], keys[j]).ratio()> 0.8:
				i_sim.append(keys[j])
		similars.append(i_sim)
	return similars


def process_for_amt(rows):
	emoji_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
	new_rows = []
	for r in rows:
		new_row = r[:]
		t = new_row[3]
		t_utf8 = bytes(new_row[3], 'utf-8')
		new_row[3] = str(t_utf8, 'utf-8')
		new_row = new_row[3].translate(emoji_map)
		new_rows.append(new_row)
	return new_rows

'''
for r in rows_nourls:
	new_r = r[:]
	new_r[3] = strip_urls(r[3])
	rows_no2.append(new_r)

'''
    



    
