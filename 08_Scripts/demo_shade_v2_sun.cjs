// Record SunCalc inputs separately from shade masks; hours are JST.
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const SunCalc = require(path.join(root, '06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/node_modules/suncalc'));
const lat = 35.691, lon = 139.7715;
const samples = [];
for (const date of ['2026-03-21', '2026-07-15', '2026-12-21']) {
  for (let hour = 9; hour <= 16; hour++) {
    const time = `${date}T${String(hour).padStart(2, '0')}:00:00+09:00`;
    const p = SunCalc.getPosition(new Date(time), lat, lon);
    samples.push({date, hour, time, altitude:p.altitude, azimuth:p.azimuth,
      altitudeDegrees:p.altitude*180/Math.PI,
      azimuthNorthDegrees:((p.azimuth*180/Math.PI+180)%360+360)%360});
  }
}
const out = path.join(root, '04_Data/Ready/Simulation_Demo/V2/shade-sun.json');
fs.mkdirSync(path.dirname(out), {recursive:true});
fs.writeFileSync(out, JSON.stringify({latitude:lat,longitude:lon,timezone:'Asia/Tokyo',
  azimuthConvention:'SunCalc radians: zero south, positive west; north-clockwise degrees also provided',
  samples},null,2));
console.log(out);
