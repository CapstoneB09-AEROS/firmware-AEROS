// Sumber rumus (LaTeX). String.raw dipakai supaya garis miring terbalik tidak perlu digandakan.
export default {
  '01-tegangan-ke-rs': String.raw`R_s \;=\; R_L \cdot \frac{V_{CC} - V}{V} \qquad R_L = 9970\ \Omega,\quad V_{CC} = 4{,}64\ \mathrm{V}`,
  '02-filter-sma6': String.raw`\overline{R_s}(t) \;=\; \frac{1}{6}\sum_{i=0}^{5} R_s(t-i) \qquad \text{(rata-rata 6 detik terakhir)}`,
  '03-rasio': String.raw`\mathrm{rasio} \;=\; \frac{\overline{R_s}}{R_0} \qquad R_0 = \text{hambatan di udara bersih (disimpan di memori ESP32)}`,
  '04-kurva-ppm-co': String.raw`\begin{aligned} \frac{R_s}{R_0} &= A \cdot \mathrm{ppm}^{-\beta} && \text{(kurva datasheet)} \\[6pt] \mathrm{ppm}_{CO} &= \left(\frac{A}{\mathrm{rasio}}\right)^{1/\beta} && A = 3{,}46,\ \ \beta = 0{,}840 \\[6pt] \mathrm{ppm}_{CO} &= 0 \quad \text{bila rasio} \ge 0{,}5 \ (\approx 10\ \mathrm{ppm}) \end{aligned}`,
  '05-ambang-dalam-rasio': String.raw`\begin{aligned} \mathrm{rasio}(30\ \mathrm{ppm}) &= 3{,}46 \cdot 30^{-0{,}84} \approx 0{,}199 \quad \text{(selesai)} \\ \mathrm{rasio}(35\ \mathrm{ppm}) &= 3{,}46 \cdot 35^{-0{,}84} \approx 0{,}175 \quad \text{(waspada)} \\ \mathrm{rasio}(87\ \mathrm{ppm}) &= 3{,}46 \cdot 87^{-0{,}84} \approx 0{,}081 \quad \text{(bahaya)} \end{aligned}`,
  '06-uji-arah': String.raw`\Delta \;=\; \frac{\overline{R_s}(30\ \mathrm{s}) - \overline{R_s}(0)}{\overline{R_s}(0)} \qquad \begin{cases} \Delta > +5\% & \Rightarrow \text{sumber DALAM (CO turun)} \\ \text{selain itu} & \Rightarrow \text{sumber LUAR, jendela ditutup} \end{cases}`,
  '07-contoh-angka': String.raw`\begin{aligned} V = 47{,}9\ \mathrm{mV} \;&\Rightarrow\; R_s = 9970\cdot\frac{4{,}64-0{,}0479}{0{,}0479} \approx 955\ \mathrm{k\Omega} \\[4pt] \mathrm{rasio} = \frac{955}{5470} \approx 0{,}175 \;&\Rightarrow\; \mathrm{ppm}_{CO} = \left(\frac{3{,}46}{0{,}175}\right)^{1/0{,}84} \approx 35\ \mathrm{ppm} \end{aligned}`,
  '08-ads1115': String.raw`V \;=\; \frac{\overline{n}}{32768}\,V_{FS}, \quad \overline{n} = \frac{1}{16}\sum_{k=1}^{16} n_k, \quad V_{FS}\in\{1{,}024;\ 2{,}048;\ 4{,}096\}\ \mathrm{V}`,
  '09-checksum-co2': String.raw`\mathrm{ppm}_{CO_2} = 256\,b_2 + b_3 \qquad \mathrm{cs} = \big(\mathrm{0xFF} - \textstyle\sum_{i=1}^{7} b_i + 1\big) \bmod 256 \;\stackrel{?}{=}\; b_8`,
  '10-arus-basis': String.raw`I_B \;=\; \frac{V_{GPIO} - V_{BE}}{R_B} \;=\; \frac{3{,}3 - 0{,}7}{470\ \Omega} \;\approx\; 5{,}5\ \mathrm{mA}`,
  '11-hmac': String.raw`\mathrm{signature} \;=\; \mathrm{HMAC\text{-}SHA256}\big(K,\ \text{"r4|device|nonce|timestamp|...|demo"}\big)`,
  '12-model-udara': String.raw`\frac{dC}{dt} \;=\; P - N\,(C - C_{luar}) \qquad P = \frac{n\,G\,10^{6}}{V}`,
  '13-waktu-tutup-jendela': String.raw`t_{GPIO18\ HIGH} = \underbrace{0{,}5}_{\text{bip}} + \underbrace{3}_{\text{jeda}} = 3{,}5\ \mathrm{s} \qquad t_{GPIO18\ LOW} = 3{,}5 + 5 = 8{,}5\ \mathrm{s}`,
};
