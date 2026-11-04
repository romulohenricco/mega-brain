#!/usr/bin/env node
/**
 * Claude Code Hook: PreCompact Session Digest
 *
 * Registered in .claude/settings.json. Passes the hook's JSON stdin to the
 * local Python digest writer; importing the hook keeps the handler API.
 *
 * @see .claude/hooks/precompact_digest.py
 * @see Story MIS-3 - Session Digest (PreCompact Hook)
 */

'use strict';

const { spawnSync } = require('node:child_process');
const { readFileSync } = require('node:fs');
const path = require('node:path');

const digestWriter = path.join(__dirname, 'precompact_digest.py');

async function onPreCompact(context = {}) {
  // Prefer real Python on Windows, before the python3 Microsoft Store alias.
  const candidates = process.platform === 'win32'
    ? [['python', []], ['py', ['-3']], ['python3', []]]
    : [['python3', []], ['python', []]];
  const input = JSON.stringify(context);

  for (const [command, args] of candidates) {
    const result = spawnSync(command, [...args, digestWriter], {
      input,
      encoding: 'utf8',
      env: { ...process.env, PYTHONUTF8: '1' },
      windowsHide: true,
      // All attempts together stay below the registered 10-second hook limit.
      timeout: 2500,
    });
    if (!result.error && result.status === 0) return;
  }
  // Hook failures must not prevent Claude Code from compacting the session.
  console.error('[PreCompact Hook] Local Python digest writer unavailable, skipping');
}

module.exports = onPreCompact;

if (require.main === module) {
  try {
    const input = readFileSync(0, 'utf8').trim();
    onPreCompact(input ? JSON.parse(input) : {}).catch(() => {
      console.error('[PreCompact Hook] Could not save session digest, skipping');
    });
  } catch {
    console.error('[PreCompact Hook] Invalid hook input, skipping');
  }
}
