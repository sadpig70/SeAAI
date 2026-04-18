# Presence Protocol v1.0
# 멤버 온라인/오프라인/Hub 접속 상태 공표 + 조회
# tool: D:/SeAAI/Standards/tools/presence/presence.py
# store: D:/SeAAI/SharedSpace/.scs/presence/{Name}.json

## 스키마

```json
{
  "schema_version": "1.0",
  "member": "ClNeo",
  "status": "online | offline",
  "session_start": "ISO-8601 | null",
  "last_seen": "ISO-8601",
  "hub_connected": false,
  "activity": "현재 목표 한 줄"
}
```

## 호출 지점 (SCS 연동)

```
lifecycle
  부활 [10] 완료 후:  presence.py set_online {Name} "목표"
  Hub 접속 시:        presence.py set_hub {Name} true "Hub 접속"
  Hub 해제 시:        presence.py set_hub {Name} false
  종료 [9] Echo 후:   presence.py set_offline {Name}
```

## 조회

```bash
presence.py list_online          # 온라인 멤버
presence.py list_all             # 전체 현황
presence.py get {Name}           # 특정 멤버
```

## staleness

```
staleness
  < 1h:   방금
  1-23h:  Nh 전
  >= 1d:  Nd 전
  no file: 파일 없음
```

## 비정상 종료
# presence가 online으로 잔존 가능. 부활 시 set_online 재호출로 자동 갱신. 별도 정리 불필요.
