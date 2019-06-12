import src.pkg.makeBody as makeBody
import json
import os
# import pytest


def testLoadKeysInit():
    """ init KeyHolder.keyFile and use loadKeys() with no arguments
    """
    keyholder = makeBody.KeyHolder("./tests/sample_keys/all_keys_in.json")
    assert keyholder.keyFile == "./tests/sample_keys/all_keys_in.json"
    assert keyholder.loadedConsumerKeys() is False

    keyholder.loadKeys()
    assert keyholder.loadedConsumerKeys() is True


def testLoadKeysNotInit():
    """ init KeyHolder.keyFile to none and pass file string to loadKeys
    """
    keyholder = makeBody.KeyHolder()
    assert keyholder.keyFile is None
    assert keyholder.loadedConsumerKeys() is False

    keyholder.loadKeys("./tests/sample_keys/all_keys_in.json")
    assert keyholder.loadedConsumerKeys() is True


def testLoadNonExistKeyFile():
    """Try loading a non-existing key file
    """
    keyholder = makeBody.KeyHolder()
    assert keyholder.keyFile is None
    try:
        keyholder.loadKeys()
    except Exception:
        assert True
    try:
        keyholder.loadKeys("nonexist.json")
    except Exception:
        assert True


def testSaveEmptyKeyFile():
    """Try loading a non-existing key file
    """
    keyholder = makeBody.KeyHolder()
    assert keyholder.keyFile is None
    keyholder.saveKeysToFile("./tests/sample_keys/keys_out.json")


def testSaveKeysToFile():
    """Load keys from a file and save to another file
    """
    keyholder = makeBody.KeyHolder()
    keyholder.loadKeys("./tests/sample_keys/all_keys_in.json")
    keyholder.saveKeysToFile("./tests/sample_keys/keys_out.json")
    with open("./tests/sample_keys/all_keys_in.json", 'r') as inkeysfp:
        with open("./tests/sample_keys/keys_out.json", 'r') as writtenkeysfp:
            inkeys = json.load(inkeysfp)
            writtenkeys = json.load(writtenkeysfp)
            assert inkeys == writtenkeys
    os.remove("./tests/sample_keys/keys_out.json")


def testConnectKeysNotLoaded(capsys):
    """Fail a connection because keys were never loaded
    """
    keyholder = makeBody.KeyHolder()
    keyholder.connectToTwitter()
    captured = capsys.readouterr()
    assert captured.out != ""


def testConnectInvalidAccessToken():
    """Load all keys and try to connect with invalid access_token
    """
    keyholder = makeBody.KeyHolder()
    keyholder.loadKeys("./tests/sample_keys/all_keys_in.json")
    keyholder.connectToTwitter()
