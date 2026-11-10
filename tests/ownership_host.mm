#include "4DPluginAPI.h"
#include "PrivateTypes.h"
#include "EntryPoints.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <string>

static void require(bool value, const char* message)
{
    if (!value) {
        std::fprintf(stderr, "ownership: %s\n", message);
        std::exit(1);
    }
}

static std::map<PA_Unichar*, size_t> strings;
static std::map<PA_Handle, size_t> handles;
static std::map<PA_Picture, unsigned> pictures;
static bool nullEmpty;
static bool commandFailure;
static CUTF16String expected;

static CUTF16String utf16(const char* bytes, size_t count)
{
    CFStringRef s = CFStringCreateWithBytes(NULL, (const UInt8*)bytes, count,
                                          kCFStringEncodingUTF8, false);
    require(s != NULL, "valid synthetic UTF-8");
    CUTF16String result(CFStringGetLength(s), 0);
    if (!result.empty())
        CFStringGetCharacters(s, CFRangeMake(0, result.size()), &result[0]);
    CFRelease(s);
    return result;
}

static PA_Unistring makeString(const PA_Unichar* source)
{
    size_t length = 0;
    if (source)
        while (source[length]) ++length;
    PA_Unistring result = {};
    if (length || !nullEmpty) {
        result.fString = (PA_Unichar*)std::malloc((length + 1) * sizeof(PA_Unichar));
        require(result.fString != NULL, "allocate string");
        strings[result.fString] = length;
        if (length) std::memcpy(result.fString, source, length * sizeof(PA_Unichar));
        result.fString[length] = 0;
    }
    result.fLength = length;
    return result;
}

static void disposeString(PA_Unistring s)
{
    if (!s.fString) {
        require(s.fLength == 0, "null string length");
        return;
    }
    require(strings.erase(s.fString) == 1, "double disposal or borrowed string disposal");
    std::free(s.fString);
}

static void checkString(PA_Unistring s, const CUTF16String& wanted)
{
    require(s.fLength == (PA_long32)wanted.size(), "exact UTF-16 length");
    if (!s.fString) {
        require(wanted.empty(), "null only represents empty");
        return;
    }
    require(strings.count(s.fString) == 1, "string survives consumer");
    require(strings.at(s.fString) == wanted.size(), "allocation matches content");
    require(CUTF16String(s.fString, s.fLength) == wanted, "exact UTF-16 content");
    require(s.fString[s.fLength] == 0, "string terminator");
}

static PA_Picture newPicture()
{
    void* p = std::malloc(1);
    require(p != NULL, "allocate picture");
    pictures[p] = 1;
    return p;
}

static void releasePicture(PA_Picture p)
{
    if (!p) return;
    require(pictures.count(p) == 1, "picture is live");
    if (--pictures[p] == 0) {
        pictures.erase(p);
        std::free(p);
    }
}

static void clearVariable(PA_Variable* v)
{
    if (v->fType == eVK_Unistring) {
        disposeString(v->uValue.fString);
    } else if (v->fType == eVK_Picture) {
        releasePicture(v->uValue.fPicture);
    } else if (v->fType == eVK_ArrayUnicode) {
        PA_Handle h = v->uValue.fArray.fData;
        require(handles.count(h) == 1, "array handle is live");
        auto* elements = (PA_Unistring*)*h;
        for (PA_long32 i = 0; i <= v->uValue.fArray.fNbElements; ++i)
            disposeString(elements[i]);
        PA_DisposeHandle(h);
    }
    *v = {};
    v->fType = eVK_Undefined;
}

