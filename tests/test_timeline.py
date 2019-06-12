import src.pkg.makeBody as makeBody
import json
import os
import tweepy


def testLoadBodyNonexistFile(capsys):
    timeline = makeBody.Timeline(tweepy.api)
    assert timeline is not None
