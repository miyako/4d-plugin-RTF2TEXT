/* rtfconv.h */
/* This header file is for RTFCONV.DLL */

/* by Harigaya Soichi */
/* updated at 8 Mar 2009 */

/* Please include <windows.h> before "rtfconv.h" */

#ifndef RTFCONV_H
#define RTFCONV_H

#ifdef __cplusplus
extern "C" {
#endif


#include <stddef.h>

#if defined _MSC_VER && _MSC_VER < 1300 || defined __BORLANDC__ && __BORLANDC__ < 1370
#ifndef _INTPTR_T_DEFINED
#define _INTPTR_T_DEFINED
#ifdef _WIN64
  typedef __int64 intptr_t ;
#else
  typedef int intptr_t ;
#endif
#endif
#endif



typedef struct {
   size_t cbSize ;
   const char *pEuropean ;
   const char *pJapanese ;
   const char *pChineseSimplified ;
   const char *pChineseTraditional ;
   const char *pKorean ;
   const char *pThai ;
} RTFFONTINFO ;



typedef struct {
   int C ;
   const char *pFontName ;
} RTFFONTEXINFO ;



typedef struct {
   int C ;
   int nLangId ;
} RTFLANGIDINFO ;



typedef struct {

   size_t cbSize ;
   unsigned long dwConversionMode ;
   unsigned long dwAdditionalMode ;
   const char *pUnmappableCharFormat ;

// Writing RTF
   int nDefaultCjkCodePage ;
   int nFontSize ;
   const RTFFONTINFO *pFontInfo ;

   const RTFFONTEXINFO *pFontExInfo ;
   size_t nNumberOfFontExInfo ;

   const RTFLANGIDINFO *pLangIdInfo ;
   size_t nNumberOfLangIdInfo ;

// Reserved
   const void *pReserved ;

} RTFCONVEXINFO ;




/* Functions */
int WINAPI RtfconvExA ( const char *pSrcFileName, const char *pDstFileName, int nSrcCodePage, int nDstCodePage, const RTFCONVEXINFO *pRtfconvExInfo ) ;
int WINAPI RtfconvExW ( const wchar_t *pSrcFileName, const wchar_t *pDstFileName, int nSrcCodePage, int nDstCodePage, const RTFCONVEXINFO *pRtfconvExInfo ) ;
intptr_t WINAPI RtfconvStringEx ( const void *pSrcBuffer, void *pDstBuffer, int nSrcCodePage, int nDstCodePage, const RTFCONVEXINFO *pRtfconvExInfo, size_t nMaxLen ) ;
int WINAPI RtfconvCharEx ( int C, int nSrcCodePage, int nDstCodePage, const RTFCONVEXINFO *pRtfconvExInfo ) ;
int WINAPI IsRtfconvValidCodePage ( int nCodePage ) ;
int WINAPI GetRtfconvLastError ( void ) ;
int WINAPI AbortRtfconv ( void ) ;
int WINAPI GetDllVersion ( void ) ;


#ifdef UNICODE
#define RtfconvEx RtfconvExW
#else
#define RtfconvEx RtfconvExA
#endif



/* for Backward Compatibility */
/* Obsolete Functions, not thread-safe */
int WINAPI RtfconvA ( const char *pSrcFileName, const char *pDstFileName, int nSrcCodePage, int nDstCodePage, unsigned long dwConversionMode ) ;
int WINAPI RtfconvW ( const wchar_t *pSrcFileName, const wchar_t *pDstFileName, int nSrcCodePage, int nDstCodePage, unsigned long dwConversionMode ) ;
intptr_t WINAPI RtfconvString ( const void *pSrcBuffer, void *pDstBuffer, int nSrcCodePage, int nDstCodePage, unsigned long dwConversionMode, size_t nMaxLen ) ;
int WINAPI RtfconvChar ( int C, int nSrcCodePage, int nDstCodePage, unsigned long dwConversionMode ) ;
int WINAPI SetUnicodeFormat ( const char *pFormat ) ;
int WINAPI SetFontName ( int nCodePage, const char *pFontName ) ;
int WINAPI SetFontNameEx ( int nUnicode, const char *pFontName ) ;
int WINAPI SetDefaultCodePage ( int nCodePage ) ;
int WINAPI SetFontSize ( int nSize ) ;
int WINAPI SetLangId ( int nUnicode, int nLangId ) ;
int WINAPI SetAdditionalMode ( unsigned long dwMode ) ;
int WINAPI PrintFileStartA ( int nDstCodePage, const char *pDstFileName ) ;
int WINAPI PrintFileStartW ( int nDstCodePage, const wchar_t *pDstFileName ) ;
int WINAPI PrintFileEndA ( int nDstCodePage, const char *pDstFileName ) ;
int WINAPI PrintFileEndW ( int nDstCodePage, const wchar_t *pDstFileName ) ;
intptr_t WINAPI PrintFileStartString ( int nDstCodePage, void *pDstBuffer, size_t nMaxLen ) ;
intptr_t WINAPI PrintFileEndString ( int nDstCodePage, void *pDstBuffer, size_t nMaxLen ) ;
int WINAPI SetRtfconvWindow ( HWND hWnd, int IsDialog ) ;
#ifndef CHNCONV_H
int WINAPI IsAvailableCodePage ( int nCodePage ) ;
#endif


#ifdef UNICODE
#define Rtfconv RtfconvW
#define PrintFileStart PrintFileStartW
#define PrintFileEnd PrintFileEndW
#else
#define Rtfconv RtfconvA
#define PrintFileStart PrintFileStartA
#define PrintFileEnd PrintFileEndA
#endif



/* Return Values of RtfconvEx, GetRtfconvLastError */
#define RTFCONV_SUCCESS          0
#define RTFCONV_ERROR_UNKNOWN    1
#define RTFCONV_ERROR_READ       2
#define RTFCONV_ERROR_WRITE      3
#define RTFCONV_ERROR_RTFFORMAT  4
#define RTFCONV_ERROR_RTFBRACE   5
#define RTFCONV_ERROR_MEMORY     6
#define RTFCONV_ERROR_CODEPAGE   7
#define RTFCONV_ERROR_ABORTED    8
#define RTFCONV_ERROR_SEMAPHORE  9
#define RTFCONV_ERROR_PARAM      10


/* for Backward Compatibility */
/* Return Values of RtfconvEx, GetRtfconvLastError */
#define RTFCONV_ERROR_OVERFLOW   RTFCONV_ERROR_MEMORY



/* for dwConversionMode */
#define CONVMODE_OUTPUT_CODE_NUMBER                   1
#define CONVMODE_NO_VARIANT_KANJI                     2
#define CONVMODE_NO_VARIANT_EUROPEAN                  4
#define CONVMODE_CONVERT_PUA                          8
#define CONVMODE_NO_HANKANA                        0x10
#define CONVMODE_NO_ZENALPHA                       0x20
#define CONVMODE_NO_ZENSPACE                       0x40
#define CONVMODE_NO_ZENSYMBOL                      0x80
#define CONVMODE_USE_LOCAL_FONT                   0x100
#define CONVMODE_NO_GBK                           0x200
#define CONVMODE_NO_CW                            0x400
#define CONVMODE_OUTPUT_GB18030                   0x800
#define CONVMODE_OUTPUT_CR                       0x1000
#define CONVMODE_OUTPUT_LF                       0x2000
#define CONVMODE_OUTPUT_HIDDEN                   0x4000
#define CONVMODE_EUC_HOJO                        0x8000
#define CONVMODE_USE_DLL_TABLE                  0x10000
#define CONVMODE_NO_OUTPUT_BOM                  0x20000
#define CONVMODE_ENDIAN_AUTO                    0x40000
#define CONVMODE_OUTPUT_LINK                    0x80000
#define CONVMODE_OUTPUT_RUBY                   0x100000
#define CONVMODE_OUTPUT_CODE_NUMBER_HTML       0x200000
#define CONVMODE_INPUT_CODE_NUMBER_HTML        0x400000
#define CONVMODE_USE_SYSTEM_TABLE              0x800000
#define CONVMODE_YEN_NO_BACKSLASH             0x1000000
#define CONVMODE_UTF8_WITH_BOM                0x2000000
#define CONVMODE_OUTPUT_NUMBER_SURROGATE      0x4000000
#define CONVMODE_VARIANT_ONLY_ROUNDTRIP       0x8000000
#define CONVMODE_DELETE_EOF                  0x10000000
#define CONVMODE_INPUT_CODE_NUMBER_C         0x20000000
#define CONVMODE_PEEKMESSAGE                 0x80000000

#define CONVMODE_NO_VARIANT            (CONVMODE_NO_VARIANT_KANJI|CONVMODE_NO_VARIANT_EUROPEAN)


/* for Backward Compatibility */
/* for dwConversionMode */
#define CONVMODE_NOT_OUTPUT_BOM           CONVMODE_NO_OUTPUT_BOM
#define CONVMODE_VARIANT_ONLY_ROUNDABLE   CONVMODE_VARIANT_ONLY_ROUNDTRIP
#define CONVMODE_CONVERT_DBCS_PUA         CONVMODE_CONVERT_PUA



/* for dwAdditionalMode */
#define ADDITIONAL_MODE_PUA_TO_HKSCS                  1
#define ADDITIONAL_MODE_HKSCS_CJKB_TO_PUA             2
#define ADDITIONAL_MODE_HKSCS_CJKA_TO_PUA             4
#define ADDITIONAL_MODE_HKSCS_ALL_TO_PUA              8
#define ADDITIONAL_MODE_HKSCS_CJK41_TO_PUA         0x10
#define ADDITIONAL_MODE_GBK_TO_LINSHIDAIMA         0x20
#define ADDITIONAL_MODE_LINSHIDAIMA_TO_GBK         0x40
#define ADDITIONAL_MODE_GBK_OUTPUT_FANTIZI         0x80
#define ADDITIONAL_MODE_JIS_OUTPUT_NO_VENDOR      0x100
#define ADDITIONAL_MODE_JIS_INPUT_MAC             0x200
#define ADDITIONAL_MODE_JIS_OUTPUT_MAC            0x400
#define ADDITIONAL_MODE_JIS_INPUT_NO_VENDOR       0x800
#define ADDITIONAL_MODE_JIS_NO_JIS83_NEW_STYLE   0x1000
#define ADDITIONAL_MODE_JIS_NO_JIS83_OLD_STYLE   0x2000
#define ADDITIONAL_MODE_JIS_INPUT_2004           0x4000
#define ADDITIONAL_MODE_JIS_OUTPUT_2004          0x8000
#define ADDITIONAL_MODE_KS_NO_UHC               0x10000
#define ADDITIONAL_MODE_KS_PUNC                 0x20000
#define ADDITIONAL_MODE_OVERLINE_NO_TILDE       0x40000
#define ADDITIONAL_MODE_RTFFONT_XP             0x100000
#define ADDITIONAL_MODE_RTFFONT_VISTA          0x200000
#define ADDITIONAL_MODE_HKSCS_1999           0x20000000
#define ADDITIONAL_MODE_HKSCS_2001           0x40000000
#define ADDITIONAL_MODE_HKSCS_2004           0x80000000


/* for Backward Compatibility */
/* for dwAdditionalMode */
#define ADDITIONAL_MODE_GBK_TO_PUA     ADDITIONAL_MODE_GBK_TO_LINSHIDAIMA
#define ADDITIONAL_MODE_PUA_TO_GBK     ADDITIONAL_MODE_LINSHIDAIMA_TO_GBK
#define ADDITIONAL_MODE_GBKLD_TO_PUA   ADDITIONAL_MODE_GBK_TO_LINSHIDAIMA
#define ADDITIONAL_MODE_PUA_TO_GBKLD   ADDITIONAL_MODE_LINSHIDAIMA_TO_GBK
#define ADDITIONAL_MODE_JIS_NO_VENDOR  ADDITIONAL_MODE_JIS_OUTPUT_NO_VENDOR



/* Definitions of Codepage */
/* Following definitions are same as definitions of Windows. */

/* DOS */
#define CP_US                    437      /* US ASCII as known as OEM */
#define CP_ARABIC_ASMO_708       708      /* Arabic (ASMO 708) */
#define CP_ARABIC_ASMO_449P      709      /* Arabic (ASMO 449+) */
#define CP_ARABIC_TPASMO         720      /* Arabic (Transparent ASMO, DOS) */
#define CP_GREEK                 737      /* Greek (formerly 437G) */
#define CP_BALTIC                775      /* Baltic */
#define CP_EUROPEAN              850      /* European (MS-DOS) as knonw as Latin 1 */
#define CP_CENTRAL_EUROPEAN      852      /* Central European (MS-DOS) as knonw as Latin 2 */
#define CP_TURKISH_OLD           853      /* Turkish (MS-DOS) Latin 3 */
#define CP_CYRILLIC              855      /* Cyrillic (IBM) */
#define CP_HEBREW_OLD            856      /* Hebrew (IBM) */
#define CP_TURKISH               857      /* Turkish (IBM) */
#define CP_PORTUGUESE            860      /* Portuguese (MS-DOS) */
#define CP_ICELANDIC             861      /* Icelandic (MS-DOS) */
#define CP_HEBREW                862      /* Hebrew */
#define CP_CANADIAN_FRENCH       863      /* Canadian French (MS-DOS) */
#define CP_ARABIC                864      /* Arabic */
#define CP_NORDIC                865      /* Nordic (MS-DOS) */
#define CP_RUSSIAN               866      /* Russian (MS-DOS) */
#define CP_MODERN_GREEK          869      /* Modern Greek (IBM) */
#define CP_CZECH                 895      /* Czech (Kamenicky CS) */

/* DOS & Windows */
#define CP_THAI                  874      /* Thai */
#define CP_JAPANESE              932      /* Japanese (Shift-JIS) */
#define CP_CHINESE_SIMPLIFIED    936      /* Chinese Simplified (GB2312/GBK) */
#define CP_KOREAN                949      /* Korean (EUC-KR) */
#define CP_CHINESE_TRADITIONAL   950      /* Chinese Traditional (BIG5) */

/* UTF-16 */
#define CP_UTF16                 1200     /* Unicode UTF-16 (Little Endian) */
#define CP_UTF16_BE              1201     /* Unicode UTF-16 (Big Endian) */

/* Windows */
#define CP_ANSI_CENTRAL_EUROPEAN 1250     /* Central European (Windows) */
#define CP_ANSI_CYRILLIC         1251     /* Cyrillic (Windows) */
#define CP_ANSI_EUROPEAN         1252     /* Western European (Windows) */
#define CP_ANSI_GREEK            1253     /* Greek (Windows) */
#define CP_ANSI_TURKISH          1254     /* Turkish (Windows) */
#define CP_ANSI_HEBREW           1255     /* Hebrew (Windows) */
#define CP_ANSI_ARABIC           1256     /* Arabic (Windows) */
#define CP_ANSI_BALTIC           1257     /* Baltic (Windows) */
#define CP_ANSI_VIETNAMESE       1258     /* Vietnamese (Windows) */

/* Korean DOS */
#define CP_KOREAN_JOHAB          1361     /* Korean (Johab) */

/* Macintosh */  /* only valid in version 5.20 or later */
#define CP_MAC_EUROPEAN          10000    /* European (Mac) */
#define CP_MAC_ARABIC            10004    /* Arabic (Mac) */
#define CP_MAC_HEBREW            10005    /* Hebrew (Mac) */
#define CP_MAC_GREEK             10006    /* Greek (Mac) */
#define CP_MAC_CYRILLIC          10007    /* Cyrillic (Mac) */
#define CP_MAC_ROMANIAN          10010    /* Romanian (Mac) */
#define CP_MAC_UKRAINIAN         10017    /* Ukrainian (Mac) */
#define CP_MAC_THAI              10021    /* Thai (Mac) */
#define CP_MAC_CENTRAL_EUROPEAN  10029    /* Central European (Mac) */
#define CP_MAC_ICELANDIC         10079    /* Icelandic (Mac) */
#define CP_MAC_TURKISH           10081    /* Turkish (Mac) */
#define CP_MAC_CROATIAN          10082    /* Croatian (Mac) */

/* US-ASCII */
#define CP_US_ASCII              20127    /* US-ASCII 7-bit */

/* KOI8 */
#define CP_CYRILLIC_KOI8R        20866    /* Cyrillic (KOI8-R) */
#define CP_CYRILLIC_KOI8U        21866    /* Cyrillic (KOI8-U) */

/* ISO */
#define CP_ISO_EUROPEAN          28591    /* Western European (ISO-8859-1) as known as Latin 1 */
#define CP_ISO_CENTRAL_EUROPEAN  28592    /* Central European (ISO-8859-2) as known as Latin 2 */
#define CP_ISO_TURKISH_OLD       28593    /*        (ISO-8859-3) as known as Latin 3 */
#define CP_ISO_BALTIC            28594    /* Baltic (ISO-8859-4) as known as Latin 4 */
#define CP_ISO_CYRILLIC          28595    /* Cyrillic (ISO-8859-5) as known as Latin 5 */
#define CP_ISO_ARABIC            28596    /* Arabic (ISO-8859-6) */
#define CP_ISO_GREEK             28597    /* Greek (ISO-8859-7) as known as Latin 7 */
#define CP_ISO_HEBREW_VISUAL     28598    /* Hebrew (ISO-8859-8) */
#define CP_ISO_TURKISH           28599    /* Turkish (ISO-8859-9) as known as Latin 8 */
/* the following ISO codepages are only valid in version 5.30 or later */
#define CP_ISO_NORDIC            28600    /* Nordic (ISO-8859-10) Latin 6 */
#define CP_ISO_BALTIC_EX         28603    /* Baltic (ISO-8859-13)  Latin 7 */
#define CP_ISO_CELTIC            28604    /* Celtic (ISO-8859-14)  Latin 8 */
#define CP_ISO_EUROPEAN_EX       28605    /* Western European Extended (ISO-8859-15)  Latin 9 */
#define CP_ISO_CENTRAL_EUROPEAN_EX  28606    /* Central European Extended (ISO-8859-16)  Latin 10 */

/* Other Asian Character Codes */
#define CP_ISO_JAPANESE             50220    /* Japanese (ISO-2022-JP) */
#define CP_ISO_KOREAN               50225    /* Korean (ISO-2022-KR) */
#define CP_EUC_JAPANESE             51932    /* Japanese (EUC-JP) */
#define CP_HZ_CHINESE_SIMPLIFIED    52936    /* Chinese Simplified (HZ) */
#define CP_CHINESE_SIMPLIFIED_EX    54936    /* Chinese Simplified (GB18030) */

/* ISCII */  /* only valid in version 4.30 or later */
#define CP_ISCII_DEVANAGARI      57002    /* Devanagari */
#define CP_ISCII_BENGALI         57003    /* Bengali */
#define CP_ISCII_TAMIL           57004    /* Tamil */
#define CP_ISCII_TELUGU          57005    /* Telugu */
#define CP_ISCII_ASSAMESE        57006    /* Assamese */
#define CP_ISCII_ORIYA           57007    /* Oriya */
#define CP_ISCII_KANNADA         57008    /* Kannada */
#define CP_ISCII_MALAYALAM       57009    /* Malayalam */
#define CP_ISCII_GUJARATHI       57010    /* Gujarathi */
#define CP_ISCII_PANJABI         57011    /* Panjabi */

/* RTFCONV-specific definition */
#define CP_GEORGIAN                 58000    /* Georgian (GEOSTD8) */
#define CP_ARMENIAN                 58001    /* Armenian (ARMSCII-8) */
#define CP_ARMENIAN_8A              58002    /* Armenian (ARMSCII-8A) */
#define CP_GEORGIAN_AC              58003    /* Georgian (Georgian Academy) */
#define CP_GEORGIAN_PS              58004    /* Georgian (Georgian Parliament-Soros) */
#define CP_CYRILLIC_KOI8RU          58010    /* Cyrillic (KOI8-RU) */
#define CP_CYRILLIC_KOI8T           58011    /* Cyrillic (KOI8-T) */
#define CP_CYRILLIC_KOI8C           58012    /* Cyrillic (KOI8-C) */
#define CP_CYRILLIC_KOI8O           58013    /* Cyrillic (KOI8-O) */
#define CP_CYRILLIC_KOI8UNI         58014    /* Cyrillic (KOI8-UNI) */
#define CP_CYRILLIC_ISOIR111        58015    /* Cyrillic (ISO-IR-111, ECMA-Cyrillic) */
#define CP_CYRILLIC_ASIAN           58017    /* Cyrillic (Cyrillc Asian) */
#define CP_CYRILLIC_KAZ             58018    /* Cyrillic (KZ-1048) */
#define CP_PERSIAN_ISIRI            58060    /* Farsi (ISIRI-3342) */
#define CP_TAMIL_TSCII              58100    /* Tamil (TSCII) */
#define CP_TAMIL_TAM                58101    /* Tamil (Tamil Monolingual) */
#define CP_TAMIL_TAB                58102    /* Tamil (Tamil Bilingual) */
#define CP_VIETNAMESE_TCVN          58200    /* Vietnamese (TCVN-1) */
#define CP_VIETNAMESE_VISCII        58201    /* Vietnamese (VISCII) */
#define CP_VIETNAMESE_VPS           58202    /* Vietnamese (VPS) */
#define CP_VIETNAMESE_VNI           58203    /* Vietnamese (VNI) */
#define CP_VIETNAMESE_VIQR          58204    /* Vietnamese (Vietnamese Quoted-Readable) */
#define CP_VIETNAMESE_TCVN2         58205    /* Vietnamese (TCVN-2) */
#define CP_VIETNAMESE_TCVN3         58206    /* Vietnamese (TCVN-3) */
#define CP_CHINESE_HKSCS              951    /* Chinese Traditional (BIG5+HKSCS) */
#define CP_EUC_CHINESE_TRADITIONAL  58950    /* Chinese Traditional (EUC) */

/* UTF-7/8 */
#ifndef CP_UTF7
#define CP_UTF7                  65000    /* Unicode UTF-7 */
#endif
#ifndef CP_UTF8
#define CP_UTF8                  65001    /* Unicode UTF-8 */
#endif

/* UTF-32 */
#define CP_UTF32                 65005    /* Unicode UTF-32 */
#define CP_UTF32_BE              65006    /* Unicode UTF-32 (Big Endian) */



/* for Backward Compatibility */
#define CP_JIS_JAPANESE          CP_ISO_JAPANESE
#define CP_UNICODE_BIG           CP_UNICODE_BE
#define CP_ISO_BALTIC_RIM        CP_ISO_BALTIC_EX
#define CP_MAC_WESTERN_EUROPEAN  CP_MAC_EUROPEAN
#ifndef CP_UNICODE
#define CP_UNICODE               CP_UTF16
#endif
#define CP_UNICODE_BE            CP_UTF16_BE
#define CP_UTF_7                 CP_UTF7
#define CP_UTF_8                 CP_UTF8
#define CP_UTF_32                CP_UTF32
#define CP_UTF_32_BE             CP_UTF32_BE



/******************************** GB18030 ******************************************
 * In specification of SOURCE codepage, CP_CHINESE_SIMPLIFIED (936) is equivalent
   to CP_CHINESE_SIMPLIFIED_EX (54936).
 * In specification of DESTINATION codepage, CP_CHINESE_SIMPLIFIED (936) with
   CONVMODE_OUTPUT_GB18030 is equivalent to CP_CHINESE_SIMPLIFIED_EX (54936).
************************************************************************************/


#ifdef __cplusplus
}
#endif

#endif
