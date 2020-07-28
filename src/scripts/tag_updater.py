"""
This a script to update all the old template tags.

It reads in a json file containing the old tags, replaces the tags with more uniform tags
and writes the results to a new file.
"""

# Standard Python Libraries
import json
import sys

old_target_name_tags = ["%To_Name%"]

old_target_email_tags = ["%To%"]

old_customer_system_tags = [
    "<ORG SYSTEM>",
    "[CUST_SYSTEM]",
    "<ORG WEB PLATFORM/SERVICE>",
    "[System Name]",
    "<ORG INTRANET>",
]

old_customer_tags = [
    "<ORG>",
    "<Customer Name>",
    "[CUSTOMER]",
    "[CUSTOMER LONG NAME]",
    "[CUSTOMER NAME]",
    "[Written Out Customer Name]",
    "[Customer]",
    "[CUSTOMER-NAME]",
    "[Customer Name]",
    "[CustomerName]",
    "[CUSTOMER_NAME]",
    "[Stakeholder Long Name]",
    "[Stakeholder]",
    "[UNIVERSITY_NAME]",
    "[AGENCY NAME]",
    "[Organization]",
    "[ORGANIZATION]",
    "[Organization Name]",
    "<CUST_NAME>",
    "[CUST_Name]",
    "[Organization Type]",
    "[ORG/CITY/TOWN/STATE]",
    "[CUSTOMER GROUP FOR PAYMENTS]",
    "[CUSTOMER SPECIFIC GROUP]",
    "[Actual Division that Handles Pay]",
    "<CUST_IT_Dept_NAME>",
    "<CUST_IT_Dept_NAME",
    "[Related Budget/Finance Department]",
    "[PROGRAM DEPARTMENT]",
    "[KNOWN CUSTOMER OFFICE]",
    "[CUSTOMER HR OFFICE]",
    "[CUSTOMER LEADERSHIP OFFICE]",
    "[CUSTOMER SPECIFIC OFFICE]",
    "[County Election's Staff, Information Systems personnel across the State]",
]

old_customer_email_tags = [
    "[CUSTOMER EMAIL]",
    "[SPOOFED CUSTOMER EMAIL]",
    "[CUSTOMER OFFICE EMAIL]",
    "<NAME@SPOOFED INTERNAL ADDR>",
]

old_address_tags = [
    "[Insert Address Here]",
    "[Location]",
    "[RELATED ADDRESS]",
    "[Related Org Address]",
    "[ACTUAL ADDRESS OF DEPT]",
]

old_date_tags = [
    "[DATE]",
    "[CAMPAIGN END DATE, YEAR]",
    "[Date of End of Campaign]",
    "[Date of Start of Campaign]",
    "[DATE AFTER CAMPAIGN]",
    "[Campaign End Date]",
    "[Date of Campaign End]",
    "[Insert Date]",
    "[Insert Date and Time]",
    "[RECENT DATE]",
    "[Upcoming Date]",
    "[MONTH YEAR]",
    "[MONTH DAY, YEAR]",
]

old_link_tags = [
    "<[%]URL[%]>",
    "<Spoofed Link>",
    "[Spoofed Related Site]",
    "<link>",
    "<Link>",
    "[<%URL%>]",
    "<spoofed link>",
    "[Spoofed Link]",
    "connect.spoofed.org",
    "connect.SPOOFED.org",
    "SPOOFED.org",
    "<hidden link>",
    "<LINK TO ACTUAL CUST PAYMENT SITE OR SIMILAR>",
    "[RELEVANT EXTERNAL SPECIFIC SITE]",
    "<[Fake link]>",
    "<HIDDEN>",
    "<HIDDEN LINK>",
    "<[EMBEDDED LINK]>",
    "<LINK>",
    "<embedded link>",
    "[LINK]",
    "[WRITTEN OUT SPOOFED CUSTOMER LINK]",
    "[EMBEDDED LINK]",
    "[Fake link]",
    "[insert spoofed link]",
    "[Insert Fake Link]",
    "[PLAUSIBLE SPOOFED URL]",
    "[insert fake URL]",
    "[spoof fake URL]",
    "[Related URL to State Law or Rule]",
    "[Fake Web Page URL]",
    "%]URL[%",
    "%URL%",
    "<<%URL%>>",
]

old_state_tags = [
    "[State]",
    "[State or Entity]",
    "[Entity or State]",
    "[Entity]",
    "[county or entity]",
]

old_season_tags = ["[Season]", "[Select Summer/Spring/Fall/Winter]"]

old_customer_location_tags = [
    "[Customer Location, ex. Town of...]",
    "[Customer Location ex. Town of...]",
    "[Customer City]",
    "[CUST_LOCATION/NETWORK]",
    "<CITY/ORG NAME>",
    "[Location or Customer]",
    "[Customer Location]",
    "[Insert location]",
    "[LEGIT_LOCATION]",
]

