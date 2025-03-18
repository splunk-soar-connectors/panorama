# File: panorama_create_edl.py
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

import phantom.app as phantom
import xmltodict
from phantom.action_result import ActionResult

import panorama_consts as consts
from actions import BaseAction


class CreateEdl(BaseAction):
    def generate_dict_for_xml(self, action_result):
        source = self._param["source"]
        edl_list_type = consts.PAN_EDL_TYPES.get(self._param["list_type"].lower())

        if len(source) > 255:
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_MESSAGE.format(
                    "creating external dynamic list", "Length of source for edl is over the limit, edl source can have 255 characters at max"
                ),
            ), {}

        if edl_list_type not in ["predefined-ip", "predefined-url", "ip", "domain", "url", "imsi", "imei"]:
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_MESSAGE.format(
                    "creating external dynamic list", f"Invalid list type for edl, please enter a valid list type. {consts.PAN_EDL_TYPES_STR}"
                ),
            ), {}

        dict_for_xml = {"type": {edl_list_type: {"url": source}}}

        # edl description
        edl_description = self._param.get("description", "")
        if edl_description:
            if len(edl_description) > 255:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format(
                        "creating external dynamic list",
                        "Length of description for edl is over the limit, edl description can have 255 characters at max",
                    ),
                ), {}

            dict_for_xml["type"][edl_list_type]["description"] = edl_description

        # check if recurring is required
        recurring_dict = {}
        if edl_list_type not in ["predefined-ip", "predefined-url"]:
            certificate_profile = self._param.get("certificate_profile", None)
            if certificate_profile:
                if len(certificate_profile) > 31:
                    return action_result.set_status(
                        phantom.APP_ERROR,
                        consts.PAN_ERROR_MESSAGE.format(
                            "creating external dynamic list",
                            "Length of certificate profile for edl is over the limit, edl description can have 31 characters at max",
                        ),
                    ), {}
                dict_for_xml["type"][edl_list_type]["certificate-profile"] = certificate_profile

            check_for_updates = self._param.get("check_for_updates", "Five-minute")
            check_for_updates = check_for_updates.lower()
            if check_for_updates not in ["five-minute", "hourly", "daily", "weekly", "monthly"]:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format(
                        "creating external dynamic list",
                        f"Invalid check for update value, please enter a check for update value. {consts.PAN_EDL_CHECK_UPDATE_STR}",
                    ),
                ), {}

            if check_for_updates in ["weekly", "monthly", "daily"]:
                hour = self._param.get("hour", "0")

                try:
                    hour = int(hour)
                except Exception:
                    return action_result.set_status(
                        phantom.APP_ERROR,
                        consts.PAN_ERROR_MESSAGE.format(
                            "creating external dynamic list", "Invalid datatype for hour, hour must be integer and in range 00-23"
                        ),
                    ), {}

                if not (0 <= hour <= 23):
                    return action_result.set_status(
                        phantom.APP_ERROR,
                        consts.PAN_ERROR_MESSAGE.format("creating external dynamic list", "Invalid hour, hour must be in range 00-23"),
                    ), {}

                # Formatting time for query
                hour = "%02d" % hour  # noqa: UP031

                if check_for_updates == "weekly":
                    day_of_week = self._param.get("day_of_week", "Sunday").lower()
                    if day_of_week not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                        return action_result.set_status(
                            phantom.APP_ERROR,
                            consts.PAN_ERROR_MESSAGE.format(
                                "creating external dynamic list",
                                f"Invalid day_of_week value, please enter a valid day_of_week value. {consts.PAN_EDL_WEEK_DAY_STR}",
                            ),
                        ), {}

                    recurring_dict[check_for_updates] = {"day-of-week": day_of_week, "at": hour}

                elif check_for_updates == "monthly":
                    day_of_month = self._param.get("day_of_month")

                    if not day_of_month:
                        return action_result.set_status(
                            phantom.APP_ERROR,
                            consts.PAN_ERROR_MESSAGE.format(
                                "creating external dynamic list", "day_of_month is a required key for the selected check update time"
                            ),
                        ), {}

                    try:
                        day_of_month = int(day_of_month)
                    except Exception:
                        return action_result.set_status(
                            phantom.APP_ERROR,
                            consts.PAN_ERROR_MESSAGE.format(
                                "creating external dynamic list",
                                "Invalid datatype for day_of_month, day_of_month must be integer and in range 1-31",
                            ),
                        ), {}
                    if not (1 <= day_of_month <= 31):
                        return action_result.set_status(
                            phantom.APP_ERROR,
                            consts.PAN_ERROR_MESSAGE.format(
                                "creating external dynamic list", "Invalid day_of_month, day_of_month must be in range 1-31"
                            ),
                        ), {}

                    # formatting date of month
                    day_of_month = str(day_of_month)
                    recurring_dict[check_for_updates] = {"day-of-month": day_of_month, "at": hour}
                elif check_for_updates == "daily":
                    recurring_dict[check_for_updates] = {"at": hour}
            else:
                recurring_dict[check_for_updates] = None

        if recurring_dict:
            dict_for_xml["type"][edl_list_type]["recurring"] = recurring_dict

        if edl_list_type == "domain":
            expand_subdomain = self._param.get("expand_for_subdomains", "no").lower()
            if expand_subdomain not in ["yes", "no"]:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format(
                        "creating external dynamic list", "Invalid value for expand subdomain, the value can contain value either yes or no"
                    ),
                ), {}

            if expand_subdomain:
                dict_for_xml["type"][edl_list_type]["expand-domain"] = expand_subdomain

        exception_list = self._param.get("exception_list", "")
        if exception_list:
            exception_list = [x.strip() for x in exception_list.split(",")]
            exception_list = list(filter(None, exception_list))
            if exception_list:
                dict_for_xml["type"][edl_list_type]["exception-list"] = {"member": exception_list}

        return phantom.APP_SUCCESS, dict_for_xml

    def execute(self, connector):
        connector.debug_print("Starting create EDL action")
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        edl_name = self._param["name"]
        device_group = self._param["device_group"]

        # get existing data of edl
        status = connector.util._get_edl_data(self._param, action_result)
        if phantom.is_success(status):
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("Creating external dynamic list", "EDL already exists")
            ), {}

        create_xpath = f"{consts.EDL_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param))}/entry[@name='{edl_name}']"

        xml_status, result_dict = self.generate_dict_for_xml(action_result)

        if phantom.is_fail(xml_status):
            return action_result.get_status()

        # convert dict to xml
        element_xml = xmltodict.unparse(result_dict, short_empty_elements=True)
        element_xml = element_xml.replace('<?xml version="1.0" encoding="utf-8"?>\n', "")

        # if its not shared group
        if device_group.lower() != "shared":
            disable_override = self._param.get("disable_override", "no")
            disable_override = disable_override.lower()
            if disable_override not in ["yes", "no"]:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format(
                        "creating external dynamic list",
                        "Invalid value for expand disable override, the value can contain value either yes or no",
                    ),
                ), {}

            # disable override
            if disable_override:
                override_text = f"<disable-override>{disable_override}</disable-override>"
            element_xml = f"{element_xml}{override_text}"

        data = {"type": "config", "action": "set", "key": connector.util._key, "xpath": create_xpath, "element": element_xml}

        status, response = connector.util._make_rest_call(data, action_result)

        action_result.update_summary({"create_edl": response})
        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("creating external dynamic list", action_result.get_message())
            )

        connector.debug_print("fetching response msg")
        message = action_result.get_message()

        if self._param.get("should_commit_changes", False):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, f"Response Received: {message}")
