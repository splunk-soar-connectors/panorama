# File: panorama_create_edl.py
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

import xmltodict
import panorama_consts as consts
from actions import BaseAction


class CreateEdl(BaseAction):

    def generate_xml_string_for_edl(self):

        source =  self._param["source"]
        edl_list_type = consts.PAN_EDL_TYPES.get(self._param["list_type"])

        dict_for_xml = {
            "type" : {
                edl_list_type : {
                    "url" : source
                }
            }
        }

        # edl description
        edl_description = self._param.get("description","")
        if edl_description:
            dict_for_xml["type"][edl_list_type]["description"] = edl_description


        # check if recurring is required
        recurring_dict = {}
        if edl_list_type not in ["predefined-ip","predefined-url"]:
            
            check_for_updates =  self._param.get("check_for_updates", "")
            
            if not check_for_updates:
                self._action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format(
                    "creating external dynamic list", 
                    "check_for_updates is a required key for the selected edl type"
                ))
                return phantom.APP_ERROR , {}
            
            if check_for_updates not in ["five-minute", "hourly"]:

                at_hour = self._param.get("at_hour")

                if not at_hour:
                    self._action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format(
                        "creating external dynamic list", 
                        "at_hour is a required key for the selected check update time"
                    ))
                    return phantom.APP_ERROR , {}
            
                if not (at_hour > 0 and at_hour < 24):
                    self._action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format(
                        "creating external dynamic list", 
                        "Invalid hour, hour must be in range 00-24"
                    ))
                    return phantom.APP_ERROR , {}
                
                # Formatting time for query
                at_hour = "%02d" % at_hour

                if check_for_updates == "weekly":
                    day_of_week = self._param.get("day", "")

                    if not day_of_week:
                        self._action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format(
                            "creating external dynamic list", 
                            "day_of_week is a required key for the selected check update time"
                        ))
                        return phantom.APP_ERROR , {}

                    recurring_dict[check_for_updates] = {
                        "day-of-week" : day_of_week,
                        "at" : at_hour
                    }
                    
                elif check_for_updates == "monthly":
                    date_of_month = self._param.get("date_of_month", "")

                    if not date_of_month:
                        self._action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format(
                            "creating external dynamic list", 
                            "date_of_month is a required key for the selected check update time"
                        ))
                        return phantom.APP_ERROR , {}
                    
                    if not (date_of_month > 1 and date_of_month < 31) :
                        self._action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format(
                            "creating external dynamic list", 
                            "Invalid date, date must be in range 1-31"
                        ))
                        return phantom.APP_ERROR , {}
                    
                    # formatting date of month
                    date_of_month = "%02d" % date_of_month

                    recurring_dict[check_for_updates] = {
                        "day-of-month" : date_of_month,
                        "at" : at_hour
                    }
                elif check_for_updates == "daily":
                    recurring_dict[check_for_updates] = {
                        "at" :  at_hour
                    }
            else:
                recurring_dict[check_for_updates] = None
        
        if recurring_dict:
            dict_for_xml["type"][edl_list_type]["recurring"] = recurring_dict
        
        if edl_list_type == "domain":
            expand_subdomain = self._param.get("expand_for_subdomains", False)
            if expand_subdomain:
                dict_for_xml["type"][edl_list_type]["expand-domain"] = "yes"

        
        certificate_profile = self._param.get("certificate_profile", None)
        if certificate_profile:
            dict_for_xml["type"][edl_list_type]["certificate-profile"] = certificate_profile
        
        exception_list = self._param.get("exception_list","")
        if exception_list:
            exception_list = exception_list.split(",")
            dict_for_xml["type"][edl_list_type]["exception-list"] = {
                "member" : exception_list
            }
            
        return phantom.APP_SUCCESS, dict_for_xml
            

    def execute(self):
        self._connector.debug_print("starting create EDL action")

        edl_name =  self._param["name"]

        create_xpath = f"{consts.EDL_XPATH.format(config_xpath=self._connector.util._get_config_xpath(self._param))}/entry[@name='{edl_name}']"

        xml_status, result_dict =  self.generate_xml_string_for_edl()

        if phantom.is_fail(xml_status):
            return self._action_result.get_status()
        
        # convert dict to xml
        element_xml = xmltodict.unparse(result_dict, short_empty_elements=True)
        element_xml =element_xml.replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n","")


        # if its not shared group
        device_group =  self._param["device_group"]
        if device_group != "shared":
            disable_override = self._param.get("disable_override")
        
            #disable override 
            override = "yes" if disable_override else "no"
            override_text = f"<disable-override>{override}</disable-override>"
            element_xml =  f"{element_xml}{override_text}"

        data = {
            'type': 'config',
            'action': 'set',
            'key': self._connector.util._key,
            'xpath': create_xpath,
            'element': element_xml
        }

        status, response  =  self._connector.util._make_rest_call(data, self._action_result)

        self._action_result.update_summary({'create_edl': response})
        if phantom.is_fail(status):
            return self._action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("create edl", self._action_result.get_message()))
        
        message = self._action_result.get_message()

        if self._param.get('should_commit_changes', True):
            status = self._connector.util._commit_and_commit_all(self._param, self._action_result)
            if phantom.is_fail(status):
                return self._action_result.get_status()

        return self._action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
