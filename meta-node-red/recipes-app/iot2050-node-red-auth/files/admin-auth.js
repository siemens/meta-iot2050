// Copyright (c) Siemens AG, 2026
// SPDX-License-Identifier: MIT
'use strict';

const http = require('node:http');

function query (path, data) {
  const body = Buffer.from(JSON.stringify(data));
  if (body.length > 16384) return Promise.resolve(null);

  return new Promise(resolve => {
    const request = http.request({
      socketPath: '/run/iot2050-node-red-auth/auth.sock',
      path,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': body.length,
      },
    }, response => {
      const chunks = [];
      let length = 0;
      response.on('data', chunk => {
        length += chunk.length;
        if (length <= 4096) {
          chunks.push(chunk);
          return;
        }
        response.destroy();
        resolve(null);
      });
      response.on('error', () => resolve(null));
      response.on('end', () => {
        if (response.statusCode !== 200) {
          resolve(null);
          return;
        }
        try {
          const user = JSON.parse(Buffer.concat(chunks).toString()).user;
          resolve(user && user.username === data.username && ['*', 'read'].includes(user.permissions)
            ? { username: user.username, permissions: user.permissions } : null);
        } catch {
          resolve(null);
        }
      });
    });
    request.setTimeout(10000, () => request.destroy());
    request.on('error', () => resolve(null));
    request.end(body);
  });
}

module.exports = {
  type: 'credentials',
  sessionExpiryTime: 3600,
  users: username => query('/editor/user', { username }),
  authenticate: (username, password) => query('/editor/authenticate', { username, password }),
  default: () => Promise.resolve(null),
};
