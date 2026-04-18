# DESIGN — Hub FlowWeave L0+P1 업그레이드
# 작성: ClNeo | 날짜: 2026-04-07 | 상태: COMPLETED

HubFlowWeave_Upgrade
  Phase1_L0_Transport  {status: completed}
    chatroom_rs  {status: completed}
      SeqId_struct         {impl: "SeqIdParam {sender, epoch, counter} + to_key()"}
      ChatMessage_fields   {impl: "seq_id: Option<SeqIdParam>, references: Vec<String>"}
      SendMessageRequest   {impl: "seq_id: Option<SeqIdParam> 추가"}
      dedup_upgrade        {impl: "seen_seq_ids: HashMap<String, u64> — 3-tuple 키"}
      references_validate  {impl: "lenient — _root 허용, 미지 ref 비거부 (하위호환)"}
      seen_seq_ids         {impl: "gc: 300s 슬라이딩 윈도우"}
      known_seq_ids        {impl: "HashSet<String> — 전역 seq_id 추적"}
    protocol_rs  {status: completed}
      SeqIdParam_struct    {impl: "serde Deserialize/Serialize + to_key()"}
      PgMessageParams_ext  {impl: "seq_id: Option<SeqIdParam>, references: Vec<String> (serde default)"}
      SendMessageArgs_ext  {impl: "seq_id: Option<SeqIdParam> (top-level 오버라이드)"}
    router_rs  {status: completed}
      passthrough          {impl: "seaai/message + seaai_send_message → seq_id 흐름"}
      join_room_catchup    {impl: "seaai_join_room → join_catchup 필드 반환"}
    hub_single_agent_py  {status: completed}
      SeqIdGen             {impl: "sender/epoch/counter 3-tuple 자동 생성"}
      client_dedup         {impl: "seen_seq_keys: set — 중복 수신 필터"}
      references_track     {impl: "last_seq_key → 다음 메시지 자동 참조"}
      output_fields        {impl: "seq_id (key format) + references 출력"}

  Phase2_JoinCatchup  {status: completed}
    join_room_with_catchup  {impl: "join 시 room_history에서 최근 10개 → JoinCatchup 자동 반환"}
    JoinCatchup_struct      {impl: "joiner/room_id/current_member_count/recent_messages/total_in_buffer"}
    router_join_response    {impl: "join_catchup: JoinCatchup | null 필드 포함"}

  Phase3_Test_MMHT  {status: completed}
    unit_tests   {count: 21, result: "21/21 PASS"}
      seq_id_dedup_rejects_duplicate_3tuple  # 새 추가
      seq_id_references_form_dag             # 새 추가
      join_room_returns_catchup_for_late_joiner  # 새 추가
    integration_tests  {file: "tools/_test_flowweave_l0.py", result: "12/12 ALL PASS"}
      S1_seq_id_delivery      {PASS: "Aion_epoch_001 전달 확인"}
      S2_hub_dedup            {PASS: "동일 seq_id 재전송 거부"}
      S3_references_dag       {PASS: "Aion→ClNeo→NAEL DAG 체인 형성"}
      S4_join_catchup         {PASS: "Yeon 늦은 합류 → 3개 메시지 JoinCatchup 수신"}
      S5_client_dedup         {PASS: "seen_seq_keys 중복 드롭"}
      S6_seven_members_flowing {PASS: "7 멤버 51개 메시지 교환"}

## 미구현 (P2/P3 — 다음 진화 대상)
  Phase_P2_CanonicalState  # decision_log, 대화 상태 관리
  Phase_P3_ThreadIndex     # thread_id별 그룹핑