old_month_tags = ["[Month]", "[Month Year of Campaign]", "[MONTH]", "<Month>"]

old_year_tags = ["<year>", "<Year>", "[CAMPAIGN END DATE, YEAR]", "[Year]", "[YEAR]"]

old_spoof_name_tags = [
    "<FAKE NAME>",
    "[SPOOFED NAME]",
    "[NAME]",
    "[GENERIC FIRST NAME]",
    "[GENERIC NAME]",
    "[APPROVED HIGH LEVEL NAME]",
    "[Fake Name]",
    "[fakename]",
    "[MADE UP NAME]",
    "[FAKE NAME]",
    "FIRST LAST",
    "[FAKE_NAME]",
]

old_event_tags = ["[list relevant weather event]", "[CUSTOMER SPECIFIC EVENT]", "[APPLICABLE EVENT]"]

old_time_frame_tags = [
    "[Change time frame as needed]",
    "[TIMEFRAME]"
    ]

old_domain_tags = [
    "[domain]",
    "[Domain]",
    "[DOMAIN]",
    "[Spoofed Domain]",
    "[SpoofedDomain]",
    "[SPOOFED_DOMAIN]",
    "[UNIVERSITY-DOMAIN]",
    "[UNIVERSITY_DOMAIN]",
    "[NCATS_DOMAIN]",
    "[NCATS DOMAIN]",
    "NCATS-DOMAIN>",
    "[WRITTEN OUT SPOOFED CUSTOMER SURVEY DOMAIN]",
    "[CUSTOMER-DOMAIN]",
    "[WRITTEN OUT SPOOFED CUSTOMER DOMAIN]",
    "[Similar Customer Domain]",
    "[Spoofed Similar Org Domain]",
    "[spoofed.domain.tld]",
    "spoofed.domain.tld",
    "fake.domain.tld",
    "NCATS_DOMAIN.tld",
    "ncats.domain.tld",
    "spoofedfakeinteneral.ncatsdomain.tld",
    "CUST_DOMAIN.NCATS-DOMAIN>",
    "[SPOOFED_CUST_DOMAIN]",
    "[CUSTOM_DOMAIN]",
    "[CUST_DOMAIN]",
    "[CUST_DOMAIN_SPOOF]",
    "FAKE-BUSINESS-SITE.tld",
    "NCATS-DOMAIN.tld",
    "[UNRELATED_DOMAIN.tld]",
    "[GENERIC_DOMAIN.tld]",
    "NCATS.domain",
    "[subdomain.domain.tld]",
    "DOMAIN.org",
    "domain.com",
    "domain.net",
    "domain.tld",
]

old_acronym_tags = [
    "[Group Acronym]",
    "[Acronym]",
    "(Acronym)",
    "(ACRONYM)",
    "[ACRONYM]",
    "<Acronym>",
    "<ACRONYM>",
    "[GROUP ACRONYM]",
    "[CUSTOMER ACRONYM]",
    "[CUSTOMER SPECIFIC GROUP ACRONYM]",
    "[CustomerAcronymLikeSite]",
    "[Stakeholder Acronym]",
    "[customeracronymorname]",
]

old_slogan_tags = ["[CUSTOMER SLOGAN]"]

old_signature_tags = ["[Organization Signature]", "[Signature]", "[SIGNATURE LINE]"]

old_topic_tags = ["[TOPIC]"]

old_token_tags = ["%TOKEN%", "[LEGIT CONTRACT #]", "[LEGIT SOLICITATION #]"]

old_program_tags = [
    "[TimeCardProgram]",
    "[Time Card Program]",
    "[NAME OF PARKING OR COMMUTER PROGRAM]",
]

old_logo_tags = ["[LOGO]"]

old_job_tags = [
    "[CUSTOMER-RELEVENT-JOB-ROLE]",
    "[Relevant Position]",
    "[LEGIT_JOB]",
    "[LEGIT_JOB_PREFIX]",
    "[PROPER TITLE FOR OFFICE SUPPLY MANAGER]",
    "[Relevant Skill]",
]

old_number_tags = [
    "[amount or number]",
]

# New Uniform Tags
# Parameter_Name, Parameter_Type (GoPhish or Con-PCA), User Parameter Description, Data Source
#        "<%URL%>": "{{.URL}}",
#        "<%TARGET_FIRST_NAME%>": "{{.FirstName}}",
#        "<%TARGET_LAST_NAME%>": "{{.LastName}}",
#        "<%TARGET_FULLL_NAME%>": "{{.FirstName}} {{.LastName}}",
#        "<%TARGET_EMAIL%>": "{{.Email}}",
#        "<%TARGET_POSITION%>": "{{.Position}}",
#        "<%FROM%>": "{{.From}}",

