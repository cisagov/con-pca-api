"""Validate subscription utils."""
# cisagov Libraries
from api.services import SubscriptionService

subscription_service = SubscriptionService()


def is_subscription_valid(target_count, campaign_minutes):
    """
    Check to see if subscription is valid and will remain within required rates for warmup.

    No more than 100 total emails an hour and no more than 1000 per day on first subscription.

    No more than a 20% increase in any given 24 hour window.

    For more details, check this documentation https://www.mailgun.com/blog/domain-warmup-reputation-stretch-before-you-send/.
    """
    daily_rate = get_daily_rate(target_count, campaign_minutes)
    hourly_rate = get_hourly_rate(target_count, campaign_minutes)
    current_daily_rate = get_all_daily_rates()

    if current_daily_rate == 0:
        if hourly_rate > 100:
            needed_targets, needed_minutes = get_needed_hourly_rate(
                campaign_minutes, target_count, needed_hourly_rate=100
            )
            message = (
                "There cannot be more than 100 emails per hour."
                f"You will need to reduce targets to {needed_targets}, "
                f"or increase minutes to {needed_minutes}."
            )
            return False, message
        if daily_rate > 1000:
            needed_targets, needed_minutes = get_needed_daily_rate(
                campaign_minutes, target_count, needed_daily_rate=1000
            )
            message = (
                "There cannot be more than 1000 emails per day. "
                f"You will need to reduce targets to {needed_targets}, "
                f"or increase minutes to {needed_minutes}."
            )
            return False, message
    else:
        percent_increase = get_daily_percent_increase(current_daily_rate, daily_rate)
        new_daily_rate = current_daily_rate + daily_rate
        if new_daily_rate <= 1000:
            return True, ""
        if percent_increase > 20:
            needed_targets, needed_minutes = get_needed_percent_increase(
                campaign_minutes,
                target_count,
                current_daily_rate,
                needed_percent_increase=20,
            )
            message = (
                "There cannot be more than a 20% increase in a 24 hour window. "
                f"You will need to reduce targets to {needed_targets}, "
                f"or increase minutes to {needed_minutes}."
            )
            return False, message

    return True, ""


def get_needed_hourly_rate(campaign_minutes, target_count, needed_hourly_rate=100):
    """
    Get needed hourly rate for initial campaigns.

    target_count / campaign_hours = hourly_rate
    needed_hourly_rate * campaign_hours = needed_target_count
    target_count / needed_hourly_rate = needed_campaign_hours
    """
    campaign_hours = campaign_minutes / 60

    # Given: hourly_rate = target_count / campaign_hours
    # Expected: needed_target_count = hourly_rate * campaign_hours
    needed_target_count = needed_hourly_rate * campaign_hours

    # Given: hourly_rate = target_count / campaign_hours
    # Expected: needed_campaign_hours = target_count / needed_hourly_rate
    needed_campaign_hours = target_count / needed_hourly_rate
    needed_campaign_minutes = needed_campaign_hours * 60
    return int(needed_target_count), needed_campaign_minutes


def get_needed_daily_rate(
    campaign_minutes, target_count, current_daily_rate=0, needed_daily_rate=1000
):
    """
    Get needed hourly rate for campaigns.

    needed_daily_rate - current_daily_rate = needed_daily_rate

    target_count / campaign_days = daily_rate
    needed_daily_rate * campaign_days = needed_target_count
    target_count / needed_daily_rate = needed_campaign_days
    """
    needed_daily_rate = needed_daily_rate - current_daily_rate
    campaign_days = campaign_minutes / (60 * 24)

    needed_target_count = needed_daily_rate * campaign_days

    needed_campaign_days = target_count / needed_daily_rate
    needed_campaign_minutes = needed_campaign_days * 60 * 24

    return int(needed_target_count), needed_campaign_minutes


def get_needed_percent_increase(
    campaign_minutes, target_count, current_daily_rate, needed_percent_increase=20
):
    """
    Get needed percent increase for campaigns.

    (rate_increase / current_rate) * 100 = percent_increase
    percent_increase / 100 = rate_increase / current_rate
    (needed_percent_increase / 100) * current_rate = rate_increase
    """
    rate_increase = needed_percent_increase / 100 * current_daily_rate
    increase_needed = current_daily_rate + rate_increase
    return get_needed_daily_rate(
        campaign_minutes=campaign_minutes,
        target_count=target_count,
        current_daily_rate=current_daily_rate,
        needed_daily_rate=increase_needed,
    )


def get_hourly_rate(target_count, campaign_minutes):
    """Get hourly rate of emails sent."""
    campaign_hours = campaign_minutes / 60
    return target_count / campaign_hours


def get_daily_rate(target_count, campaign_minutes):
    """Get daily rate of emails sent."""
    campaign_days = campaign_minutes / (60 * 24)
    return target_count / campaign_days


def get_all_daily_rates():
    """Get rates of all subscriptions."""
    subscriptions = subscription_service.get_list(
        parameters={"active": True}, fields=["cycles"]
    )
    daily_rate = 0
    for subscription in subscriptions:
        if subscription.get("cycles"):
            current_cycle = subscription["cycles"][-1]
            delta = (
                current_cycle.get("send_by_date", current_cycle["end_date"])
                - current_cycle["start_date"]
            )
            minutes = int(delta.total_seconds() / 60)
            daily_rate += get_daily_rate(current_cycle["total_targets"], minutes)
    return daily_rate


def get_daily_percent_increase(current_rate, increase):
    """Get the daily percentage increase of emails by the new subscription."""
    percent_change = (increase / current_rate) * 100
    return percent_change
