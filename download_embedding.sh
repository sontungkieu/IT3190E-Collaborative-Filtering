#!/bin/bash

# ------------------------------------------------------------------------------
# Enhanced Bash script to download a large Google Drive file and move it into a “data” directory,
# correctly handling Google Drive’s “virus scan warning” page by extracting all hidden inputs
# (including confirm token and uuid) and using the form’s action URL.
#
# Usage:
#   1. Make this script executable:
#        chmod +x download_from_drive.sh
#   2. Run it:
#        ./download_from_drive.sh
#
# What it does:
#   1) Defines the FILEID of your shared Drive link.
#   2) Makes a first curl request (following redirects) to grab the HTML for the “Download anyway” form.
#   3) Parses that HTML to extract:
#        • action URL (e.g. https://drive.usercontent.google.com/download)
#        • confirm token (hidden input “confirm”)
#        • uuid (hidden input “uuid”)
#   4) Reconstructs the final download URL as:
#        <action_url>?id=<FILEID>&export=download&confirm=<confirm_token>&uuid=<uuid>
#   5) Uses curl (with –L and –b <cookie_jar>) to fetch the actual file bytes.
#   6) Verifies that the downloaded file is not an HTML page.
#   7) Creates “data/” if it doesn’t exist, then moves the file there.
#
# Adjust FILEID and OUTPUT_NAME below to match your use case.
# ------------------------------------------------------------------------------

# 1) Google Drive “file/d/<FILEID>/view” link’s ID:
FILEID="1cr-X9LIYzdd3WUeAdubGxzgulxvAW2ZE"

# 2) Output filename (including correct extension, e.g. .json, .zip, .pdf):
OUTPUT_NAME="output_embeddings.json"

# 3) Temporary cookie jar (unique per PID)
COOKIE_JAR="/tmp/gcookie_$$.txt"

# 4) Step 1: Fetch the HTML form containing the hidden inputs.
#    We use -L to follow any redirects and store cookies in COOKIE_JAR.
HTML_PAGE="$(curl -s -L -c "${COOKIE_JAR}" "https://drive.google.com/uc?export=download&id=${FILEID}")"

# 5) Parse the form’s action URL from the HTML. Example:
#      <form id="download-form" action="https://drive.usercontent.google.com/download" method="get">
#    We want: https://drive.usercontent.google.com/download
ACTION_URL="$(echo "${HTML_PAGE}" | grep -Po 'form[^>]*action="\Khttps?://[^"]+')"
if [ -z "${ACTION_URL}" ]; then
  echo "⚠️  Unable to find the form action URL in the HTML. Aborting."
  exit 1
fi

# 6) Parse the “confirm” token (hidden input name="confirm" value="…")
CONFIRM_TOKEN="$(echo "${HTML_PAGE}" | grep -Po 'name="confirm" value="\K[^"]+')"

# 7) Parse the “uuid” (hidden input name="uuid" value="…")
UUID="$(echo "${HTML_PAGE}" | grep -Po 'name="uuid" value="\K[^"]+')"

# 8) If no confirm token was found, we must still attempt a direct download URL.
if [ -n "${CONFIRM_TOKEN}" ]; then
  echo "ℹ️  Found confirm token: ${CONFIRM_TOKEN}"
  echo "ℹ️  Found uuid: ${UUID}"
  DOWNLOAD_URL="${ACTION_URL}?id=${FILEID}&export=download&confirm=${CONFIRM_TOKEN}&uuid=${UUID}"
else
  echo "ℹ️  No confirm token found; attempting direct-download URL instead."
  DOWNLOAD_URL="https://drive.google.com/uc?export=download&id=${FILEID}"
fi

# 9) Step 2: Actually download the file, following redirects and using the stored cookies.
curl -L -b "${COOKIE_JAR}" "${DOWNLOAD_URL}" -o "${OUTPUT_NAME}"

# 10) Clean up the temporary cookie jar
rm -f "${COOKIE_JAR}"

# 11) Verify that the first line of the saved file isn’t an HTML page:
FIRST_LINE="$(head -n 1 "${OUTPUT_NAME}" 2>/dev/null)"
if [[ "${FIRST_LINE}" == "<!DOCTYPE html>"* ]]; then
  echo "⚠️  Download appears to have returned HTML instead of the file."
  echo "   First line: ${FIRST_LINE}"
  echo "   Perhaps the confirm token failed or the FILEID is incorrect."
  exit 1
fi

echo "✅ Download succeeded: ${OUTPUT_NAME}"

# 12) Ensure “data” directory exists; if not, create it.
if [ ! -d "data" ]; then
  mkdir "data"
  echo "📂 Created directory: data/"
fi

# 13) Move the downloaded file into “data/”
mv "${OUTPUT_NAME}" data/
echo "📦 Moved '${OUTPUT_NAME}' ➔ data/${OUTPUT_NAME}"

# Done
