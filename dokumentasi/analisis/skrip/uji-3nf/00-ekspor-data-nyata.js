require('/Users/maritzavania/Downloads/aeros-sensor/worker/node_modules/dotenv').config({ path: '/Users/maritzavania/Downloads/aeros-sensor/worker/.env', quiet: true });
const s = require('/Users/maritzavania/Downloads/aeros-sensor/worker/src/config/supabaseClient');
const fs = require('fs');
const q = (v) => v === null || v === undefined ? 'null' : (typeof v === 'number' ? String(v) : "'" + String(v).replace(/'/g, "''") + "'");
(async () => {
  let out = [];
  const dev = await s.from('devices').select('device_id,is_active,created_at');
  dev.data.forEach(r => out.push(`insert into devices(device_id,is_active,created_at) values (${q(r.device_id)},${r.is_active},${q(r.created_at)});`));
  const al = await s.from('alert_logs').select('id,device_id,alert_type,created_at,resolved_at').eq('device_id','AEROS_01').order('created_at');
  al.data.forEach(r => out.push(`insert into alert_logs(id,device_id,alert_type,created_at,resolved_at) values (${q(r.id)},${q(r.device_id)},${q(r.alert_type)},${q(r.created_at)},${q(r.resolved_at)});`));
  let all = [], from = 0;
  while (true) {
    const r = await s.from('sensor_readings').select('id,device_id,nonce,co_ppm,co2_ppm,status,measured_at,received_at,window_status,co_peak_ppm,co2_peak_ppm,co_peak_second,co2_peak_second').eq('device_id','AEROS_01').order('measured_at').range(from, from+999);
    if (r.error) { console.error(r.error.message); process.exit(1); }
    all = all.concat(r.data); if (r.data.length < 1000) break; from += 1000;
  }
  all.forEach(r => out.push(`insert into sensor_readings(id,device_id,nonce,co_ppm,co2_ppm,status,measured_at,received_at,window_status,co_peak_ppm,co2_peak_ppm,co_peak_second,co2_peak_second) values (${[r.id,r.device_id,r.nonce,r.co_ppm,r.co2_ppm,r.status,r.measured_at,r.received_at,r.window_status,r.co_peak_ppm,r.co2_peak_ppm,r.co_peak_second,r.co2_peak_second].map(q).join(',')});`));
  fs.writeFileSync(process.argv[2], out.join('\n') + '\n');
  console.log('devices', dev.data.length, 'alert_logs', al.data.length, 'sensor_readings', all.length);
  process.exit(0);
})();
