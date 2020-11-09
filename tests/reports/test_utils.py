from src.reports import utils
import pytest
from unittest import mock
from faker import Faker
from datetime import datetime, timezone, timedelta


fake = Faker()


def subscription():
    return {
        "subscription_uuid": "12334",
        "active": True,
        "customer_uuid": "changeme",
        "dhs_contact_uuid": "changeme",
        "keywords": "research development government work job",
        "name": "1",
        "primary_contact": {
            "active": True,
            "email": "Matt.Daemon@example.com",
            "first_name": "Matt",
            "last_name": "Daemon",
            "mobile_phone": "555-555-5555",
            "office_phone": "555-555-5555",
        },
        "sending_profile_name": "SMTP",
        "start_date": datetime(2020, 7, 1, 5, 49, 2),
        "status": "  Waiting on SRF",
        "target_email_list": [
            {
                "email": "Bat.Man@example.com",
                "first_name": "Bat",
                "last_name": "Man",
                "position": "admin",
            },
            {
                "email": "Ben.Aflex@example.com",
                "first_name": "Ben",
                "last_name": "Aflex",
                "position": "admin",
            },
            {
                "email": "David.Young@example.com",
                "first_name": "David",
                "last_name": "Young",
                "position": "intern",
            },
            {
                "email": "George.Clooney@example.com",
                "first_name": "George",
                "last_name": "Clooney",
                "position": "intern",
            },
            {
                "email": "Jane.Doe@example.com",
                "first_name": "Jane",
                "last_name": "Doe",
                "position": "intern",
            },
            {
                "email": "Jane.Moore@example.com",
                "first_name": "Jane",
                "last_name": "Moore",
                "position": "manager",
            },
            {
                "email": "John.Smith@example.com",
                "first_name": "John",
                "last_name": "Smith",
                "position": "manager",
            },
        ],
        "templates_selected_uuid_list": [],
        "cycles": [
            {
                "cycle_uuid": "2bfd4b54-b587-4fa2-a60d-4daba861959e",
                "start_date": datetime(
                    2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc
                ),
                "end_date": datetime(
                    2020, 10, 30, 5, 49, 2, 960000, tzinfo=timezone.utc
                ),
                "active": True,
                "campaigns_in_cycle": [1],
                "phish_results": {
                    "sent": 1,
                    "opened": 0,
                    "clicked": 0,
                    "submitted": 0,
                    "reported": 0,
                },
                "phish_results_dirty": False,
                "override_total_reported": -1,
                "campaign_list": [],
            }
        ],
        "campaigns": [],
        "url": "https://inl.gov",
        "created_by": "dev user",
        "cb_timestamp": fake.date_time(),
        "last_updated_by": "dev user",
        "lub_timestamp": fake.date_time(),
    }


def get_customer():
    return {
        "customer_uuid": fake.uuid4(),
        "name": fake.name(),
        "identifier": fake.word(),
        "address_1": fake.street_address(),
        "city": fake.city(),
        "state": fake.state(),
        "zip_code": fake.zipcode(),
        "customer_type": "government",
        "industry": "feds",
        "sector": "energy",
        "contact_list": [
            {
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "title": fake.job(),
                "office_phone": fake.phone_number(),
                "mobile_phone": fake.phone_number(),
                "email": fake.email(),
                "notes": fake.paragraph(),
                "active": True,
            }
        ],
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }


def get_dhs():
    return {
        "dhs_contact_uuid": "1234",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "title": fake.job(),
        "office_phone": fake.phone_number(),
        "mobile_phone": fake.phone_number(),
        "email": fake.email(),
        "notes": fake.paragraph(),
        "active": True,
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }


def get_recommendation():
    return {
        "recommendations_uuid": "1234",
        "name": "foo bar",
        "appearance": {"grammar": 0, "link_domain": 1, "logo_graphics": 0},
        "behavior": {"curiosity": 1, "duty_obligation": 0, "fear": 0, "greed": 0},
        "sender": {"authoritative": 0, "external": 0, "internal": 0},
        "relevancy": {"organization": 0, "public_news": 0},
        "created_by": fake.name(),
        "cb_timestamp": fake.date_time(),
        "last_updated_by": fake.name(),
        "lub_timestamp": fake.date_time(),
    }


