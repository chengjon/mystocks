/**
 * MyStocks Frontend - PM2 Ecosystem Configuration
 * Phase 3: Bloomberg Terminal Style Verification Environment
 *
 * Production-ready PM2 configuration for MyStocks Vue 3 frontend
 * with comprehensive logging and monitoring
 */

module.exports = {
  apps: [
    {
      name: 'mystocks-frontend',
      script: 'serve', // Using serve for static production build
      args: 'dist -l 8080', // Serve dist directory on port 8080 with logging

      // Environment configuration
      env: {
        NODE_ENV: 'production',
        PORT: 8080
      },

      // Instance configuration
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',

      // Logging configuration
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      // Process management
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,

      // Additional configuration
      kill_timeout: 5000,
      listen_timeout: 10000,
      shutdown_with_message: true,

      // Source map support for debugging
      source_map_support: true,

      // Instance variables
      node_args: '--max-old-space-size=1024'
    }
  ],

  /**
   * Deployment configuration (optional, for future CI/CD integration)
   */
  deploy: {
    production: {
      user: 'root',
      host: 'localhost',
      ref: 'origin/main',
      repo: 'git@github.com:your-org/mystocks.git',
      path: '/opt/claude/mystocks_spec/web/frontend',
      'post-deploy': 'npm install && npm run build && pm2 reload ecosystem.config.js --env production'
    }
  }
}
