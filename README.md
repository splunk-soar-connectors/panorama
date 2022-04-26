[comment]: # "Auto-generated SOAR connector documentation"
# Panorama

Publisher: Splunk  
Connector Version: 3\.3\.0  
Product Vendor: Palo Alto Networks  
Product Name: Panorama  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.2\.0  

This app integrates with the Palo Alto Networks Panorama product to support several containment and investigative actions

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2016-2022 Splunk Inc."
[comment]: # ""
[comment]: # "  Licensed under Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0.txt)"
[comment]: # ""
### Overview

The Panorama app has been tested with PanOS version 7.0.4 and should work with any version above.

All the containment actions (like **block ip** etc.), take a policy name and the policy type as
parameters. The action first creates an object (Application Group, Address Group, etc.) on the
Panorama device to represent the object being blocked. This object is then added to the specified
policy. It does not modify any other policy parameters including the **Action** . Therefore you must
pre-configure the policy action as **Drop** .

Most of the actions execute a commit on the panorama device followed by a commit on the device
group. This second commit results in Panorama sending the commit to each device that belongs to a
device group, which could take some time. It is a good idea to add a time interval between two
panorama actions when executing a playbook

Panorama restricts object names to 31 characters. This could result in object names that are created
by Phantom being truncated in some cases.

It is usually a good idea to have one Policy created on the Panorama device to handle the **block**
of each type of object. The panorama_app playbook that is available on the community github repo
assumes this type of configuration. Note that to block URLs on Panorama, they are included in a URL
Filtering profile that is usually added to an **Allow** policy. Please see the PanOS documentation
for more details.

### Commit Configuration

You can use the commit API request to commit a candidate configuration to a firewall. Commit actions
are called at the end of all Contain actions (e.g. BlockIP).

Contain and Correct actions can be run in parallel by making use of (1) the flag
**should_commit_changes** and (2) the action **commit changes** . To run Contain or Correct actions
in parallel, the actions should have **should_commit_changes** as False. Once all Contain and
Correct actions with disabled **should_commit_changes** are completed, the action **commit changes**
should be run. This ensures there won't be any duplicated commits to the same device groups.

You can learn more about Commit Configuration below: (API)

-   [Commit and
    Commit-All](https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-panorama-api/pan-os-xml-api-request-types/commit-configuration-api.html)
-   [Panorama Commit Operations - Learn about Partial
    commits](https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-web-interface-help/panorama-web-interface/panorama-commit-operations.html)

### Audit Comment Archive

If the option "Require audit comment on policies" (Panorama -> Management) is enabled, Audit
comments must be specified to a given Policy rule before committing any changes to that rule.

WARNING: Additionally, the length of an Audit comment can be at most 256 characters.

You can learn more about Audit comment below:

