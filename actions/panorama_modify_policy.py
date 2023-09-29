# File: panorama_modify_policy.py
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

from actions import BaseAction
from actions.panorama_create_policy import CreatePolicy
from panorama_consts import PAN_JSON_DISABLE, PAN_JSON_ICMP_UNREACHABLE


class ModifyPolicy(BaseAction):

    def execute(self, connector):

        connector.debug_print("Inside Modify policy action")

        temporary_action_result = connector.add_action_result(ActionResult(dict(self._param)))

        self._param[PAN_JSON_ICMP_UNREACHABLE] = self._param.get(PAN_JSON_ICMP_UNREACHABLE, "none").lower()
        self._param[PAN_JSON_DISABLE] = self._param.get(PAN_JSON_DISABLE, "none").lower()

        if self._param[PAN_JSON_ICMP_UNREACHABLE] not in ["none", "true", "false"]:
            return temporary_action_result.set_status(
                phantom.APP_ERROR,
                "Please enter a valid value for 'icmp unreachable' from [,none','true','false']"
            )
        elif self._param[PAN_JSON_ICMP_UNREACHABLE] == "none":
            del self._param[PAN_JSON_ICMP_UNREACHABLE]

        if self._param[PAN_JSON_DISABLE] not in ["none", "true", "false"]:
            return temporary_action_result.set_status(
                phantom.APP_ERROR,
                "Please enter a valid value for 'disable' from ['none','true','false']"
            )
        elif self._param[PAN_JSON_DISABLE] == "none":
            del self._param[PAN_JSON_DISABLE]

        connector.remove_action_result(temporary_action_result)

        policy_rule_obj = CreatePolicy(self._param)
        response = policy_rule_obj.execute(connector)

        return response
