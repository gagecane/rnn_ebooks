import src.pkg.makeBody as makeBody
import json
import os
import tweepy


def testLoadBodyNonexistFile(capsys):
    body = makeBody.OfflineBody("./tests/nonexist.json")
    assert body.getJsonBody() is None
    captured = capsys.readouterr()
    assert captured.out != ""


def testLoadBodyFromFile(capsys):
    body = makeBody.OfflineBody("./tests/sample_inputs/sample_body.json")
    loadedBody = body.getJsonBody()
    assert loadedBody is not None
    with open("./tests/sample_inputs/sample_body.json", 'r') as infile:
        assert loadedBody == json.load(infile)


def testPrintBody(capsys):
    body = makeBody.OfflineBody("./tests/sample_inputs/sample_body.json")
    body.outputHtm = "./tests/out.htm"
    body.printJsonBody()
    assert os.path.exists("./tests/out.htm")
    os.remove("./tests/out.htm")


def testOnlineBody(capsys):
    timeline = makeBody.Timeline(tweepy.api)
    body = makeBody.OnlineBody(
        "@fakeuser", timeline)
    assert body is not None
