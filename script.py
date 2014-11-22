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

def gen_stop_words():
    stop_words = stopwords.words("english")
    stop_words += ["usa","slo","slovenia","worldcup","...","svn","yes","fuck","shit","crap","goal","wc2010","worldcup","n't","'s"]
    return stop_words

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

def is_proper_english(tweet,threshold = 3):

    dict_obj = construct_dictionary("dictionary")
    words = nltk.word_tokenize(tweet)
    scores = []
    #print words
    for word in words:
        if word.isalpha():
            scores.append(dict_obj.get(word,0))
    #print scores
    if len(scores) - scores.count(0) < threshold:
        return False
    else:
        return True

def extract_minutewise_tweets(source_file, base_time, output_file, threshold):
    """
        Filtering criteria: Remove tweets with RT, @, http://
    """
    
    patterns = ["http://",".com","RT", "@","fuck","crap","shit","wtf","i","we","our"]
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

            try:
                tweet.decode("ascii")
            except UnicodeDecodeError:
                continue

            tweet = tweet.lower()

            if any(i in tweet for i in patterns):
                continue

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
    stop_words = gen_stop_words()
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
        for word in set(nltk.word_tokenize(tweet)):
            if word in top_k_words:
                score += sorted_word_score[top_k_words.index(word)][1]
                #score += words_k+10 - top_k_words.index(word)
        tweet_score.append((tweet,score))

    sorted_tweets = sorted(tweet_score, key=operator.itemgetter(1),reverse = True)
    
    count = 0
    for (tweet,score) in sorted_tweets:
        if count > tweets_k:
            break
        print tweet,score
        count += 1

    result = [tweet for (tweet,score) in sorted_tweets]

    return result[:tweets_k]

def k_subsets_i(n, k):
    '''
    Yield each subset of size k from the set of intergers 0 .. n - 1
    n -- an integer > 0
    k -- an integer > 0
    '''
    # Validate args
    if n < 0:
        raise ValueError('n must be > 0, got n=%d' % n)
    if k < 0:
        raise ValueError('k must be > 0, got k=%d' % k)
    # check base cases
    if k == 0 or n < k:
        yield set()
    elif n == k:
        yield set(range(n))

    else:
        # Use recursive formula based on binomial coeffecients:
        # choose(n, k) = choose(n - 1, k - 1) + choose(n - 1, k)
        for s in k_subsets_i(n - 1, k - 1):
            s.add(n - 1)
            yield s
        for s in k_subsets_i(n - 1, k):
            yield s

def k_subsets(s, k):
    s = list(s)
    n = len(s)
    for k_set in k_subsets_i(n, k):
        yield set([s[i] for i in k_set])

def generate_nck(n,k):
    result = []
    for t in k_subsets(range(0,n),k):
        result.append(list(t))
    return result

def refine_tweets_jaccard(tweets, no_of_tweets):

    pairs = generate_nck(len(tweets),no_of_tweets) 

    pair_score = []
    for pair in pairs:
        score = 0
        for i in range(0,len(pair)):
            for j in range(i+1,len(pair)):
                score += jaccard_similarity(tweets[pair[i]],tweets[pair[j]])
                #print i,j,jaccard_similarity(tweets[pair[i]],tweets[pair[j]])
        #print pair,score
        pair_score.append((pair,score))

    sorted_pair_score = sorted(pair_score, key=operator.itemgetter(1))

    top_k_index = sorted_pair_score[0][0]
    result = []
    for i in range(0,len(top_k_index)):
        result.append(tweets[top_k_index[i]])
        print tweets[top_k_index[i]]

    return result

        
def jaccard_similarity(tweet1, tweet2):
    """
        Returns the jaccard similarity between two tweets.

        N(A) n N(B)
        -----------
        N(A) u N(B)
    """

    stop_words = gen_stop_words()
    words1 = []
    words2 = []
    for word in nltk.word_tokenize(tweet1):
        if len(word) > 2 and word not in stop_words:
            words1.append(word)

    for word in nltk.word_tokenize(tweet2):
        if len(word) > 2 and word not in stop_words:
            words2.append(word)


    words1 = set(words1)
    words2 = set(words2)
    
    return (len(list(words1&words2))+0.)/len(list(words1|words2))

def top_k_tweets_jaccard(tweets,k):
    """
        For each tweet, score is the sum of jaccard similarity of the tweet with the remaining tweets
        in the set.
    """
    temp_scores = {}
    scores = {}

    stop_words = gen_stop_words()

    for i in range(0,len(tweets)):
        for j in range(0,len(tweets)):
            if i!=j and not temp_scores.has_key(str(j)+":"+str(i)):
                temp_scores[str(i)+":"+str(j)] = jaccard_similarity(tweets[i],tweets[j])
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
    
