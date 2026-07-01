// API-Client — die UI spricht NUR diese Endpunkte (= nur den Backend-Port, ADR-0002).
// Kein direkter SoCo/HA-Zugriff im Frontend.

async function req(method, path, body) {
  const opt = { method };
  if (body !== undefined) {
    opt.headers = { 'content-type': 'application/json' };
    opt.body = JSON.stringify(body);
  }
  const r = await fetch(path, opt);
  if (!r.ok) throw new Error(`${method} ${path} → ${r.status}`);
  return r.status === 204 ? null : r.json();
}

export const api = {
  getState: () => req('GET', './api/state'),
  play: (room) => req('POST', `./api/rooms/${room}/play`),
  pause: (room) => req('POST', `./api/rooms/${room}/pause`),
  next: (room) => req('POST', `./api/rooms/${room}/next`),
  previous: (room) => req('POST', `./api/rooms/${room}/previous`),
  groupVolume: (room, level) => req('POST', `./api/rooms/${room}/group-volume`, { level }),
  groupVolumeRel: (room, delta) => req('POST', `./api/rooms/${room}/group-volume/rel`, { delta }),
  groupMute: (room, on) => req('POST', `./api/rooms/${room}/group-mute`, { on }),
  roomVolume: (room, level) => req('POST', `./api/rooms/${room}/volume`, { level }),
  roomMute: (room, on) => req('POST', `./api/rooms/${room}/mute`, { on }),
  sources: (room) => req('GET', `./api/rooms/${room}/sources`),
  playSource: (room, sourceId) =>
    req('POST', `./api/rooms/${room}/play-source`, { source_id: sourceId }),
};
