# File: panorama_custom_block_policy.py
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
from panorama_consts import (PAN_JSON_APPLICATION, PAN_JSON_CATEGORY, PAN_JSON_DESTINATION_ADDRESS, PAN_JSON_DIR, PAN_JSON_OBJ_TYPE,
                             PAN_JSON_OBJ_VAL, PAN_JSON_POL_SOURCE_ADD, VALUE_LIST_VALIDATION_MESSAGE)


class CustomBlockPolicy(BaseAction):

    def execute(self, connector):

        connector.debug_print("Inside Create custom block policy action")

        temporary_action_result = connector.add_action_result(ActionResult(dict(self._param)))

        self._param[PAN_JSON_DIR] = self._param.get(PAN_JSON_DIR, "both").lower()

        if self._param[PAN_JSON_DIR] not in ["from", "to", "both"]:
            return temporary_action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(["from", "to", "both"],
                                                                                                    PAN_JSON_DIR))

        if self._param[PAN_JSON_OBJ_TYPE] in ['ip', 'address-group', 'edl']:
            if self._param[PAN_JSON_DIR] == "from":
                self._param[PAN_JSON_POL_SOURCE_ADD] = self._param[PAN_JSON_OBJ_VAL]
                self._param[PAN_JSON_DESTINATION_ADDRESS] = "any"

            elif self._param[PAN_JSON_DIR] == "to":
                self._param[PAN_JSON_DESTINATION_ADDRESS] = self._param[PAN_JSON_OBJ_VAL]
                self._param[PAN_JSON_POL_SOURCE_ADD] = "any"

            elif self._param[PAN_JSON_DIR] == "both":
                self._param[PAN_JSON_POL_SOURCE_ADD] = self._param[PAN_JSON_OBJ_VAL]
                self._param[PAN_JSON_DESTINATION_ADDRESS] = self._param[PAN_JSON_OBJ_VAL]

            self._param["application"] = "any"

        elif self._param[PAN_JSON_OBJ_TYPE] == "application":
            self._param[PAN_JSON_APPLICATION] = self._param[PAN_JSON_OBJ_VAL]
            self._param[PAN_JSON_DESTINATION_ADDRESS] = "any"
            self._param[PAN_JSON_POL_SOURCE_ADD] = "any"

        elif self._param[PAN_JSON_OBJ_TYPE] == "url-category":
            self._param[PAN_JSON_CATEGORY] = self._param[PAN_JSON_OBJ_VAL]
            self._param["application"] = "any"
            self._param[PAN_JSON_DESTINATION_ADDRESS] = "any"
            self._param[PAN_JSON_POL_SOURCE_ADD] = "any"

        self._param["service"] = "any"
        self._param["source_zone"] = "any"
        self._param["destination_zone"] = "any"
        self._param["action"] = "drop"

        connector.remove_action_result(temporary_action_result)

        policy_rule_obj = CreatePolicy(self._param)
        response = policy_rule_obj.execute(connector)

        return response
