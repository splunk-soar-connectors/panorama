# File: panorama_create_address_group.py
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
from panorama_consts import (ADD_GRP_TYPE_VAL_LIST, PAN_ERROR_MESSAGE, PAN_JSON_ADD_GRP_DIS_OVER, PAN_JSON_ADD_GRP_TYPE, PAN_JSON_DEVICE_GRP,
                             param_mapping)


class CreateAddressGroup(BaseAction):

    def make_rest_call_helper(self, connector, xpath, element, action_result, where=None, dst=None):
        data = {
            'type': 'config',
            'action': 'set',
            'key': connector.util._key,
            'xpath': xpath,
            'element': element
        }
        if where and dst:
            data.update({'where': where, 'dst': dst})
        status, response = connector.util._make_rest_call(data, action_result)
        return status, response

    def execute(self, connector):

        connector.debug_print("Inside create address group action.")

        self._param["disable_override"] = self._param.get("disable_override", "none").lower()
        self._param[PAN_JSON_ADD_GRP_TYPE] = self._param.get(PAN_JSON_ADD_GRP_TYPE, "none").lower()
        for param in self._param.copy():
            if param in param_mapping:
                new_key = param_mapping[param]
                self._param[new_key] = self._param[param]
                del self._param[param]

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        device_grp = self._param[PAN_JSON_DEVICE_GRP]
        address_or_match = self._param.get("address_or_match")

        if self._param[PAN_JSON_ADD_GRP_DIS_OVER] not in ["yes", "no", "none"]:
            return action_result.set_status(phantom.APP_ERROR,
                                            "Please enter a valid value for 'disable-override' parameter from ['yes','no']")

        if (device_grp == "shared" and self._param[PAN_JSON_ADD_GRP_DIS_OVER]) or self._param[PAN_JSON_ADD_GRP_DIS_OVER] == "none":
            del self._param[PAN_JSON_ADD_GRP_DIS_OVER]

        if (self._param[PAN_JSON_ADD_GRP_TYPE] and not address_or_match) or (address_or_match and not self._param[PAN_JSON_ADD_GRP_TYPE]):
            return action_result.set_status(phantom.APP_ERROR,
                                            "Parameters 'type' and 'address_or_match' are inter-dependent \
                                                hence please provide input for both or none.")

        if self._param[PAN_JSON_ADD_GRP_TYPE] not in ADD_GRP_TYPE_VAL_LIST and connector.get_action_identifier() != "modify_address_group":
            return action_result.set_status(phantom.APP_ERROR,
                                            "Please enter a valid value for 'type' field as 'static' or 'dynamic'")

        if self._param[PAN_JSON_ADD_GRP_TYPE] == "none":
            del self._param[PAN_JSON_ADD_GRP_TYPE]

        status, add_grp_present = connector.util._does_policy_exist(self._param, action_result, param_name='address_group')
        if add_grp_present and connector.get_action_identifier() != "modify_address_group":
            return action_result.set_status(
                phantom.APP_ERROR,
                "An address group with this name already exists. Please use another name."
            )

        element = connector.util._get_action_element(self._param)
        if self._param.get(PAN_JSON_ADD_GRP_TYPE) == "dynamic":
            status, temp_element = connector.util._element_prep(
                "dynamic", param_val=self._param["address_or_match"], member=False, is_bool=False)
            element += temp_element
        elif self._param.get(PAN_JSON_ADD_GRP_TYPE) == "static":
            status, temp_element = connector.util._element_prep(param_name="static", param_val=self._param.get("address_or_match"), member=True)
            element += temp_element

        xpath = connector.util._get_security_policy_xpath(self._param, action_result, param_name="address_group")[1]

        status, response = self.make_rest_call_helper(connector, xpath, element, action_result)
        action_result.add_data(response)
        message = action_result.get_message()

        if "not a valid" in message and "tag" in message:
            tags = [value.strip() for value in self._param.get("tag", "").split(',') if value.strip()]

            status, response = connector.util._create_tag(connector, action_result, self._param, tags)

            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error occurred while creating the tags."))
            else:
                status, response = self.make_rest_call_helper(connector, xpath, element, action_result)
                action_result.add_data(response)

            message = action_result.get_message()

        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error Occurred: ", {message}))

        if self._param["should_commit_changes"]:
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, f"Successful: {message}")