-   [Audit Comment
    Archive](https://docs.paloaltonetworks.com/pan-os/10-1/pan-os-web-interface-help/policies/audit-comment-archive.html)
-   [Making changes to Audit comments via
    API](https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-panorama-api/pan-os-xml-api-request-types/run-operational-mode-commands-api.html)


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Panorama asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**device** |  required  | string | Device IP/Hostname
**verify\_server\_cert** |  optional  | boolean | Verify server certificate
**username** |  required  | string | Username
**password** |  required  | password | Password

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity  
[block url](#action-block-url) - Block an URL  
[unblock url](#action-unblock-url) - Unblock an URL  
[block application](#action-block-application) - Block an application  
[unblock application](#action-unblock-application) - Unblock an application  
[block ip](#action-block-ip) - Block an IP  
[unblock ip](#action-unblock-ip) - Unblock an IP  
[list applications](#action-list-applications) - List the applications that the device knows about and can block  
[run query](#action-run-query) - Run a query on Panorama  
[commit changes](#action-commit-changes) - Commit changes to the firewall and device groups  

## action: 'test connectivity'
Validate the asset configuration for connectivity

Type: **test**  
Read only: **True**

This action logs into the device using a REST Api call to check the connection and credentials configured\.

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'block url'
Block an URL

Type: **contain**  
Read only: **False**

This action does the following to block a URL\:<ul><li>Create an URL Filtering profile object named '<b>Phantom URL List for \[device\_group\]</b>' containing the URL to block\.</br>If the profile is already present, then it will be updated to include the URL to block\. IMPORTANT\: For Version 9 and above, a URL Filtering profile no longer includes allow\-list/block\-list\. The official workaround is to use a Custom URL category instead\. Therefore, we create a new Custom URL category with the same name as the profile and link it to the profile\. Then, We configure the profile to block the URL category on both 'SITE ACCESS' and 'USER CREDENTIAL SUBMISSION' columns\.</li><li>If a <b>policy\_name</b> is provided, re\-configure the policy \(specified in the <b>policy\_name</b> parameter\) to use the created URL Filtering profile\. The URL filtering profile created in the previous step will be linked to the Profile Settings of the specified policy\.</br>If the policy is not found on the device, the action will return an error\.</li><li>If <b>should\_commit\_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group\. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it\.</li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**url** |  required  | URL to block | string |  `url` 
**device\_group** |  required  | Device group to configure, or 'shared' | string | 
**policy\_type** |  optional  | Block policy type | string | 
**policy\_name** |  optional  | Policy to use | string | 
**use\_partial\_commit** |  optional  | Whether to perform Partial commit admin\-level changes\. Config's username is included as the administrator name in the request\. Otherwise, plain commit is used by default\. | boolean | 
**audit\_comment** |  optional  | Audit comment to be used with the policy name\. Maximum 256 characters\. | string | 
**should\_commit\_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.url | string |  `url` 
action\_result\.parameter\.device\_group | string | 
action\_result\.parameter\.policy\_type | string | 
action\_result\.parameter\.policy\_name | string | 
action\_result\.parameter\.use\_partial\_commit | boolean | 
action\_result\.parameter\.audit\_comment | string | 
action\_result\.parameter\.should\_commit\_changes | boolean | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'unblock url'
Unblock an URL

Type: **correct**  
Read only: **False**

For Version 8 and below, this action will remove the URL from the URL Filtering profile that was created/updated in the <b>block url</b> action\. For Version 9 and above, this action will remove the URL from the Custom URL category that was created/updated in the <b>block url</b> action\. If <b>should\_commit\_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group\. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**url** |  required  | URL to unblock | string |  `url` 
**device\_group** |  required  | Device group to configure, or 'shared' | string | 
**use\_partial\_commit** |  optional  | Whether to perform Partial commit admin\-level changes\. Config's username is included as the administrator name in the request\. Otherwise, plain commit is used by default\. | boolean | 
**should\_commit\_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.url | string |  `url` 
action\_result\.parameter\.device\_group | string | 
action\_result\.parameter\.use\_partial\_commit | boolean | 
action\_result\.parameter\.should\_commit\_changes | boolean | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'block application'
Block an application

Type: **contain**  
Read only: **False**

This action does the following to block an application\:<ul><li>Create an Application group named '<b>Phantom App List for \[device\_group\]</b>' containing the application to block\.</br>If the group is already present, then it will be updated to include the application\.</li><li>If a <b>policy\_name</b> is provided, re\-configure the policy \(specified in the <b>policy\_name</b> parameter\) to use the created application group\.</br>If the policy is not found on the device, the action will return an error\.</li><li>If <b>should\_commit\_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group\. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it\.</li></ul>To get a list of applications that can be blocked, execute the <b>list applications</b> action\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**application** |  required  | Application to block | string |  `network application` 
**device\_group** |  required  | Device group to configure, or 'shared' | string | 
**policy\_type** |  optional  | Block policy type | string | 
**policy\_name** |  optional  | Policy to use | string | 
**use\_partial\_commit** |  optional  | Whether to perform Partial commit admin\-level changes\. Config's username is included as the administrator name in the request\. Otherwise, plain commit is used by default\. | boolean | 
**audit\_comment** |  optional  | Audit comment to be used with the policy name\. Maximum 256 characters\. | string | 
**should\_commit\_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.application | string |  `network application` 
action\_result\.parameter\.device\_group | string | 
action\_result\.parameter\.policy\_type | string | 
action\_result\.parameter\.policy\_name | string | 
action\_result\.parameter\.use\_partial\_commit | boolean | 
action\_result\.parameter\.audit\_comment | string | 
action\_result\.parameter\.should\_commit\_changes | boolean | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'unblock application'
Unblock an application

Type: **correct**  
Read only: **False**

This action will remove the application from the Application group that was created/updated in the <b>block application</b> action\. If <b>should\_commit\_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group\. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it\.<br>Note\: This action will pass for any non\-existing application name as API doesn't return an error for an incorrect application name\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**application** |  required  | Application to unblock | string |  `network application` 
**device\_group** |  required  | Device group to configure or 'shared' | string | 
**use\_partial\_commit** |  optional  | Whether to perform Partial commit admin\-level changes\. Config's username is included as the administrator name in the request\. Otherwise, plain commit is used by default\. | boolean | 
**should\_commit\_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.application | string |  `network application` 
action\_result\.parameter\.device\_group | string | 
action\_result\.parameter\.use\_partial\_commit | boolean | 
action\_result\.parameter\.should\_commit\_changes | boolean | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'block ip'
Block an IP

Type: **contain**  
Read only: **False**

<p>This action uses a multistep approach to block an IP\. The approach differs whether <b>is\_source\_address</b> is true or not\.  By default, it is false\.  The procedure is as follows\:</p><ul><li>Create an address entry named '<b>\[ip\_address\] Added By Phantom</b>' with the specified IP address<li>If the option <b>should\_add\_tag</b> is enabled, the container id of the phantom action is added as a tag to the address entry when it's created<li>If <b>is\_source\_address</b> is false\:<ul><li> add this entry to an address group called <b>Phantom Network List for \[device\_group\]</b></li><li>The address entry and group will be created in the device group specified in the <b>device\_group</b> parameter</li><li>If a <b>policy\_name</b> is provided, configure the address group as a <i>destination</i> to the policy specified in the <b>policy\_name</b> parameter</li></ul>If <b>is\_source\_address</b> is true\:<ul><li>add this entry to an address group called <b>PhantomNtwrkSrcLst\[device\_group\]</b></li><li>The address entry and group will be created in the device group specified in the <b>device\_group</b> parameter</li><li>If a <b>policy\_name</b> is provided, configure the address group as a <i>source</i> to the policy specified in the <b>policy\_name</b> parameter</ul><b>Note\:</b> If the policy is not found on the device, the action will return an error\.<li>If <b>should\_commit\_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group\. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it\.</li></ul><p><b>Please Note\:</b> If the Panorama Policy that is used to block a source or destination address has 'Any' in the Source Address or Destination Address field, Block IP will succeed but it will not work\.  Therefore, make sure that the policy that the address group will be appended to has no 'Any' in the field that you are blocking from\.  i\.e, if you are blocking an IP from source, make sure the policy does not have 'Any' under Source Address\.</p><p>The address group name is limited to 32 characters\.  The device group chosen will be appended to the address group name created\.  If the resulting name is too long, the name will be trimmed, which may result in clipped or unusual names\.  This is as intended, as it is a limitation by Panorama\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** |  required  | IP to block | string |  `ip` 
**is\_source\_address** |  optional  | Source address | boolean | 
**device\_group** |  required  | Device group to configure, or 'shared' | string | 
**policy\_type** |  optional  | Block policy type | string | 
**policy\_name** |  optional  | Policy to use | string | 
**use\_partial\_commit** |  optional  | Whether to perform Partial commit admin\-level changes\. Config's username is included as the administrator name in the request\. Otherwise, plain commit is used by default\. | boolean | 
**audit\_comment** |  optional  | Audit comment to be used with the policy name\. Maximum 256 characters\. | string | 
**should\_add\_tag** |  optional  | Whether a new tag should added as part of adding a new IP address | boolean | 
**should\_commit\_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.ip | string |  `ip` 
action\_result\.parameter\.is\_source\_address | boolean | 
action\_result\.parameter\.device\_group | string | 
action\_result\.parameter\.policy\_type | string | 
action\_result\.parameter\.policy\_name | string | 
action\_result\.parameter\.use\_partial\_commit | boolean | 
action\_result\.parameter\.audit\_comment | string | 
action\_result\.parameter\.should\_add\_tag | boolean | 
action\_result\.parameter\.should\_commit\_changes | boolean | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'unblock ip'
Unblock an IP

Type: **correct**  
Read only: **False**

This action will remove the address entry from the Address group that was created/updated in the <b>block ip</b> action\.  This action behaves differently based upon whether <b>is\_source\_address</b> is true or false\.  By default, it is false\.<br>If <b>is\_source\_address</b> is false\:<ul><li>The given IP address will be removed from the <b>Phantom Network List for \[device\_group\]</b> Address Group\.</li></ul>If <b>is\_source\_address</b> is true\:<ul><li>The given IP address will be removed from the <b>PhantomNtwrkSrcLst\[device\_group\]</b> Address Group\.</li></ul>If <b>should\_commit\_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group\. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** |  required  | IP to unblock | string |  `ip` 
**is\_source\_address** |  optional  | Source address | boolean | 
**device\_group** |  required  | Device group to configure, or 'shared' | string | 
**use\_partial\_commit** |  optional  | Whether to perform Partial commit admin\-level changes\. Config's username is included as the administrator name in the request\. Otherwise, plain commit is used by default\. | boolean | 
**should\_commit\_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.ip | string |  `ip` 
action\_result\.parameter\.device\_group | string | 
action\_result\.parameter\.is\_source\_address | boolean | 
action\_result\.parameter\.use\_partial\_commit | boolean | 
action\_result\.parameter\.should\_commit\_changes | boolean | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'list applications'
List the applications that the device knows about and can block

Type: **investigate**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.data\.\*\.\@name | string |  `network application` 
action\_result\.data\.\*\.category | string | 
action\_result\.data\.\*\.has\-known\-vulnerability | string | 
action\_result\.data\.\*\.used\-by\-malware | string | 
action\_result\.data\.\*\.\@ori\_country | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.consume\-big\-bandwidth | string | 
action\_result\.data\.\*\.able\-to\-transfer\-file | string | 
action\_result\.data\.\*\.technology | string | 
action\_result\.data\.\*\.pervasive\-use | string | 
action\_result\.data\.\*\.\@ori\_lauguage | string | 
action\_result\.data\.\*\.subcategory | string | 
action\_result\.data\.\*\.prone\-to\-misuse | string | 
action\_result\.data\.\*\.default\.port\.member | string | 
action\_result\.data\.\*\.evasive\-behavior | string | 
action\_result\.data\.\*\.references\.entry\.link | string | 
action\_result\.data\.\*\.references\.entry\.\@name | string | 
action\_result\.data\.\*\.tunnel\-other\-application | string | 
action\_result\.data\.\*\.\@id | string | 
action\_result\.data\.\*\.risk | string | 
action\_result\.data\.\*\.application\-container | string | 
action\_result\.data\.\*\.use\-applications\.member\.\#text | string | 
action\_result\.data\.\*\.use\-applications\.member\.\@minver | string | 
action\_result\.data\.\*\.use\-applications\.\@minver | string | 
action\_result\.data\.\*\.\@minver | string | 
action\_result\.data\.\*\.references\.entry\.\*\.link | string | 
action\_result\.data\.\*\.references\.entry\.\*\.\@name | string | 
action\_result\.data\.\*\.use\-applications\.member | string | 
action\_result\.data\.\*\.file\-type\-ident | string | 
action\_result\.data\.\*\.virus\-ident | string | 
action\_result\.data\.\*\.use\-applications\.member | string | 
action\_result\.data\.\*\.tunnel\-applications\.member | string | 
action\_result\.data\.\*\.data\-ident | string | 
action\_result\.data\.\*\.implicit\-use\-applications\.member | string | 
action\_result\.data\.\*\.default\.port\.member | string | 
action\_result\.data\.\*\.udp\-timeout | string | 
action\_result\.data\.\*\.default\.ident\-by\-ip\-protocol | string | 
action\_result\.data\.\*\.file\-forward | string | 
action\_result\.data\.\*\.use\-applications\.member\.\*\.\#text | string | 
action\_result\.data\.\*\.use\-applications\.member\.\*\.\@minver | string | 
action\_result\.data\.\*\.tunnel\-applications\.member\.\*\.\#text | string | 
action\_result\.data\.\*\.tunnel\-applications\.member\.\*\.\@minver | string | 
action\_result\.data\.\*\.tunnel\-applications\.\@minver | string | 
action\_result\.data\.\*\.ottawa\-name | string | 
action\_result\.data\.\*\.implicit\-use\-applications\.member | string | 
action\_result\.data\.\*\.decode | string | 
action\_result\.data\.\*\.breaks\-decryption | string | 
action\_result\.data\.\*\.tunnel\-applications\.member\.\#text | string | 
action\_result\.data\.\*\.tunnel\-applications\.member\.\@minver | string | 
action\_result\.data\.\*\.tunnel\-applications\.member | string | 
action\_result\.data\.\*\.related\-applications\.member | string | 
action\_result\.data\.\*\.child | string | 
action\_result\.data\.\*\.timeout | string | 
action\_result\.data\.\*\.analysis | string | 
action\_result\.data\.\*\.not\-support\-ssl | string | 
action\_result\.data\.\*\.enable\-url\-filter | string | 
action\_result\.data\.\*\.decode\.\#text | string | 
action\_result\.data\.\*\.decode\.\@minver | string | 
action\_result\.data\.\*\.correlate\.rules\.entry\.threshold | string | 
action\_result\.data\.\*\.correlate\.rules\.entry\.interval | string | 
action\_result\.data\.\*\.correlate\.rules\.entry\.protocol | string | 
action\_result\.data\.\*\.correlate\.rules\.entry\.track\-by\.member | string | 
action\_result\.data\.\*\.correlate\.rule\-match | string | 
action\_result\.data\.\*\.correlate\.interval | string | 
action\_result\.data\.\*\.correlate\.key\-by\.member | string | 
action\_result\.data\.\*\.tunnel\-other\-application\.\#text | string | 
action\_result\.data\.\*\.tunnel\-other\-application\.\@minver | string | 
action\_result\.data\.\*\.tcp\-timeout | string | 
action\_result\.data\.\*\.ident\-by\-dport | string | 
action\_result\.data\.\*\.file\-forward | string | 
action\_result\.data\.\*\.ident\-by\-sport | string | 
action\_result\.data\.\*\.preemptive | string | 
action\_result\.data\.\*\.use\-applications\.\*\.member | string | 
action\_result\.data\.\*\.netx\-vmotion | string | 
action\_result\.data\.\*\.ha\-safe | string | 
action\_result\.data\.\*\.timeout | string | 
action\_result\.data\.\*\.doc\-review | string | 
action\_result\.data\.\*\.default\.\*\.ident\-by\-ip\-protocol | string | 
action\_result\.data\.\*\.default\.\*\.port\.member | string | 
action\_result\.data\.\*\.discard\-timeout | string | 
action\_result\.data\.\*\.udp\-discard\-timeout | string | 
action\_result\.data\.\*\.default\.ident\-by\-icmp\-type | string | 
action\_result\.data\.\*\.deprecated | string | 
action\_result\.data\.\*\.alg\-disable\-capability | string | 
action\_result\.data\.\*\.risk | string | 
action\_result\.data\.\*\.tcp\-discard\-timeout | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary\.total\_applications | numeric | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'run query'
Run a query on Panorama

Type: **investigate**  
Read only: **True**

This action runs a query on Panorama and returns the set of logs matching the search criteria\.<br><br>Use the <b>range</b> parameter to limit the number of logs returned by the action\. If no range is given, the action will use the range <b>1\-5000</b>\. The action can retrieve up to a maximum of 5000 logs\. If more logs need to be retrieved, rerun the action with the next sequential range of values\.<br><br>The <b>log\_type</b> parameter can be one of the following\:<ul><li><b>traffic</b> \- traffic logs</li><li><b>url</b> \- URL filtering logs</li><li><b>data</b> \- data filtering logs</li><li><b>threat</b> \- threat logs</li><li><b>config</b> \- config logs</li><li><b>system</b> \- system logs</li><li><b>hipmatch</b> \- HIP match logs</li><li><b>wildfire</b> \- wildfire logs</li><li><b>corr</b> \- correlated event logs</li><li><b>corr\-categ</b> \- correlated events by category</li><li><b>corr\-detail</b> \- correlated event details\.</li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**log\_type** |  required  | Log type to query | string | 
**query** |  required  | Query to run | string | 
**range** |  optional  | Range of result logs to retrieve \(e\.g 1\-5000 or 100\-700\) | string | 
**direction** |  optional  | Direction to search | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.query | string | 
action\_result\.parameter\.log\_type | string | 
action\_result\.parameter\.direction | string | 
action\_result\.parameter\.range | string | 
action\_result\.data\.\*\.job\.id | string | 
action\_result\.data\.\*\.job\.tdeq | string | 
action\_result\.data\.\*\.job\.tenq | string | 
action\_result\.data\.\*\.job\.tlast | string | 
action\_result\.data\.\*\.job\.status | string | 
action\_result\.data\.\*\.job\.cached\-logs | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.to | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.app | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.dst | string |  `ip` 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.src | string |  `ip` 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.from | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.rule | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.type | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.vsys | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.bytes | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.dport | string |  `port` 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.flags | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.proto | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.seqno | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.sport | string |  `port` 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.start | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.\@logid | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.action | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.domain | string |  `domain` 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.dstloc | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.logset | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.serial | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.srcloc | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.elapsed | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.packets | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.padding | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.pbf\-c2s | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.pbf\-s2c | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.subtype | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.vsys\_id | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.category | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.cpadding | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.flag\-nat | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.natdport | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.natsport | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.flag\-pcap | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.pkts\_sent | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.repeatcnt | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.sessionid | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.bytes\_sent | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.config\_ver | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.flag\-proxy | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.inbound\_if | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.sym\-return | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.actionflags | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.device\_name | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.outbound\_if | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.transaction | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.flag\-flagged | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.receive\_time | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.action\_source | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.non\-std\-dport | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.pkts\_received | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.time\_received | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.bytes\_received | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.captive\-portal | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.decrypt\-mirror | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.time\_generated | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.dg\_hier\_level\_1 | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.dg\_hier\_level\_2 | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.dg\_hier\_level\_3 | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.dg\_hier\_level\_4 | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.flag\-url\-denied | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.temporary\-match | string | 
action\_result\.data\.\*\.log\.logs\.entry\.\*\.session\_end\_reason | string | 
action\_result\.data\.\*\.log\.logs\.\@count | string | 
action\_result\.data\.\*\.log\.logs\.\@progress | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary\.num\_logs | numeric | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'commit changes'
Commit changes to the firewall and device groups

Type: **generic**  
Read only: **False**

The action then proceeds to commit the changes to Panorama, followed by a commit to the device group\.<br>If the device group happens to be shared, then a commit will be sent to all the device groups belonging to it\.<br> If <b>partial\_commit\_excluded\_values</b> is provided, Partial commit will exclude those parts of the configuration\.<br> If <b>partial\_commit\_no\_locations</b> is provided, Partial commit will exclude pushing changes to those locations\.<br> You can learn more about Partial commit usage below\: <br><ul><li><a href='https\://docs\.paloaltonetworks\.com/pan\-os/10\-2/pan\-os\-cli\-quick\-start/use\-the\-cli/commit\-configuration\-changes' target='\_blank'>Commit Configuration Changes</a></li><li><a href='https\://docs\.paloaltonetworks\.com/pan\-os/8\-1/pan\-os\-web\-interface\-help/panorama\-web\-interface/panorama\-commit\-operations' target='\_blank'>Panorama Commit Operations</a></li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**device\_group** |  required  | Device group to configure, or 'shared' | string | 
**use\_partial\_commit** |  optional  | Whether to perform Partial commit admin\-level changes\. Config's username is included as the administrator name in the request\. Otherwise, plain commit is used by default\. | boolean | 
**partial\_commit\_excluded\_values** |  optional  | A space\-separated, comma\-separated or line\-separated list of Partial Commit Excluded values | string | 
**partial\_commit\_no\_locations** |  optional  | A space\-separated, comma\-separated or line\-separated list of Partial Commit no\-locations | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.device\_group | string | 
action\_result\.parameter\.use\_partial\_commit | boolean | 
action\_result\.parameter\.partial\_commit\_excluded\_values | string | 
action\_result\.parameter\.partial\_commit\_no\_locations | string | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 