static void host(short selector, EngineBlock* eb)
{
    eb->fError = eER_NoErr;
    switch (selector) {
        case EX_CREATE_UNISTRING:
            eb->fUniString1 = makeString((PA_Unichar*)eb->fHandle);
            break;
        case EX_DISPOSE_UNISTRING:
            disposeString(eb->fUniString1);
            break;
        case EX_SET_UNISTRING: {
            PA_Unistring copy = makeString((PA_Unichar*)eb->fHandle);
            disposeString(eb->fUniString1);
            eb->fUniString1 = copy;
            break;
        }
        case EX_CLEAR_VARIABLE:
            clearVariable((PA_Variable*)eb->fPtr1);
            break;
        case EX_CREATE_PICTURE:
            eb->fPicture = newPicture();
            break;
        case EX_DISPOSE_PICTURE:
            releasePicture(eb->fPicture);
            break;
        case EX_DUPLICATE_PICTURE:
            if (eb->fPicture) {
                require(pictures.count(eb->fPicture) == 1, "retain live picture");
                if (eb->fParam1 == 0) ++pictures[eb->fPicture];
                else eb->fPicture = newPicture();
            }
            break;
        case EX_GET_PICTURE_DATA:
            // No representations. Failed output is deliberately unspecified;
            // the wrapper must inspect the error before using it.
            eb->fError = eER_IdxPgOutOfRange;
            std::memset(&eb->fUniString1, 0xa5, sizeof(eb->fUniString1));
            break;
        case EX_HANDLE_MANAGER: {
            PA_Handle h = eb->fHandle;
            switch (eb->fParam1) {
                case 1:
                    h = (PA_Handle)std::malloc(sizeof(char*));
                    require(h != NULL, "allocate handle");
                    *h = (char*)std::calloc(1, eb->fParam2 ? eb->fParam2 : 1);
                    require(*h != NULL, "allocate handle data");
                    handles[h] = eb->fParam2;
                    eb->fHandle = h;
                    break;
                case 2:
                    require(handles.erase(h) == 1, "dispose live handle");
                    std::free(*h);
                    std::free(h);
                    break;
                case 3: {
                    require(handles.count(h) == 1, "resize live handle");
                    char* data = (char*)std::realloc(*h, eb->fParam2 ? eb->fParam2 : 1);
                    require(data != NULL, "resize handle data");
                    *h = data;
                    handles[h] = eb->fParam2;
                    break;
                }
                case 4:
                    eb->fParam2 = handles.at(h);
                    break;
                case 5:
                    require(handles.count(h) == 1, "lock live handle");
                    eb->fParam3 = (sLONG_PTR)*h;
                    break;
                case 6:
                    require(handles.count(h) == 1, "unlock live handle");
                    break;
                default:
                    require(false, "unexpected handle operation");
            }
            break;
        }
        case EX_CONVERT_CHARSET_TO_CHARSET: {
            require(eb->fParam2 == eVTC_UTF_8 && eb->fParam4 == eVTC_UTF_16,
                    "conversion fixture direction");
            CUTF16String converted = utf16((char*)eb->fPtr1, eb->fParam1);
            size_t bytes = converted.size() * sizeof(PA_Unichar);
            require(bytes <= (size_t)eb->fParam3, "byte capacity");
            if (bytes) std::memcpy(eb->fPtr2, converted.data(), bytes);
            // No terminator is promised; the caller owns its extra zeroed space.
            eb->fParam3 = bytes;
            break;
        }
        case EX_EXECUTE_COMMAND_BY_ID: {
            auto** args = (PA_Variable**)eb->fPtr1;
            auto* result = (PA_Variable*)eb->fPtr2;
            require(result->fType == eVK_Undefined, "void command return");
            if (eb->fParam1 == 678) {
                checkString(args[0]->uValue.fString, expected);
                if (!commandFailure) {
                    PA_ClearVariable(args[1]);
                    PA_SetPictureVariable(args[1], newPicture());
                }
            } else if (eb->fParam1 == 1002) {
                checkString(args[1]->uValue.fString, expected);
                require(pictures.count(args[0]->uValue.fPicture) == 1, "conversion input survives");
            } else if (eb->fParam1 == 457) {
                require(pictures.count(args[0]->uValue.fPicture) == 1, "borrowed picture survives");
                PA_SetLongintVariable(args[1], 17);
                PA_SetLongintVariable(args[2], 23);
            } else if (eb->fParam1 == 679) {
                require(pictures.count(args[0]->uValue.fPicture) == 1, "thumbnail input survives");
                PA_ClearVariable(args[1]);
                PA_SetPictureVariable(args[1], newPicture());
            } else {
                require(eb->fParam1 == 988, "known synchronous picture command");
                require(pictures.count(args[0]->uValue.fPicture) == 1, "transform input survives");
            }
            if (commandFailure) eb->fError = eER_IncompatibleTypes;
            break;
        }
        default:
            std::fprintf(stderr, "unexpected engine selector: %d\n", selector);
            require(false, "unimplemented engine operation");
    }
}

