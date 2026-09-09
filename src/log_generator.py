import random
from datetime import datetime, timedelta
from pathlib import Path


SERVICES = [
    "order-service",
    "payment-service",
    "customer-service",
    "pos-integration",
]


def generate_log(timestamp, request_id, order_id):
    # Decide what kind of event happens
    event_type = random.choices(
        ["success", "slow", "client_error", "server_error", "timeout"],
        weights=[70, 10, 8, 7, 5],
        k=1,
    )[0]

    service = random.choice(SERVICES)

    if event_type == "success":
        level = "INFO"
        status_code = random.choice([200, 201])
        response_time = random.randint(20, 300)
        message = "Request completed successfully"

    elif event_type == "slow":
        level = "WARNING"
        status_code = 200
        response_time = random.randint(1000, 3000)
        message = "Request completed but response was slow"

    elif event_type == "client_error":
        level = "WARNING"
        status_code = random.choice([400, 401, 403, 404])
        response_time = random.randint(50, 500)
        message = "Invalid client request"

    elif event_type == "server_error":
        level = "ERROR"
        status_code = random.choice([500, 502, 503])
        response_time = random.randint(300, 2000)
        message = "Internal service failure"

    else:
        level = "ERROR"
        status_code = 504
        response_time = 3000
        message = "Upstream service timeout"

    return (
        f"{timestamp:%Y-%m-%d %H:%M:%S} "
        f"{level} "
        f"{service} "
        f"request_id={request_id} "
        f"order_id={order_id} "
        f"status={status_code} "
        f"response_time={response_time}ms "
        f"{message}"
    )


def generate_logs(number_of_logs=1000):
    output_directory = Path("data/raw")
    output_directory.mkdir(parents=True, exist_ok=True)

    output_file = output_directory / "application.log"

    start_time = datetime.now() - timedelta(hours=1)

    with output_file.open("w", encoding="utf-8") as file:
        for i in range(number_of_logs):
            timestamp = start_time + timedelta(seconds=i * 5)

            request_id = f"req-{i + 1:06d}"
            order_id = f"ORD-{random.randint(10000, 99999)}"

            log = generate_log(
                timestamp,
                request_id,
                order_id,
            )

            file.write(log + "\n")

    print(f"Generated {number_of_logs} logs.")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    generate_logs()