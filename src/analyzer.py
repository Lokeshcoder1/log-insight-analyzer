def classify_failure(status_code):
    if status_code == 504:
        return "TIMEOUT"

    if status_code in (401, 403):
        return "AUTHENTICATION_OR_AUTHORIZATION_FAILURE"

    if status_code == 400:
        return "INVALID_REQUEST"

    if status_code == 404:
        return "RESOURCE_NOT_FOUND"

    if status_code == 429:
        return "RATE_LIMITED"

    if 500 <= status_code <= 599:
        return "SERVER_ERROR"

    return "UNKNOWN"

def generate_diagnosis(root_cause):
    classification = classify_failure(root_cause["status_code"])

    if classification == "TIMEOUT":
        return {
            "summary": f"{root_cause['service']} timed out while processing the request.",
            "recommended_action": (
                "Check the service response time, upstream dependencies, "
                "and network connectivity."
            )
        }

    if classification == "AUTHENTICATION_OR_AUTHORIZATION_FAILURE":
        return {
            "summary": f"{root_cause['service']} rejected the request due to authentication or authorization.",
            "recommended_action": (
                "Verify API credentials, access tokens, permissions, "
                "and integration configuration."
            )
        }

    if classification == "INVALID_REQUEST":
        return {
            "summary": f"{root_cause['service']} rejected the request because the request data was invalid.",
            "recommended_action": (
                "Inspect the request payload and validate required fields, "
                "data types, and API contract."
            )
        }

    if classification == "RESOURCE_NOT_FOUND":
        return {
            "summary": f"{root_cause['service']} could not find the requested resource.",
            "recommended_action": (
                "Verify the resource identifier and check whether the "
                "resource exists in the downstream system."
            )
        }

    if classification == "RATE_LIMITED":
        return {
            "summary": f"{root_cause['service']} rejected the request because the rate limit was exceeded.",
            "recommended_action": (
                "Check API rate limits and request frequency. "
                "Consider retry or backoff handling."
            )
        }

    if classification == "SERVER_ERROR":
        return {
            "summary": f"{root_cause['service']} encountered an internal server error.",
            "recommended_action": (
                "Inspect the service logs and downstream dependencies "
                "for the failure."
            )
        }

    return {
        "summary": f"{root_cause['service']} returned an unexpected error.",
        "recommended_action": (
            "Inspect the service logs, request payload, and downstream dependencies."
        )
    }


def analyze_request(logs):
    if not logs:
        return {
            "status": "not_found",
            "message": "No logs found for this request"
        }

    logs.sort(key=lambda log: log["timestamp"])

    errors = [
        log for log in logs
        if log["log_level"] == "ERROR"
    ]

    if not errors:
        return {
            "status": "success",
            "message": "No errors detected",
            "event_count": len(logs)
        }

    root_cause = errors[0]

    classification = classify_failure(
        root_cause["status_code"])

    diagnosis=generate_diagnosis(root_cause)


    return {
        "status": "failed",
        "event_count": len(logs),
        "error_count": len(errors),
        "root_cause": {
            "service": root_cause["service"],
            "status_code": root_cause["status_code"],
            "classification": classification,
            "response_time": root_cause["response_time"],
            "message": root_cause["message"]
        },
        "diagnosis":diagnosis
    }