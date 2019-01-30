#!/usr/bin/python

import time
import os

def check_scores(number):
    os.system('clear')  

    scoresdata = open('email_scores.txt','r').readlines()
    
    scores = {}
    for i in scoresdata:
        splitdata = i.split(',')
        if int(splitdata[1])-int(splitdata[2]) in scores:
            scores[int(splitdata[1])-int(splitdata[2])].append((splitdata[0],splitdata[3].replace('\n','')))
        else:
            scores[int(splitdata[1])-int(splitdata[2])] = [(splitdata[0],splitdata[3].replace('\n',''))]
    keys = scores.keys()
    keys.sort(reverse=True)
    n = 1
    curr = keys[0]
    if len(keys) < number:
        listlength = len(keys)
    else:
        listlength = number
    print "** Particle Picking Top {0} Leaderboard **".format(listlength)
    print '\n    NAME                                      SCORE       TIME'
    
    for i in keys[0:listlength]:
        if i < curr:
            n +=1
    	m=0
        for j in scores[i]:
            print '{0:>2}) {1:<40} {2:>6}       {3:>5}'.format(n,scores[i][m][0],i,':'.join(scores[i][m][1].split('.')[0].split(':')[1:3])) 
            m+=1
            curr = i
    wait = raw_input('')
    check_scores(num)
num = raw_input('number of scores to display: ') or 10
num = int(num)
check_scores(num)
