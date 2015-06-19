import os
import settings
from threading import Thread
import subprocess

from controllers import errors
from files import createFile

def buildImage(datastore, contextToken, imageName, imageToken, dockerClient=settings.DK_DEFAULT_BUILD_HOST):
    # launch build
    # TODO: replace commandline docker API with docker-py client (fix docker host socket permission and TLS)
    def buildThread():
        cwd =  os.path.join(settings.FS_BUILDS, contextToken)
        cwd =  os.path.join(cwd, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
        cwd =  os.path.join(cwd, imageName)

        command = 'docker build -t '+ datastore.getContext(contextToken)['group'] + '/'+ imageName.lower() +' . ' + '1> '+ settings.FS_DEF_DOCKER_BUILD_LOG +' 2> '+ settings.FS_DEF_DOCKER_BUILD_ERR_LOG
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)

        response = ''
        for line in p.stdout.readlines():
            response+=line+os.linesep

        fileUtils.createFile(os.path.join(cwd, settings.FS_DEF_DOCKER_BUILD_PID), str(p.pid))

        retval = p.wait()

    thread = Thread(target = buildThread)
    thread.start()

def isDockerBuildRunning(contextToken, imageName):
    '''
    Checks if the docker build process is still running. Returns True if the process still runs and False if the process is not running.
    '''
    pidpath = os.path.join(settings.FS_BUILDS, contextToken)
    pidpath = os.path.join(pidpath, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    pidpath = os.path.join(pidpath, imageName)
    pidpath = os.path.join(pidpath, settings.FS_DEF_DOCKER_BUILD_PID)
    try:
        file = open(pidpath, 'r')
    except IOError:
        return True
    pid = int(file.read(10));
    if pid > 1:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            pass
    return False


def getBuildErrors(contextToken, imageName):
    '''
    Retrieve errors in error building log. None if no errors.
    '''
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_ERR_LOG)
    if os.stat(path).st_size == 0:
        return None
    content = ''
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

def getBuildLog(contextToken, imageName):
    '''
    Retrieve standard building log.
    '''
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_LOG)
    content = ''
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

def stopBuild(contextToken, imageName):
    '''
    Stops the build process. Return True if could stop and False it not.
    '''
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_PID)
    try:
        file = open(pidpath, 'r')
    except IOError:
        return True
    pid = int(file.read(10));
    if pid > 1:
        try:
            os.kill(pid, 9)
            return True
        except OSError:
            return False

def runComposition(datastore, token, dockerClient=settings.DK_DEFAULT_BUILD_HOST):
    # launch compose
    # TODO: replace commandline docker API with docker-compose native calls
    def composeThread():
        cwd =  os.path.join(settings.FS_COMPOSITIONS, token)
        command = 'docker-compose up ' + '&> '+ settings.FS_DEF_DOCKER_COMPOSE_LOG
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)

        response = ''
        for line in p.stdout.readlines():
            response+=line+os.linesep

        fileUtils.createFile(os.path.join(cwd, settings.FS_DEF_DOCKER_COMPOSE_PID), str(p.pid))

        retval = p.wait()

    thread = Thread(target = composeThread)
    thread.start()

def purge():
    '''
    Deletes all containers and images. Force if running. This operation is synchronous.
    Returns True if succefull, false if unsuccefull.
    '''
    # Prepare commands
    command1 = 'docker rm -f $(docker ps -q)'
    command2 = 'docker rmi -f $(docker images -q)'

    # Remove containers
    p1 = subprocess.Popen(command1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    response1 = ''
    for line in p1.stdout.readlines():
        response1+=line+os.linesep

    retval1 = p1.wait()

    # Remove images
    p2 = subprocess.Popen(command2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    response2 = ''
    for line in p2.stdout.readlines():
        response2+=line+os.linesep

    retval2 = p2.wait()

    # Check result
    if retval1==0 and retval2==0:
        return True
    else:
        return False