static void balanced()
{
    require(strings.empty(), "string allocation balance");
    require(handles.empty(), "handle allocation balance");
    require(pictures.empty(), "picture reference balance");
}

static void pictureCase(const std::string& name)
{
    const char* fixtures[] = {"", "ascii.png", "\xe6\x97\xa5\xe6\x9c\xac.png",
                             "\xf0\x9f\x98\x80.png"};
    for (const char* fixture : fixtures) {
        expected = utf16(fixture, std::strlen(fixture));
        CPicture p;
        if (name == "file") {
            CUTF8String path((const uint8_t*)fixture);
            p.fromFileAtPath(&path);
            require(pictures.count(p.getPicture()) == 1, "file output retained after args cleanup");
        } else if (name == "copy") {
            PA_Picture copy = p.createCopy(fixture);
            require(pictures.count(copy) == 1, "owning conversion handoff survives");
            PA_DisposePicture(copy);
        } else if (name == "gray") {
            PA_Picture copy = p.createGrayScale();
            require(pictures.count(copy) == 1, "owning grayscale handoff survives");
            PA_DisposePicture(copy);
        } else if (name == "size") {
            unsigned width = 0, height = 0;
            p.getSize(&width, &height);
            require(width == 17 && height == 23, "picture dimensions");
        } else if (name == "thumbnail") {
            PA_Picture copy = p.createThumbnail(17, 23);
            require(pictures.count(copy) == 1, "owning thumbnail handoff survives");
            PA_DisposePicture(copy);
        } else if (name == "bytes") {
            const uint8_t bytes[] = {1, 2, 3};
            p.setBytes(bytes, sizeof(bytes));
            p.setBytes(bytes, sizeof(bytes));
            require(pictures.count(p.getPicture()) == 1, "setBytes retains result");
        } else {
            require(false, "known picture test");
        }
    }
    balanced();
}

static void arrayCase()
{
    PA_Variable array = PA_CreateVariable(eVK_ArrayUnicode);
    PA_ResizeArray(&array, 4);
    BytePtr params[] = {(BytePtr)&array};
    {
        ARRAY_TEXT source;
        const PA_Unichar zero[] = {0};
        const PA_Unichar ascii[] = {'A', 'S', 'C', 'I', 'I', 0};
        const PA_Unichar bmp[] = {0x65e5, 0x672c, 0};
        const PA_Unichar supplementary[] = {0xd83d, 0xde00, 0};
        source.appendUTF16String(zero);
        source.appendUTF16String(ascii);
        source.appendUTF16String(bmp);
        source.appendUTF16String(supplementary);
        source.appendUTF16String(ascii);
        source.toParamAtIndex(params, 1);
        require(PA_GetStringInArray(array, 1).fString !=
                PA_GetStringInArray(array, 4).fString, "independent repeated transfers");
        ARRAY_TEXT copied;
        copied.fromParamAtIndex(params, 1);
        PA_Unistring borrowed = PA_GetStringInArray(array, 1);
        C_TEXT scalarCopy;
        scalarCopy.setUTF16String(&borrowed);
        PA_ResizeArray(&array, 0);
        PA_ClearVariable(&array);
        copied.toParamAtIndex(params, 1);
        const CUTF16String wanted[] = {CUTF16String(), CUTF16String(ascii),
            CUTF16String(bmp), CUTF16String(supplementary), CUTF16String(ascii)};
        for (int i = 0; i < 5; ++i) checkString(PA_GetStringInArray(array, i), wanted[i]);
        require(CUTF16String(scalarCopy.getUTF16StringPtr()) == wanted[1], "borrowed scalar copied");
        for (int i = 0; i < 128; ++i) {
            PA_Unistring churn = PA_CreateUnistring((PA_Unichar*)ascii);
            PA_DisposeUnistring(&churn);
        }
        for (int i = 0; i < 5; ++i) checkString(PA_GetStringInArray(array, i), wanted[i]);
        copied.toParamAtIndex(params, 1);
        copied.setSize(2);
        copied.toParamAtIndex(params, 1);
    }
    PA_Unistring owned = PA_CreateUnistring((PA_Unichar*)expected.c_str());
    PA_Variable wrong = PA_CreateVariable(eVK_Longint);
    PA_SetStringInArray(wrong, 0, &owned);
    PA_SetStringInArray(array, -1, &owned);
    PA_SetStringInArray(array, 2, &owned);
    PA_Variable noData = array;
    noData.uValue.fArray.fData = NULL;
    PA_SetStringInArray(noData, 0, &owned);
    PA_SetStringInArray(array, 0, NULL);
    checkString(owned, expected);
    PA_DisposeUnistring(&owned);
    PA_ClearVariable(&array);
    balanced();
}

