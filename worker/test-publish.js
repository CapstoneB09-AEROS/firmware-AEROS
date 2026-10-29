require('dotenv').config();
const mqtt = require('mqtt');

// Setup koneksi ngambil dari .env yang sama
const connectUrl = `mqtts://${process.env.MQTT_HOST}:${process.env.MQTT_PORT}`;
const client = mqtt.connect(connectUrl, {
    clientId: `publisher_${Math.random().toString(16).slice(3)}`,
    clean: true,
    username: process.env.MQTT_USERNAME,
    password: process.env.MQTT_PASSWORD,
});

const TOPIC_SENSOR = 'proyek/esp/sensor';
const PESAN_DUMMY = JSON.stringify({
    co_ppm: 15.2,
    co2_ppm: 420.5,
    status: "Normal",
    window_status: "Tertutup"
});;

client.on('connect', () => {
    console.log('✅ Terhubung ke Broker, bersiap mengirim pesan...');
    
    // Tembak pesan ke topik
    client.publish(TOPIC_SENSOR, PESAN_DUMMY, (err) => {
        if (!err) {
            console.log(`🚀 Pesan terkirim ke topik ${TOPIC_SENSOR}: ${PESAN_DUMMY}`);
        } else {
            console.error('❌ Gagal ngirim pesan:', err);
        }
        // Langsung matiin script setelah ngirim
        client.end();
    });
});