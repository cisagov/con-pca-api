"""Database Tools."""
# Standard Python Libraries
import datetime


def parse_datetime(
    value,
    formats=(
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%f%Z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d",
    ),
):
    """Parse Datetime."""
    for time_format in formats:
        try:
            value = datetime.datetime.strptime(value, time_format)
            return value.astimezone(datetime.timezone.utc)
        except ValueError:
            pass
    raise ValueError(f"Cannot parse {value} as a datetime.datetime object")
