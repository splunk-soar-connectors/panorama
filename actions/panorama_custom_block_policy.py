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
from panorama_consts import (OBJ_TYPE_VALUE_LIST, PAN_JSON_APPLICATION, PAN_JSON_CATEGORY, PAN_JSON_DESTINATION_ADDRESS, PAN_JSON_DIR,
                             PAN_JSON_OBJ_TYPE, PAN_JSON_OBJ_VAL, PAN_JSON_POL_SOURCE_ADD, VALUE_LIST_VALIDATION_MESSAGE)


class CustomBlockPolicy(BaseAction):

    def execute(self, connector):

        connector.debug_print("Inside Create custom block policy action")

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        parameter = self._param.copy()

        parameter[PAN_JSON_DIR] = parameter.get(PAN_JSON_DIR, "both").lower()
        parameter[PAN_JSON_OBJ_TYPE] = parameter[PAN_JSON_OBJ_TYPE].lower()

        if parameter[PAN_JSON_DIR] not in ["from", "to", "both"]:
            return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(["from", "to", "both"],
                                                                                                    PAN_JSON_DIR))

        if parameter.get(PAN_JSON_OBJ_TYPE):
            if parameter.get(PAN_JSON_OBJ_TYPE).lower() not in OBJ_TYPE_VALUE_LIST:
                return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(OBJ_TYPE_VALUE_LIST, PAN_JSON_OBJ_TYPE))
            else:
                parameter[PAN_JSON_OBJ_TYPE] = parameter.get(PAN_JSON_OBJ_TYPE).lower()

        if parameter[PAN_JSON_OBJ_TYPE] in ['ip', 'address-group', 'edl']:
            if parameter[PAN_JSON_DIR] == "from":
                parameter[PAN_JSON_POL_SOURCE_ADD] = parameter[PAN_JSON_OBJ_VAL]
                parameter[PAN_JSON_DESTINATION_ADDRESS] = "any"

            elif parameter[PAN_JSON_DIR] == "to":
                parameter[PAN_JSON_DESTINATION_ADDRESS] = parameter[PAN_JSON_OBJ_VAL]
                parameter[PAN_JSON_POL_SOURCE_ADD] = "any"

            elif parameter[PAN_JSON_DIR] == "both":
                parameter[PAN_JSON_POL_SOURCE_ADD] = parameter[PAN_JSON_OBJ_VAL]
                parameter[PAN_JSON_DESTINATION_ADDRESS] = parameter[PAN_JSON_OBJ_VAL]

            parameter["application"] = "any"

        elif parameter[PAN_JSON_OBJ_TYPE] == "application":
            parameter[PAN_JSON_APPLICATION] = parameter[PAN_JSON_OBJ_VAL]
            parameter[PAN_JSON_DESTINATION_ADDRESS] = "any"
            parameter[PAN_JSON_POL_SOURCE_ADD] = "any"

        elif parameter[PAN_JSON_OBJ_TYPE] == "url-category":
            parameter[PAN_JSON_CATEGORY] = parameter[PAN_JSON_OBJ_VAL]
            parameter["application"] = "any"
            parameter[PAN_JSON_DESTINATION_ADDRESS] = "any"
            parameter[PAN_JSON_POL_SOURCE_ADD] = "any"

        parameter["service"] = "any"
        parameter["source_zone"] = "any"
        parameter["destination_zone"] = "any"
        parameter["action"] = "drop"

        obj = CreatePolicy(parameter)
        response = obj.execute(connector, action_result=action_result)

        return response
