/** @type {import('next').NextConfig} */

const CopyPlugin = require('copy-webpack-plugin');

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  modularizeImports: {
    '@mui/icons-material': {
      transform: '@mui/icons-material/{{member}}',
    },
  },
  webpack: (config, { isServer }) => {
    // Only run in server mode
    if (isServer) {
      config.plugins.push(
        new CopyPlugin({
          patterns: [
            {
              from: 'src/lib/gRPC',
              to: 'gRPC'
            },
            {
              from: 'src/lib/gRPC',
              to: 'app/gRPC'
            }
          ],
        })
      );
    }
    return config;
  },
};

module.exports = nextConfig;
