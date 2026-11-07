# DeepSeek semantic runtime profiles

This directory stores evidence-backed, version-local profiles. A profile is not a global class-name map and is not permission to install a Hook.

## Profile contract

- `schema_version`: profile schema version.
- `profile_id`: immutable build-specific identifier.
- `host_package`, `version`, `build`: APK identity supplied by repository evidence.
- `apk.sha256`: exact APK byte identity; profile is invalid for any other APK.
- `evidence.dynamic_runtime`: observed runtime facts and their scope.
- `evidence.static_dex`: extraction counts and tool-quality metadata.
- `semantic_nodes`: stable functional roles with version-local class/method descriptors.
- `hook_guidance`: safe observer-first order and explicit prohibited assumptions.
- `limitations`: known uncertainty that consumers must preserve.

## Matching rules

1. Never match by obfuscated class or method name alone.
2. Compare exact APK identity, normalized prototypes, inheritance/interfaces, field and method shape, external API call references, stable markers, and caller/callee context.
3. A candidate match is discovery evidence only. It does not authorize activation.
4. If two candidates are indistinguishable, return ambiguous and install nothing.
5. If a profile is incomplete, stale, or tied to a different APK hash, reject it.
6. Keep static DEX evidence separate from dynamic runtime evidence and device Hook verification.

## Current profile

- `deepseek-2.7.2-code289-cn.json`: dynamic request/transport/continuation observations correlated with the exact 2.7.2 DEX descriptors.