static void scalarCase()
{
    const PA_Unichar text[] = {'A', 0x65e5, 0xd83d, 0xde00, 0};
    const CUTF16String wanted(text);
    PA_Unistring result = PA_CreateUnistring(NULL);
    {
        C_TEXT value;
        value.setUTF16String(text, wanted.size());
        PA_Unistring* resultPtr = &result;
        value.setReturn((sLONG_PTR*)&resultPtr);
    }
    checkString(result, wanted);
    PA_DisposeUnistring(&result);
    PA_Unistring nullString = {};
    C_TEXT empty;
    empty.setUTF16String(&nullString);
    require(empty.getUTF16Length() == 0, "null empty input");
    PA_Unistring owned = PA_CreateUnistring((PA_Unichar*)text);
    PA_Variable variable = PA_CreateVariable(eVK_Undefined);
    PA_SetStringVariable(&variable, &owned);
    require(variable.uValue.fString.fString == owned.fString, "scalar setter shallow alias");
    checkString(variable.uValue.fString, wanted);
    PA_ClearVariable(&variable);
    // The local descriptor is now a stale alias, not a second owner to dispose.
    balanced();
}

static void dispatcherCase()
{
    const char* rtf[] = {
        "{\\rtf1\\ansi ASCII}",
        "{\\rtf1\\ansi\\uc1 \\u26085?\\u26412?}",
        "{\\rtf1\\ansi\\uc1 \\u-10179?\\u-8704?}",
        "{\\rtf1\\ansi }",
    };
    const PA_Unichar ascii[] = {'A', 'S', 'C', 'I', 'I', 0};
    const PA_Unichar bmp[] = {0x65e5, 0x672c, 0};
    const PA_Unichar supplementary[] = {0xd83d, 0xde00, 0};
    const CUTF16String wanted[] = {CUTF16String(ascii), CUTF16String(bmp),
                                  CUTF16String(supplementary), CUTF16String()};
    for (int repeat = 0; repeat < 3; ++repeat) {
        for (int i = 0; i < 4; ++i) {
            PA_Handle blob = PA_NewHandle(std::strlen(rtf[i]));
            std::memcpy(*blob, rtf[i], std::strlen(rtf[i]));
            BytePtr args[] = {(BytePtr)&blob};
            PA_Unistring result = PA_CreateUnistring(NULL);
            PA_Unistring* resultPtr = &result;
            PluginBlock block = {args, &resultPtr, NULL};
            PluginMain(1, &block);
            checkString(result, wanted[i]);
            PA_DisposeUnistring(&result);
            PA_DisposeHandle(blob);
        }
    }
    balanced();
}

int main(int argc, char** argv)
{
    @autoreleasepool {
        require(argc == 4, "case, empty representation, command outcome");
        gCall4D = host;
        nullEmpty = std::string(argv[2]) == "null";
        commandFailure = std::string(argv[3]) == "failure";
        expected = utf16("owned", 5);
        std::string name(argv[1]);
        if (name == "array") arrayCase();
        else if (name == "scalar") scalarCase();
        else if (name == "dispatcher") dispatcherCase();
        else pictureCase(name);
        std::printf("PASS %s %s %s; strings=0 handles=0 picture-refs=0\n",
                    argv[1], argv[2], argv[3]);
    }
}
