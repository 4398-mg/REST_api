from subprocess import Popen, PIPE
from os.path import expanduser
log = open(expanduser('~')+'/REST_api/git_log.txt', 'w')

Popen('git -C /home/ubuntu/REST_api/ remote update', stdout=PIPE, stderr=PIPE, shell=True).wait()
Popen('git -C /home/ubuntu/REST_api/ status -uno', stdout=log, stderr=PIPE, shell=True).wait()

log.close()

with open(expanduser('~')+'/REST_api/git_log.txt','r') as f:
    contents = f.read()

    if('behind' in contents):
        Popen('pkill -f gunicorn', stdout=PIPE, stderr=PIPE, shell=True).wait()
        Popen('git -C /home/ubuntu/REST_api/ pull origin master', stdout=PIPE, stderr=PIPE, shell=True).wait()
        Popen('python3 /home/ubuntu/REST_api/manage.py gunicorn', stdout=PIPE, stderr=PIPE, shell=True)
