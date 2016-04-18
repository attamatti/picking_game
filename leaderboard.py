#!/usr/bin/python

import time
import os

def check_scores(number):
    os.system('clear')  
    print "** Particle Picking Leaderboard **"
    print '\n    NAME                                    SCORE'
    scoresdata = open('email_scores.txt','r').readlines()
    
    scores = {}
    for i in scoresdata:
        splitdata = i.split(',')
        if int(splitdata[2])-int(splitdata[3]) in scores:
            scores[int(splitdata[2])-int(splitdata[3])].append(splitdata[0])
        else:
            scores[int(splitdata[2])-int(splitdata[3])] = [splitdata[0]] 
    keys = scores.keys()
    keys.sort(reverse=True)
    n = 1
    curr = keys[0]
    if len(keys) < number:
        listlength = len(keys)
    else:
        listlength = number
    
    for i in keys[0:listlength]:
        if i < curr:
            n +=1
    	m=0
        for j in scores[i]:
            print '{0:>2}) {1:<40} {2:>3}'.format(n,scores[i][m],i) 
            m+=1
            curr = i
    wait = raw_input('')
    check_scores(num)
num = raw_input('number of scores to display: ') or 10
num = int(num)
check_scores(num)
