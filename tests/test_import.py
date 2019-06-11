import src.pkg.makeBody as makeBody


def testLoadKeysInit(capsys):
    """ init KeyHolder.keyFile and use loadKeys() with no arguments
    """
    keyholder = makeBody.KeyHolder("./tests/test_keys.json")
    assert keyholder.keyFile == "./tests/test_keys.json"
    assert keyholder.loadedConsumerKeys() is False
    captured = capsys.readouterr()
    assert captured.out == keyholder.errKeysNotLoaded+"\n"
    assert captured.err == ''

    keyholder.loadKeys()
    assert keyholder.loadedConsumerKeys() is True


def testLoadKeysNotInit(capsys):
    """ init KeyHolder.keyFile to none and pass file string to loadKeys
    """
    keyholder = makeBody.KeyHolder()
    assert keyholder.keyFile is None
    assert keyholder.loadedConsumerKeys() is False

    keyholder.loadKeys("./tests/test_keys.json")
    assert keyholder.loadedConsumerKeys() is True
