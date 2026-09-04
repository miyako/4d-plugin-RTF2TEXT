# 4d-plugin-RTF2TEXT

RTF2TEXT converts RTF (Rich Text Format) data into plain text. On Windows it drives the third-party [RTF Converter](http://www5b.biglobe.ne.jp/~harigaya/e/rtfcnv.html#dll) DLL; on macOS it drives Cocoa's built-in `NSAttributedString` RTF importer. Input is a `Blob` containing raw RTF bytes; output is a `Text` value containing the extracted plain text, with all RTF formatting/markup stripped.

| Command | Returns | Purpose |
|---|---|---|
| [RTF to text](#rtf-to-text) | Text | Convert an RTF `Blob` to plain `Text` |

**Platforms:** macOS, Windows

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
