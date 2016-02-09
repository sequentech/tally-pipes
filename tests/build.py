# -*- coding: utf-8 -*-

import os
from pybuilder.core import use_plugin, init, task, depends

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.distutils")


name = "agora-results-tests"
default_task = "run_unit_tests"


@init
def set_properties(project):
    pass

@task
def update_agora_results():
	# Instala la última versión disponible de Agora Results
	os.system('pip install git+https://github.com/garridev/agora-results.git@next -U')

