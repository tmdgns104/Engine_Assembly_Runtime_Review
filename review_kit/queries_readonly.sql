-- 검토용 7건 발췌 DB 전용 SELECT 예시. 운영 데이터 변경 없음.
-- :id, :since, :until은 바인딩 매개변수. 값은 query_definitions.json 참조.

-- Q01_results
SELECT i.request_id, i.inspection_id, i.state,
       i.decision AS basic_decision,
       json_extract(s.value,'$.decision') AS final_decision,
       json_extract(i.result_json,'$.reason_code') AS reason,
       json_extract(i.result_json,'$.storage_success') AS stored,
       json_extract(s.value,'$.plc_result_value') AS plc_result
FROM inspections i
LEFT JOIN service_state s
  ON s.key='integrated_decision:'||i.inspection_id
ORDER BY i.request_id;

-- Q02_counts
SELECT i.decision AS basic_decision,
       json_extract(s.value,'$.decision') AS final_decision,
       COUNT(*) AS inspection_count
FROM inspections i
LEFT JOIN service_state s
  ON s.key='integrated_decision:'||i.inspection_id
GROUP BY i.decision,json_extract(s.value,'$.decision')
ORDER BY i.decision;

-- Q03_assets
SELECT asset_id,kind,relative_path,sha256,
       width,height,bytes,capture_at,sync_state
FROM frame_assets
WHERE inspection_id=:id
ORDER BY kind,capture_at,asset_id;

-- Q04_defects
SELECT i.request_id,d.inspection_id,d.code,d.slot
FROM defects d JOIN inspections i
  ON i.inspection_id=d.inspection_id
ORDER BY i.request_id;

-- Q05_primary_events
SELECT event_id,event_type,occurred_at,
       json_extract(payload_json,'$.payload.inspection_id') AS inspection_id
FROM events
WHERE json_extract(payload_json,'$.payload.inspection_id')=:id
ORDER BY occurred_at,event_id;

-- Q06_publication
SELECT key,
       json_extract(value,'$.event') AS event,
       json_extract(value,'$.inspection_id') AS inspection_id,
       json_extract(value,'$.request_token') AS request_token
FROM service_state
WHERE key='production_publication:'||:id;

-- Q07_sync_state
SELECT 'outbox' AS table_name,state AS sync_state,COUNT(*) AS row_count
FROM outbox GROUP BY state
UNION ALL
SELECT 'frame_assets',sync_state,COUNT(*)
FROM frame_assets GROUP BY sync_state;

-- Q08_date_range
SELECT request_id,inspection_id,accepted_at,decision
FROM inspections
WHERE accepted_at>=:since AND accepted_at<:until
ORDER BY accepted_at,inspection_id;