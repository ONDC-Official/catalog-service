import isodate
from isodate import ISO8601Error

from logger.custom_logging import log_error


def calculate_duration_in_seconds(iso8601dur: str):
    try:
        duration = isodate.parse_duration(iso8601dur)
        return duration.total_seconds()
    except ISO8601Error:
        log_error(f"Got error while parsing iso8601 string {iso8601dur}")
        return 0


if __name__ == '__main__':
    print(calculate_duration_in_seconds("P"))