import tweepy
import json
import sys
# from datetime import datetime
import emoji
import os


class KeyHolder:
    """Handles consumer and oauth keys loading, saving and doing oauth to generate
       an api object
    """

    def __init__(self, keyFile=None):
        self.keyFile = keyFile
        self.keys = {}
        self.consumer_keys = ["consumer_key", "consumer_secret"]
        self.access_tokens = ["access_token", "access_token_secret"]
        self.errKeysNotLoaded = "Run loadKeys(keyFile) first and \
                            make sure your json keyfile is populated with " \
                            + ", ".join(self.consumer_keys)

    def loadedConsumerKeys(self):
        """ Check if the consumer keys were loaded into self.keys
        """
        if(any(d not in self.keys for d in self.consumer_keys)):
            print(self.errKeysNotLoaded)
            return False
        return True

    def loadKeys(self, keyFile=None):
        """Load consumer keys from a json file

        Keyword Arguments:
            keyFile {string} -- Optional keyFile name. Will use self.keyFile
                                if not populatd (default: {None})
        """
        keyFileToLoad = keyFile
        if (keyFile is None):
            keyFileToLoad = self.keyFile
        try:
            with open(keyFileToLoad, 'r') as infile:
                self.keys = json.load(infile)
        except TypeError:
            print("Error: expected a string for filename")
        except FileNotFoundError:
            print("Error: File %s does not exist" % keyFileToLoad)

    def saveKeysToFile(self, outKeyFile):
        """Save the keys dictionary to a json file
        """
        if (not self.loadedConsumerKeys()):
            print("Not writing %s before loading %s" %
                  (outKeyFile, ", ".join(self.consumer_keys)))
            return
        else:
            with open(outKeyFile, "w") as outfile:
                outfile.write(json.dumps(self.keys, indent=4, sort_keys=True))

    def connectToTwitter(self):
        """ Connect to twitter
            Requres loadKeys() was ran to load consumer_key
        """
        if (not self.loadedConsumerKeys()):
            print("Not attempting to connect to twitter without loading \
                   required keys!")
            return

        # Load oauth and get access_token and access_token_secret
        auth = tweepy.OAuthHandler(
            self.keys["consumer_key"], self.keys["consumer_secret"])

        if "access_token" in self.keys and "access_token_secret" in self.keys:
            auth.set_access_token(self.keys["access_token"],
                                  self.keys["access_token_secret"])

        # Exclude this from Coverage because tests cannot try to authenticate
        else:  # pragma: no cover
            redirect_url = "no url"
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
            self.saveKeysToFile("keys_save.json")

        api = tweepy.API(auth)
        return api


class OfflineBody:
    """For interacting with an offline body json
    """

    def __init__(self, filename, outputHtm="test.htm"):
        self.filename = filename
        self.outputHtm = outputHtm
        pass

    def printJsonBody(self):
        """Generate test.htm from the corpus and open it in a browser
        """
        data = self.getJsonBody()
        with open(self.outputHtm, 'w', encoding='utf-8-sig') as f:
            for d in data.values():
                f.write((emoji.emojize(d)+"\n").replace("\r\n", "\n")
                        .replace("\n", "<br />\n"))

        if not hasattr(sys, "_called_from_test"):  # pragma: no cover
            os.startfile(self.outputHtm)

    def getJsonBody(self):
        """Try loading body from Json file. Return the dict if the file exists

        Returns:
            Dict -- Json data or None if file does not exist
        """
        try:
            with open(self.filename, 'r') as infile:
                return json.load(infile)
        except Exception:
            print(self.filename + "does not exist.")
            return None


class OnlineBody(OfflineBody):
    """ Requires a connected Timeline.
        Save tweets from twitter to a body
    """

    def __init__(self, user, Timeline):
        self.user = user
        self.Timeline = Timeline
        self.outFilename = "./bodies/"+user.replace("@", '')+"_body.json"
        OfflineBody.__init__(self, self.outFilename)

    def buildBody(self, user, Timeline):  # pragma: no cover
        """Build a body JSON for an input user

        Arguments:
            user {string} -- Twitter handle starting with @
        """
        if (not os.path.isdir("./bodies/")):
            os.mkdir("bodies")
        MaxId = None
        LastMaxId = -1
        while(LastMaxId != MaxId):
            if(MaxId):
                LastMaxId = MaxId
            try:
                existingData = self.getJsonBody(self.outFilename)
                if(existingData is not None):
                    # Subtract one to not include the same oldest tweet
                    MaxId = min([int(d) for d in existingData.keys()])-1
                    print("Max ID: %d" % MaxId)
                else:
                    MaxId = None
                    print("No Max ID yet")
                self.Timeline.printTweetsToFile(
                    api, user, 200, self.outFilename,
                    existingData, max_id=MaxId)
            except Exception as ex:
                print(ex)
                break
        self.printJsonBody(self.outFilename)


class Timeline:

    def __init__(self, api):
        """Class for accessing user timelines. To be used with a Body to save tweets

        Arguments:
            api {tweepy.API(auth)} -- authenticated tweepy API
        """
        self.api = api
        self.existingBody = {}
        self.tweetsToWrite = {}

    def printTweetsToFile(self, user, count, filename,
                          existingBody, max_id=None):  # pragma: no cover
        """ Print a number of tweets from a specified username to a file

        Arguments:
            user {string} -- Twitter username with @
            count {number} -- Number of tweets to print
            filename {string} -- Output file name
            existingBody {dict} -- Existing contents
                                   of JSON body for this username

        Keyword Arguments:
            max_id {number} --  Max ID of tweets to retreive.
                                Will retreive older (lower ID) tweets
                                (default: {None})
        """
        self.existingBody = existingBody
        tweets = self.api.user_timeline(
            # Extended should get tweets longer than 140 but may only
            # work with api.get_status
            screen_name=user, count=count, max_id=max_id, include_rts=False)

        OutFileBody = open(filename, "w")
        if(existingBody is not None):
            self.tweetsToWrite = existingBody
        else:
            self.tweetsToWrite = {}
        for tweet in tweets:
            tid = tweet.id
            full_text = tweet.text

            # If the tweet is probably truncated, use get_status instead
            if "…" in full_text:
                full_text = api.get_status(
                    tid, tweet_mode='extended').full_text

            self.tweetsToWrite[tid] = emoji.demojize(full_text)
        json.dump(self.tweetsToWrite, OutFileBody)
        OutFileBody.close()


if __name__ == "__main__":
    keyholder = KeyHolder("consumer_keys.json")
    keyholder.loadKeys()
    api = keyholder.connectToTwitter()

    username = "@StoobsDeer"
    stoobsdeer = OfflineBody('./bodies/StoobsDeer_body.json')
