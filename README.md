# 4d-plugin-RTF2TEXT
Convert RTF to plain text

Using [RTF Converter](http://www5b.biglobe.ne.jp/~harigaya/e/rtfcnv.html#dll) on Windows, ``NSAttributedString`` on Mac.

### Platform

| carbon | cocoa | win32 | win64 |
|:------:|:-----:|:---------:|:---------:|
|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|

```
spctl -a -vv -t install RTF2TEXT.bundle: accepted
source=Notarized Developer ID
origin=Developer ID Application: keisuke miyako (Y69CWUC25B)
```

## Syntax

```
text:=RTF to text (rtf)
```

Parameter|Type|Description
------------|------------|----
rtf|BLOB|
text|TEXT|
