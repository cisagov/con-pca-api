"""Validity utils."""
# Standard Python Libraries
import math

# cisagov Libraries
from api.manager import CycleManager

cycle_manager = CycleManager()


def is_subscription_valid(target_count, cycle_minutes):
    """
    Check to see if subscription is valid and will remain within required rates for warmup.

    No more than 100 total emails an hour and no more than 1000 per day on first subscription.

    No more than a 20% increase in any given 24 hour window.

    For more details, check this documentation https://www.mailgun.com/blog/domain-warmup-reputation-stretch-before-you-send/.
    """
    daily_rate = get_daily_rate(target_count, cycle_minutes)
    hourly_rate = get_hourly_rate(target_count, cycle_minutes)
    current_daily_rate = get_all_daily_rates()

    if current_daily_rate == 0:
        if hourly_rate > 100:
            needed_targets, needed_minutes = get_needed_hourly_rate(
                cycle_minutes, target_count, needed_hourly_rate=100
            )
            message = (
                "There cannot be more than 100 emails per hour."
                f"You will need to reduce targets to {needed_targets}, "
                f"or increase minutes to {needed_minutes}."
            )
            return False, message
        if daily_rate > 1000:
            needed_targets, needed_minutes = get_needed_daily_rate(
                cycle_minutes, target_count, needed_daily_rate=1000
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
                cycle_minutes,
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


def get_hourly_rate(target_count, cycle_minutes):
    """Get hourly rate of emails sent."""
    cycle_hours = cycle_minutes / 60
    return target_count / cycle_hours


def get_daily_rate(target_count, cycle_minutes):
    """Get daily rate of emails sent."""
    cycle_days = cycle_minutes / (60 * 24)
    return target_count / cycle_days


def get_daily_percent_increase(current_rate, increase):
    """Get the daily percentage increase of emails by the new subscription."""
    percent_change = (increase / current_rate) * 100
    return percent_change


def get_needed_hourly_rate(cycle_minutes, target_count, needed_hourly_rate=100):
    """
    Get needed hourly rate for initial cycles.

    target_count / cycle_hours = hourly_rate
    needed_hourly_rate * cycle_hours = needed_target_count
    target_count / needed_hourly_rate = needed_cycle_hours
    """
    cycle_hours = cycle_minutes / 60

    # Given: hourly_rate = target_count / cycle_hours
    # Expected: needed_target_count = hourly_rate * cycle_hours
    needed_target_count = needed_hourly_rate * cycle_hours

    # Given: hourly_rate = target_count / cycle_hours
    # Expected: needed_cycle_hours = target_count / needed_hourly_rate
    needed_cycle_hours = target_count / needed_hourly_rate
    needed_cycle_minutes = needed_cycle_hours * 60
    return math.ceil(needed_target_count), math.ceil(needed_cycle_minutes)


def get_needed_daily_rate(
    cycle_minutes, target_count, current_daily_rate=0, needed_daily_rate=1000
):
    """
    Get needed hourly rate for cycles.

    needed_daily_rate - current_daily_rate = needed_daily_rate

    target_count / cycle_days = daily_rate
    needed_daily_rate * cycle_days = needed_target_count
    target_count / needed_daily_rate = needed_cycle_days
    """
    needed_daily_rate = needed_daily_rate - current_daily_rate
    cycle_days = cycle_minutes / (60 * 24)

    needed_target_count = needed_daily_rate * cycle_days

    needed_cycle_days = target_count / needed_daily_rate
    needed_cycle_minutes = needed_cycle_days * 60 * 24

    return math.ceil(needed_target_count), math.ceil(needed_cycle_minutes)


def get_needed_percent_increase(
    cycle_minutes, target_count, current_daily_rate, needed_percent_increase=20
):
    """
    Get needed percent increase for cycles.

    (rate_increase / current_rate) * 100 = percent_increase
    percent_increase / 100 = rate_increase / current_rate
    (needed_percent_increase / 100) * current_rate = rate_increase
    """
    rate_increase = needed_percent_increase / 100 * current_daily_rate
    increase_needed = current_daily_rate + rate_increase
    return get_needed_daily_rate(
        cycle_minutes=cycle_minutes,
        target_count=target_count,
        current_daily_rate=current_daily_rate,
        needed_daily_rate=increase_needed,
    )


def get_all_daily_rates():
    """Get rates of all subscriptions."""
    cycles = cycle_manager.all(
        params={"active": True},
        fields=[
            "target_count",
            "start_date",
            "send_by_date",
        ],
    )
    daily_rate = 0
    for cycle in cycles:
        delta = cycle["send_by_date"] - cycle["start_date"]
        minutes = int(delta.total_seconds() / 60)
        daily_rate += get_daily_rate(cycle["target_count"], minutes)
    return daily_rate
