# This file is part of tally-pipes.
# Copyright (C) 2014-2022  Sequent Tech Inc <legal@sequentech.io>

# tally-pipes is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# tally-pipes  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with tally-pipes.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import tempfile
import shutil
from tally_pipes.utils.deterministic_tar import deterministic_tar_open, deterministic_tar_add


def tar_tallies(
    data_list,
    config,
    tar_list,
    destdir,
    election_id,
    segmented_election_config_path=None
):
    results_config = json.dumps(config)
    results = json.dumps(
        data_list[0]['results'],
        indent=4, 
        ensure_ascii=False, 
        sort_keys=True, 
        separators=(',', ': ')
    )

    tempdir = tempfile.mkdtemp()
    results_path = os.path.join(tempdir, "%d.results.json" % election_id)
    config_path = os.path.join(tempdir, "%d.config.results.json" % election_id)

    with open(results_path, 'w') as f:
        f.write(results)
        f.write('\n')
    with open(config_path, 'w') as f:
        f.write(results_config)

    extra_paths = []
    extra_arc_names = []
    if segmented_election_config_path is not None:
        segmented_election_config = open(segmented_election_config_path).read()
        temp_segmented_election_config_path = os.path.join(
            tempdir,
            "segmented_election_config.json"
        )
        extra_paths += [temp_segmented_election_config_path]
        extra_arc_names += ["segmented_election_config.json"]
        with open(temp_segmented_election_config_path, 'w') as file:
            file.write(segmented_election_config)

    paths = [results_path, config_path] + extra_paths + tar_list
    arc_names = ["results.json", "config.json"] + extra_arc_names + [
      "%d.tar.gz" % int(os.path.dirname(tar2).split("/")[-1])
      for tar2 in tar_list
    ]

    # create tar
    tar_path = os.path.join(destdir, "%d.tar" % election_id)
    tar = deterministic_tar_open(tar_path, "w")

    for path, arc_name in zip(paths, arc_names):
        deterministic_tar_add(tar, path, arc_name)
    tar.close()

    shutil.rmtree(tempdir)
