"""
Called by GH Actions when the nightly build fails.

This reports an error to the #nightly-build-failures Slack channel.
"""

import os

import requests

if "SLACK_WEBHOOK_URL" in os.environ:
    print("Reporting to #nightly-build-failures slack channel")  # noqa: T201
    response = requests.post(
        os.environ["SLACK_WEBHOOK_URL"],
        json={
            "text": (
                "A Nightly build failed. See "
                "https://github.com/wagtail/"
                "wagtail-modeladmin/actions/runs/"
                f'{os.environ["GITHUB_RUN_ID"]}',
            )
        },
    )

    print(f"Slack responded with: {response}")  # noqa: T201

else:
    print(  # noqa: T201
        "Unable to report to #nightly-build-failures slack channel because "
        "SLACK_WEBHOOK_URL is not set"
    )
