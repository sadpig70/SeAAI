# PGF Design: AI_Desktop v2

```pg
AI_Desktop
├─ SecurityCore
│  ├─ DenyUnknownTool
│  ├─ DenyUnknownAction
│  ├─ EnforcePermissions
│  └─ AuditEveryCall
├─ SeAAIBridge
│  ├─ MailBox
│  ├─ Echo
│  ├─ MemberState
│  ├─ Hub
│  ├─ Approval
│  ├─ AuditQuery
│  └─ BrowserGateway
└─ LegacyCut
   ├─ RemoveGenericOSTools
   ├─ RemoveWebSearch
   └─ RemoveAutoToolGenerator
```

## PPR

```pg
def AI_Rebuild_AIDesktopV2():
    AI_Read_Legacy()
    AI_Freeze_Target_Surface()
    AI_Generate_Minimal_Server()
    AI_Attach_SeAAI_Dynamic_Tools()
    AI_Add_Shared_Browser_Gateway()
    AI_Verify_Deliverables()
```

