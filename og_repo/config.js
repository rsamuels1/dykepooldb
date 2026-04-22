// ── CB⚡DB CONFIG ─────────────────────────────────────────────────────────────
// Single source of truth. Update handles here — takes effect everywhere.
// Format: lowercase, no @, exact handle as it appears on Bluesky.

// app password ltnd-nahy-shas-zihb

const APPROVED = new Set([
    'dykepooltables.bsky.social'
    // add new approved contributors above this line
]);

const BSKY_API    = 'https://public.api.bsky.app/xrpc';
const FETCH_LIMIT = 100;


// curl -X POST https://bsky.social \
// -H "Content-Type: application/json" \
// -d '{"identifier": "dykepooltables.bsky.social", "password": "ltnd-nahy-shas-zihb"}'

// await agent.post({
//   text: 'Hello world! I posted this via the API.',
//   createdAt: new Date().toISOString()
// })

// curl -X POST $PDSHOST/xrpc/com.atproto.repo.createRecord \
//     -H "Authorization: Bearer $ACCESS_JWT" \
//     -H "Content-Type: application/json" \
//     -d "{\"repo\": \"$dykepooltables\", \"collection\": \"app.bsky.feed.post\", \"record\": {\"text\": \"Hello world! I posted this via the API.\", \"createdAt\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}}"