import random
from datetime import datetime, timedelta
from pathlib import Path


SERVICES = [
    "pos-integration",
    "order-service",
    "payment-service",
]

FLOW_TYPES = [
    "success",
    "payment_failure",
    "payment_timeout",
]

FLOW_WEIGHTS = [75, 15, 10]


def create_event(
    timestamp,
    level,
    service,
    request_id,
    order_id,
    status_code,
    response_time,
    message,
):
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


def generate_request_flow(timestamp, request_id, order_id):
    flow_type = random.choices(
        FLOW_TYPES,
        weights=FLOW_WEIGHTS,
        k=1,
    )[0]

    events = []

    # 1. POS sends the order
    events.append(
        create_event(
            timestamp,
            "INFO",
            "pos-integration",
            request_id,
            order_id,
            200,
            random.randint(30, 150),
            "Order received from POS",
        )
    )

    timestamp += timedelta(seconds=1)

    # 2. Order service validates the order
    events.append(
        create_event(
            timestamp,
            "INFO",
            "order-service",
            request_id,
            order_id,
            200,
            random.randint(20, 120),
            "Order validated successfully",
        )
    )

    timestamp += timedelta(seconds=1)

    # 3. Payment service
    if flow_type == "success":
        events.append(
            create_event(
                timestamp,
                "INFO",
                "payment-service",
                request_id,
                order_id,
                200,
                random.randint(50, 300),
                "Payment processed successfully",
            )
        )

        timestamp += timedelta(seconds=1)

        events.append(
            create_event(
                timestamp,
                "INFO",
                "order-service",
                request_id,
                order_id,
                201,
                random.randint(20, 150),
                "Order completed successfully",
            )
        )

    elif flow_type == "payment_failure":
        events.append(
            create_event(
                timestamp,
                "ERROR",
                "payment-service",
                request_id,
                order_id,
                500,
                random.randint(500, 1500),
                "Payment processing failed",
            )
        )

        timestamp += timedelta(seconds=1)

        events.append(
            create_event(
                timestamp,
                "ERROR",
                "order-service",
                request_id,
                order_id,
                500,
                random.randint(50, 200),
                "Order failed because payment failed",
            )
        )

    else:
        events.append(
            create_event(
                timestamp,
                "ERROR",
                "payment-service",
                request_id,
                order_id,
                504,
                3000,
                "Payment service timeout",
            )
        )

        timestamp += timedelta(seconds=1)

        events.append(
            create_event(
                timestamp,
                "ERROR",
                "order-service",
                request_id,
                order_id,
                504,
                random.randint(50, 200),
                "Order failed because payment service timed out",
            )
        )

    return events


def generate_logs(number_of_requests=250):
    output_directory = Path("data/raw")
    output_directory.mkdir(parents=True, exist_ok=True)

    output_file = output_directory / "application.log"

    start_time = datetime.now() - timedelta(hours=1)

    with output_file.open("w", encoding="utf-8") as file:
        current_time = start_time

        for i in range(number_of_requests):
            request_id = f"req-{i + 1:06d}"
            order_id = f"ORD-{random.randint(10000, 99999)}"

            events = generate_request_flow(
                current_time,
                request_id,
                order_id,
            )

            for event in events:
                file.write(event + "\n")

            current_time += timedelta(seconds=5)

    print(f"Generated logs for {number_of_requests} requests.")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    generate_logs()