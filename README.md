# 4d-plugin-RTF2TEXT

RTF2TEXT converts RTF (Rich Text Format) data into plain text. On Windows it drives the third-party [RTF Converter](http://www5b.biglobe.ne.jp/~harigaya/e/rtfcnv.html#dll) DLL; on macOS it drives Cocoa's built-in `NSAttributedString` RTF importer. Input is a `Blob` containing raw RTF bytes; output is a `Text` value containing the extracted plain text, with all RTF formatting/markup stripped.

| Command | Returns | Purpose |
|---|---|---|
| [RTF to text](#rtf-to-text) | Text | Convert an RTF `Blob` to plain `Text` |

**Platforms:** macOS, Windows

Manual source-only **Bump version** and independent zero-input **Build**
workflows are documented in [the release guide](.github/README.md).

---

## Requirements & platform notes

- **On Windows**, the plugin depends on the RTF Converter DLL (`rtfcnv.dll`, from the third-party [RTF Converter](http://www5b.biglobe.ne.jp/~harigaya/e/rtfcnv.html#dll) project). This DLL must be present alongside the plugin for the command to function — the plugin itself does not embed the RTF parsing logic on Windows.
- **On macOS**, RTF parsing is done via `NSAttributedString`'s built-in RTF document-type support (part of Foundation/AppKit) — there is no separate DLL/framework to install.
- There is exactly one mandatory parameter; there is no optional/overloaded form of this command.
- **Failure is silent, not a 4D error.** If the input isn't valid RTF (or is empty/corrupt), the command returns an empty `Text` rather than raising a 4D error — see [Error handling](#error-handling--troubleshooting) below.
- The command is documented (`manifest.json`) as thread-safe, so it's safe to call from preemptive/worker processes as well as the main process.

---

## RTF to text

### Syntax

```4d
text:=RTF to text(rtf)
```

| Parameter | Type | Description |
|---|---|---|
| `rtf` | Blob | Raw RTF document bytes to convert |
| Result | Text | Plain text extracted from `rtf`, with RTF markup removed |

### Description

`RTF to text` takes a `Blob` of RTF bytes and returns the plain-text content of the document, discarding all RTF formatting codes (fonts, colors, styles, etc.) — only the readable text survives.

The conversion is platform-specific, and while the two platforms are expected to produce equivalent plain text for well-formed RTF, they use entirely different underlying engines, so exact whitespace/line-break handling at the edges of malformed or unusual RTF is not guaranteed to be identical between macOS and Windows.

If the `Blob` doesn't contain parseable RTF (empty, truncated, or corrupt data), the command does not raise a 4D error — it simply returns an empty `Text`. Always check the result rather than assuming a non-empty document guarantees non-empty output.

### Example

```4d
// Read an RTF file into a Blob, then convert it to plain text
var $rtf : Blob
var $text : Text

DOCUMENT TO BLOB("letter.rtf"; $rtf)
$text:=RTF to text($rtf)

If ($text#"")
	ALERT($text)
Else
	ALERT("Could not extract text — check that the file is valid RTF")
End if
```

```4d
// Converting RTF content already held in memory (e.g. from a BLOB field)
var $text : Text

$text:=RTF to text([Notes]rtfContent)
[Notes]plainText:=$text
```

---

## Error handling & troubleshooting

- **Empty result instead of an error.** An invalid, empty, or corrupt `rtf` `Blob` produces an empty `Text` result, not a 4D error — always test the returned text (`If ($text#"")`) rather than relying on error-catching.
- **Missing DLL on Windows.** If `rtfcnv.dll` isn't deployed alongside the plugin on a Windows machine, RTF conversion will fail (silently returning empty text, per the point above) even for valid RTF input. Confirm the DLL is present in your plugin's Windows Resources when troubleshooting a Windows-only failure that doesn't reproduce on Mac.
- **No Linux support.** This plugin has no Linux build — it's Mac/Windows only, consistent with 4D's own supported server/client platforms.
- **Very large or unusual RTF documents.** Conversion of an extremely large or malformed RTF blob returns an empty `Text` rather than hanging or crashing 4D — you'll get back an empty string, not a stuck process, but it's still worth validating the size/source of RTF you feed in if you're processing untrusted documents in bulk.

---

## Quick reference

```4d
var $rtf : Blob
var $text : Text

DOCUMENT TO BLOB("letter.rtf"; $rtf)
$text:=RTF to text($rtf)
```

## Native helper ownership

The exported command is scalar-only: both source and bundled manifests declare
`RTF to text(&O):T`, and dispatcher selector 1 calls `RTF_to_text`. It copies the
input BLOB and returns text through the SDK's content setter, not a shallow
text-array transfer. The picture and array helpers are compiled by Xcode and
both Visual Studio projects, but the dispatcher does not call them.

The picture helpers retain pictures stored in `CPicture`; temporary owning
references must be released after that retain. Command input picture arguments
start undefined before shallow assignment, avoiding an overwritten owning empty
picture. String arguments use the content setter on their initialized string,
and are cleared once after the synchronous command. Returned picture handoffs
are detached from the temporary argument and remain owned by their caller.
Charset conversion returns **bytes**; `createCopy` divides by the UTF-16 unit
size before constructing its string.

The bundled SDK implementation (`4D Plugin API/4DPluginAPI.c`) is the ownership
reference; its v14 comment and the headers' v13 comments are not verified SDK
release identifiers. `PA_SetStringInArray` disposes the old element and shallowly
transfers the descriptor only for a Unicode array with data, an index from zero
through its element count, and a non-null descriptor pointer. Rejections leave
the caller owning the string. `PA_GetStringInArray` is borrowed.
`ARRAY_TEXT` copies borrowed input into C++ strings and creates an independent
descriptor for each output; it must not dispose accepted transfers.

Run the non-release native regression on macOS:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_ownership.py -v
```

It directly compiles the actual dispatcher, every wrapper translation unit and
the full unchanged bundled SDK with an engine-boundary shim, ASan and UBSan.
The same harness verifies named failures of immutable baseline
`c669cd5c1ea4e90dd854fe794a324b4533f11472` and fixed-source passes. Fixtures cover
ASCII, BMP, supplementary and empty text; allocated and null empty strings;
borrowed copies, independent transfers, replacement, shrink, clear and rejected
assignments; synchronous argument cleanup and owning picture handoff survival.
It checks exact contents, lengths, terminators and string/handle/picture balances
explicitly (LeakSanitizer is disabled on macOS). SDK structs are two-byte packed,
so UBSan alignment checking alone is disabled. A synthetic RTF check also runs
the actual macOS dispatcher/Cocoa importer. No Windows converter or actual 4D
host execution is implied. No signing, packaging or release target is invoked.

The bounded audit also includes all numeric/date/time/Boolean array and scalar
wrappers, `C_BLOB`, `C_TEXT`, `C_POINTER`, their headers, SDK platform/type/entry
headers, build include/compile lists and the third-party converter declaration
(not modified). This SDK has no object-property or collection-element getter
API. Pointer-value metadata ownership in dormant `C_POINTER::getVariable` and
SDK-only application-path/picture-format output ownership remain unverified;
no speculative cleanup is added. The unrelated SDK resize-allocation-failure
count corruption is not certified by normal-array tests or changed here.
