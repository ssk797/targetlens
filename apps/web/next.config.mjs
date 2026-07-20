/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Next 15.5's experimental segment explorer can emit a broken client
  // manifest during Fast Refresh. Keep the dev overlay, but disable that
  // optional explorer until the dependency release stabilizes.
  experimental: {
    devtoolSegmentExplorer: false,
  },
};

export default nextConfig;