#        "<%CUSTOMER_NAME%>": customer_info["name"],
#        "<%CUSTOMER_EMAIL%>":
#        "<%CUSTOMER_SYSTEM%>":
#        "<%CUSTOMER_ADDRESS_FULL%>": customer_full_address,
#        "<%CUSTOMER_ADDRESS_1%>": customer_info["address_1"],
#        "<%CUSTOMER_ADDRESS_2%>": customer_info["address_2"],
#        "<%CUSTOMER_STATE%>": customer_info["state"],
#        "<%CUSTOMER_CITY%>": customer_info["city"],
#        "<%CUSTOMER_ZIPCODE%>": customer_info["zip_code"],
#        "<%CURRENT_SEASON%>": current_season(today),
#        "<%CURRENT_DATE_LONG%>": today.strftime("%B %d, %Y"),
#        "<%CURRENT_DATE_SHORT%>": today.strftime("%m/%d/%y"),
#        "<%CURRENT_MONTH_NUM%>": today.strftime("%m"),
#        "<%CURRENT_MONTH_LONG%>": today.strftime("%B"),
#        "<%CURRENT_MONTH_SHORT%>": today.strftime("%b"),
#        "<%CURRENT_YEAR_LONG%>": today.strftime("%Y"),
#        "<%CURRENT_YEAR_SHORT%>": today.strftime("%y"),
#        "<%CURRENT_DAY%>": today.strftime("%d"),
#        "<%SPOOF_NAME%>": "FAKE NAME GENERATOR",
#        "<%EVENT%>": "Relevant Event",
#        "<%TIMEFRAME%>": "Relevant Timeframe",
#        "<%DOMAIN%>": "Relevenat Domain",
#        "<%ACRONYM%>": "Relevant Acronym",
#        "<%SLOGAN%>": "Relevant Slogan",
#        "<%SIGNATURE%>": "Relevenat Signature",
#        "<%TOPIC%>": "Relevant Topic",
#        "<%TOKEN%>": "Relevant Token",
#        "<%PROGRAM%>": "Relevant Program",
#        "<%LOGO%>": "Relevant Logo"
#        "<%JOB_ROLE%>": "Relevant Job"
#        "<%NUMBER%>": Relevant amount or number"


def main():

    if len(sys.argv) != 3:
        print("Usage: {} [inputfile] [outputfile]".format(sys.argv[0]))
        exit()

    with open(sys.argv[1]) as file:
        data = json.load(file)

    updated_tags = {
        "<%URL%>": old_link_tags,
        "<%TARGET_FULL_NAME%>": old_target_name_tags,
        "<%TARGET_EMAIL%>": old_target_email_tags,
        "<%CUSTOMER_SYSTEM%>": old_customer_system_tags,
        "<%CUSTOMER_NAME%>": old_customer_tags,
        "<%CUSTOMER_EMAIL%>": old_customer_email_tags,
        "<%CUSTOMER_ADDRESS_FULL%>": old_address_tags,
        "<%CUSTOMER_STATE%>": old_state_tags,
        "<%CUSTOMER_CITY%>": old_customer_location_tags,
        "<%CURRENT_SEASON%>": old_season_tags,
        "<%CURRENT_DATE_LONG%>": old_date_tags,
        "<%CURRENT_MONTH_LONG%>": old_month_tags,
        "<%CURRENT_YEAR_LONG%>": old_year_tags,
        "<%SPOOF_NAME%>": old_spoof_name_tags,
        "<%EVENT%>": old_event_tags,
        "<%TIMEFRAME%>": old_time_frame_tags,
        "<%DOMAIN%>": old_domain_tags,
        "<%ACRONYM%>": old_acronym_tags,
        "<%SLOGAN%>": old_slogan_tags,
        "<%SIGNATURE%>": old_signature_tags,
        "<%TOPIC%>": old_topic_tags,
        "<%TOKEN%>": old_token_tags,
        "<%PROGRAM%>": old_program_tags,
        "<%LOGO%>": old_logo_tags,
        "<%JOB_ROLE%>": old_job_tags,
        "<%NUMBER%>": old_number_tags,
    }

    # Update tags in old template data file
    for template in data:
        name = template["name"]
        subject = template["subject"]
        text = template["text"]
        html = template["html"]
        from_address = template["from_address"]

        for key in updated_tags:
            old_tags_list = updated_tags[key]

            for old_tag in old_tags_list:
                name = name.replace(old_tag, key)
                subject = subject.replace(old_tag, key)
                text = text.replace(old_tag, key)
                from_address = from_address.replace(old_tag, key)
                html = html.replace(old_tag, key)

        template["name"] = name
        template["subject"] = subject
        template["text"] = text
        template["from_address"] = from_address
        template["html"] = html

    with open(sys.argv[2], "w") as file:
        json.dump(data, file, indent=2)


if __name__ == "__main__":
    main()
