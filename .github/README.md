# Manual source versions and releases

Run **Bump version** on a branch with its required `patch`, `minor`, or
`major` choice (default `patch`). It validates the immutable selected commit,
creates one source-only direct child as `github-actions[bot]`, and pushes only
that branch. It never builds, tags, releases, or starts Build. Both remote
reads and the executable committed pre-push guard reject stale branch
advertisements, including rewinds, deletions, and same-result races.

Run **Build** independently using Actions' built-in branch/tag selector.
There are no custom inputs. Every job checks out `github.sha`; the version
comes from the selected source, not a typed tag. Build is not restricted to
the default branch. Publication uses a single repository-wide concurrency
group with cancellation disabled; this does not promise FIFO ordering.

## Source authority

At intake `91f8db7d5b21d01a28e84ded6a10a9b68f6e9058`, API default,
symbolic `origin/HEAD`, and advertised HEAD all selected `master`.
The original Bump header, introduced by
`39d149d16f90ffb214eee70c4a5a85ccbf1ce981`, explicitly coordinates
`MARKETING_VERSION`, `CURRENT_PROJECT_VERSION`, and the two plist version
keys, despite its body updating only the selected project key.

The migration does not increment `1.0.4`. It narrowly aligns the six stale
`CURRENT_PROJECT_VERSION = 1.0.0` tokens and the actual copied source
`English.lproj/InfoPlist.strings` short/info `1.1` tokens to `1.0.4`.
The six configurations retain their original identities and
Development/Deployment/Default names. Source `Info.plist` requires its
short version; its absent build key remains absent. References are preserved
and resolved; conflicting, duplicate, cyclic, missing, or noncanonical fields
fail before writes. Edits preserve source encoding, BOM, individual line
endings, modes, and unrelated values.

The tracked prebuilt bundle, including its stale UTF-16 destination
localization, is not source authority and is unchanged by Bump or migration.
Manifest/4D counters, projects, resources, prebuilt Windows payloads and
runtime dependencies are otherwise preserved.

## Native scope

The original jobs remain: Ubuntu version preflight, Windows x64 Release
MSBuild, then macOS Default universal. The Windows CMD invocation retains
the v143 and Windows SDK 10.0 overrides. The exact project output is collected
with `rtfconv.dll`, `cnstbl.dll`, `mbctbl.dll`, and `sbctbl.dll`; the existing
PE import-closure verifier checks the binary and required DLLs. macOS retains
deployment target 11.0, exact required `arm64` and `x86_64` slices (extra
slices remain allowed), its frameworks, resources, and Windows artifact merge.
The original workflow did not inspect macOS runtime dylib architectures; this
migration does not add that restriction.

The dependency verifier stops on every failed `dumpbin` invocation, rather
than allowing a later successful image check to mask an earlier failure.
Windows checkout disables automatic newline conversion so the same raw-source
guard works on both platforms; Git index modes remain checked on NTFS even
though its files cannot represent POSIX executable bits.

The original target's custom legacy signing/altool shell phase is bypassed
only when the workflow's build explicitly sets `RTF2TEXT_MANUAL_RELEASE=1`.
All original commands remain unchanged for local Xcode builds without this
flag. This prevents duplicate legacy signing/notarization and deletion of
tracked unversioned ZIP/DMG files; the manual workflow owns signing and
notarization of its new versioned packages.

Cleanup is selective and symlink-prevalidated, not whole-bundle, lowercase
plugins, or Default-sibling deletion. Final validation retains generated
bytes and independently checks HEAD, index, hidden flags, raw nongenerated
bytes, and ignored/untracked paths. Only exact generated leaves and proven
intermediate paths are allowed. XCBuildData permits only `build.db`,
`build.db-wal`, `build.db-shm`, and 32-lowercase-hex `.xcbuilddata` descendants.
Unexpected ignored source, `build.db-evil`, and `evil.xcbuilddata` are rejected.
Built XML/binary plist, compiled/text localization and exact copied
`manifest.json`/`constants.xlf` are checked again at publication.

Developer ID signing, strict verification, two notary submissions, and DMG
stapling remain required. Notarization requires both exit zero and strict
JSON `status: Accepted`. Certificate/notary secrets are used only by the
manual hosted workflow. No local native/sign/notary/4D execution is required
for the offline tests.

## Create-only publication and recovery

Publication requires explicit nonempty `GH_TOKEN`, immutable `GITHUB_SHA`,
and the exact API-canonical identity `miyako/4d-plugin-RTF2TEXT`.
Authenticated release pages, including drafts, are read until an empty page;
strict JSON/schema checks fail closed. Exact API and Git tag absence is
checked before native work and after signing/notarization/stapling.

The publisher separately creates `vX.Y.Z` at the selected SHA, verifies it
through API and Git, creates a new public release with a new positive ID,
then uploads exactly `RTF2TEXT-X.Y.Z.zip` and `RTF2TEXT-X.Y.Z.dmg` to that ID.
The original empty body and disabled generated-notes policy are preserved.
There is no update, reuse, clobber, deletion, rollback, retry, or automatic
dispatch. A same-SHA tag creation race is still a failure.

On failure, inspect the reported retained tag, release ID and confirmed or
possibly uploaded assets manually. Partial state is deliberately retained.
Do not rerun an occupied version blindly; an operator must decide how to
recover, or bump source and manually build a new version.

## Offline regression suite

Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` and
`actionlint .github/workflows/*.yml`. Python needs PyYAML and Windows tests
need PowerShell. Native and credential commands run only behind closed-PATH
stubs; Git race tests use disposable local bare repositories. The original
CMD build is asserted statically, not replaced with a simulated CMD adapter.
The suite does not prove hosted toolchains, credentials, or Apple services.
