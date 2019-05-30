import tweepy
import json


keyFile = "consumer_keys.json"


def downloadTweets(user):
    """Download as many tweets as possible from a Twitter user

    Arguments:
        user {string} -- [twitter handle with @]
    """
    # Configure authentication
    authorisation = tweepy.OAuthHandler(
        keys["consumer_key"], keys["consumer_secret"])
    authorisation.set_access_token(keys["access_token"], keys["access_secret"])
    api = tweepy.API(authorisation)
    # Requests most recent tweets from a users timeline
    tweets = api.user_timeline(screen_name=user, count=2,
                               max_id=936533580481814529)
    for tweet in tweets:
        tid = tweet.id
        print(tid)


def loadKeys():
    """Load a consumer key from a file
    """
    global keys
    keys = {}
    with open(keyFile, 'r') as infile:
        keys = json.load(infile)


def saveKeyToFile():
    """Save the keys dictionary to a file of key=value
    """
    try:
        x = keys["consumer_key"]
        x = keys["consumer_secret"]
    except KeyError:
        print("Error! Not writing %s before loadKeys()" % keyFile)
    with open("consumer_keys.json", "w") as outfile:
        outfile.write(json.dumps(keys, indent=4, sort_keys=True))


def connectToTwitter():
    """ Connect to twitter
    """
    try:
        x = keys["consumer_key"]
    except KeyError:
        print("Need to populate consumer_key! Run loadKeys() first")

    auth = tweepy.OAuthHandler(keys["consumer_key"], keys["consumer_secret"])

    if "access_token" in keys:
        auth.set_access_token(keys["access_token"],
                              keys["access_token_secret"])

    else:
        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepError:
            print('Error! Failed to get request token.')
        print(redirect_url)

        verifier = input('\n Visit the above URL and input the pin: ')

        try:
            auth.get_access_token(verifier)
        except tweepy.TweepError:
            print('Error! Failed to get access token.')

        keys["access_token"] = auth.access_token
        keys["access_token_secret"] = auth.access_token_secret
        saveKeyToFile()
    '''
    To store the access token depends on your application.
    Basically you need to store 2 string values: key and secret:

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(key, secret)
    '''

    api = tweepy.API(auth)
    return api


def printTweets(api, user, count):
    """Print a number of tweets from a specified username

    Arguments:
        api {tweepy.API(auth)} -- authenticated tweepy API
        user {string} -- Twitter username with @
        count {number} -- Number of tweets to print
    """
    tweets = api.user_timeline(screen_name=user, count=count,
                               max_id=936533580481814529)
    for tweet in tweets:
        print(tweet.text)
        tid = tweet.id
        print(tid)


if __name__ == "__main__":
    loadKeys()
    api = connectToTwitter()
    printTweets(api, "@StoobsDeer", 2)
    # twitter_users = ["@StoobsDeer"]

    # for twitter_user in twitter_users:
    #     downloadTweets(twitter_user)
