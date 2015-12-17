#!/usr/bin/env python
import os
from git import Git, Repo, GitCmdObjectDB

ssh_cmd = 'ssh -i ~/.ssh/blah'
g = Git()
g.update_environment(GIT_SSH_COMMAND=ssh_cmd)
Repo._clone(g, 'ssh://git@git.swisscom.ch:7999/ansible/inventories.git', '/tmp/foobar', GitCmdObjectDB, None)


#r.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd)
#r.clone_from('ssh://git@git.swisscom.ch:7999/ansible/inventories.git', '/tmp/foobar')
