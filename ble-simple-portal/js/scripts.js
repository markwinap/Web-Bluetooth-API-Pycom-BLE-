const enc = new TextDecoder('utf-8');
let device = null;
let server = null;
let char1 = null;
let char2 = null;
let buff = [];

window.onload = (event) => {
  // Attach click events to buttons
  // Añadir eventos de click a los botones
  document
    .getElementById('request_device')
    .addEventListener('click', requestDevice);
  document
    .getElementById('notifications')
    .addEventListener('click', startNotifications);
  document.getElementById('disconect').addEventListener('click', disconect);
  document
    .getElementById('color')
    .addEventListener('change', (e) => getRGBColor(e.target.value));
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
  // https://developer.mozilla.org/en-US/docs/Web/API/BluetoothRemoteGATTCharacteristic/startNotifications
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
  //https://developer.mozilla.org/en-US/docs/Web/API/Bluetooth/requestDevice
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

  //Connect
  // Conectar
  server = await device.gatt.connect().catch((err) => console.log(err));

  //Get Primary Service
  //Obtener el servicio primario
  service = await server
    .getPrimaryService(12345)
    .catch((err) => console.log(err));

  //Get Primary Service Characteristic
  //Obtener la caracteristica del servicio primario
  char1 = await service
    .getCharacteristic(54321)
    .catch((err) => console.log(err));
  // Connect to second characteristic
  char2 = await service
    .getCharacteristic(64321)
    .catch((err) => console.log(err));
}

function addText(id, txt) {
  document.getElementById(id).innerHTML = txt;
}

function renderLog() {
  let temp = '';
  const clone = [...buff];
  for (let i of clone.reverse()) {
    temp += `<div>${i}</div>`;
  }
  addText('log', temp);
}

function disconect() {
  server.disconnect();
  addText('status', 'Disconnected / Desconectado');
}

function getRGBColor(h) {
  console.log(h);
  let r = 0,
    g = 0,
    b = 0;
  //parseInt("0xff")
  // 3 digits
  if (h.length == 4) {
    r = parseInt(`0x${h[1]}${h[1]}`);
    g = parseInt(`0x${h[2]}${h[2]}`);
    b = parseInt(`0x${h[3]}${h[3]}`);
  }
  // 6 digits
  else if (h.length == 7) {
    r = parseInt(`0x${h[1]}${h[2]}`);
    g = parseInt(`0x${h[3]}${h[4]}`);
    b = parseInt(`0x${h[5]}${h[6]}`);
  }
  char2.writeValue(new Uint8Array([r, g, b]).buffer);
}
