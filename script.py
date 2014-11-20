from datetime import datetime
import re
import operator
import pickle
import csv
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords

fmt = "%Y-%m-%d %H:%M:%S"
base_time = "2010-06-18 13:45:00"

def construct_dictionary(file_name):
    dict_obj = {}
    f = open("dictionary","r")
    lines = f.readlines()
    for line in lines:
        dict_obj[line.strip()] = dict_obj.get(line.strip(),0) + 1

    return dict_obj

def calculate_time_freq(source_file, base_time, output_file):

    freq_obj = {}
    f = open(source_file, 'r')
    r = csv.reader(f, delimiter = '\t')
    base_time = datetime.strptime(base_time, fmt)

    while (1):
        try:
            t= r.next()
        except StopIteration:
            break

        print r.line_num

        mat=re.match('(\d{4})[/.-](\d{2})[/.-](\d{2})\s(\d{2})[/.:](\d{2})[/.:](\d{2})$',t[0])
        if mat is not None:
            d = datetime.strptime(t[0],fmt)
            #d = d - base_time
            #key = d.seconds/60
            key = format(d.hour,"02d")+":"+format(d.minute,"02d")
            freq_obj[key] = freq_obj.get(key,0)+1
        else:
            continue

    f.close()
    f = open(output_file,"w")
    for key in sorted(freq_obj.keys()):
        f.write(str(key)+"\t"+str(freq_obj[key])+"\n")
    f.close()

    print "max is ", max(freq_obj.values())

    print "COMPLETED"

def is_proper_english(tweet,threshold):

    dict_obj = construct_dictionary("dictionary")
    words = nltk.word_tokenize(tweet)
    synsets_len = []
    #print words
    for word in words:
        if word.isalpha():
            synsets_len.append(dict_obj.get(word,0))
    #print synsets_len
    if synsets_len.count(0) > threshold:
        return False
    else:
        return True

def extract_minutewise_tweets(source_file, base_time, output_file, threshold):
    """
        Filtering criteria: Remove tweets with RT, @, http://
    """
    
    patterns = ["http://",".com","RT", "@"]
    tweets_obj = {}
    f = open(source_file, 'r')
    r = csv.reader(f, delimiter = '\t')
    base_time = datetime.strptime(base_time, fmt)
    while (1):
        try:
            t= r.next()
        except StopIteration:
            break

        print r.line_num

        mat=re.match('(\d{4})[/.-](\d{2})[/.-](\d{2})\s(\d{2})[/.:](\d{2})[/.:](\d{2})$',t[0])
        if mat is not None:
            if t[2] != "en":
                continue
            tweet = t[3]
            if any(i in tweet for i in patterns):
                continue

            try:
                tweet.decode("ascii")
            except UnicodeDecodeError:
                continue

            tweet = tweet.lower()
            if not is_proper_english(tweet,threshold):
                continue

            print tweet

            d = datetime.strptime(t[0],fmt)
            d = d - base_time
            key = d.seconds/60
            #key = format(d.hour,"02d")+":"+format(d.minute,"02d")
            if tweets_obj.has_key(key):
                tweets_obj[key].append(tweet)
            else:
                tweets_obj[key] = [tweet]
        else:
            continue
    pickle.dump(tweets_obj, open(output_file,'w'))

    return tweets_obj

def top_k_tweets(tweets, words_k, tweets_k):
    """
        Using the top-k-words approach.
        tweets: Set of tweets
        words_k : gives the no of top words consider
        tweets_k : No of top tweets to be returned by the function
    """
    word_score = {}
    tweet_score = []
    stop_words = stopwords.words("english")
    stop_words += ["usa","slo","slovenia","worldcup","...","svn","yes","fuck","goal","shit","wc2010","worldcup"]
    for tweet in tweets:
        words = nltk.word_tokenize(tweet)
        for word in words:
            if len(word) > 2 and word not in stop_words:
                word_score[word] = word_score.get(word,0)+1

    sorted_word_score = sorted(word_score.items(), key=operator.itemgetter(1),reverse = True)

    count = 0

    top_k_words = []
    #Take the top_k words in to a separate list
    for entry in sorted_word_score:
        if count > words_k:
            break
        top_k_words.append(entry[0])
        print entry
        count += 1

    #Calculating score of each tweet
    for tweet in tweets:
        score = 0
        for word in nltk.word_tokenize(tweet):
            if word in top_k_words:
                score += words_k+10 - top_k_words.index(word)
        tweet_score.append((tweet,score))

    sorted_tweets = sorted(tweet_score, key=operator.itemgetter(1),reverse = True)

    count = 0
    for (tweet,score) in sorted_tweets:
        if count > tweets_k:
            break
        print tweet,score
        count += 1

    return sorted_tweets
        
def jaccard_similarity(tweet1, tweet2,stop_words):
    """
        Returns the jaccard similarity between two tweets.

        N(A) n N(B)
        -----------
        N(A) u N(B)
    """

    words1 = set(nltk.word_tokenize(tweet1)) - set(stop_words)
    words2 = set(nltk.word_tokenize(tweet2)) - set(stop_words)
    
    return (len(list(words1&words2))+0.)/len(list(words1|words2))

def top_k_tweets_jaccard(tweets,k):
    """
        For each tweet, score is the sum of jaccard similarity of the tweet with the remaining tweets
        in the set.
    """
    temp_scores = {}
    scores = {}

    stop_words = stopwords.words("english")
    stop_words += ["usa","slo","slovenia","worldcup","...","svn","yes","fuck","goal","shit","wc2010","worldcup"]

    for i in range(0,len(tweets)):
        for j in range(0,len(tweets)):
            if i!=j and not temp_scores.has_key(str(j)+":"+str(i)):
                temp_scores[str(i)+":"+str(j)] = jaccard_similarity(tweets[i],tweets[j],stop_words)
                print i,j
    
    print "Scores calculated"

    for i in range(0,len(tweets)):
        score = 0
        for j in range(0,len(tweets)):
            if i<j:
                score += temp_scores.get(str(i)+":"+str(j),0)
            if i>j:
                score += temp_scores.get(str(j)+":"+str(i),0)
        scores[i] = score
                
    sorted_scores = sorted(scores.items(), key=operator.itemgetter(1),reverse = True)

    count = 0
    for (index,score) in sorted_scores:
        if count > k:
            break
        print tweets[index],score
        count += 1
    
