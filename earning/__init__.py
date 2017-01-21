import os, requests, datetime
import sys
from datetime import timedelta
import datetime
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
from dateutil import parser
import pickle

__author__ = 'Xiaowei Yan'
__version__ = '1.0'

__all__ = ['earning','yahoo']

class earning(object):


    def __init__(self,start,to):
        self.start = start
        self.to = to


    def yahoo_date(self):
        b = str(self.start)
    	be = datetime.date(int(b[0:4]),int(b[4:6]),int(b[6:8]))
    	t = str(self.to)
    	to = datetime.date(int(t[0:4]),int(t[4:6]),int(t[6:8]))
    	interval = to - be
    	l = []
    	d = timedelta(days = 1)
    	for i in range(interval.days):
    		date = be + d*i
    		if date.weekday() in set([5,6]):
    			continue
    		if date.month < 10:
    			month = '0' + str(date.month)
    		else:
    			month = str(date.month)
    		if date.day < 10:
    			day = '0' + str(date.day)
    		else:
    			day = str(date.day)
    		l.append(str(date.year)+month+day)
    	return(l)


    def nasdaq_date(self):
        b = str(self.start)
    	be = datetime.date(int(b[0:4]),int(b[4:6]),int(b[6:8]))
    	t = str(self.to)
    	to = datetime.date(int(t[0:4]),int(t[4:6]),int(t[6:8]))
    	interval = to - be
    	l = []
    	d = timedelta(days = 1)
    	for i in range(interval.days):
    		date = be + d*i
    		if date.weekday() in set([5,6]):
    			continue
    		l.append(date.strftime('%Y-%b-%d'))
        return(l)


    def yahoo_get_info(self,url):
    	page = requests.get(url)
    	soup = BeautifulSoup(page.text,'lxml')
    	ticker = soup.select('tr > td > a[href*="finance"]')[1:]
    	tic = [i.get_text().encode('utf8') for i in ticker]
    	time = soup.select('tr > td > small')[1:-1]
    	t = [i.get_text().encode('utf8') for i in time]
    	while '' in t:
    			t.remove('')
    	date = url[-13:-5]
    	df = pd.DataFrame({'time':date,'ticker':tic,'release':t})
    	try:
    		df = df[df['ticker'].str.contains('\.') == False]
    	except:
    		pass
    	return df


    def nasdaq_get_info(self,url):
    	page = requests.get(url)
    	soup = BeautifulSoup(page.text,'lxml')
    	table = soup.find_all('table',attrs = {'class':'USMN_EarningsCalendar'})[0]
    	tr = table.find_all('tr')[1:]
    	name = [x.text.encode('utf8') for x in table.find_all('a')][3:]
    	name = [x for x in name if x]
    	ticker = [x[x.find("(")+1:x.find(")")] for x in name]
    	cap = []
    	bad = []
    	badtr = []
    	badnum = []
    	release = []
    	for i in range(len(tr)):
    	    try:
    	        cap.append(tr[i].find_all('td')[1].a.get_text().split('$')[1])
    	    except:
    	        bad.append(tr[i])
    	        badnum.append(i)
    	tr = [x for x in tr if x not in bad]
    	ticker = [x for x in ticker if ticker.index(x) not in badnum]
    	consensus = [x.find_all('td')[4].get_text().strip() for x in tr]
    	num = [x.find_all('td')[5].get_text().strip() for x in tr]
    	eps = [x.find_all('td')[7].get_text().strip() for x in tr]
    	surprise = [x.find_all('td')[8].get_text().strip() for x in tr]
    	s = pd.DataFrame({'ticker':ticker,'consensus':consensus,'cap':cap,'num':num,'eps':eps,'surprise':surprise},index = ticker)
    	s = s[s.consensus != '$n/a']
    	s = s[s.eps != 'n/a']
    	s['consensus'] = [x.split('$')[1] for x in s.consensus]
    	s['eps'] = [x.split('$')[1] for x in s.eps]
    	s.consensus = map(float,s.consensus)
    	s.num = map(int,s.num)
    	s = s.replace({'Met':0})
    	s = s[s.surprise != 'N/A']
    	s.surprise = map(float,s.surprise)
    	date = parser.parse(url[-11:]).strftime('%Y%m%d')
    	s['time'] = date
    	return s


    def re_arrange(self,yahoo,nasdaq,date):
    	a,b = yahoo.ix[date],nasdaq.ix[date]
    	a,b  = a.set_index(a.ticker),b.set_index(b.ticker)
    	try:
    		df = pd.concat([a,b],axis = 1,join_axes = [b.index])
    	except:
    		df = pd.concat([a,b],axis = 1,join_axes = [a.index])
    	df = df.dropna()
    	df = df.ix[:,~df.columns.duplicated()]
    	df = df.set_index(df.time)
    	return(df)

    def yahoo_table(self):
        l = self.yahoo_date()
        yahoo_url = ['https://biz.yahoo.com/research/earncal/' + l[i] + '.html' for i in range(len(l))]
        yahoo = self.yahoo_get_info(yahoo_url[0])
        llll = len(yahoo_url)
        for i in range(1,len(yahoo_url)):
        	if i%10 == 0:
        		print 'yahoo getting page %d out of %d' %(i,llll)
        	a = self.yahoo_get_info(yahoo_url[i])
        	yahoo = pd.concat([yahoo,a])
        yahoo.release[yahoo.release.str.contains('am')] = 'Before Market Open'
        yahoo.release[yahoo.release.str.contains('pm')] = 'After Market Close'
        yahoo = yahoo[yahoo.release != 'Time Not Supplied']
        return yahoo

    def nasdaq_table(self):
        date = self.nasdaq_date()
        nasdaq_url = ['http://www.nasdaq.com/earnings/earnings-calendar.aspx?date=' + x for x in date]
        nasdaq = []
        a = 0
        while len(nasdaq) == 0:
        	nasdaq = self.nasdaq_get_info(nasdaq_url[a])
        	a+=1
        for i in range(a+1,len(nasdaq_url)):
        	try:
        		if i%10 == 0:
        			print 'nasdaq getting page %d' %i
        		a = self.nasdaq_get_info(nasdaq_url[i])
        		if len(a) == 0:
        			pass
        		else:
        			nasdaq = pd.concat([nasdaq,a])
        	except:
        		print i
        return nasdaq


    def output(self):
        yahoo = self.yahoo_table()
        nasdaq = self.nasdaq_table()
        yahoo = yahoo.set_index(yahoo.time)
        nasdaq = nasdaq.set_index(nasdaq.time)
        index = [x for x in yahoo.index if x in nasdaq.index]
        index = list(set(index))
        full = self.re_arrange(nasdaq,yahoo,index[0])
        num = len(index)
        for i in range(1,num):
        	try:
        		a = self.re_arrange(nasdaq,yahoo,index[i])
        		full = pd.concat([full,a])
        		if i%50 == 0:
        			print "process %d out of %f" %(i,num)
        	except:
        		print i
        return full
