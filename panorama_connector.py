# File: panorama_connector.py
#
# Copyright (c) 2016-2025 Splunk Inc.
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

import sys
from importlib import import_module

# Phantom App imports
import phantom.app as phantom
import requests
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

from actions import BaseAction
from panorama_utils import PanoramaUtils


class PanoramaConnector(BaseConnector):
    def __init__(self):
        # Call the BaseConnectors init first
        super().__init__()

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
            self.debug_print("State file is corrupted or missing")
            self.state = {"app_version": self.get_app_json().get("app_version")}

        self.config = self.get_config()
        # Create the util object and use it throughout the action lifecycle
        self.util = PanoramaUtils(self)
        self.base_url = f"https://{self.config[phantom.APP_JSON_DEVICE]}/api/"

        self._dev_sys_key = "device-group"

        if self.config["username"] != self.state.get("username"):
            self.state["username"] = self.config["username"]
            status = self.util._generate_token(self)
            if phantom.is_fail(status):
                self.append_to_message("Unable to generate new token")
                return self.get_status()
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
        # Creating temporary temp_action_result object for validating common params
        temp_action_result = self.add_action_result(ActionResult(dict(param)))
        status = self.util._common_param_check(temp_action_result, param)
        if phantom.is_fail(status):
            return temp_action_result.get_status()
        self.remove_action_result(temp_action_result)

        try:
            for action_class in base_action_sub_classes:
                if action_class.__module__ == action_name:
                    action = action_class(param)
                    return action.execute(self)
        except Exception:
            return phantom.APP_ERROR


if __name__ == "__main__":
    import argparse
    import json

    import pudb

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument("input_test_json", help="Input Test JSON file")
    argparser.add_argument("-u", "--username", help="username", required=False)
    argparser.add_argument("-p", "--password", help="password", required=False)
    argparser.add_argument("-v", "--verify", action="store_true", help="verify", required=False, default=False)
    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password
    verify = args.verify

    if username is not None and password is None:
        # User specified a username but not a password, so ask
        import getpass

        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = PanoramaConnector._get_phantom_base_url() + "/login"

            print("Accessing the Login page")
            r = requests.get(login_url, verify=verify)
            csrftoken = r.cookies["csrftoken"]

            data = dict()
            data["username"] = username
            data["password"] = password
            data["csrfmiddlewaretoken"] = csrftoken

            headers = dict()
            headers["Cookie"] = "csrftoken=" + csrftoken
            headers["Referer"] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=verify, data=data, headers=headers)
            session_id = r2.cookies["sessionid"]
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = PanoramaConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json["user_session_token"] = session_id
            connector._set_csrf_info(csrftoken, headers["Referer"])

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)
