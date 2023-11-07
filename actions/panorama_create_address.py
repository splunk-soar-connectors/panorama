# File: panorama_create_address.py
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


class CreateAddress(BaseAction):

    def _generate_xml_string_for_address(self, connector, action_result):
        """Create a tag and add tags into Panorama platform as per tags. Generate the XML string based on given input parameters.

        Args:
            connector: Connector object
            action_result: Action result object

        Returns:
            xml_string: XML string
        """
        xml_tag_string = None
        address_ip_type = self._param["type"].lower()
        address_ip = self._param["value"]

        if address_ip_type not in consts.IP_ADD_TYPE.keys():
            return action_result.set_status(
                phantom.APP_ERROR, f"Invalid ip_type parameter. Please select the valid ip address type FROM {consts.IP_ADD_TYPE.keys()}"
                ), ""

        xml_string = f"<{consts.IP_ADD_TYPE[address_ip_type]}>{address_ip}</{consts.IP_ADD_TYPE[address_ip_type]}>"

        # address tags Add tags into panorama platform
        address_tags = self._param.get("tag", "")
        address_tags = [value.strip() for value in address_tags.split(',') if value.strip()]
        if address_tags:
            tag_status, xml_tag_string = connector.util._create_tag(connector, action_result, self._param, address_tags)
            if phantom.is_fail(tag_status):
                return action_result.get_status(), ""
            if xml_tag_string:
                xml_string += xml_tag_string
        # Address description
        address_description = self._param.get("description")
        if address_description:
            xml_string += f"<description>{address_description}</description>"

        # if its not shared group
        device_group = self._param["device_group"]
        if device_group.lower() != "shared":
            disable_override = self._param.get("disable_override", "no").lower()
            if disable_override not in ["yes", "no"]:
                return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format(
                        "creating address",
                        "Invalid value for expand disable override, the value can contain value either yes or no"
                    )), ""
            xml_string += f"<disable-override>{disable_override}</disable-override>"

        return phantom.APP_SUCCESS, xml_string

    def execute(self, connector):

        connector.debug_print("starting create address action")
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        address_name = self._param["name"]

        # Check the given address already exist or not
        address_present = connector.util._does_address_exist(self._param, action_result)
        if address_present:
            connector.debug_print("Given address already exist...")
            return action_result.set_status(phantom.APP_ERROR, f"{address_name} - address already exist")

        create_xpath = f"{consts.ADDRESS_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param), name=address_name)}"

        xml_status, element_xml = self._generate_xml_string_for_address(connector=connector, action_result=action_result)

        if phantom.is_fail(xml_status):
            return action_result.get_status()

        data = {
            'type': 'config',
            'action': 'set',
            'key': connector.util._key,
            'xpath': create_xpath,
            'element': element_xml
        }

        status, response = connector.util._make_rest_call(data, action_result)

        action_result.update_summary({'create_address': response})
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("create address", action_result.get_message()))

        message = action_result.get_message()

        if self._param.get('should_commit_changes', False):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
