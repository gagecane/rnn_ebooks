import tweepy
import json
# from datetime import datetime
import emoji
import os
from pathlib import Path


class KeyHolder:
    """Handles consumer and oauth keys loading, saving and doing oauth to generate
       an api object
    """

    keyFile = ""
    keys = {}
    consumer_keys = ["consumer_key", "consumer_secret"]
    access_tokens = ["access_token", "access_token_secret"]

    def __init__(self, keyFile):
        keyFile = keyFile

    def loadedConsumerKeys(self):
        """ Check if the consumer keys were loaded into self.keys
        """
        if(any(d not in self.keys for d in self.required_keys)):
            print("Run loadKeys(keyFile) first and \
                make sure your json keyfile is populated with %s "
                  % ", ".join(self.required_keys))
            return False
        return True

    def loadKeys(self, keyFile):
        """Load a consumer key from a json file
        """
        try:
            with open(keyFile, 'r') as infile:
                self.keys = json.load(infile)
        except FileNotFoundError:
            print("Error: File %s does not exist" % keyFile)

    def saveKeyToFile(self, keyFile):
        """Save the keys dictionary to a json file
        """
        if (not self.loadedConsumerKeys()):
            print("Not writing %s before loading %s" %
                  (keyFile, ", ".join(self.required_keys)))
            return
        else:
            with open("consumer_keys.json", "w") as outfile:
                outfile.write(json.dumps(self.keys, indent=4, sort_keys=True))

    def connectToTwitter(self):
        """ Connect to twitter
            Requres loadKeys() was ran to load consumer_key
        """
        if (not self.loadedConsumerKeys()):
            print("Not attempting to connect to twitter without loading required keys!")
            return

        # Load oauth and get access_token and access_token_secret
        auth = tweepy.OAuthHandler(
            self.keys["consumer_key"], self.keys["consumer_secret"])

        if "access_token" in self.keys and "access_token_secret" in self.keys:
            auth.set_access_token(self.keys["access_token"],
                                  self.keys["access_token_secret"])

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

            self.keys["access_token"] = auth.access_token
            self.keys["access_token_secret"] = auth.access_token_secret
            self.saveKeyToFile()

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


def getHello():
    """For testing import
    """
    return("Hello")


if __name__ == "__main__":
    keyholder = KeyHolder("consumer_keys.json")
    keyholder.loadKeys()
    api = keyholder.connectToTwitter()
    username = "@StoobsDeer"
    buildBody(username)
    # outFilename = username+"_body%s.json" % datetime.now()
    #                                       .strftime("%Y%m%d-%H%M%S")

    # for twitter_user in twitter_users:
    #     downloadTweets(twitter_user)
