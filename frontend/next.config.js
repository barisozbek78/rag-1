/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  trailingSlash: true, // Bu satir statik sayfalarda linklerin düzgün çalışmasını sağlar
  images: {
    unoptimized: true,
    domains: ['localhost', 'drive.google.com'],
  },
}

module.exports = nextConfig
