#!/usr/bin/env python3
"""Validate a semantic profile against an APKTool Smali tree and APK summary."""
import argparse
import json
import pathlib
import re
import sys

METHOD = re.compile(r"^([^\s]+)$")

def parse_smali(root):
    classes = {}
    for path in pathlib.Path(root).rglob("*.smali"):
        try:
            lines = path.read_text(errors="replace").splitlines()
        except OSError:
            continue
        descriptor = None
        superclass = None
        interfaces = set()
        fields = set()
        methods = set()
        for line in lines:
            value = line.strip()
            if value.startswith(".class "):
                match = re.search(r"\b(L[^;]+;)", value)
                if match:
                    descriptor = match.group(1)
            elif value.startswith(".super "):
                superclass = value.split()[-1]
            elif value.startswith(".implements "):
                interfaces.add(value.split()[-1])
            elif value.startswith(".field "):
                fields.add(value.split()[-1])
            elif value.startswith(".method "):
                methods.add(value.split()[-1])
        if descriptor:
            classes[descriptor] = {
                "path": str(path),
                "super": superclass,
                "interfaces": interfaces,
                "fields": fields,
                "methods": methods,
            }
    return classes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--smali-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    profile = json.loads(pathlib.Path(args.profile).read_text())
    summary = json.loads(pathlib.Path(args.summary).read_text())
    apk_hash = summary.get("sha256") or summary.get("apk_sha256")
    expected_hash = profile.get("apk", {}).get("sha256")
    if not expected_hash or apk_hash != expected_hash:
        raise SystemExit("APK identity mismatch: profile SHA-256 does not match extracted APK")

    classes = parse_smali(args.smali_root)
    if not classes:
        raise SystemExit("No Smali class descriptors found")

    missing = []
    checked_classes = 0
    checked_methods = 0
    checked_fields = 0
    for role, node in profile.get("semantic_nodes", {}).items():
        owner = node.get("class")
        if not owner:
            continue
        actual = classes.get(owner)
        if actual is None:
            missing.append({"role": role, "class": owner, "kind": "class"})
            continue
        checked_classes += 1
        if node.get("super") and node["super"] != actual["super"]:
            missing.append({"role": role, "class": owner, "kind": "super",
                            "expected": node["super"], "actual": actual["super"]})
        for interface in node.get("interfaces", []):
            if interface not in actual["interfaces"]:
                missing.append({"role": role, "class": owner, "kind": "interface",
                                "expected": interface})
        expected_methods = []
        expected_methods.extend(node.get("methods", []))
        expected_methods.extend(node.get("constructors", []))
        if node.get("method"):
            expected_methods.append(node["method"])
        if node.get("constructor"):
            expected_methods.append(node["constructor"])
        for method in expected_methods:
            if "->" in method:
                method_owner, method = method.split("->", 1)
                if method_owner != owner:
                    missing.append({"role": role, "class": owner, "kind": "method-owner",
                                    "expected": method_owner})
                    continue
            checked_methods += 1
            if method not in actual["methods"]:
                missing.append({"role": role, "class": owner, "kind": "method",
                                "expected": method})
        for field in node.get("fields", []):
            checked_fields += 1
            if field not in actual["fields"]:
                missing.append({"role": role, "class": owner, "kind": "field",
                                "expected": field})

    result = {
        "profile_id": profile.get("profile_id"),
        "apk_sha256": apk_hash,
        "smali_classes_indexed": len(classes),
        "profile_classes_checked": checked_classes,
        "profile_methods_checked": checked_methods,
        "profile_fields_checked": checked_fields,
        "missing_count": len(missing),
        "missing": missing,
        "status": "validated" if not missing else "failed",
    }
    pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if not missing else 1

if __name__ == "__main__":
    sys.exit(main())
