\echo '== T1. Migrasi: status baru (kolom turunan) sama dengan status lama'
select count(*) as baris, count(*) filter (where r.status = l.status) as sama, count(*) filter (where r.status <> l.status) as beda
from sensor_readings r join status_lama l using (id);

\echo '== T2. Kolom turunan tidak bisa diubah manual (anomali pembaruan tidak mungkin)'
\set ON_ERROR_STOP off
update sensor_readings set status = 'normal' where id = (select id from sensor_readings limit 1);
\set ON_ERROR_STOP on

\echo '== T3. Batasan: nilai tidak sah ditolak'
\set ON_ERROR_STOP off
insert into sensor_readings(device_id,nonce,co_ppm,co2_ppm,co_level) values ('AEROS_01','x1',0,0,3);
insert into sensor_readings(device_id,nonce,co_ppm,co2_ppm,buzzer_state) values ('AEROS_01','x2',0,0,'mungkin');
insert into sensor_readings(device_id,nonce,co_ppm,co2_ppm,event_id) values ('AEROS_01','x3',0,0,gen_random_uuid());
insert into sensor_readings(device_id,nonce,co_ppm,co2_ppm) select device_id, nonce, 0, 0 from sensor_readings limit 1;
insert into alert_logs(id,device_id,alert_type) values ('22222222-2222-2222-2222-222222222222','AEROS_DEMO_01','waspada');
insert into sensor_readings(device_id,nonce,co_ppm,co2_ppm,event_id) values ('AEROS_01','x4',0,0,'22222222-2222-2222-2222-222222222222');
delete from alert_logs where id = '22222222-2222-2222-2222-222222222222';
\set ON_ERROR_STOP on

\echo '== T4. Hubungkan bacaan nyata ke peringatannya lewat event_id (meniru worker baru), lalu uji view'
update sensor_readings r set event_id = x.id
from (select distinct on (r2.id) r2.id as rid, a.id from sensor_readings r2
      join alert_logs a on a.device_id = r2.device_id
       and r2.measured_at between a.created_at - interval '3 seconds' and coalesce(a.resolved_at, now())
      order by r2.id, a.created_at desc) x
where r.id = x.rid;
select count(*) filter (where event_id is not null) as bacaan_ber_event, count(*) as total from sensor_readings;
select count(*) as peringatan, count(*) filter (where tingkat = 'bahaya' and alert_type = 'waspada') as tercatat_waspada_padahal_bahaya,
       count(*) filter (where tingkat = 'bahaya' and alert_type = 'bahaya') as bahaya_cocok,
       count(*) filter (where tingkat = 'waspada' and alert_type = 'waspada') as waspada_cocok
from v_alerts v join alert_logs using (id);
select left(a.id::text,8) as id, a.alert_type as tipe_lama, v.tingkat as tingkat_view, v.gas, to_char(a.created_at at time zone 'Asia/Jakarta','DD-MM HH24:MI') as mulai
from v_alerts v join alert_logs a on a.id = v.id order by a.created_at desc limit 6;
select left(alert_id::text,8) as alert, gas, tingkat_maks, puncak_ppm from v_alert_gas order by mulai_at desc limit 6;

\echo '== T5. Episode sintetis CO dan CO2 sekaligus (CO naik waspada, CO2 naik bahaya)'
insert into alert_logs(id,device_id,alert_type,created_at,resolved_at) values ('11111111-1111-1111-1111-111111111111','AEROS_01','waspada', now(), null);
insert into sensor_readings(device_id,nonce,co_ppm,co2_ppm,co_level,co2_level,buzzer_state,event_id) values
 ('AEROS_01','s1',40,900,1,1,'on','11111111-1111-1111-1111-111111111111'),
 ('AEROS_01','s2',95,4100,2,2,'on','11111111-1111-1111-1111-111111111111'),
 ('AEROS_01','s3',20,3000,0,2,'off','11111111-1111-1111-1111-111111111111');
select gas, tingkat_maks, puncak_ppm from v_alert_gas where alert_id = '11111111-1111-1111-1111-111111111111' order by gas;
select tingkat, gas from v_alerts where id = '11111111-1111-1111-1111-111111111111';
select status, count(*) from sensor_readings where event_id = '11111111-1111-1111-1111-111111111111' group by status order by 1;

\echo '== T6. Jebakan max() pada teks (alasan level berupa angka)'
select max(x) as max_teks from (values ('waspada'),('bahaya')) t(x);

\echo '== T7. Hapus alert: bacaan tidak ikut terhapus (event_id jadi kosong); hapus bacaan: alert tetap'
select count(*) as bacaan_event_s from sensor_readings where event_id = '11111111-1111-1111-1111-111111111111';
delete from sensor_readings where nonce = 's1';
select count(*) as alert_masih_ada from alert_logs where id = '11111111-1111-1111-1111-111111111111';
delete from alert_logs where id = '11111111-1111-1111-1111-111111111111';
select count(*) as bacaan_s_tersisa, count(*) filter (where event_id is null) as event_id_kosong from sensor_readings where nonce in ('s2','s3');

\echo '== T8. Aturan hapus lama: hanya bacaan TANPA event_id (ambang uji 1 hari agar ada yang terhapus)'
select count(*) as sebelum, count(*) filter (where event_id is null) as tanpa_event from sensor_readings;
delete from sensor_readings where event_id is null and measured_at < now() - interval '1 day';
select count(*) as sesudah, count(*) filter (where event_id is not null) as milik_peringatan from sensor_readings;
select count(*) as peringatan_utuh from alert_logs;
