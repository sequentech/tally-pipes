import os
import json
import tempfile
import shutil
from agora_results.utils.deterministic_tar import deterministic_tar_open, deterministic_tar_add


def tar_tallies(data, config, tar, destdir):
    eid = int(os.path.dirname(tar).split("/")[-1])
    results_config = json.dumps(config)
    results = json.dumps(data['results'], indent=4, ensure_ascii=False, sort_keys=True, separators=(',', ': '))

    tempdir = tempfile.mkdtemp()
    results_path = os.path.join(tempdir, "%d.results.json" % eid)
    config_path = os.path.join(tempdir, "%d.config.results.json" % eid)

    with open(results_path, 'w') as f:
        f.write(results)
        f.write('\n')
    with open(config_path, 'w') as f:
        f.write(results_config)

    paths = [results_path, config_path, tar]
    arc_names = ["results.json", "config.json", "%d.tar.gz" % eid]

    # create tar
    tar_path = os.path.join(destdir, "%d.tar" % eid)
    tar = deterministic_tar_open(tar_path, "w")

    for path, arc_name in zip(paths, arc_names):
        deterministic_tar_add(tar, path, arc_name)
    tar.close()

    shutil.rmtree(tempdir)
