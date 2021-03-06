import string
import random
from dataStore import DataStore

def newToken(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits, prefix='', datastore=None, randomComponent=True):
    '''
    Generates a new token. 'size' indicates de number of characters. 'chars' the allowed characters
    and 'datastore' the target datastore (if any, it will be checked that the token does not exists).
    '''
    exists = True
    aux = None
    token = prefix
    if randomComponent:
        while exists:
            aux = ''.join(random.choice(chars) for _ in range(size))
            token += aux
            if isinstance(datastore, DataStore)==False:
                exists = False
            elif datastore.checkIfExists(token) == False:
                exists = False

    return token


def newContextToken(datastore=None):
    return newToken(prefix='CT', datastore=datastore)


def newImageToken(datastore=None, contextReference='', imageName=''):
    return newToken(prefix=contextReference+'-IM'+imageName, datastore=datastore, randomComponent=False)


def newClusterToken(datastore=None):
    return newToken(prefix='CL', datastore=datastore)


def newCompositionToken(datastore=None):
    return newToken(prefix='CM', datastore=datastore)
