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
from panorama_consts import (ADD_GRP_TYPE_VAL_LIST, ADDRESS_GRP_XPATH, PAN_ERROR_MESSAGE, PAN_JSON_ADD_GRP_DIS_OVER, PAN_JSON_ADD_GRP_TYPE,
                             PAN_JSON_DEVICE_GRP, param_mapping)


class CreateAddressGroup(BaseAction):

    def make_rest_call_helper(self, connector, xpath, element, action_result):
        data = {
            'type': 'config',
            'action': 'set',
            'key': connector.util._key,
            'xpath': xpath,
            'element': element
        }

        status, response = connector.util._make_rest_call(data, action_result)
        return status, response

    def execute(self, connector):

        connector.debug_print("Inside create address group action.")

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        parameter = self._param.copy()

        description = parameter.get("description")

        for param in parameter.copy():
            if param in param_mapping:
                new_key = param_mapping.get(param)
                parameter[new_key] = parameter.get(param)
                del parameter[param]

        if description and len(description) > 1024:
            return action_result.set_status(
                phantom.APP_ERROR, "The length of description is too long. It should not exceed 1024 characters.")

        device_grp = parameter[PAN_JSON_DEVICE_GRP]
        address_or_match = parameter.get("address_or_match")

        if parameter.get(PAN_JSON_ADD_GRP_DIS_OVER):
            if parameter.get(PAN_JSON_ADD_GRP_DIS_OVER).lower() not in ["yes", "no"]:
                return action_result.set_status(phantom.APP_ERROR,
                                                "Please enter a valid value for 'disable-override' parameter from ['yes','no']")
            else:
                parameter[PAN_JSON_ADD_GRP_DIS_OVER] = parameter.get(PAN_JSON_ADD_GRP_DIS_OVER).lower()

        if (device_grp == "shared" and parameter.get(PAN_JSON_ADD_GRP_DIS_OVER)):
            del parameter[PAN_JSON_ADD_GRP_DIS_OVER]

        if parameter.get(PAN_JSON_ADD_GRP_TYPE):
            if parameter.get(PAN_JSON_ADD_GRP_TYPE).lower() not in ADD_GRP_TYPE_VAL_LIST:
                return action_result.set_status(phantom.APP_ERROR,
                                                "Please enter a valid value for 'type' field as 'static' or 'dynamic'")
            else:
                parameter[PAN_JSON_ADD_GRP_TYPE] = parameter.get(PAN_JSON_ADD_GRP_TYPE).lower()

        if (parameter.get(PAN_JSON_ADD_GRP_TYPE) and not address_or_match) or \
                (address_or_match and not parameter.get(PAN_JSON_ADD_GRP_TYPE)):
            return action_result.set_status(phantom.APP_ERROR,
                                            "Parameters 'type' and 'address_or_match' are inter-dependent \
                                            hence please provide input for both or none.")

        add_grp_present_status = connector.util._does_address_group_exist(parameter, action_result)

        if add_grp_present_status and connector.get_action_identifier() != "modify_address_group":
            return action_result.set_status(
                phantom.APP_ERROR,
                "An address group with this name already exists. Please use another name."
            )

        elif not add_grp_present_status and connector.get_action_identifier() == "modify_address_group":
            return action_result.set_status(
                phantom.APP_ERROR,
                "This address group is not present. Please enter a valid address group name."
            )
        element = connector.util._get_action_element(parameter)

        if parameter.get(PAN_JSON_ADD_GRP_TYPE):
            if parameter.get(PAN_JSON_ADD_GRP_TYPE).lower() == "dynamic":
                status, temp_element = connector.util._element_prep(
                    param_name="dynamic", param_val=parameter["address_or_match"], member=False)
                element += temp_element
            if parameter.get(PAN_JSON_ADD_GRP_TYPE).lower() == "static":
                status, temp_element = connector.util._element_prep(
                    param_name="static", param_val=parameter.get("address_or_match"), member=True)
                element += temp_element

        xpath = f"{ADDRESS_GRP_XPATH.format(config_xpath= connector.util._get_config_xpath(param), name=parameter['name'])}"
        status, _ = self.make_rest_call_helper(connector, xpath, element, action_result)
        message = action_result.get_message()

        if ("tag" and "not a valid") in message:
            tags = [value.strip() for value in parameter.get("tag", "").split(',') if value.strip(" ")]
            status, _ = connector.util._create_tag(connector, action_result, parameter, tags)

            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error occurred while creating the tags."))
            else:
                status, _ = self.make_rest_call_helper(connector, xpath, element, action_result)
            message = action_result.get_message()

        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("creating address group: ", {message}))

        if parameter["should_commit_changes"]:
            status = connector.util._commit_and_commit_all(parameter, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, f"Response Received: {message}")
