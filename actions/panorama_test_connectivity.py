# File: panorama_test_connectivity.py
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
import phantom.app as phantom
from phantom.action_result import ActionResult

import panorama_consts as consts
from actions import BaseAction

class TestConnectivityAction(BaseAction):

    def execute(self, connector):

        action_result = connector.add_action_result(ActionResult(dict(self._param)))
        
        #progress
        connector.save_progress(consts.PAN_PROG_USING_BASE_URL.format(base_url=connector.base_url))

        status =  connector.util._generate_token(action_result)

        if phantom.is_fail(status):
            action_result.append_to_message(consts.PAN_ERROR_TEST_CONNECTIVITY_FAILED)
            return action_result.get_status()
        
        connector.save_progress(consts.PAN_SUCCESS_TEST_CONNECTIVITY_PASSED)

        return action_result.set_status(
            phantom.APP_SUCCESS,
            consts.PAN_SUCCESS_TEST_CONNECTIVITY_PASSED
        )


        

        
