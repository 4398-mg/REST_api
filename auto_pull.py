from subprocess import Popen, PIPE
from os.path import expanduser
log = open(expanduser('~')+'/rest_api/git_log.txt', 'w')

Popen('git -C /home/ubuntu/rest_api/ remote update', stdout=PIPE, stderr=PIPE, shell=True).wait()
Popen('git -C /home/ubuntu/rest_api/ status -uno', stdout=log, stderr=PIPE, shell=True).wait()

log.close()

with open(expanduser('~')+'/rest_api/git_log.txt','r') as f:
    contents = f.read()

    if('behind' in contents):
        Popen('pkill -f gunicorn', stdout=PIPE, stderr=PIPE, shell=True).wait()
        Popen('git -C /home/ubuntu/rest_api/ pull origin master', stdout=PIPE, stderr=PIPE, shell=True).wait()
        Popen('python3 /home/ubuntu/rest_api/manage.py gunicorn', stdout=PIPE, stderr=PIPE, shell=True)
