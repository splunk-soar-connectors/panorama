# File: panorama_connector.py
#
# Copyright (c) 2016-2023 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
#
#
# Phantom imports
import sys
from importlib import import_module

import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

import panorama_consts as consts
from actions import BaseAction
from panorama_utils import PanoramaUtils


class PanoramaConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(PanoramaConnector, self).__init__()

        self.config = None
        self.state = None
        self.util = None
        self.is_state_updated = False
        self.base_url = None
        self.key = None

    def initialize(self):

        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self.state = self.load_state()
        if not self.state or not isinstance(self.state, dict):
            self.debug_print(consts.VISION_ERROR_STATE_FILE_CORRUPT)
            self.state = {"app_version": self.get_app_json().get("app_version")}

        self.config = self.get_config()

        self.base_url = "https://{}/api/".format(self.config[phantom.APP_JSON_DEVICE])

        self._dev_sys_key = "device-group"
        # Create the util object and use it throughout the action lifecycle
        self.util = PanoramaUtils(self)
        return phantom.APP_SUCCESS

    def finalize(self):
        if self.is_state_updated:
            # Encrypt and Save the state, this data is saved across actions and app upgrades
            self.state = self.util.encrypt_state(self.state)
            self.save_state(self.state)
        return phantom.APP_SUCCESS

    def handle_action(self, param):

        action_id = self.get_action_identifier()
        self.debug_print("action_id", self.get_action_identifier())

        action_name = f"actions.panorama_{action_id}"
        import_module(action_name, package="actions")

        base_action_sub_classes = BaseAction.__subclasses__()
        self.debug_print(f"Finding action module: {action_name}")

        # Checking common parameters
        action_result = self.add_action_result(ActionResult(dict(param)))
        status = self.util._common_param_check(action_result, param)
        if phantom.is_fail(status):
            return action_result.get_status()

        try:
            action = base_action_sub_classes[0](param)
            return action.execute(self)
        except:
            return phantom.APP_ERROR


if __name__ == '__main__':

    import json

    import pudb

    pudb.set_trace()

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)

        connector = PanoramaConnector()
        connector.print_progress_message = True
        result = connector._handle_action(json.dumps(in_json), None)

    sys.exit(0)
