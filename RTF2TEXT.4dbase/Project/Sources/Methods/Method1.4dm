//%attributes = {}
$path:=Get 4D folder:C485(Current resources folder:K5:16)+"sample.rtf"

DOCUMENT TO BLOB:C525($path; $rtf)

$txt:=RTF to text($rtf)
