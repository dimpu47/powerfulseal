
# Copyright 2017 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import copy
import subprocess

from ..metriccollectors.stdout_collector import StdoutCollector
from .action_abstract import ActionAbstract



class ActionKubectl(ActionAbstract):

    def __init__(self, name, schema, logger=None, metric_collector=None):
        self.name = name
        self.schema = schema
        self.logger = logger or logging.getLogger(__name__ + "." + name)
        self.metric_collector = metric_collector or StdoutCollector()
        self.kubectl_binary = "kubectl"

    def execute(self):
        return self.execute_kubectl(
            action=self.schema.get("action"),
            payload=self.schema.get("payload"),
        )

    def make_kubectl_command(self, action):
        return "{kubectl} {action} -f -".format(
            kubectl=self.kubectl_binary,
            action=action,
        )

    def execute_kubectl(self, action, payload):
        cmd = self.make_kubectl_command(action)
        self.logger.info("Command: %r", cmd)
        self.logger.info("Payload: %r", payload)
        process = subprocess.run(
            cmd,
            input=payload,
            capture_output=True,
            shell=True,
            text=True,
        )
        if process.stdout:
            self.logger.info(process.stdout)
        if process.stderr:
            self.logger.info(process.stderr)
        self.logger.info("Return code: %d", process.returncode)

        if process.returncode == 0:
            return True
        return False

    def get_cleanup_actions(self):
        actions = []
        if str(self.schema.get("autoDelete", True)).lower() != "false":
            delete_action = copy.deepcopy(self)
            delete_action.schema["autoDelete"] = False
            delete_action.schema["action"] = "delete"
            actions.append(delete_action)
        return actions