const enc = new TextDecoder('utf-8');
let device = null;
let server = null;
let char1 = null;
let buff = [];
window.onload = (event) => {
  document
    .getElementById('request_device')
    .addEventListener('click', requestDevice);
  document
    .getElementById('notifications')
    .addEventListener('click', startNotifications);
  document.getElementById('disconect').addEventListener('click', disconect);
};
async function startNotifications() {
  char1.addEventListener('characteristicvaluechanged', (e) => {
    const json = JSON.parse(enc.decode(e.target.value.buffer));
    console.log(json);
    addText('voltage', `V:  ${json.v}`);
    addText('celsius', `T: ${json.c} C`);
    addText('humidity', `H: ${json.h} %`);
    buff.push(JSON.stringify(json));
    renderLog();
  });
  await char1
    .startNotifications()
    .then((ress) => {
      addText('status', 'Receiving Notifications / Recibiendo Notificaciones');
    })
    .catch((err) => {
      addText('status', 'Error');
    });
}
async function requestDevice() {
  device = await navigator.bluetooth
    .requestDevice({
      acceptAllDevices: true,
      optionalServices: [12345, 12346],
    })
    .then((res) => {
      console.log('Connected');
      addText('status', 'Connected / Conectado');
      return res;
    })
    .catch((err) => {
      console.log(err);
      addText('status', 'Error');
    });
  server = await device.gatt.connect().catch((err) => console.log(err));
  service = await server
    .getPrimaryService(12345)
    .catch((err) => console.log(err));
  char1 = await service
    .getCharacteristic(54321)
    .catch((err) => console.log(err));
}
function addText(id, txt) {
  document.getElementById(id).innerHTML = txt;
}
function addTextNL(id, txt) {
  const e = document.getElementById(id);
  e.innerHTML = e.innerHTML + `<div>${txt}</div>`;
  //document.getElementById(id).innerHTML = txt;
}
function renderLog() {
  let temp = '';
  for (let i of buff.reverse()) {
    temp += `<div>${i}</div>`;
  }
  addText('log', temp);
}
function disconect() {
  server.disconnect();
  addText('status', 'Disconnected / Desconectado');
}
