from django.http import HttpRequest, HttpResponse

from zerver.decorator import webhook_view
from zerver.lib.response import json_success
from zerver.lib.typed_endpoint import JsonBodyPayload, typed_endpoint
from zerver.lib.validator import WildValue, check_string
from zerver.lib.webhooks.common import check_send_webhook_message
from zerver.models import UserProfile


def handle_build_event(
    request: HttpRequest, user_profile: UserProfile, data: WildValue, action: str
) -> None:
    app_name = data["app"]["name"].tame(check_string)
    user_email = data["user"]["email"].tame(check_string)
    status = data["status"].tame(check_string)

    # Use output_stream_url if present, otherwise fallback to dashboard URL
    output_stream_url = data.get("output_stream_url")
    if output_stream_url:
        details_url = output_stream_url.tame(check_string)
    else:
        details_url = f"https://dashboard.heroku.com/apps/{app_name}/activity"

    topic = f"{app_name} / Build"

    if action == "create":
        body = f"{user_email} triggered a build for app **{app_name}**."
    elif action == "update":
        body = f"Build triggered by {user_email} **{status}**. [View Log]({details_url})"
    else:
        return

    check_send_webhook_message(request, user_profile, topic, body)


def handle_release_event(
    request: HttpRequest, user_profile: UserProfile, data: WildValue, action: str
) -> None:
    app_name = data["app"]["name"].tame(check_string)
    user_email = data["user"]["email"].tame(check_string)
    status = data["status"].tame(check_string)
    description = data["description"].tame(check_string)

    topic = f"{app_name} / Release"

    if action == "create":
        body = f"{user_email} triggered a release ({description}) for app **{app_name}**."
    elif action == "update":
        body = f"Release ({description}) triggered by {user_email} **{status}**."
    else:
        return

    check_send_webhook_message(request, user_profile, topic, body)


@webhook_view("Heroku")
@typed_endpoint
def api_heroku_webhook(
    request: HttpRequest,
    user_profile: UserProfile,
    *,
    payload: JsonBodyPayload[WildValue],
) -> HttpResponse:
    
    # Heroku sends the interesting data in the "data" dictionary
    data = payload["data"]
    resource = payload["resource"].tame(check_string)  # "build" or "release"
    action = payload["action"].tame(check_string)      # "create", "update"

    # 1. Handle BUILD events
    if resource == "build":
        handle_build_event(request, user_profile, data, action)
    
    # 2. Handle RELEASE events
    elif resource == "release":
        handle_release_event(request, user_profile, data, action)

    # Ignore other events
    return json_success(request)