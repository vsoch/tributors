"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from tributors.utils.file import write_file, get_tmpfile
import logging
import os
import requests

bot = logging.getLogger("github")


def get_orcid_token():
    """If the user has exported a token, we discover and return it here.
       Otherwise we prompt him or her to open a browser and copy paste a code
       to the calling client.
    """
    orcid_token = os.environ.get("ORCID_TOKEN")
    orcid_id = os.environ.get("ORCID_ID")
    orcid_secret = os.environ.get("ORCID_SECRET")

    if not orcid_token and orcid_id is not None and orcid_secret is not None:
        response = requests.post(
            "https://orcid.org/oauth/token",
            headers={"Accept": "application/json"},
            data={
                "client_id": orcid_id,
                "client_secret": orcid_secret,
                "grant_type": "client_credentials",
                "scope": "/read-public",
            },
        )

        if response.status_code != 200:
            return

        response = response.json()
        orcid_token = response["access_token"]
        orcid_refresh = response["refresh_token"]

        # Write the token to file and direct the user to use it
        tmp_file = get_tmpfile()
        content = "export ORCID_TOKEN=%s\nexport ORCID_REFRESH_TOKEN=%s\n" % (
            orcid_token,
            orcid_refresh,
        )
        write_file(content, tmp_file)
        print(
            f"Orcid token exports written to {tmp_file}. "
            "In the future export these variables for headless usage."
        )

    return orcid_token


def record_search(url, token, email):
    response = requests.get(
        url,
        headers={"Authorization": "bearer %s" % token, "Accept": "application/json"},
    )
    if response.status_code != 200:
        return

    result = response.json().get("result", []) or []

    if not result:
        return

    # We found only one matching result
    if len(result) == 1:
        return result[0]["orcid-identifier"]["path"]

    # One or more results
    ids = "\n".join([x["orcid-identifier"]["path"] for x in result])
    bot.warning(
        f"Found {len(result)} results for {email}:\n\n{ids}\n"
        "You should look these up and add the correct in your .tributors lookup"
    )


def get_orcid(email, token, name=None):
    """Given a GitHub repository address, retrieve a lookup of contributors
       from the API endpoint. We look to use the GITHUB_TOKEN if exported
       to the environment, and exit if the response has any issue
    """
    # We must have a token, and an email OR name
    if not token and (not email and not name):
        return

    # First look for records based on email
    orcid_id = None
    if email:
        url = "https://pub.orcid.org/v3.0/search/?q=email:%s" % email
        orcid_id = record_search(url, token, email)

    # Attempt # 2 will use the first and last name
    if name is not None and not orcid_id:
        parts = name.split(" ")
        first, last = parts[0], " ".join(parts[1:])
        url = (
            "https://pub.orcid.org/v3.0/search/?q=given-names:%s+AND+family-name:%s"
            % (first, last)
        )
        orcid_id = record_search(url, token, name)

    return orcid_id
