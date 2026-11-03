-- Perkiraan skema yang ada sekarang (disusun dari dokumen dan kolom yang terbaca di Supabase; bukan hasil dump asli)
create table devices (device_id text primary key, is_active boolean not null default true, created_at timestamptz default now());
create table sensor_readings (
  id uuid primary key default gen_random_uuid(),
  device_id text not null references devices(device_id),
  nonce text not null,
  co_ppm double precision not null, co2_ppm double precision not null,
  status text not null check (status in ('normal','waspada','bahaya')),
  measured_at timestamptz default now(), received_at timestamptz,
  window_status smallint check (window_status between 0 and 100),
  co_peak_ppm integer, co2_peak_ppm integer, co_peak_second integer, co2_peak_second integer,
  unique (device_id, nonce));
create table alert_logs (
  id uuid primary key default gen_random_uuid(),
  device_id text not null references devices(device_id),
  reading_id uuid references sensor_readings(id) on delete cascade,
  alert_type text not null, created_at timestamptz default now(), resolved_at timestamptz, acknowledged_at timestamptz);
create table device_state (
  device_id text primary key references devices(device_id), status text, buzzer_state text,
  window_status smallint, active_alert_id uuid references alert_logs(id), ack_driver boolean, ack_at timestamptz,
  connection_status text, last_seen_at timestamptz, updated_at timestamptz, last_co_ppm integer, last_co2_ppm integer);
create table actuator_logs (
  id uuid primary key default gen_random_uuid(), alert_id uuid references alert_logs(id) on delete cascade,
  device_id text not null, buzzer_state text, window_action text, trigger_source text not null default '',
  command_id uuid unique, execution_status text, created_at timestamptz default now(), received_at timestamptz);