def generate_subscription_stat_details():
    return {
        "campaign_results": [
            {
                "campaign_id": 1234,
                "deception_level": 1,
                "campaign_stats": {},
                "reported_override_val": -1,
                "times": {},
                "ratios": {
                    "clicked_ratio": 1,
                    "opened_ratio": 1,
                    "submitted_ratio": 1,
                    "reported_ratio": 1,
                },
                "template_name": "foo bar",
                "template_uuid": "1234",
            }
        ],
        "stats_all": {},
        "stats_low_deception": {},
        "stats_mid_deception": {},
        "stats_high_deception": {},
        "clicks_over_time": {},
    }


def template():
    return {
        "appearance": {"grammar": 0, "link_domain": 1, "logo_graphics": 0},
        "behavior": {"curiosity": 1, "duty_obligation": 0, "fear": 0, "greed": 0},
        "deception_score": 1,
        "description": "Intern Resume",
        "descriptive_words": "student resumes internship intern",
        "from_address": "<%FAKER_FIRST_NAME%> <%FAKER_LAST_NAME%> <<%FAKER_FIRST_NAME%>.<%FAKER_LAST_NAME%>@domain.com>",
        "html": "<br>Hi, sorry, I don't know exactly who this would go to. I read on the site<br>that your accepting student resumes for a summe rinternship. I'ev loaded<br>mine to our school's website. Please review and let me know if we're good to<br>go.<br><a href=\"<%URL%>\">https://endermannpoly.edu/studentresources/resumes/mquesenberry3.pdf</a><br><br><br>thx, <%FAKER_FIRST_NAME%>&nbsp;<br>",
        "name": "Intern Resume",
        "relevancy": {"organization": 0, "public_news": 0},
        "retired": False,
        "retired_description": "",
        "sender": {"authoritative": 0, "external": 0, "internal": 0},
        "subject": "Intern Resume",
        "text": "Hi, sorry, I don't know exactly who this would go to. I read on the sitethat your accepting student resumes for a summe rinternship. I'ev loadedmine to our school's website. Please review and let me know if we're good togo.https://endermannpoly.edu/studentresources/resumes/mquesenberry3.pdfthx, <%FAKER_FIRST_NAME%>\u00a0",
    }


def get_moment():
    return {
        "message": "sent",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }


def test_get_closest_cycle_within_day_range():
    result = utils.get_closest_cycle_within_day_range(
        subscription(),
        datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        day_range=90,
    )

    assert result["cycle_uuid"] == "2bfd4b54-b587-4fa2-a60d-4daba861959e"


def test_get_cycle_by_date_in_range():
    result = utils.get_cycle_by_date_in_range(
        subscription(), datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc)
    )

    assert result is not None


def test_find_send_timeline_moment():
    timeline_items = [{"email": "test@test.com"}]
    result = utils.find_send_timeline_moment("test@test.com", timeline_items)

    assert result == {"email": "test@test.com"}

    result = utils.find_send_timeline_moment("test2@test.com", timeline_items)

    assert result == {}


