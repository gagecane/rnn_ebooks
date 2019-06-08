import tweepy
import json
# from datetime import datetime
import emoji
import os
from pathlib import Path

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


def printTweetsToFile(api, user, count, filename, existingBody, max_id=None):
    """ Print a number of tweets from a specified username to a file

    Arguments:
        api {tweepy.API(auth)} -- authenticated tweepy API
        user {string} -- Twitter username with @
        count {number} -- Number of tweets to print
        filename {string} -- Output file name
        existingBody {dict} -- Existing contents of JSON body for this username

    Keyword Arguments:
        max_id {number} --  Max ID of tweets to retreive.
                            Will retreive older (lower ID) tweets
                            (default: {None})
    """
    tweets = api.user_timeline(
        # Extended should get tweets longer than 140 but may only
        # work with api.get_status
        screen_name=user, count=count, max_id=max_id, include_rts=False)

    OutFileBody = open(filename, "w")
    if(existingBody is not None):
        tweetsToWrite = existingBody
    else:
        tweetsToWrite = {}
    for tweet in tweets:
        tid = tweet.id
        full_text = tweet.text

        # If the tweet is probably truncated, use get_status instead
        if "…" in full_text:
            full_text = api.get_status(tid, tweet_mode='extended').full_text

        tweetsToWrite[tid] = emoji.demojize(full_text)

    json.dump(tweetsToWrite, OutFileBody)
    OutFileBody.close()


def printJsonBody(filename):
    """Generate test.htm from the corpus and open it in a browser

    Arguments:
        filename {string} -- The input json file to print
    """
    with open(filename, 'r') as infile:
        data = json.load(infile)
        with open('test.htm', 'w', encoding='utf-8-sig') as f:
            for d in data.values():
                f.write((emoji.emojize(d)+"\n").replace("\r\n", "\n")
                        .replace("\n", "<br />\n"))
        os.startfile('test.htm')


def getJsonBody(filename):
    """Try loading body from Json file. Return the dict if the file exists

    Arguments:
        filename {string} -- Json body filename

    Returns:
        Dict -- Json data or None if file does not exist
    """
    try:
        with open(filename, 'r') as infile:
            return json.load(infile)
    except Exception:
        print(filename + "does not already exist. Creating new file.")
        Path(filename).touch()
        return None


def buildBody(username):
    """Build a body JSON for an input username

    Arguments:
        username {string} -- Twitter handle starting with @
    """
    if (not os.path.isdir("./bodies/")):
        os.mkdir("bodies")
    outFilename = "./bodies/"+username.replace("@", '')+"_body.json"
    MaxId = None
    LastMaxId = -1
    while(LastMaxId != MaxId):
        if(MaxId):
            LastMaxId = MaxId
        try:
            data = getJsonBody(outFilename)
            if(data is not None):
                # Subtract one to not include the same oldest tweet
                MaxId = min([int(d) for d in data.keys()])-1
                print("Max ID: %d" % MaxId)
            else:
                MaxId = None
                print("No Max ID yet")
            printTweetsToFile(
                api, username, 200, outFilename, data, max_id=MaxId)
        except Exception as ex:
            print(ex)
            break
    printJsonBody(outFilename)


if __name__ == "__main__":
    loadKeys()
    api = connectToTwitter()
    username = "@StoobsDeer"
    buildBody(username)
    # outFilename = username+"_body%s.json" % datetime.now()
    #                                       .strftime("%Y%m%d-%H%M%S")

    # for twitter_user in twitter_users:
    #     downloadTweets(twitter_user)
