import ctypes
from ctypes import wintypes
from enum import IntEnum


#########
# Enums #
#########


class TokenInformationClass(IntEnum):
    TokenUser = 1,
    TokenGroups = 2,
    TokenPrivileges = 3,
    TokenOwner = 4,
    TokenPrimaryGroup = 5,
    TokenDefaultDacl = 6,
    TokenSource = 7,
    TokenType = 8,
    TokenImpersonationLevel = 9,
    TokenStatistics = 10,
    TokenRestrictedSids = 11,
    TokenSessionId = 12,
    TokenGroupsAndPrivileges = 13,
    TokenSessionReference = 14,
    TokenSandBoxInert = 15,
    TokenAuditPolicy = 16,
    TokenOrigin = 17,
    TokenElevationType = 18,
    TokenLinkedToken = 19,
    TokenElevation = 20,
    TokenHasRestrictions = 21,
    TokenAccessInformation = 22,
    TokenVirtualizationAllowed = 23,
    TokenVirtualizationEnabled = 24,
    TokenIntegrityLevel = 25,
    TokenUIAccess = 26,
    TokenMandatoryPolicy = 27,
    TokenLogonSid = 28,
    TokenIsAppContainer = 29,
    TokenCapabilities = 30,
    TokenAppContainerSid = 31,
    TokenAppContainerNumber = 32,
    TokenUserClaimAttributes = 33,
    TokenDeviceClaimAttributes = 34,
    TokenRestrictedUserClaimAttributes = 35,
    TokenRestrictedDeviceClaimAttributes = 36,
    TokenDeviceGroups = 37,
    TokenRestrictedDeviceGroups = 38,
    TokenSecurityAttributes = 39,
    TokenIsRestricted = 40,
    TokenProcessTrustLevel = 41,
    TokenPrivateNameSpace = 42,
    TokenSingletonAttributes = 43,
    TokenBnoIsolation = 44,
    TokenChildProcessFlags = 45,
    TokenIsLessPrivilegedAppContainer = 46,
    TokenIsSandboxed = 47,
    TokenOriginatingProcessTrustLevel = 48,
    MaxTokenInfoClass = 49


##############
# Structures #
##############


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD)
    ]


P_PROCESS_INFORMATION = ctypes.POINTER(PROCESS_INFORMATION)


class STARTUPINFOW(ctypes.Structure):

    def __init__(self, **kwargs):
        super(STARTUPINFOW, self).__init__(**kwargs)
        self.cb = ctypes.sizeof(STARTUPINFOW)

    _fields_ = [
        ('cb', wintypes.DWORD),
        ('lpReserved', wintypes.LPWSTR),
        ('lpDesktop', wintypes.LPWSTR),
        ('lpTitle', wintypes.LPWSTR),
        ('dwX', wintypes.DWORD),
        ('dwY', wintypes.DWORD),
        ('dwXSize', wintypes.DWORD),
        ('dwYSize', wintypes.DWORD),
        ('dwXCountChars', wintypes.DWORD),
        ('dwYCountChars', wintypes.DWORD),
        ('dwFillAttribute', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('wShowWindow', wintypes.WORD),
        ('cbReserved2', wintypes.WORD),
        ('lpReserved2', wintypes.LPBYTE),
        ('hStdInput', wintypes.HANDLE),
        ('hStdOutput', wintypes.HANDLE),
        ('hStdError', wintypes.HANDLE),
    ]


P_STARTUPINFOW = ctypes.POINTER(STARTUPINFOW)
