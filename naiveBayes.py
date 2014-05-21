import re
import math
from subprocess import Popen
import os, sys, stat
import shutil

def getwords(doc):
    splitter=re.compile('\\W*')
    # Split the words by non-alpha characters
    words=[s.lower( ) for s in splitter.split(doc)
    if len(s)>2 and len(s)<20]
    # Return the unique set of words only
    return dict([(w,1) for w in words])
    
class classifier:
    def __init__(self,getfeatures,filename=None):
        # Counts of feature/category combinations
        self.fc={}
        # Counts of documents in each category
        self.cc={}
        self.getfeatures=getfeatures
 
# Increase the count of a feature/category pair
    def incf(self,f,cat):
        self.fc.setdefault(f,{})
        self.fc[f].setdefault(cat,0)
        self.fc[f][cat]+=1
# Increase the count of a category
    def incc(self,cat):
     self.cc.setdefault(cat,0)
     self.cc[cat]+=1
     # The number of times a feature has appeared in a category
    def fcount(self,f,cat):
     if f in self.fc and cat in self.fc[f]:
        return float(self.fc[f][cat])
     return 0.0
    # The number of items in a category
    def catcount(self,cat):
     if cat in self.cc:
        return float(self.cc[cat])
     return 0
    # The total number of items
    def totalcount(self):
        return sum(self.cc.values( ))
    # The list of all categories
    def categories(self):
        return self.cc.keys( )
 
    def train(self,item,cat):
         features=self.getfeatures(item)
         # Increment the count for every feature with this category
         for f in features:
            self.incf(f,cat)
         # Increment the count for this category
         self.incc(cat)
 
    def fprob(self,f,cat):
         if self.catcount(cat)==0: 
            return 0122 
         # The total number of times this feature appeared in this
         # category divided by the total number of items in this category
         return self.fcount(f,cat)/self.catcount(cat)

    def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
         # Calculate current probability
         basicprob=prf(f,cat)
         # Count the number of times this feature has appeared in
         # all categories
         totals=sum([self.fcount(f,c) for c in self.categories( )])
         # Calculate the weighted average
         bp=((weight*ap)+(totals*basicprob))/(weight+totals)
         return bp   
   

	
class naivebayes(classifier):
    
    def __init__(self,getfeatures):
        classifier.__init__(self,getfeatures)
        self.thresholds={}
	
    def docprob(self,item,cat):
	    features=self.getfeatures(item)
	    # Multiply the probabilities of all the features together
	    p=1
 	    for f in features: p*=self.weightedprob(f,cat,self.fprob)
 	    return p
           
    def setthreshold(self,cat,t):
        self.thresholds[cat]=t

    def getthreshold(self,cat):
        if cat not in self.thresholds: return 1.0
        return self.thresholds[cat]        
    
    def classify(self,item,default=None):
		probs={}
		maxi = 0.0
		
		for cat in self.categories( ):
			probs[cat]=self.prob(item,cat)       
			if probs[cat]>=maxi:
				maxi=probs[cat]
				best=cat	
			
			# Make sure the probability exceeds threshold*next best
		for cat in probs:
			if cat==best: continue
			if (probs[cat]*self.getthreshold(best))>probs[best]: return default
		return best         

    def prob(self,item,cat):
        catprob=self.catcount(cat)/self.totalcount( )
        docprob=self.docprob(item,cat)
        return docprob*catprob 	  
	
  
        
def train(cl):
	with open('SPAMTrain.label') as spamRead:
		count = 1
		spam = 0
		for line in spamRead:   
			if(count != 1):
				filterValue = line[0]
				fileName = line[2:].strip()
				print(fileName)			
				if(filterValue == "0"):
					spam = spam +1
				#open the indvi files and read entrire
				print("learning file"+ str(count)+"  :" + fileName)
				fp = open("TRAINING/"+fileName)
				cl.train(fp.read(),filterValue)
			count = count + 1
			
		print("...........................................................\n" + "actual no. of spams in training case : " + str(spam) + "\n...........................................................")
	spamRead.close()
	
def testing(cl):				
	files = os.listdir("ExtractTest/")			#Give the testing folder here
	count = 0
	spam_count = 0
	none =0
	for file in files:
		with open('ExtractTest/'+file) as test:				#Give the testing folder here
			content = test.read()
			if(cl.classify(content, default = "haha") == "0"):
				print(file +  " spam")
				spam_count = spam_count +1 
			elif(cl.classify(content, default = "haha") == "1"):
				count = count +1
			else:
				none = none +1	
	print("no. of spam mails  " + str(spam_count))
	print("no. of ham mails   " + str(count))
	print("not known mails    " + str(none))	
			
cl = naivebayes(getwords)

def sampletrain(cl):
	cl.train('Nobody owns the water.','good')
	cl.train('the quick rabbit jumps fences','good')
	cl.train('buy pharmaceuticals now','bad')
	cl.train('make quick money at the online casino','bad')
	cl.train('the quick brown fox jumps','good')



#	0 - Spam
#	1 - Ham

sampletrain(cl)	
train(cl)			
cl.setthreshold('0',3)
testing(cl)

'''
print(cl.prob('quick rabbit','good'))
print(cl.prob('quick rabbit','bad'))
print(cl.classify('quick rabbit',default='unknown'))
'''
