# IOT2050 Conf WEBUI

This is the IOT2050 configuration webUI, it is used to setup the device and it's
extension modules.

Currently it only supports IOT2050 SM variant.

This exposes a http service on the 2050 port from the IOT2050 device, please use
`http://<IP_TO_IOT>:2050` to access it.

The web server is managed by the `iot2050-conf-webui.service` systemd service,
thus the `systemctl` command could be used to start/stop or enable/disable this
web server.

Supported browser: Firefox, Chrome, Edge, etc. IE is not supported.

## Development 

This application is using Next.JS + Material UI.

There are two `npm-shrinkwrap.json` files:

- `npm-shrinkwrap.json`
- `npm-shrinkwrap.json.nodev`

The later one removes all the `devDependencies`, it is only for packaging
purpose, due to some npm packaging issue, the `devDependencies` must be removed
from the package.json.

If any new dependency package is added, make sure to generate both these files.

To update the dependencies, run the following commands on the **target** Debian
version within the `files` directory:

```shell
npx npm-check-updates -u
npm install --install-strategy=shallow
```

This will update the dependencies listed in `package.json` and update the
`npm-shrinkwrap.json`.

Install dependencies and run via `npm`:

```shell
# install dependencies
npm install

# run for development
npm run dev -- -p 2050

# run for production
npm run build
npm run start -- -p 2050
```

Open [http://localhost:2050](http://localhost:2050) with your browser to see the
result.