def test_add_moment_no_duplicates():
    moment = {
        "message": "sent",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    timeline_items = [{"email": "test@test.com"}]

    result = utils.add_moment_no_duplicates(moment, timeline_items, "sent")

    assert result == None


def test_add_moment_no_duplicates():
    moment = {
        "message": "sent",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    timeline_items = [{"email": "test@test.com"}]

    result = utils.add_moment_no_duplicates(moment, timeline_items, "sent")

    assert result == None


def test_append_timeline_moment():
    moment = {
        "message": "Email Sent",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    timeline_items = [
        {
            "message": "Email Sent",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        }
    ]

    utils.append_timeline_moment(moment, timeline_items)

    assert len(timeline_items) == 2

    moment = {
        "message": "Email Opened",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "opened": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    utils.append_timeline_moment(moment, timeline_items)

    assert len(timeline_items) == 2

    moment = {
        "message": "Clicked Link",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "clicked": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    utils.append_timeline_moment(moment, timeline_items)
    assert len(timeline_items) == 2

    moment = {
        "message": "Submitted Data",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "submitted": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    utils.append_timeline_moment(moment, timeline_items)
    assert len(timeline_items) == 2

    moment = {
        "message": "Email Reported",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "reported": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    utils.append_timeline_moment(moment, timeline_items)
    assert len(timeline_items) == 2


def test_generate_time_difference_stats():
    list_of_times = [timedelta(days=90)]

    result = utils.generate_time_difference_stats(list_of_times)

    expected_result = {
        "count": 1,
        "average": 1,
        "minimum": 1,
        "median": 1,
        "maximum": 1,
    }

    assert result != None
    assert result["count"] == 1
    assert result["average"] == timedelta(days=90)
    assert result["minimum"] == timedelta(days=90)
    assert result["median"] == timedelta(days=90)
    assert result["maximum"] == timedelta(days=90)


def test_generate_campaign_statistics():
    campaign_timeline_summary = [
        {
            "message": "Email Sent",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        },
        {
            "message": "Email Opened",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened_difference": timedelta(days=1),
        },
        {
            "message": "Email Reported",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted_difference": timedelta(days=1),
        },
    ]

    result = utils.generate_campaign_statistics(campaign_timeline_summary)
    assert result != None


def test_date_in_range():
    date = datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc)
    date_not_in = datetime(2020, 7, 22, 19, 37, 54, 960000, tzinfo=timezone.utc)
    min_date = datetime(2020, 7, 1, 19, 37, 54, 960000, tzinfo=timezone.utc)
    max_date = datetime(2020, 7, 10, 19, 37, 54, 960000, tzinfo=timezone.utc)

    result_true = utils.date_in_range(date, min_date, max_date)
    result_false = utils.date_in_range(date_not_in, min_date, max_date)

    assert result_true == True
    assert result_false == False


def test_filter_campaign_timeline_by_date_range():
    campaign_timeline_summary = [
        {
            "message": "Email Sent",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        },
        {
            "message": "Email Opened",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened_difference": timedelta(days=1),
        },
        {
            "message": "Email Reported",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted_difference": timedelta(days=1),
        },
    ]

    start_date = datetime(2020, 7, 1, 19, 37, 54, 960000, tzinfo=timezone.utc)
    end_date = datetime(2020, 7, 10, 19, 37, 54, 960000, tzinfo=timezone.utc)

    utils.filter_campaign_timeline_by_date_range(
        campaign_timeline_summary, start_date, end_date
    )

    assert len(campaign_timeline_summary) == 5


def test_get_unique_moments():
    campaign_timeline_summary = [
        {
            "message": "Email Sent",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        },
        {
            "message": "Email Opened",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened_difference": timedelta(days=1),
        },
        {
            "message": "Email Reported",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted_difference": timedelta(days=1),
        },
    ]

    start_date = datetime(2020, 7, 1, 19, 37, 54, 960000, tzinfo=timezone.utc)
    end_date = datetime(2020, 7, 10, 19, 37, 54, 960000, tzinfo=timezone.utc)

    results = utils.get_unique_moments(campaign_timeline_summary)

    assert len(results) == 4
    assert len(results) != len(campaign_timeline_summary)


def test_count_timeline_moments():
    campaign_timeline_summary = [
        {
            "message": "Email Sent",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        },
        {
            "message": "Email Opened",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened_difference": timedelta(days=1),
        },
        {
            "message": "Email Reported",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted_difference": timedelta(days=1),
        },
    ]

    results = utils.count_timeline_moments(campaign_timeline_summary)

    assert results["sent"] == 1
    assert results["opened"] == 1
    assert results["clicked"] == 2
    assert results["submitted"] == 0
    assert results["reported"] == 1
