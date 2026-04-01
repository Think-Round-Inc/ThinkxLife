const path = require('path')

/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
    domains: [],
  },
  // Add empty turbopack config to silence the warning
  // The path alias '@' is already configured in tsconfig.json
  turbopack: {},
  // Keep webpack config for compatibility, but it won't be used with Turbopack
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Ensure path aliases work in all environments
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
    }
    return config
  },
}

module.exports = nextConfig
