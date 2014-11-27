from plot import *
from script import *

def match_summary(tweets_file = "refined_tweets_ascii_3_latest_all_patterns", time_freq_file = "time_freq", k = 1, top_words = 20, top_tweets = 20, tweets_per_moment = 3):
    """
        Generates the summary of the match using all the methods as described in the report
    """

    moments = important_moments(time_freq_file)
    tweets = pickle.load(open(tweets_file,'r'))
    summary_words = []
    summary_refined = []
    for moment in moments:
        tweets_moment = []
        for i in range(moment-k,moment+k+1):
            tweets_moment += tweets[i]

        top_k_tweets_moment = top_k_tweets(tweets_moment, top_words, top_tweets)
        summary_words.append(top_k_tweets_moment[0:tweets_per_moment])
        r = refine_tweets_jaccard(top_k_tweets_moment,tweets_per_moment)
        summary_refined.append(r)

    print "SUMMARY : just using top k words"
    print summary_words

    print "SUMMARY : after refining"
    print summary_refined
    
