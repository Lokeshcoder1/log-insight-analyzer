from datetime import datetime
from pathlib import Path
import re


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2}) "
    r"(?P<log_level>\w+) "
    r"(?P<service>\S+) "
    r"request_id=(?P<request_id>\S+) "
    r"order_id=(?P<order_id>\S+) "
    r"status=(?P<status_code>\d+) "
    r"response_time=(?P<response_time>\d+)ms "
    r"(?P<message>.*)$"
)


def parse_log_line(line):
    match = LOG_PATTERN.match(line.strip())

    if not match:
        return None

    data = match.groupdict()

    data["timestamp"] = datetime.strptime(
        data["timestamp"],
        "%Y-%m-%d %H:%M:%S",
    )

    data["status_code"] = int(data["status_code"])
    data["response_time"] = int(data["response_time"])

    return data


def parse_log_file(file_path):
    parsed_logs = []
    invalid_lines = 0

    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            parsed_log = parse_log_line(line)

            if parsed_log is None:
                invalid_lines += 1
                continue

            parsed_logs.append(parsed_log)

    print(f"Parsed logs: {len(parsed_logs)}")
    print(f"Invalid logs: {invalid_lines}")

    return parsed_logs


if __name__ == "__main__":
    log_file = Path("data/raw/application.log")

    logs = parse_log_file(log_file)

    for log in logs[:5]:
        print(log)