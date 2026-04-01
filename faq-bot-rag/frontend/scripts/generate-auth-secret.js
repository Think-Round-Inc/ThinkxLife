#!/usr/bin/env node

/**
 * Generate a secure secret for NextAuth.js
 * Usage: node scripts/generate-auth-secret.js
 */

const crypto = require('crypto');

function generateSecret() {
  return crypto.randomBytes(32).toString('base64');
}

function main() {
  const secret = generateSecret();

  console.log('🔐 Generated NextAuth Secret:');
  console.log('');
  console.log(`NEXTAUTH_SECRET=${secret}`);
  console.log('');
  console.log('Add this to your .env.local file');
  console.log('');
  console.log('⚠️  Keep this secret secure and never commit it to version control!');
}

if (require.main === module) {
  main();
}

module.exports = { generateSecret };
