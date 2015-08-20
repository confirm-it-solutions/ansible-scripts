#!/usr/bin/env python
#
# Dynamic inventory script for ansible, to create dynamic groups based on a
# hosts tier and location. The hosts are defined in a YAML file inside the
# projects repository.
#
# The MIT License (MIT)
#
# Copyright (c) 2015 confirm IT solutions
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import sys
import yaml
import json
import re

# Get environment variables.
try:
    project   = os.environ['PROJECT'].replace('-', '_')
    inventory = os.environ['INVENTORY']
except KeyError:
    sys.stderr.write(
        'ERROR: Environment variable PROJECT and/or INVENTORY not set!\n')
    sys.stderr.flush()
    sys.exit(1)

# Get path to project and inventory dir.
project_dir   = '/var/lib/awx/projects'
inventory_dir = None
for d in os.listdir(project_dir):
    if re.search('_\d+__{0}$'.format(project), d):
        inventory_dir  = os.path.join(project_dir, d, 'inventories')

# Check if we've a inventory dir.
if inventory_dir is None:
    sys.stderr.write('ERROR: Inventory dir not found!\n')
    sys.stderr.flush()
    sys.exit(1)

# Get path for inventory file.
inventory_file = os.path.join(inventory_dir, '{0}.yml'.format(inventory))

# Read inventory file.
with open(inventory_file, 'r') as stream:
    # Parse YAML.
    data = yaml.load(stream)

    # Prepare result dict.
    result = {
        '_meta': {
            'hostvars': {}
        },
        inventory: {
            'children': []
        }
    }

    # Loop through inventory YAML and build result yaml.
    for tier, group in data.iteritems():

        # Build group name for inv-tier.
        inv_tier = '{0}-{1}'.format(inventory, tier)

        # Create empty tier & inv-tier groups.
        result[tier] = {
            'children': []
        }
        result[inv_tier] = {
            'children': [tier]
        }

        # Add tier to inv group.
        result[inventory]['children'].append(tier)

        for loc, hosts in group.iteritems():

            # Build group names for tier-loc, inv-loc and inv-tier-loc.
            tier_loc     = '{0}-{1}'.format(tier, loc)
            inv_loc      = '{0}-{1}'.format(inventory, loc)
            inv_tier_loc = '{0}-{1}'.format(inventory, tier_loc)

            # Add tier-loc to tier group.
            result[tier]['children'].append(tier_loc)

            # Add tier-loc to inv-loc group.
            if inv_loc not in result:
                result[inv_loc] = {
                    'children': []
                }
            result[inv_loc]['children'].append(tier_loc)

            # Add inv-loc to loc group.
            if loc not in result:
                result[loc] = {
                    'children': [inv_loc]
                }
            elif inv_loc not in result[loc]['children']:
                result[loc]['children'].append(inv_loc)

            # Create tier-loc and inv-tier-loc groups.
            result[tier_loc] = {
                'hosts': hosts
            }
            result[inv_tier_loc] = {
                'children': [tier_loc]
            }

    print json.dumps(result)
