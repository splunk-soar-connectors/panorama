# File: panorama_modify_edl.py
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

import json

import phantom.app as phantom
import xmltodict
from phantom.action_result import ActionResult

import panorama_consts as consts
from actions import BaseAction


class ModifyEdl(BaseAction):
    def _generate_xml_string_for_edl(self, connector, action_result):
        # get all the elements data
        edl_name = self._param["name"]

        # optional parameters data
        source = self._param.get("source")
        edl_list_type = self._param.get("list_type")
        edl_description = self._param.get("description")
        hour = self._param.get("hour")
        day_of_month = self._param.get("day_of_month")
        certificate_profile = self._param.get("certificate_profile")
        exception_list = self._param.get("exception_list")

        check_for_updates = self._param.get("check_for_updates")
        check_for_updates = check_for_updates.lower() if check_for_updates else None

        day_of_week = self._param.get("day_of_week")
        day_of_week = day_of_week.lower() if day_of_week else None

        expand_subdomain = self._param.get("expand_for_subdomains")
        expand_subdomain = expand_subdomain.lower() if expand_subdomain else None

        disable_override = self._param.get("disable_override")
        disable_override = disable_override.lower() if disable_override else None

        param_data_list = [
            source,
            edl_list_type,
            edl_description,
            check_for_updates,
            hour,
            day_of_week,
            day_of_month,
            expand_subdomain,
            certificate_profile,
            exception_list,
            disable_override,
        ]

        # check if there is no update in the values
        if all(item is None for item in param_data_list):
            return action_result.set_status(phantom.APP_ERROR, "No values to update, please provide valid values to be updated"), ""

        # get existing data of edl
        status = connector.util._get_edl_data(self._param, action_result)

        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("modifying external dynamic list", action_result.get_message())
            ), ""

        existing_data = action_result.get_data()
        existing_data = existing_data.pop()

        try:
            existing_data = json.dumps(existing_data)
            existing_data = json.loads(existing_data)
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_MESSAGE.format("modifying external dynamic list", connector.util._get_error_message_from_exception(e)),
            ), ""

        if existing_data["@total-count"] == "0":
            return action_result.set_status(phantom.APP_ERROR, "EDL object doesn't exist"), ""

        existing_data = existing_data.get("entry")

        data_type_set = {"predefined-ip", "predefined-url", "ip", "domain", "url", "imsi", "imei"}
        old_edl_list_type = next((data for data in existing_data["type"] if data in data_type_set), None)

        # fetch edl type if updated
        if edl_list_type:
            edl_list_type = consts.PAN_EDL_TYPES.get(edl_list_type.lower())
            if edl_list_type not in ["predefined-ip", "predefined-url", "ip", "domain", "url", "imsi", "imei"]:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format(
                        "modifying external dynamic list",
                        f"Invalid list type for edl, please enter a valid list type. {consts.PAN_EDL_TYPES_STR}",
                    ),
                ), ""
        elif old_edl_list_type:
            edl_list_type = old_edl_list_type

        # fetch source if updated
        if source:
            if len(source) > 255:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format(
                        "modifying external dynamic list",
                        "Length of source for edl is over the limit, edl source can have 255 characters at max",
                    ),
                ), ""
        else:
            source = existing_data["type"][old_edl_list_type]["url"]
            if isinstance(source, dict):
                source = source["#text"]

        dict_for_xml = {"entry": {"@name": edl_name, "type": {edl_list_type: {"url": source}}}}

        # edl description
        if edl_description:
            if len(edl_description) > 255:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format(
                        "modifying external dynamic list",
                        "Length of description for edl is over the limit, edl description can have 255 characters at max",
                    ),
                ), ""
            dict_for_xml["entry"]["type"][edl_list_type]["description"] = edl_description
        else:
            old_description = existing_data["type"][old_edl_list_type].get("description")
            if old_description:
                if isinstance(old_description, dict):
                    old_description = old_description.get("#text")

                dict_for_xml["entry"]["type"][edl_list_type]["description"] = old_description

        # check if recurring is required
        recurring_dict = {}
        if edl_list_type not in ["predefined-ip", "predefined-url"]:
            if certificate_profile:
                if len(certificate_profile) > 31:
                    return action_result.set_status(
                        phantom.APP_ERROR,
                        consts.PAN_ERROR_MESSAGE.format(
                            "modifying external dynamic list",
                            "Length of certificate profile for edl is over the limit, edl description can have 31 characters at max",
                        ),
                    ), ""
                dict_for_xml["entry"]["type"][edl_list_type]["certificate-profile"] = certificate_profile
            else:
                certificate_profile = existing_data["type"][old_edl_list_type].get("certificate-profile")

                if isinstance(certificate_profile, dict):
                    certificate_profile = certificate_profile.get("#text")
                if certificate_profile:
                    dict_for_xml["entry"]["type"][edl_list_type]["certificate-profile"] = certificate_profile

            valid_cfu_values = {"five-minute", "hourly", "weekly", "monthly", "daily"}
            old_check_for_updates = ""
            old_hour = None
            old_day_of_week = None
            old_day_of_month = None
            if old_edl_list_type not in ["predefined-ip", "predefined-url"]:
                for key in existing_data["type"][old_edl_list_type]["recurring"].keys():
                    if key in valid_cfu_values:
                        old_check_for_updates = key
                        break

                # fetch data for recurring params
                if old_check_for_updates in ["weekly", "monthly", "daily"]:
                    # fetch hour data from existing data
                    old_hour = existing_data["type"][old_edl_list_type]["recurring"][old_check_for_updates].get("at")

                    if old_check_for_updates == "weekly":
                        # fetch day_of_week data from existing data
                        old_day_of_week = existing_data["type"][old_edl_list_type]["recurring"][old_check_for_updates].get("day-of-week")

                    elif old_check_for_updates == "monthly":
                        # fetch day_of_week data from existing data
                        old_day_of_month = existing_data["type"][old_edl_list_type]["recurring"][old_check_for_updates].get("day-of-month")

            # if user has not provided value for check_for_updates
            if not check_for_updates:
                if not old_check_for_updates:
                    return action_result.set_status(
                        phantom.APP_ERROR,
                        consts.PAN_ERROR_MESSAGE.format(
                            "modifying external dynamic list", "check_for_updates is a required key for the selected edl type"
                        ),
                    ), ""
                check_for_updates = old_check_for_updates

            if check_for_updates not in ["five-minute", "hourly", "daily", "weekly", "monthly"]:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format(
                        "modifying external dynamic list",
                        f"Invalid check for update value, please enter a check for update value. {consts.PAN_EDL_CHECK_UPDATE_STR}",
                    ),
                ), ""
            if check_for_updates in ["weekly", "monthly", "daily"]:
                if not hour:
                    if not old_hour:
                        return action_result.set_status(
                            phantom.APP_ERROR,
                            consts.PAN_ERROR_MESSAGE.format(
                                "modifying external dynamic list", "hour is a required key for the selected check update time"
                            ),
                        ), ""
                    hour = old_hour
                    if isinstance(hour, dict):
                        hour = hour.get("#text")

                try:
                    hour = int(hour)
                except Exception:
                    return action_result.set_status(
                        phantom.APP_ERROR,
                        consts.PAN_ERROR_MESSAGE.format(
                            "modifying external dynamic list", "Invalid datatype for hour, hour must be integer and in range 00-23"
                        ),
                    ), ""

                if not (0 <= hour <= 23):
                    return action_result.set_status(
                        phantom.APP_ERROR,
                        consts.PAN_ERROR_MESSAGE.format("modifying external dynamic list", "Invalid hour, hour must be in range 00-23"),
                    ), ""

                # Formatting time for query
                hour = "%02d" % hour  # noqa: UP031

                if check_for_updates == "weekly":
                    # check if date_of_week is provided or not
                    if not day_of_week:
                        if not old_day_of_week:
                            return action_result.set_status(
                                phantom.APP_ERROR,
                                consts.PAN_ERROR_MESSAGE.format(
                                    "modifying external dynamic list", "day_of_week is a required key for the selected check update time"
                                ),
                            ), ""
                        day_of_week = old_day_of_week
                        if isinstance(day_of_week, dict):
                            day_of_week = day_of_week.get("#text")

                    if day_of_week not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                        return action_result.set_status(
                            phantom.APP_ERROR,
                            consts.PAN_ERROR_MESSAGE.format(
                                "modifying external dynamic list",
                                f"Invalid day_of_week value, please enter a valid day_of_week value. {consts.PAN_EDL_WEEK_DAY_STR}",
                            ),
                        ), ""

                    recurring_dict[check_for_updates] = {"day-of-week": day_of_week, "at": hour}

                elif check_for_updates == "monthly":
                    # check if day_of_month is provided or not
                    if not day_of_month:
                        if not old_day_of_month:
                            return action_result.set_status(
                                phantom.APP_ERROR,
                                consts.PAN_ERROR_MESSAGE.format(
                                    "modifying external dynamic list", "day_of_month is a required key for the selected check update time"
                                ),
                            ), ""
                        day_of_month = old_day_of_month
                        if isinstance(day_of_month, dict):
                            day_of_month = day_of_month.get("#text")
                    try:
                        day_of_month = int(day_of_month)
                    except Exception:
                        return action_result.set_status(
                            phantom.APP_ERROR,
                            consts.PAN_ERROR_MESSAGE.format(
                                "modifying external dynamic list",
                                "Invalid datatype for day_of_month, day_of_month must be integer and in range 1-31",
                            ),
                        ), ""

                    if not (1 <= day_of_month <= 31):
                        return action_result.set_status(
                            phantom.APP_ERROR,
                            consts.PAN_ERROR_MESSAGE.format(
                                "modifying external dynamic list", "Invalid day_of_month, day_of_month must be in range 1-31"
                            ),
                        ), ""

                    # formatting date of month
                    day_of_month = str(day_of_month)

                    recurring_dict[check_for_updates] = {"day-of-month": day_of_month, "at": hour}

                elif check_for_updates == "daily":
                    recurring_dict[check_for_updates] = {"at": hour}
            else:
                recurring_dict[check_for_updates] = None

        if recurring_dict:
            dict_for_xml["entry"]["type"][edl_list_type]["recurring"] = recurring_dict

        if edl_list_type == "domain":
            if expand_subdomain not in ["yes", "no", None]:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format(
                        "modifying external dynamic list", "Invalid value for expand subdomain, the value can contain value either yes or no"
                    ),
                ), ""

            if expand_subdomain:
                dict_for_xml["entry"]["type"][edl_list_type]["expand-domain"] = expand_subdomain
            else:
                expand_subdomain = existing_data["type"][old_edl_list_type].get("expand-domain")

                if isinstance(expand_subdomain, dict):
                    expand_subdomain = expand_subdomain.get("#text")
                if expand_subdomain:
                    dict_for_xml["entry"]["type"][edl_list_type]["expand-domain"] = expand_subdomain

        if exception_list:
            exception_list = [x.strip() for x in exception_list.split(",")]
            exception_list = list(filter(None, exception_list))
            if exception_list:
                dict_for_xml["entry"]["type"][edl_list_type]["exception-list"] = {"member": exception_list}
        else:
            exception_list = existing_data["type"][old_edl_list_type].get("exception-list", {}).get("member")

            if exception_list:
                list_data = []
                if isinstance(exception_list, list):
                    for data in exception_list:
                        if isinstance(data, dict):
                            list_data.append(data.get("#text"))
                        else:
                            list_data.append(data)
                elif isinstance(exception_list, dict):
                    list_data.append(exception_list.get("#text"))

                dict_for_xml["entry"]["type"][edl_list_type]["exception-list"] = {"member": list_data}

        # if its not shared group
        device_group = self._param["device_group"]
        if device_group.lower() != "shared":
            if disable_override not in ["yes", "no", None]:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_MESSAGE.format(
                        "modifying external dynamic list", "Invalid value for disable override, the value can contain value either yes or no"
                    ),
                ), ""

            if disable_override:
                dict_for_xml["entry"]["disable-override"] = disable_override
            else:
                disable_override = existing_data.get("disable-override")

                if isinstance(disable_override, dict):
                    disable_override = disable_override.get("#text")
                if disable_override:
                    dict_for_xml["entry"]["disable-override"] = disable_override

        # convert dict to xml
        element_xml = xmltodict.unparse(dict_for_xml, short_empty_elements=True)
        element_xml = element_xml.replace('<?xml version="1.0" encoding="utf-8"?>\n', "")

        return phantom.APP_SUCCESS, element_xml

    def execute(self, connector):
        connector.debug_print("starting modify edl action")

        # create an action_result object
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        connector.debug_print("Starting modify edl action")

        edl_name = self._param["name"]

        xml_status, element_xml_string = self._generate_xml_string_for_edl(connector, action_result)
        if phantom.is_fail(xml_status):
            return action_result.get_status()

        create_xpath = f"{consts.EDL_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param))}/entry[@name='{edl_name}']"

        data = {"type": "config", "action": "edit", "key": connector.util._key, "xpath": create_xpath, "element": element_xml_string}

        status, response = connector.util._make_rest_call(data, action_result)

        action_result.update_summary({"modify_edl": response})
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("modify edl", action_result.get_message()))

        connector.debug_print("fetching response msg")
        message = action_result.get_message()

        if self._param.get("should_commit_changes", False):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, f"Response Received: {message}")
