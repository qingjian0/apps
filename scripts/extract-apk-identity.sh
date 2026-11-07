#!/usr/bin/env bash
set -euo pipefail

APK="${1:?usage: bash scripts/extract-apk-identity.sh APK OUTPUT_DIR}"
OUT="${2:?usage: bash scripts/extract-apk-identity.sh APK OUTPUT_DIR}"
if [[ ! -s "$APK" ]]; then
  echo "APK is missing or empty: $APK" >&2
  exit 2
fi

SDK_ROOT="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-/usr/local/lib/android/sdk}}"
if [[ ! -d "$SDK_ROOT/build-tools" ]]; then
  echo "Android SDK build-tools directory not found: $SDK_ROOT/build-tools" >&2
  exit 3
fi

APKSIGNER="$(find "$SDK_ROOT/build-tools" -type f -name apksigner -print | sort -V | tail -n 1)"
AAPT="$(find "$SDK_ROOT/build-tools" -type f -name aapt -print | sort -V | tail -n 1)"
if [[ -z "$APKSIGNER" || -z "$AAPT" ]]; then
  echo "apksigner and aapt are required from Android SDK build-tools" >&2
  exit 4
fi

mkdir -p "$OUT"
sha256sum "$APK" > "$OUT/apk.sha256"
"$AAPT" dump badging "$APK" > "$OUT/aapt-badging.txt"
"$APKSIGNER" verify --verbose --print-certs "$APK" > "$OUT/apksigner-verify.txt" 2>&1

python3 - "$APK" "$OUT" "$APKSIGNER" "$AAPT" <<'PY'
import hashlib
import json
import pathlib
import re
import subprocess
import sys

apk = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
apksigner = sys.argv[3]
aapt = sys.argv[4]
badging = (out / "aapt-badging.txt").read_text(errors="replace")
signing = (out / "apksigner-verify.txt").read_text(errors="replace")

package = re.search(
    r"^package: name='([^']+)' versionCode='([^']+)' versionName='([^']*)'",
    badging, re.MULTILINE
)
if not package:
    raise SystemExit("aapt did not emit a parseable package/version identity")

certs = sorted(set(re.findall(
    r"Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F]{64})", signing
)))
if not certs:
    raise SystemExit("apksigner did not emit any signer certificate SHA-256 digest")

aggregate = hashlib.sha256()
aggregate.update(b"roi-host-signers-v1\n")
for cert in certs:
    aggregate.update(cert.lower().encode("ascii"))
    aggregate.update(b"\n")

schemes = {}
for match in re.finditer(
    r"Verified using (v[0-9]+) scheme \([^\n]+\): (true|false)", signing
):
    schemes[match.group(1)] = match.group(2) == "true"

identity = {
    "apk_file": apk.name,
    "apk_bytes": apk.stat().st_size,
    "apk_sha256": hashlib.sha256(apk.read_bytes()).hexdigest(),
    "package_name": package.group(1),
    "version_code": int(package.group(2)),
    "version_name": package.group(3),
    "signer_certificate_sha256": aggregate.hexdigest(),
    "signer_certificates_sha256": [x.lower() for x in certs],
    "signature_schemes_verified": schemes,
    "identity_scope": "repository_base_apk_only",
    "split_apk_set_included": False,
    "tools": {
        "apksigner": subprocess.check_output([apksigner, "version"], text=True).strip(),
        "aapt": pathlib.Path(aapt).name,
    },
}
if identity["package_name"] != "com.deepseek.chat":
    raise SystemExit("unexpected APK package: " + identity["package_name"])
(out / "apk-identity.json").write_text(json.dumps(identity, indent=2) + "\n")
print(json.dumps(identity, indent=2))
PY
