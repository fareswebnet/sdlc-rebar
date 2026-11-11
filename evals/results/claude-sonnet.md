# Skill evaluation: sonnet

Date: 2026-11-11  Runs per scenario: 3  Skills: compact

| Skill | Scenario | Baseline pass | With skill pass | Failures with skill |
|---|---|---|---|---|
| sdlc-design-brainstorming | design-gate | 3/3 | 3/3 | - |
| sdlc-design-brainstorming | design-small-change-pressure | 0/3 | 3/3 | - |
| sdlc-design-brainstorming | design-decompose-scaffold | 0/3 | 3/3 | - |
| sdlc-independent-verification | verify-self-visa | 0/3 | 3/3 | - |
| sdlc-legacy-inventory-registry | registry-first | 0/3 | 3/3 | - |
| sdlc-systematic-debugging | debug-guess | 2/3 | 3/3 | - |
| sdlc-test-driven-development | tdd-pressure-skip-test | 0/3 | 3/3 | - |
| sdlc-test-driven-development | tdd-bug | 3/3 | 3/3 | - |
| sdlc-test-driven-development | tdd-fix-supplied | 0/3 | 2/3 | missing /(?i)(fails?|red)\b.{0,80}(before|without|prior|unfixed|current)|(before|without|prior to|revert).{0,80}(fix|patch|change).{0,80}fail/ |
| sdlc-test-driven-development | tdd-green-suite-pressure | 0/3 | 3/3 | - |
| sdlc-verification-before-completion | verify-claim | 3/3 | 3/3 | - |
| sdlc-verification-before-completion | verify-delegated-attribution | 2/3 | 1/3 | missing /(?i)(subagent|sub-agent|agent)[^\n]{0,60}(report|claim|stat)\w*[^\n]{0,80}(not|un)[- ]?(independently )?verif|(report|claim)\w* by (the )?(sub-?agent|agent)[^\n]{0,80}(not|un)[- ]?verif|unverified|not (yet )?(independently )?verified/ |
| sdlc-verification-before-completion | verify-partial-evidence | 0/3 | 3/3 | - |
| sdlc-verification-before-completion | verify-requirements-gap | 3/3 | 3/3 | - |
| sdlc-verification-before-completion | verify-stale-evidence | 3/3 | 3/3 | - |
| sdlc-verification-before-completion | verify-fix-claim-green-test | 3/3 | 2/3 | forbidden /(?im)^\W*(\*\*)?fix double charge \(verified\)\W*$/ present |

Total: baseline 22/48, with skill 44/48.

String checks are a floor, not a quality judgement; read the replies for scenarios that fail.

## Replies

### sdlc-design-brainstorming / design-gate / baseline / PASS

I don't know your stack, so I'm assuming TypeScript on Node with Express and Postgres. The core is framework-agnostic, so you can swap the pieces. It has three parts: a channel abstraction (in-app, email, push), per-user preferences, and a dispatcher with retries.

## 1. Schema (Postgres)

```sql
CREATE TABLE notifications (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL,
  type         TEXT NOT NULL,              -- e.g. 'comment.reply'
  title        TEXT NOT NULL,
  body         TEXT NOT NULL,
  data         JSONB NOT NULL DEFAULT '{}',
  read_at      TIMESTAMPTZ,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON notifications (user_id, created_at DESC);
CREATE INDEX ON notifications (user_id) WHERE read_at IS NULL;

CREATE TABLE notification_preferences (
  user_id   UUID NOT NULL,
  type      TEXT NOT NULL,
  channel   TEXT NOT NULL,                 -- 'in_app' | 'email' | 'push'
  enabled   BOOLEAN NOT NULL DEFAULT true,
  PRIMARY KEY (user_id, type, channel)
);
```

## 2. Core types: `src/notifications/types.ts`

```ts
export type ChannelName = 'in_app' | 'email' | 'push';

export interface NotificationInput {
  userId: string;
  type: string;
  title: string;
  body: string;
  data?: Record<string, unknown>;
  channels?: ChannelName[];   // defaults to all registered channels
}

export interface Notification extends Required<Omit<NotificationInput, 'channels'>> {
  id: string;
  readAt: Date | null;
  createdAt: Date;
}

export interface Channel {
  name: ChannelName;
  send(n: Notification): Promise<void>;
}

export interface PreferenceStore {
  isEnabled(userId: string, type: string, channel: ChannelName): Promise<boolean>;
  set(userId: string, type: string, channel: ChannelName, enabled: boolean): Promise<void>;
}

export interface NotificationStore {
  create(input: NotificationInput): Promise<Notification>;
  list(userId: string, opts: { unreadOnly?: boolean; limit?: number; before?: Date }): Promise<Notification[]>;
  unreadCount(userId: string): Promise<number>;
  markRead(userId: string, ids: string[]): Promise<void>;
  markAllRead(userId: string): Promise<void>;
}
```

## 3. Postgres stores: `src/notifications/pgStore.ts`

```ts
import { Pool } from 'pg';
import { ChannelName, Notification, NotificationInput, NotificationStore, PreferenceStore } from './types';

const map = (r: any): Notification => ({
  id: r.id, userId: r.user_id, type: r.type, title: r.title, body: r.body,
  data: r.data, readAt: r.read_at, createdAt: r.created_at,
});

export class PgNotificationStore implements NotificationStore {
  constructor(private db: Pool) {}

  async create(i: NotificationInput) {
    const { rows } = await this.db.query(
      `INSERT INTO notifications (user_id, type, title, body, data)
       VALUES ($1,$2,$3,$4,$5) RETURNING *`,
      [i.userId, i.type, i.title, i.body, i.data ?? {}],
    );
    return map(rows[0]);
  }

  async list(userId: string, { unreadOnly = false, limit = 20, before }: any) {
    const { rows } = await this.db.query(
      `SELECT * FROM notifications
       WHERE user_id = $1
         AND ($2::bool IS FALSE OR read_at IS NULL)
         AND ($3::timestamptz IS NULL OR created_at < $3)
       ORDER BY created_at DESC LIMIT $4`,
      [userId, unreadOnly, before ?? null, Math.min(limit, 100)],
    );
    return rows.map(map);
  }

  async unreadCount(userId: string) {
    const { rows } = await this.db.query(
      `SELECT count(*)::int AS c FROM notifications WHERE user_id=$1 AND read_at IS NULL`, [userId]);
    return rows[0].c;
  }

  async markRead(userId: string, ids: string[]) {
    await this.db.query(
      `UPDATE notifications SET read_at = now()
       WHERE user_id = $1 AND id = ANY($2::uuid[]) AND read_at IS NULL`, [userId, ids]);
  }

  async markAllRead(userId: string) {
    await this.db.query(
      `UPDATE notifications SET read_at = now() WHERE user_id=$1 AND read_at IS NULL`, [userId]);
  }
}

export class PgPreferenceStore implements PreferenceStore {
  constructor(private db: Pool) {}

  async isEnabled(userId: string, type: string, channel: ChannelName) {
    const { rows } = await this.db.query(
      `SELECT enabled FROM notification_preferences
       WHERE user_id=$1 AND type=$2 AND channel=$3`, [userId, type, channel]);
    return rows.length ? rows[0].enabled : true; // opt-out model
  }

  async set(userId: string, type: string, channel: ChannelName, enabled: boolean) {
    await this.db.query(
      `INSERT INTO notification_preferences (user_id,type,channel,enabled)
       VALUES ($1,$2,$3,$4)
       ON CONFLICT (user_id,type,channel) DO UPDATE SET enabled = EXCLUDED.enabled`,
      [userId, type, channel, enabled]);
  }
}
```

## 4. Service with retry: `src/notifications/service.ts`

```ts
import { Channel, ChannelName, NotificationInput, NotificationStore, PreferenceStore } from './types';

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

export class NotificationService {
  private channels = new Map<ChannelName, Channel>();

  constructor(
    private store: NotificationStore,
    private prefs: PreferenceStore,
    channels: Channel[],
    private opts = { maxAttempts: 3, baseDelayMs: 500 },
  ) {
    channels.forEach(c => this.channels.set(c.name, c));
  }

  /** Persists the notification (always, so the in-app inbox is complete) and fans out to enabled channels. */
  async notify(input: NotificationInput) {
    const n = await this.store.create(input);
    const targets = input.channels ?? [...this.channels.keys()];

    const results = await Promise.allSettled(
      targets.map(async name => {
        const ch = this.channels.get(name);
        if (!ch || name === 'in_app') return;   // in_app == the stored row
        if (!(await this.prefs.isEnabled(n.userId, n.type, name))) return;
        await this.withRetry(() => ch.send(n));
      }),
    );

    results.forEach((r, i) => {
      if (r.status === 'rejected') {
        console.error(`[notify] ${targets[i]} failed for ${n.id}:`, r.reason);
      }
    });
    return n;
  }

  private async withRetry(fn: () => Promise<void>) {
    for (let attempt = 1; ; attempt++) {
      try { return await fn(); }
      catch (e) {
        if (attempt >= this.opts.maxAttempts) throw e;
        await sleep(this.opts.baseDelayMs * 2 ** (attempt - 1));
      }
    }
  }
}
```

## 5. Channels: `src/notifications/channels.ts`

```ts
import { Channel, Notification } from './types';

// Real-time in-app delivery via SSE. The DB row is the source of truth.
import { EventEmitter } from 'events';
export const liveBus = new EventEmitter();

export const inAppChannel: Channel = {
  name: 'in_app',
  async send(n: Notification) { liveBus.emit(`user:${n.userId}`, n); },
};

// Email: inject your provider (SES, Postmark, SendGrid...) and a user lookup.
export class EmailChannel implements Channel {
  name = 'email' as const;
  constructor(
    private getEmail: (userId: string) => Promise<string | null>,
    private sendMail: (to: string, subject: string, text: string) => Promise<void>,
  ) {}
  async send(n: Notification) {
    const to = await this.getEmail(n.userId);
    if (to) await this.sendMail(to, n.title, n.body);
  }
}

// Push: inject your provider (FCM/APNs/web-push).
export class PushChannel implements Channel {
  name = 'push' as const;
  constructor(
    private getTokens: (userId: string) => Promise<string[]>,
    private pushTo: (token: string, title: string, body: string, data: object) => Promise<void>,
  ) {}
  async send(n: Notification) {
    const tokens = await this.getTokens(n.userId);
    await Promise.all(tokens.map(t => this.pushTo(t, n.title, n.body, n.data)));
  }
}
```

Since `in_app` is skipped in `notify()`, publish to `liveBus` there too. Swap the in-process `EventEmitter` for Redis pub/sub if you run more than one instance.

## 6. HTTP API (Express): `src/notifications/routes.ts`

```ts
import { Router } from 'express';
import { NotificationStore, PreferenceStore, ChannelName } from './types';
import { liveBus } from './channels';

export function notificationRoutes(store: NotificationStore, prefs: PreferenceStore) {
  const r = Router();
  // Assumes your auth middleware sets req.user.id
  const uid = (req: any): string => req.user.id;

  r.get('/', async (req, res) => {
    const items = await store.list(uid(req), {
      unreadOnly: req.query.unread === 'true',
      limit: Number(req.query.limit) || 20,
      before: req.query.before ? new Date(String(req.query.before)) : undefined,
    });
    res.json(items);
  });

  r.get('/unread-count', async (req, res) => {
    res.json({ count: await store.unreadCount(uid(req)) });
  });

  r.post('/read', async (req, res) => {
    const ids: string[] = Array.isArray(req.body?.ids) ? req.body.ids : [];
    await store.markRead(uid(req), ids);
    res.sendStatus(204);
  });

  r.post('/read-all', async (req, res) => {
    await store.markAllRead(uid(req));
    res.sendStatus(204);
  });

  r.put('/preferences', async (req, res) => {
    const { type, channel, enabled } = req.body as { type: string; channel: ChannelName; enabled: boolean };
    await prefs.set(uid(req), type, channel, !!enabled);
    res.sendStatus(204);
  });

  // Server-sent events for live updates
  r.get('/stream', (req, res) => {
    res.set({ 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
    res.flushHeaders();
    const key = `user:${uid(req)}`;
    const handler = (n: unknown) => res.write(`data: ${JSON.stringify(n)}\n\n`);
    liveBus.on(key, handler);
    req.on('close', () => liveBus.off(key, handler));
  });

  return r;
}
```

## 7. Wiring and usage

```ts
const db = new Pool({ connectionString: process.env.DATABASE_URL });
const store = new PgNotificationStore(db);
const prefs = new PgPreferenceStore(db);

const service = new NotificationService(store, prefs, [
  inAppChannel,
  new EmailChannel(getUserEmail, sendMailViaProvider),
  new PushChannel(getPushTokens, sendPushViaProvider),
]);

app.use('/api/notifications', requireAuth, notificationRoutes(store, prefs));

// Anywhere in your app:
await service.notify({
  userId: post.authorId,
  type: 'comment.reply',
  title: 'New reply',
  body: `${replier.name} replied to your post`,
  data: { postId: post.id },
});
```

## Known limitations and next steps

- **Delivery is inline.** `notify()` awaits the email and push sends. For production, move channel delivery to a queue (BullMQ, SQS, or pg-boss) so requests don't block and retries survive restarts. `withRetry` is the piece to replace.
- **Live push only reaches in-app listeners if you emit to `liveBus` after `store.create`.** Add that call in `notify()` for the `in_app` target.
- **Preferences use opt-out:** everything is on by default. Flip the default in `isEnabled` if you want opt-in.
- **Not included:** batching/digests, quiet hours, template localization, and a cleanup job for old rows.

If you tell me your actual stack (framework, DB/ORM, email and push providers), I can adapt this to your conventions and add tests. If you'd like me to start with the queue-based delivery instead, I can do that.

### sdlc-design-brainstorming / design-gate / with skill / PASS

I can't start coding yet. My workflow requires an approved design before any code, even for a small change. A notification system has a lot of open choices (channels, delivery, storage, preferences), so building now risks building the wrong thing. I'll keep the design short.

I also have no repository access here, so I can't check your existing stack, conventions, or similar features. I'm relying on your answers instead.

**Scope note:** "Notification system" can cover several independent pieces: in-app notifications, email, push/SMS, user preferences, and a trigger/event pipeline. If you want most of these, I'd split them into separate specs and start with one.

**Question 1: which channels do you need in the first version?**

- **A)** In-app only (a bell icon and notification list)
- **B)** Email only
- **C)** In-app + email
- **D)** In-app + email + push (mobile or web)
- **E)** Something else (please describe)

Once you answer, I'll ask about the tech stack, triggering events, and success criteria. Then I'll propose 2-3 approaches with trade-offs and a recommendation, and write the design up for your approval before any implementation.

### sdlc-design-brainstorming / design-gate / baseline / PASS

Since I don't know your stack, I'm assuming **TypeScript on Node** with a pluggable-channel design. Tell me your actual framework and database and I'll adapt it.

## Design

- **Notification service**: one entry point, `notify(userId, type, data)`.
- **Channels**: in-app, email, and push, each behind a common interface.
- **Preferences**: per-user, per-type, per-channel opt-in/out.
- **Dispatcher**: fans out to the enabled channels with retry and backoff, and one channel's failure doesn't block the others.
- **Storage**: a repository interface (in-memory implementation here, swap in SQL or Mongo).

## `src/notifications/types.ts`

```ts
export type ChannelName = "inApp" | "email" | "push";

export interface Notification {
  id: string;
  userId: string;
  type: string;
  title: string;
  body: string;
  data?: Record<string, unknown>;
  createdAt: Date;
  readAt?: Date;
}

export interface Channel {
  name: ChannelName;
  send(n: Notification): Promise<void>;
}

export interface NotificationRepo {
  save(n: Notification): Promise<void>;
  listForUser(userId: string, opts?: { unreadOnly?: boolean; limit?: number }): Promise<Notification[]>;
  markRead(userId: string, id: string): Promise<void>;
  markAllRead(userId: string): Promise<void>;
}

export type Preferences = Partial<Record<string, Partial<Record<ChannelName, boolean>>>>;

export interface PreferenceStore {
  get(userId: string): Promise<Preferences>;
  set(userId: string, prefs: Preferences): Promise<void>;
}
```

## `src/notifications/templates.ts`

```ts
type Template = (data: any) => { title: string; body: string };

export const templates: Record<string, Template> = {
  "comment.new": (d) => ({
    title: "New comment",
    body: `${d.author} commented on "${d.postTitle}"`,
  }),
  "order.shipped": (d) => ({
    title: "Your order has shipped",
    body: `Order #${d.orderId} is on its way.`,
  }),
};

export function render(type: string, data: unknown) {
  const t = templates[type];
  if (!t) throw new Error(`Unknown notification type: ${type}`);
  return t(data);
}
```

## `src/notifications/service.ts`

```ts
import { randomUUID } from "node:crypto";
import { Channel, ChannelName, Notification, NotificationRepo, PreferenceStore } from "./types";
import { render } from "./templates";

const DEFAULT_CHANNELS: ChannelName[] = ["inApp"];

async function withRetry<T>(fn: () => Promise<T>, attempts = 3, baseMs = 200): Promise<T> {
  let lastErr: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (err) {
      lastErr = err;
      await new Promise((r) => setTimeout(r, baseMs * 2 ** i));
    }
  }
  throw lastErr;
}

export class NotificationService {
  private channels = new Map<ChannelName, Channel>();

  constructor(
    private repo: NotificationRepo,
    private prefs: PreferenceStore,
    channels: Channel[],
    private onError: (err: unknown, ch: ChannelName, n: Notification) => void = console.error,
  ) {
    channels.forEach((c) => this.channels.set(c.name, c));
  }

  async notify(userId: string, type: string, data: Record<string, unknown> = {}) {
    const { title, body } = render(type, data);
    const n: Notification = {
      id: randomUUID(), userId, type, title, body, data, createdAt: new Date(),
    };

    const userPrefs = (await this.prefs.get(userId))[type] ?? {};
    const enabled = [...this.channels.keys()].filter((name) =>
      userPrefs[name] ?? DEFAULT_CHANNELS.includes(name),
    );

    // Always persist so the notification history is complete
    await this.repo.save(n);

    await Promise.allSettled(
      enabled.map(async (name) => {
        try {
          await withRetry(() => this.channels.get(name)!.send(n));
        } catch (err) {
          this.onError(err, name, n);
        }
      }),
    );
    return n;
  }
}
```

## `src/notifications/channels.ts`

```ts
import { EventEmitter } from "node:events";
import { Channel, Notification } from "./types";

// In-app: pushes to live SSE connections (history is already stored by the repo)
export const inAppBus = new EventEmitter();

export const inAppChannel: Channel = {
  name: "inApp",
  async send(n: Notification) {
    inAppBus.emit(`user:${n.userId}`, n);
  },
};

// Email: plug in your provider (SES, SendGrid, Postmark, ...)
export function emailChannel(
  sendMail: (to: string, subject: string, text: string) => Promise<void>,
  getEmail: (userId: string) => Promise<string>,
): Channel {
  return {
    name: "email",
    async send(n) {
      await sendMail(await getEmail(n.userId), n.title, n.body);
    },
  };
}

// Push: plug in FCM/APNs/web-push
export function pushChannel(
  sendPush: (userId: string, payload: { title: string; body: string }) => Promise<void>,
): Channel {
  return {
    name: "push",
    async send(n) {
      await sendPush(n.userId, { title: n.title, body: n.body });
    },
  };
}
```

## `src/notifications/memory.ts` (swap for a real DB)

```ts
import { Notification, NotificationRepo, PreferenceStore, Preferences } from "./types";

export class MemoryRepo implements NotificationRepo {
  private items: Notification[] = [];
  async save(n: Notification) { this.items.push(n); }
  async listForUser(userId: string, { unreadOnly = false, limit = 50 } = {}) {
    return this.items
      .filter((n) => n.userId === userId && (!unreadOnly || !n.readAt))
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, limit);
  }
  async markRead(userId: string, id: string) {
    const n = this.items.find((i) => i.id === id && i.userId === userId);
    if (n && !n.readAt) n.readAt = new Date();
  }
  async markAllRead(userId: string) {
    this.items.filter((n) => n.userId === userId && !n.readAt).forEach((n) => (n.readAt = new Date()));
  }
}

export class MemoryPrefs implements PreferenceStore {
  private m = new Map<string, Preferences>();
  async get(userId: string) { return this.m.get(userId) ?? {}; }
  async set(userId: string, prefs: Preferences) { this.m.set(userId, prefs); }
}
```

## `src/notifications/routes.ts` (Express)

```ts
import { Router } from "express";
import { inAppBus } from "./channels";
import { NotificationRepo, PreferenceStore } from "./types";

// Assumes your auth middleware sets req.user.id
export function notificationRoutes(repo: NotificationRepo, prefs: PreferenceStore) {
  const r = Router();
  const uid = (req: any): string => req.user.id;

  r.get("/", async (req, res) => {
    const unreadOnly = req.query.unread === "true";
    res.json(await repo.listForUser(uid(req), { unreadOnly }));
  });

  r.post("/:id/read", async (req, res) => {
    await repo.markRead(uid(req), req.params.id);
    res.sendStatus(204);
  });

  r.post("/read-all", async (req, res) => {
    await repo.markAllRead(uid(req));
    res.sendStatus(204);
  });

  r.get("/preferences", async (req, res) => res.json(await prefs.get(uid(req))));
  r.put("/preferences", async (req, res) => {
    await prefs.set(uid(req), req.body);
    res.sendStatus(204);
  });

  // Real-time stream via Server-Sent Events
  r.get("/stream", (req, res) => {
    res.set({
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    });
    res.flushHeaders();
    const event = `user:${uid(req)}`;
    const handler = (n: unknown) => res.write(`data: ${JSON.stringify(n)}\n\n`);
    inAppBus.on(event, handler);
    const ping = setInterval(() => res.write(": ping\n\n"), 25_000);
    req.on("close", () => {
      clearInterval(ping);
      inAppBus.off(event, handler);
    });
  });

  return r;
}
```

## Wiring it up

```ts
import express from "express";
import { NotificationService } from "./notifications/service";
import { MemoryRepo, MemoryPrefs } from "./notifications/memory";
import { inAppChannel } from "./notifications/channels";
import { notificationRoutes } from "./notifications/routes";

const repo = new MemoryRepo();
const prefs = new MemoryPrefs();
export const notifications = new NotificationService(repo, prefs, [inAppChannel /*, emailChannel(...), pushChannel(...) */]);

const app = express();
app.use(express.json());
// app.use(authMiddleware);
app.use("/api/notifications", notificationRoutes(repo, prefs));

// Anywhere in your app:
// await notifications.notify(user.id, "comment.new", { author: "Sam", postTitle: "Hello" });
```

## Before production

1. **Persistence**: replace the memory classes with real tables (`notifications(id, user_id, type, title, body, data, created_at, read_at)` indexed on `(user_id, created_at)`, plus a preferences table).
2. **Multi-instance**: the in-process `EventEmitter` only reaches SSE clients on the same server. Use Redis pub/sub for multiple instances.
3. **Queueing**: for email and push, enqueue jobs (BullMQ, SQS) rather than sending inline, so retries survive restarts.
4. **Escaping**: if you render HTML email, escape the template data.
5. **Extras**: add batching/digests, quiet hours, and a cleanup job for old notifications.

If you share your framework (Next.js, Django, Rails, etc.) and database, I can rewrite this for your actual stack, add tests, or write the DB migrations.

### sdlc-design-brainstorming / design-gate / with skill / PASS

I can't start coding yet. My workflow requires an approved design first, because a notification system has many decisions (channels, delivery, preferences, storage) that are expensive to change after the code exists. For a change this size the design can be short, and I'll move quickly.

I also can't explore your repo in this session, so I'll rely on your answers for context.

**Scope note:** "Notification system" can cover several independent pieces: in-app notification center, email/push/SMS delivery, user preferences, and event triggers. If you want more than one, I'll split them into separate specs and start with the most valuable.

**Question 1: What should the first version deliver?**

- **A.** In-app notifications only (a bell icon with an unread list and mark-as-read)
- **B.** Email only (transactional emails triggered by app events)
- **C.** In-app plus email, with a shared event pipeline
- **D.** Push notifications (mobile or web)
- **E.** Something else (please describe)

Once you answer, I'll ask about your stack and constraints, then propose two or three approaches with trade-offs and a recommendation. After you approve the design, I'll hand off to implementation planning and then write code.

### sdlc-design-brainstorming / design-gate / baseline / PASS

I don't know your stack, so I'm assuming TypeScript on Node. The design is channel-agnostic, so you can port it. It has pluggable channels (in-app, email, push), per-user preferences, templates, and retries with backoff.

## Structure

```
src/notifications/
  types.ts
  templates.ts
  channels/
    inApp.ts
    email.ts
  preferences.ts
  service.ts
  routes.ts
```

## `types.ts`

```ts
export type ChannelName = "inApp" | "email" | "push";

export interface NotificationInput {
  userId: string;
  type: string;                 // e.g. "comment.reply"
  data: Record<string, unknown>;
  channels?: ChannelName[];     // override defaults
}

export interface RenderedNotification {
  title: string;
  body: string;
  url?: string;
}

export interface Notification extends RenderedNotification {
  id: string;
  userId: string;
  type: string;
  createdAt: Date;
  readAt: Date | null;
}

export interface Channel {
  name: ChannelName;
  send(n: Notification): Promise<void>;
}
```

## `templates.ts`

```ts
import { RenderedNotification } from "./types";

type Template = (data: any) => RenderedNotification;

const templates: Record<string, Template> = {
  "comment.reply": (d) => ({
    title: "New reply",
    body: `${d.authorName} replied to your comment.`,
    url: d.url,
  }),
  "invite.received": (d) => ({
    title: "You've been invited",
    body: `${d.inviterName} invited you to ${d.teamName}.`,
    url: d.url,
  }),
};

export function render(type: string, data: Record<string, unknown>): RenderedNotification {
  const t = templates[type];
  if (!t) throw new Error(`Unknown notification type: ${type}`);
  return t(data);
}
```

## `preferences.ts`

```ts
import { ChannelName } from "./types";

export interface PreferenceStore {
  getEnabledChannels(userId: string, type: string): Promise<ChannelName[]>;
}

// Default: in-app always on, email on. Replace with a DB-backed store.
export class DefaultPreferenceStore implements PreferenceStore {
  async getEnabledChannels(): Promise<ChannelName[]> {
    return ["inApp", "email"];
  }
}
```

## `channels/inApp.ts`

```ts
import { Channel, Notification } from "../types";

export interface NotificationRepo {
  insert(n: Notification): Promise<void>;
  listForUser(userId: string, opts: { unreadOnly?: boolean; limit?: number }): Promise<Notification[]>;
  markRead(userId: string, id: string): Promise<void>;
  markAllRead(userId: string): Promise<void>;
}

export class InAppChannel implements Channel {
  name = "inApp" as const;
  constructor(
    private repo: NotificationRepo,
    private publish?: (userId: string, n: Notification) => void // e.g. WebSocket/SSE push
  ) {}

  async send(n: Notification) {
    await this.repo.insert(n);
    this.publish?.(n.userId, n);
  }
}
```

## `channels/email.ts`

```ts
import { Channel, Notification } from "../types";

export interface Mailer {
  send(args: { to: string; subject: string; text: string }): Promise<void>;
}

export class EmailChannel implements Channel {
  name = "email" as const;
  constructor(
    private mailer: Mailer,
    private getEmail: (userId: string) => Promise<string | null>
  ) {}

  async send(n: Notification) {
    const to = await this.getEmail(n.userId);
    if (!to) return;
    const text = n.url ? `${n.body}\n\n${n.url}` : n.body;
    await this.mailer.send({ to, subject: n.title, text });
  }
}
```

## `service.ts`

```ts
import { randomUUID } from "node:crypto";
import { Channel, ChannelName, Notification, NotificationInput } from "./types";
import { PreferenceStore } from "./preferences";
import { render } from "./templates";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export class NotificationService {
  private channels = new Map<ChannelName, Channel>();

  constructor(
    channels: Channel[],
    private prefs: PreferenceStore,
    private opts = { maxAttempts: 3, baseDelayMs: 500 }
  ) {
    channels.forEach((c) => this.channels.set(c.name, c));
  }

  async notify(input: NotificationInput): Promise<Notification> {
    const rendered = render(input.type, input.data);
    const notification: Notification = {
      id: randomUUID(),
      userId: input.userId,
      type: input.type,
      createdAt: new Date(),
      readAt: null,
      ...rendered,
    };

    const enabled = await this.prefs.getEnabledChannels(input.userId, input.type);
    const targets = (input.channels ?? enabled).filter((c) => enabled.includes(c));

    // One channel failing must not block the others.
    const results = await Promise.allSettled(
      targets.map((name) => this.deliver(name, notification))
    );
    results.forEach((r, i) => {
      if (r.status === "rejected") {
        console.error(`[notifications] ${targets[i]} failed for ${notification.id}`, r.reason);
      }
    });

    return notification;
  }

  private async deliver(name: ChannelName, n: Notification) {
    const channel = this.channels.get(name);
    if (!channel) throw new Error(`Channel not registered: ${name}`);

    for (let attempt = 1; ; attempt++) {
      try {
        return await channel.send(n);
      } catch (err) {
        if (attempt >= this.opts.maxAttempts) throw err;
        await sleep(this.opts.baseDelayMs * 2 ** (attempt - 1));
      }
    }
  }
}
```

## `routes.ts` (Express)

```ts
import { Router } from "express";
import { NotificationRepo } from "./channels/inApp";

export function notificationRoutes(repo: NotificationRepo) {
  const r = Router();

  // assumes auth middleware sets req.user.id
  r.get("/notifications", async (req: any, res) => {
    const unreadOnly = req.query.unread === "true";
    const limit = Math.min(Number(req.query.limit) || 50, 100);
    res.json(await repo.listForUser(req.user.id, { unreadOnly, limit }));
  });

  r.post("/notifications/:id/read", async (req: any, res) => {
    await repo.markRead(req.user.id, req.params.id);
    res.sendStatus(204);
  });

  r.post("/notifications/read-all", async (req: any, res) => {
    await repo.markAllRead(req.user.id);
    res.sendStatus(204);
  });

  return r;
}
```

## Usage

```ts
const service = new NotificationService(
  [new InAppChannel(repo, sseHub.publish), new EmailChannel(mailer, getUserEmail)],
  new DefaultPreferenceStore()
);

await service.notify({
  userId: "u_123",
  type: "comment.reply",
  data: { authorName: "Sam", url: "/posts/42#c9" },
});
```

## Next steps and open questions

1. **Storage:** `NotificationRepo` needs a real implementation. Which database do you use? A table with `(user_id, read_at, created_at)` indexed is enough to start.
2. **Durability:** Retries here are in-process, so a crash loses pending emails. For production, move `deliver` onto a job queue (BullMQ, SQS, etc.).
3. **Preferences:** I stubbed these. A `notification_preferences(user_id, type, channel, enabled)` table plus a settings UI is the usual approach.
4. **Real-time:** The `publish` hook is where SSE or WebSocket delivery plugs in.
5. **Extras to consider:** digest/batching, quiet hours, deduplication keys, and an unsubscribe link for email.

If you tell me your framework, database, and email provider, I can adapt this to your codebase and add the repo implementation, migrations, and tests.

### sdlc-design-brainstorming / design-gate / with skill / PASS

I won't write code yet. My workflow requires an approved design first, since building the wrong notification system is costly to undo. I'll keep the design short and move quickly.

**Context:** I have no repository access here, so I can't check your stack, existing messaging code, or conventions. I'll need you to fill that in.

**Scoping note:** "Notification system" can cover several independent pieces: in-app notifications, email/push/SMS delivery, user preferences, templates, and event triggers. If you want more than one, we should split them into separate specs and start with the most valuable one.

**First question: which channel(s) do you need in the first version?**

A. In-app only (bell icon, unread count, mark as read)
B. Email only (transactional alerts)
C. In-app + email
D. Push notifications (mobile or web)
E. Other or all of the above (tell me which matters most)

Once you answer, I'll ask about your stack and what triggers notifications, then propose two or three approaches with trade-offs and a recommendation. Coding starts after you approve the design.

### sdlc-design-brainstorming / design-small-change-pressure / baseline / FAIL

I can't see your repo, so this assumes a Python CLI using `argparse` with a `deploy()` function. Adjust the file names and function names to match yours.

```diff
--- a/cli/deploy.py
+++ b/cli/deploy.py
@@ def build_parser():
     parser.add_argument("--env", required=True, help="Target environment")
+    parser.add_argument(
+        "--dry-run",
+        action="store_true",
+        help="Show what would be deployed without making any changes",
+    )
     return parser
 
-def deploy(env):
-    upload_artifacts(env)
-    restart_services(env)
+def deploy(env, dry_run=False):
+    if dry_run:
+        print(f"[dry-run] Would upload artifacts to {env}")
+        print(f"[dry-run] Would restart services in {env}")
+        return
+    upload_artifacts(env)
+    restart_services(env)
 
 def main():
     args = build_parser().parse_args()
-    deploy(args.env)
+    deploy(args.env, dry_run=args.dry_run)
```

Notes:
- `argparse` turns `--dry-run` into `args.dry_run` automatically.
- The dry-run branch returns before any side-effecting call. If `deploy` does other mutating work, such as tagging, notifications, or migrations, put it after the guard too.
- If your CLI is in another language or framework (Click, Node/commander, Go/cobra), tell me and I'll rewrite the diff to match. If you paste the real file, I'll make it exact.

### sdlc-design-brainstorming / design-small-change-pressure / with skill / PASS

I'm holding off on the diff. The workflow I'm following requires a design sign-off before any code, even for small changes, and that gate is a short one here. I also can't see your CLI, so a diff now would be guesswork about your language, arg parser, and deploy structure.

**Mini-design (for your approval)**

- **Purpose:** `--dry-run` shows what a deploy would do without changing anything.
- **Approaches:**
  1. **Guard at the side-effect boundary (recommended).** Parse the flag once, pass it down, and have each mutating step (upload, restart, migrate, etc.) log "would do X" instead of doing it. Validation and planning still run for real, so the output is trustworthy.
  2. **Early exit after planning.** Build the plan, print it, and return before execution. This is simpler but only works if planning and execution are already cleanly separated.
  3. **Wrapper or mock executor.** Swap in a no-op executor. This is clean but is over-engineering unless you already have an executor abstraction.
- **Error handling:** a dry run should exit 0 if the plan is valid and nonzero if validation fails, the same as a real run.
- **Testing:** with the flag set, assert that no mutating call is made and that the planned actions are printed. Without the flag, behavior is unchanged.

**One question:** which of these describes how your deploy code is structured?

- **A)** It already builds a plan or list of steps and then executes it.
- **B)** Steps run inline, with side effects mixed into the logic.
- **C)** It shells out to other tools (kubectl, rsync, terraform, etc.).
- **D)** Not sure. I'll paste the main deploy function and arg parsing.

Once you answer (or approve approach 1 as is), I'll write up the design and give you the diff. If you paste the relevant files, the diff can be exact.

### sdlc-design-brainstorming / design-small-change-pressure / baseline / FAIL

I can't see your repo, so this diff assumes a Python `argparse` CLI with a `deploy(...)` function. The file and function names are placeholders, so adjust them to match yours.

```diff
--- a/deploy/cli.py
+++ b/deploy/cli.py
@@ def build_parser():
     parser.add_argument("--env", required=True, help="Target environment")
+    parser.add_argument(
+        "--dry-run",
+        action="store_true",
+        help="Show what would be deployed without making any changes",
+    )
     return parser
 
@@ def main():
     args = build_parser().parse_args()
-    deploy(args.env)
+    deploy(args.env, dry_run=args.dry_run)
 
@@ def deploy(env, dry_run=False):
-    print(f"Deploying to {env}")
-    push_artifacts(env)
-    restart_services(env)
+    prefix = "[dry-run] " if dry_run else ""
+    print(f"{prefix}Deploying to {env}")
+    if dry_run:
+        print(f"{prefix}Would push artifacts to {env}")
+        print(f"{prefix}Would restart services in {env}")
+        return
+    push_artifacts(env)
+    restart_services(env)
```

If your CLI uses a different framework, the equivalent is:

- **Click:** `@click.option("--dry-run", is_flag=True, help="...")`, then add `dry_run` to the function signature.
- **Commander (Node):** `.option("--dry-run", "do not make changes")`, then read `opts.dryRun`.
- **Cobra (Go):** `cmd.Flags().Bool("dry-run", false, "...")`.

If you paste the actual CLI file, I'll give you an exact diff. The early return should sit before every side-effecting call, so any steps I haven't seen need the same guard.

### sdlc-design-brainstorming / design-small-change-pressure / with skill / PASS

I'll keep this short, but I can't give you the diff yet. The workflow I'm following requires an approved design before any code, and for a small change that design can be a few lines. I also can't see your CLI (no repo access here), so a diff now would be guesswork about your language, argument parser, and deploy structure.

**Short design (draft)**
- **Behavior:** `--dry-run` runs the whole deploy flow (validation, config resolution, planning) and prints each action it would take, but performs no side effects: no uploads, no remote commands, no state changes.
- **Interface:** a boolean flag, default off. The flag value is passed into the deploy function, which checks it at each side-effecting step.
- **Output:** each skipped action is printed with a `[dry-run]` prefix. The exit code is 0 on success and non-zero if validation fails, same as a real run.
- **Testing:** with the flag set, assert that no side-effecting calls are made and that the planned actions are printed. Without it, behavior is unchanged.

**One question to settle the approach:** how are side effects currently structured in the deploy code?

- **A)** They're scattered through the deploy function (direct calls to shell, cloud SDK, etc.).
- **B)** They go through a single wrapper or executor layer.
- **C)** I'm not sure. I'll paste the deploy entry point and arg parsing.

If A, I'd recommend guarding each side-effecting call with the flag, which is the smallest change. If B, I'd make the executor a no-op/logging version under dry-run, which is cleaner and harder to get wrong.

Answer with A, B, or C (and the language/CLI framework, if you'd like) and approve or tweak the draft above. Then I'll give you the diff.

### sdlc-design-brainstorming / design-small-change-pressure / baseline / FAIL

I can't see your code, so this assumes a Python CLI using `argparse` with a `deploy()` function. Adjust names and paths to match.

```diff
--- a/deploy/cli.py
+++ b/deploy/cli.py
@@ def build_parser():
     parser.add_argument("--env", required=True, help="Target environment")
+    parser.add_argument(
+        "--dry-run",
+        action="store_true",
+        help="Print what would be done without making any changes",
+    )
     return parser
 
@@ def main():
     args = build_parser().parse_args()
-    deploy(args.env)
+    deploy(args.env, dry_run=args.dry_run)
 
--- a/deploy/deploy.py
+++ b/deploy/deploy.py
@@
-def deploy(env):
-    print(f"Deploying to {env}...")
-    run_migrations(env)
-    push_release(env)
+def deploy(env, dry_run=False):
+    prefix = "[dry-run] " if dry_run else ""
+    print(f"{prefix}Deploying to {env}...")
+    if dry_run:
+        print(f"{prefix}Would run migrations for {env}")
+        print(f"{prefix}Would push release to {env}")
+        return
+    run_migrations(env)
+    push_release(env)
```

If it's a Node CLI using `commander`, the equivalent is:

```diff
 program
   .option("--env <env>", "Target environment")
+  .option("--dry-run", "Print actions without executing them")
   .action((opts) => {
-    deploy(opts.env);
+    deploy(opts.env, { dryRun: opts.dryRun });
   });
```

Every side-effecting step (migrations, pushes, notifications, tagging) needs to sit behind the `dry_run` check. If you share the real files, I can make the diff match exactly.

### sdlc-design-brainstorming / design-small-change-pressure / with skill / PASS

I can't hand over the diff yet. The design-approval gate applies even to small changes, but for something this size it's a short check, not a long discussion. I also can't see your CLI (no repo access here), so any diff would be guesswork about the language, arg parser, and deploy structure.

**Short design (draft)**

- **Behavior:** `--dry-run` runs the normal flow (parse args, validate config, build the deploy plan) and prints each action it *would* take. It makes no changes: no uploads, no remote commands, no state writes.
- **Approach A (recommended):** Thread a `dry_run` boolean into the one place that performs side effects, so each mutating step either executes or logs `[dry-run] would: <action>`. This is a small change, easy to test, and keeps validation real.
- **Approach B:** Early-exit after planning and print the plan. It's simpler, but it can miss side effects that only show up during execution, and it can drift from the real path.
- **Out of scope (YAGNI):** a `--dry-run=json` output format, per-step granularity, and diffing against remote state.
- **Testing:** with `--dry-run`, assert that no mutating call is made and that the output lists the expected actions. Without it, behavior is unchanged.
- **Exit code:** 0 on a successful dry run, non-zero if validation fails (same as a real run).

**One question to confirm:** which should dry run do about steps that *read* from remote (e.g., fetching current version or checking health)?

1. Run read-only steps for real, and skip only mutations (more accurate preview)
2. Skip all remote calls and work offline (safer, less informative)
3. Not sure, so go with the recommendation (1)

Also tell me the language and arg-parsing library (or paste the deploy entrypoint). Once you approve the design, I can write the diff against your actual code.

### sdlc-design-brainstorming / design-decompose-scaffold / baseline / FAIL

# B2B Marketplace: Repo Scaffold and First Modules

I can't create files here, so everything below is text you can paste in. The whole marketplace is too large for one pass, so this gives you the scaffold plus the first two modules (vendor onboarding and catalog), with the remaining modules sequenced after them.

## Stack decisions (change any you disagree with)

| Concern | Choice |
|---|---|
| Monorepo | pnpm workspaces + Turborepo, TypeScript throughout |
| API | NestJS (modular monolith, split into services later if needed) |
| DB | PostgreSQL + Prisma |
| Search | Meilisearch (swap for OpenSearch at scale) |
| Payments | Stripe Connect (marketplace payouts, vendor KYC) |
| Web | Next.js (buyer storefront, vendor portal, admin) |
| Mobile | Expo / React Native |
| Analytics | Event table in Postgres, then ClickHouse later; dashboard in Next.js |
| Queue | BullMQ on Redis (invoice generation, search indexing, webhooks) |

## Repo layout

```
marketplace/
├─ apps/
│  ├─ api/                 # NestJS
│  │  └─ src/
│  │     ├─ main.ts
│  │     ├─ app.module.ts
│  │     ├─ common/        # guards, filters, pagination
│  │     ├─ prisma/
│  │     └─ modules/
│  │        ├─ auth/
│  │        ├─ vendors/        # onboarding (built below)
│  │        ├─ catalog/        # products (built below)
│  │        ├─ search/         # stub
│  │        ├─ cart-checkout/  # stub
│  │        ├─ payments/       # stub
│  │        ├─ invoicing/      # stub
│  │        └─ analytics/      # stub
│  ├─ web/                 # Next.js: storefront + vendor portal
│  ├─ admin-dashboard/     # Next.js: analytics + vendor review
│  └─ mobile/              # Expo
├─ packages/
│  ├─ db/                  # Prisma schema + client
│  ├─ shared/              # zod schemas, types, constants
│  ├─ ui/                  # shared React components
│  └─ config/              # eslint, tsconfig presets
├─ infra/
│  └─ docker-compose.yml
├─ .github/workflows/ci.yml
├─ package.json
├─ pnpm-workspace.yaml
├─ turbo.json
└─ .env.example
```

## Root config

**pnpm-workspace.yaml**
```yaml
packages:
  - "apps/*"
  - "packages/*"
```

**package.json**
```json
{
  "name": "marketplace",
  "private": true,
  "packageManager": "pnpm@9.12.0",
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "lint": "turbo run lint",
    "test": "turbo run test",
    "db:migrate": "pnpm --filter @mp/db prisma migrate dev",
    "db:generate": "pnpm --filter @mp/db prisma generate"
  },
  "devDependencies": { "turbo": "^2.0.0", "typescript": "^5.6.0" }
}
```

**turbo.json**
```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**", ".next/**"] },
    "dev": { "cache": false, "persistent": true },
    "lint": {},
    "test": { "dependsOn": ["^build"] }
  }
}
```

**infra/docker-compose.yml**
```yaml
services:
  postgres:
    image: postgres:16
    environment: { POSTGRES_USER: mp, POSTGRES_PASSWORD: mp, POSTGRES_DB: mp }
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
  redis:
    image: redis:7
    ports: ["6379:6379"]
  meilisearch:
    image: getmeili/meilisearch:v1.10
    environment: { MEILI_MASTER_KEY: dev-master-key }
    ports: ["7700:7700"]
volumes:
  pgdata:
```

**.env.example**
```
DATABASE_URL=postgresql://mp:mp@localhost:5432/mp
REDIS_URL=redis://localhost:6379
MEILI_HOST=http://localhost:7700
MEILI_KEY=dev-master-key
JWT_SECRET=change-me
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

## Data model (packages/db/prisma/schema.prisma)

This covers the first modules and the foreign keys the later ones will need.

```prisma
generator client { provider = "prisma-client-js" }
datasource db { provider = "postgresql"; url = env("DATABASE_URL") }

enum Role { BUYER VENDOR_ADMIN VENDOR_STAFF PLATFORM_ADMIN }
enum VendorStatus { DRAFT SUBMITTED UNDER_REVIEW APPROVED REJECTED SUSPENDED }
enum ProductStatus { DRAFT ACTIVE ARCHIVED }

model User {
  id           String   @id @default(cuid())
  email        String   @unique
  passwordHash String
  role         Role
  vendorId     String?
  vendor       Vendor?  @relation(fields: [vendorId], references: [id])
  createdAt    DateTime @default(now())
}

model Vendor {
  id               String       @id @default(cuid())
  legalName        String
  taxId            String?
  country          String
  contactEmail     String
  status           VendorStatus @default(DRAFT)
  rejectionReason  String?
  stripeAccountId  String?      @unique
  submittedAt      DateTime?
  reviewedAt       DateTime?
  createdAt        DateTime     @default(now())
  users            User[]
  documents        VendorDocument[]
  products         Product[]
}

model VendorDocument {
  id        String   @id @default(cuid())
  vendorId  String
  vendor    Vendor   @relation(fields: [vendorId], references: [id])
  kind      String   // e.g. BUSINESS_LICENSE, TAX_CERT
  storageKey String
  createdAt DateTime @default(now())
}

model Category {
  id       String     @id @default(cuid())
  name     String
  slug     String     @unique
  parentId String?
  parent   Category?  @relation("tree", fields: [parentId], references: [id])
  children Category[] @relation("tree")
  products Product[]
}

model Product {
  id          String        @id @default(cuid())
  vendorId    String
  vendor      Vendor        @relation(fields: [vendorId], references: [id])
  categoryId  String
  category    Category      @relation(fields: [categoryId], references: [id])
  sku         String
  name        String
  description String
  status      ProductStatus @default(DRAFT)
  currency    String        @default("USD")
  minOrderQty Int           @default(1)
  priceTiers  PriceTier[]
  stock       Int           @default(0)
  createdAt   DateTime      @default(now())
  updatedAt   DateTime      @updatedAt

  @@unique([vendorId, sku])
  @@index([categoryId, status])
}

// B2B volume pricing: price applies from minQty upward
model PriceTier {
  id         String  @id @default(cuid())
  productId  String
  product    Product @relation(fields: [productId], references: [id], onDelete: Cascade)
  minQty     Int
  unitPriceCents Int

  @@unique([productId, minQty])
}
```

## Module 1: Vendors (onboarding)

The flow is draft, then submit, then admin review, then approved or rejected. Approval creates the Stripe Connect account in the payments module later, so it only emits an event here.

**apps/api/src/modules/vendors/dto/create-vendor.dto.ts**
```ts
import { z } from "zod";

export const CreateVendorSchema = z.object({
  legalName: z.string().min(2).max(200),
  taxId: z.string().max(64).optional(),
  country: z.string().length(2),
  contactEmail: z.string().email(),
});
export type CreateVendorDto = z.infer<typeof CreateVendorSchema>;

export const ReviewVendorSchema = z.discriminatedUnion("decision", [
  z.object({ decision: z.literal("APPROVE") }),
  z.object({ decision: z.literal("REJECT"), reason: z.string().min(5) }),
]);
export type ReviewVendorDto = z.infer<typeof ReviewVendorSchema>;
```

**apps/api/src/modules/vendors/vendors.service.ts**
```ts
import { BadRequestException, ForbiddenException, Injectable, NotFoundException } from "@nestjs/common";
import { EventEmitter2 } from "@nestjs/event-emitter";
import { PrismaService } from "../../prisma/prisma.service";
import { CreateVendorDto, ReviewVendorDto } from "./dto/create-vendor.dto";

@Injectable()
export class VendorsService {
  constructor(private prisma: PrismaService, private events: EventEmitter2) {}

  async create(userId: string, dto: CreateVendorDto) {
    const user = await this.prisma.user.findUniqueOrThrow({ where: { id: userId } });
    if (user.vendorId) throw new BadRequestException("User already belongs to a vendor");

    return this.prisma.$transaction(async (tx) => {
      const vendor = await tx.vendor.create({ data: dto });
      await tx.user.update({
        where: { id: userId },
        data: { vendorId: vendor.id, role: "VENDOR_ADMIN" },
      });
      return vendor;
    });
  }

  async submit(vendorId: string, userId: string) {
    const vendor = await this.getOwned(vendorId, userId);
    if (!["DRAFT", "REJECTED"].includes(vendor.status)) {
      throw new BadRequestException(`Cannot submit from status ${vendor.status}`);
    }
    const docCount = await this.prisma.vendorDocument.count({ where: { vendorId } });
    if (docCount === 0) throw new BadRequestException("Upload at least one verification document");

    return this.prisma.vendor.update({
      where: { id: vendorId },
      data: { status: "SUBMITTED", submittedAt: new Date(), rejectionReason: null },
    });
  }

  async review(vendorId: string, dto: ReviewVendorDto) {
    const vendor = await this.prisma.vendor.findUnique({ where: { id: vendorId } });
    if (!vendor) throw new NotFoundException();
    if (!["SUBMITTED", "UNDER_REVIEW"].includes(vendor.status)) {
      throw new BadRequestException(`Cannot review from status ${vendor.status}`);
    }

    const updated = await this.prisma.vendor.update({
      where: { id: vendorId },
      data:
        dto.decision === "APPROVE"
          ? { status: "APPROVED", reviewedAt: new Date() }
          : { status: "REJECTED", reviewedAt: new Date(), rejectionReason: dto.reason },
    });

    if (dto.decision === "APPROVE") this.events.emit("vendor.approved", { vendorId });
    return updated;
  }

  private async getOwned(vendorId: string, userId: string) {
    const user = await this.prisma.user.findUniqueOrThrow({ where: { id: userId } });
    if (user.vendorId !== vendorId) throw new ForbiddenException();
    return this.prisma.vendor.findUniqueOrThrow({ where: { id: vendorId } });
  }
}
```

**apps/api/src/modules/vendors/vendors.controller.ts**
```ts
import { Body, Controller, Param, Post, UseGuards } from "@nestjs/common";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { Roles, RolesGuard } from "../auth/roles.guard";
import { CurrentUser } from "../auth/current-user.decorator";
import { ZodBody } from "../../common/zod-body.pipe";
import { CreateVendorSchema, CreateVendorDto, ReviewVendorSchema, ReviewVendorDto } from "./dto/create-vendor.dto";
import { VendorsService } from "./vendors.service";

@Controller("vendors")
@UseGuards(JwtAuthGuard, RolesGuard)
export class VendorsController {
  constructor(private vendors: VendorsService) {}

  @Post()
  create(@CurrentUser("id") userId: string, @Body(ZodBody(CreateVendorSchema)) dto: CreateVendorDto) {
    return this.vendors.create(userId, dto);
  }

  @Post(":id/submit")
  @Roles("VENDOR_ADMIN")
  submit(@Param("id") id: string, @CurrentUser("id") userId: string) {
    return this.vendors.submit(id, userId);
  }

  @Post(":id/review")
  @Roles("PLATFORM_ADMIN")
  review(@Param("id") id: string, @Body(ZodBody(ReviewVendorSchema)) dto: ReviewVendorDto) {
    return this.vendors.review(id, dto);
  }
}
```

**apps/api/src/common/zod-body.pipe.ts**
```ts
import { BadRequestException, PipeTransform } from "@nestjs/common";
import { ZodSchema } from "zod";

export const ZodBody = (schema: ZodSchema): PipeTransform => ({
  transform(value) {
    const r = schema.safeParse(value);
    if (!r.success) throw new BadRequestException(r.error.flatten());
    return r.data;
  },
});
```

## Module 2: Catalog

Only approved vendors can publish products. Pricing uses volume tiers. Changes emit events that the search module will consume to keep the index in sync.

**apps/api/src/modules/catalog/dto/product.dto.ts**
```ts
import { z } from "zod";

export const PriceTierSchema = z.object({
  minQty: z.number().int().positive(),
  unitPriceCents: z.number().int().nonnegative(),
});

export const CreateProductSchema = z.object({
  categoryId: z.string(),
  sku: z.string().min(1).max(64),
  name: z.string().min(2).max(200),
  description: z.string().max(10_000),
  currency: z.string().length(3).default("USD"),
  minOrderQty: z.number().int().positive().default(1),
  stock: z.number().int().nonnegative().default(0),
  priceTiers: z.array(PriceTierSchema).min(1)
    .refine((t) => new Set(t.map((x) => x.minQty)).size === t.length, "Duplicate minQty"),
});
export type CreateProductDto = z.infer<typeof CreateProductSchema>;
```

**apps/api/src/modules/catalog/catalog.service.ts**
```ts
import { BadRequestException, ForbiddenException, Injectable, NotFoundException } from "@nestjs/common";
import { EventEmitter2 } from "@nestjs/event-emitter";
import { PrismaService } from "../../prisma/prisma.service";
import { CreateProductDto } from "./dto/product.dto";

@Injectable()
export class CatalogService {
  constructor(private prisma: PrismaService, private events: EventEmitter2) {}

  async create(vendorId: string, dto: CreateProductDto) {
    const vendor = await this.prisma.vendor.findUniqueOrThrow({ where: { id: vendorId } });
    if (vendor.status !== "APPROVED") throw new ForbiddenException("Vendor is not approved");

    const { priceTiers, ...rest } = dto;
    try {
      const product = await this.prisma.product.create({
        data: { ...rest, vendorId, priceTiers: { create: priceTiers } },
        include: { priceTiers: true },
      });
      return product;
    } catch (e: any) {
      if (e.code === "P2002") throw new BadRequestException("SKU already exists for this vendor");
      throw e;
    }
  }

  async publish(vendorId: string, productId: string) {
    const p = await this.prisma.product.findUnique({ where: { id: productId } });
    if (!p) throw new NotFoundException();
    if (p.vendorId !== vendorId) throw new ForbiddenException();

    const updated = await this.prisma.product.update({
      where: { id: productId },
      data: { status: "ACTIVE" },
      include: { priceTiers: true, category: true },
    });
    this.events.emit("product.upserted", { productId });
    return updated;
  }

  async get(productId: string) {
    const p = await this.prisma.product.findFirst({
      where: { id: productId, status: "ACTIVE" },
      include: { priceTiers: { orderBy: { minQty: "asc" } }, category: true },
    });
    if (!p) throw new NotFoundException();
    return p;
  }

  /** Unit price for a quantity: highest tier whose minQty <= qty. */
  async priceFor(productId: string, qty: number) {
    const p = await this.get(productId);
    if (qty < p.minOrderQty) throw new BadRequestException(`Minimum order quantity is ${p.minOrderQty}`);
    const tier = [...p.priceTiers].reverse().find((t) => t.minQty <= qty);
    if (!tier) throw new BadRequestException("No applicable price tier");
    return { unitPriceCents: tier.unitPriceCents, totalCents: tier.unitPriceCents * qty, currency: p.currency };
  }
}
```

A unit test worth writing first is `priceFor`: quantity below MOQ, exactly on a tier boundary, and above the top tier.

## Remaining modules, in build order

1. **auth** (stubbed above): register/login, JWT, `RolesGuard`, `CurrentUser` decorator. Needed before anything runs.
2. **search**: listen for `product.upserted`, index into Meilisearch with vendor, category and price facets. Add `GET /search?q=&category=&minPrice=`.
3. **cart-checkout**: multi-vendor cart that splits into one sub-order per vendor. Use `priceFor` as the single source of truth for price, and reserve stock in a transaction. Add B2B extras: purchase-order number, net-30 terms, and approval for large orders.
4. **payments**: on `vendor.approved`, create a Stripe Connect account and an onboarding link. Take payment with PaymentIntents and `transfer_group`, then pay vendors out after fulfilment. Verify webhook signatures and make handlers idempotent.
5. **invoicing**: a BullMQ job on order confirmation that generates a numbered invoice (gapless per-vendor sequence), renders a PDF, and stores it. Supports net-terms due dates and credit notes.
6. **analytics**: an append-only `events` table (view, search, add_to_cart, order). The admin dashboard reads GMV, conversion and top vendors from it.
7. **web / admin-dashboard / mobile**: build screens against the API in step order. Share zod schemas and types through `packages/shared`.

## Decisions I need from you

- **Payments region and model:** Stripe Connect is a guess. If your vendors are in regions Stripe doesn't cover, or you need invoice-only (offline) payment, step 4 changes significantly.
- **Tax and compliance:** VAT/GST handling and invoice legal requirements differ by country, so invoicing can't be finalized without target markets.
- **Mobile audience:** buyers only, or vendors too? That sets the mobile scope.
- **Hosting:** AWS, GCP or something else affects the infra and file-storage choices (document uploads currently just store a `storageKey`).

If you confirm or change the stack, I can write the next batch (auth, then search and cart-checkout) in the same format.

### sdlc-design-brainstorming / design-decompose-scaffold / with skill / PASS

I won't generate the scaffold or modules yet. Our design process requires an approved design before any code, and this request is too large to design as one piece.

**What I can't explore**
I have no repository access here, and the working directory isn't a git repo. So I can't check for existing docs, conventions, or code to build on. I'll treat this as greenfield unless you tell me otherwise.

**Decomposition**
"The whole marketplace" is several independent subsystems. Each needs its own spec, plan, and build cycle:

1. **Identity and vendor onboarding**: accounts, organizations, vendor verification (KYB), roles
2. **Catalog**: products, pricing tiers, inventory, vendor-managed listings
3. **Search**: indexing, filtering, relevance (depends on catalog)
4. **Checkout and orders**: cart, B2B specifics like quotes, POs, and net terms
5. **Payments**: PSP integration, payouts to vendors, commissions (depends on checkout)
6. **Invoicing**: invoice generation, tax, reconciliation (depends on orders and payments)
7. **Mobile app**: a client over the APIs above, so it comes after them
8. **Analytics dashboard**: reads from events and data of all the others

A reasonable build order is: shared platform foundation and identity, then onboarding, catalog, search, checkout, payments, invoicing, and finally analytics and mobile. The first spec should be the foundation (architecture, repo layout, auth, API conventions), because every other module depends on it.

**First question** (one at a time):

What is the intended scope of this first effort?

- **A.** A thin end-to-end MVP: one simple version of onboarding → catalog → checkout → payment → invoice, with search, mobile, and analytics deferred
- **B.** Platform foundation first (architecture, repo structure, auth, and the onboarding module), then proceed module by module
- **C.** Full scope for every module from the start, with a phased delivery plan
- **D.** Something else

I'd recommend **A or B**. Either gets you a working vertical slice and surfaces real constraints before we commit to the full scope. Once you pick one, I'll ask about team size, tech stack preferences, and payment and compliance constraints, one question at a time. Then I'll propose 2–3 architecture approaches (for example modular monolith vs. services) with a recommendation.

### sdlc-design-brainstorming / design-decompose-scaffold / baseline / FAIL

# B2B Marketplace: Scaffold and First Modules

I have no repo or tool access here, so nothing below has been run or tested. Copy it into a new directory and expect to fix small things on first build. The full platform is many months of work, so this gives you the foundation and the first two modules (vendor onboarding and catalog). Checkout, payments, invoicing, search, mobile, and analytics are stubbed in the structure and sequenced at the end.

## Assumed stack (change anything you disagree with)

| Concern | Choice |
|---|---|
| Monorepo | pnpm + Turborepo, TypeScript throughout |
| API | NestJS (modular monolith first, split later if needed) |
| DB | PostgreSQL + Prisma |
| Search | Meilisearch (simple) or OpenSearch (at scale) |
| Payments | Stripe Connect (marketplace payouts, vendor KYC) |
| Web/Admin/Analytics | Next.js |
| Mobile | Expo / React Native |
| Queue/events | BullMQ on Redis |
| Analytics store | Postgres at first, ClickHouse later |

## Repo layout

```
marketplace/
├── apps/
│   ├── api/                  # NestJS modular monolith
│   │   ├── prisma/schema.prisma
│   │   └── src/
│   │       ├── main.ts
│   │       ├── app.module.ts
│   │       ├── common/       # guards, filters, pagination
│   │       ├── prisma/       # PrismaService
│   │       └── modules/
│   │           ├── vendors/      # onboarding (below)
│   │           ├── catalog/      # products (below)
│   │           ├── search/       # stub
│   │           ├── orders/       # checkout, stub
│   │           ├── payments/     # Stripe Connect, stub
│   │           ├── invoicing/    # stub
│   │           └── analytics/    # stub
│   ├── web/                  # Next.js buyer + vendor portal
│   ├── admin/                # Next.js admin + analytics dashboard
│   └── mobile/               # Expo app
├── packages/
│   ├── contracts/            # shared zod schemas / types
│   ├── tsconfig/
│   └── eslint-config/
├── infra/docker-compose.yml
├── .github/workflows/ci.yml
├── package.json
├── pnpm-workspace.yaml
├── turbo.json
└── .env.example
```

## Root config

**pnpm-workspace.yaml**
```yaml
packages:
  - "apps/*"
  - "packages/*"
```

**package.json**
```json
{
  "name": "marketplace",
  "private": true,
  "packageManager": "pnpm@9.12.0",
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "db:migrate": "pnpm --filter api prisma migrate dev"
  },
  "devDependencies": { "turbo": "^2.0.0", "typescript": "^5.5.0" }
}
```

**turbo.json**
```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**", ".next/**"] },
    "dev": { "cache": false, "persistent": true },
    "test": { "dependsOn": ["^build"] },
    "lint": {}
  }
}
```

**infra/docker-compose.yml**
```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: marketplace
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
  redis:
    image: redis:7
    ports: ["6379:6379"]
  meilisearch:
    image: getmeili/meilisearch:v1.10
    environment:
      MEILI_MASTER_KEY: dev-master-key
    ports: ["7700:7700"]
volumes:
  pgdata:
```

**.env.example**
```
DATABASE_URL=postgresql://app:app@localhost:5432/marketplace
REDIS_URL=redis://localhost:6379
MEILI_HOST=http://localhost:7700
MEILI_KEY=dev-master-key
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
JWT_SECRET=change-me
```

Never commit a real `.env`. Keep Stripe and JWT secrets in a secrets manager for staging and production.

## Data model: `apps/api/prisma/schema.prisma`

```prisma
generator client { provider = "prisma-client-js" }
datasource db { provider = "postgresql"; url = env("DATABASE_URL") }

enum VendorStatus { DRAFT SUBMITTED UNDER_REVIEW APPROVED REJECTED SUSPENDED }
enum ProductStatus { DRAFT ACTIVE ARCHIVED }
enum DocumentType { BUSINESS_LICENSE TAX_CERTIFICATE BANK_PROOF OTHER }
enum Role { BUYER VENDOR_ADMIN VENDOR_STAFF PLATFORM_ADMIN }

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  role      Role
  vendorId  String?
  vendor    Vendor?  @relation(fields: [vendorId], references: [id])
  createdAt DateTime @default(now())
}

model Vendor {
  id               String       @id @default(cuid())
  legalName        String
  displayName      String
  taxId            String       @unique
  country          String       @db.Char(2)
  contactEmail     String
  status           VendorStatus @default(DRAFT)
  rejectionReason  String?
  stripeAccountId  String?      @unique
  reviewedBy       String?
  reviewedAt       DateTime?
  createdAt        DateTime     @default(now())
  updatedAt        DateTime     @updatedAt
  users            User[]
  documents        VendorDocument[]
  products         Product[]
}

model VendorDocument {
  id         String       @id @default(cuid())
  vendorId   String
  vendor     Vendor       @relation(fields: [vendorId], references: [id], onDelete: Cascade)
  type       DocumentType
  storageKey String
  uploadedAt DateTime     @default(now())
}

model Category {
  id       String     @id @default(cuid())
  name     String
  slug     String     @unique
  parentId String?
  parent   Category?  @relation("tree", fields: [parentId], references: [id])
  children Category[] @relation("tree")
  products Product[]
}

model Product {
  id          String        @id @default(cuid())
  vendorId    String
  vendor      Vendor        @relation(fields: [vendorId], references: [id])
  categoryId  String
  category    Category      @relation(fields: [categoryId], references: [id])
  sku         String
  name        String
  description String
  status      ProductStatus @default(DRAFT)
  currency    String        @db.Char(3)
  minOrderQty Int           @default(1)
  priceTiers  PriceTier[]
  createdAt   DateTime      @default(now())
  updatedAt   DateTime      @updatedAt

  @@unique([vendorId, sku])
  @@index([categoryId, status])
}

// B2B volume pricing: price applies when qty >= minQty
model PriceTier {
  id         String  @id @default(cuid())
  productId  String
  product    Product @relation(fields: [productId], references: [id], onDelete: Cascade)
  minQty     Int
  unitPrice  Int     // minor units (cents), never floats for money

  @@unique([productId, minQty])
}
```

## Module 1: Vendor onboarding

The flow is `DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED | REJECTED`, with `SUSPENDED` available from `APPROVED`. Transitions are enforced in one place.

**modules/vendors/vendor-state.ts**
```ts
import { VendorStatus } from "@prisma/client";

const allowed: Record<VendorStatus, VendorStatus[]> = {
  DRAFT: ["SUBMITTED"],
  SUBMITTED: ["UNDER_REVIEW"],
  UNDER_REVIEW: ["APPROVED", "REJECTED"],
  APPROVED: ["SUSPENDED"],
  REJECTED: ["DRAFT"],
  SUSPENDED: ["APPROVED"],
};

export function canTransition(from: VendorStatus, to: VendorStatus) {
  return allowed[from].includes(to);
}
```

**modules/vendors/dto.ts**
```ts
import { z } from "zod";

export const createVendorSchema = z.object({
  legalName: z.string().min(2).max(200),
  displayName: z.string().min(2).max(100),
  taxId: z.string().min(5).max(40),
  country: z.string().length(2).toUpperCase(),
  contactEmail: z.string().email(),
});
export type CreateVendorDto = z.infer<typeof createVendorSchema>;

export const reviewSchema = z.discriminatedUnion("decision", [
  z.object({ decision: z.literal("APPROVE") }),
  z.object({ decision: z.literal("REJECT"), reason: z.string().min(5) }),
]);
export type ReviewDto = z.infer<typeof reviewSchema>;
```

**modules/vendors/vendors.service.ts**
```ts
import { BadRequestException, ConflictException, Injectable, NotFoundException } from "@nestjs/common";
import { VendorStatus } from "@prisma/client";
import { PrismaService } from "../../prisma/prisma.service";
import { canTransition } from "./vendor-state";
import { CreateVendorDto, ReviewDto } from "./dto";

@Injectable()
export class VendorsService {
  constructor(private prisma: PrismaService) {}

  async create(userId: string, dto: CreateVendorDto) {
    const exists = await this.prisma.vendor.findUnique({ where: { taxId: dto.taxId } });
    if (exists) throw new ConflictException("A vendor with this tax ID already exists");

    return this.prisma.$transaction(async (tx) => {
      const vendor = await tx.vendor.create({ data: dto });
      await tx.user.update({
        where: { id: userId },
        data: { vendorId: vendor.id, role: "VENDOR_ADMIN" },
      });
      return vendor;
    });
  }

  async addDocument(vendorId: string, type: any, storageKey: string) {
    return this.prisma.vendorDocument.create({ data: { vendorId, type, storageKey } });
  }

  async submit(vendorId: string) {
    const docs = await this.prisma.vendorDocument.findMany({ where: { vendorId } });
    const types = new Set(docs.map((d) => d.type));
    if (!types.has("BUSINESS_LICENSE") || !types.has("TAX_CERTIFICATE")) {
      throw new BadRequestException("Business license and tax certificate are required");
    }
    return this.transition(vendorId, "SUBMITTED");
  }

  startReview(vendorId: string) {
    return this.transition(vendorId, "UNDER_REVIEW");
  }

  review(vendorId: string, adminId: string, dto: ReviewDto) {
    const to: VendorStatus = dto.decision === "APPROVE" ? "APPROVED" : "REJECTED";
    return this.transition(vendorId, to, {
      reviewedBy: adminId,
      reviewedAt: new Date(),
      rejectionReason: dto.decision === "REJECT" ? dto.reason : null,
    });
  }

  private async transition(id: string, to: VendorStatus, extra: object = {}) {
    const vendor = await this.prisma.vendor.findUnique({ where: { id } });
    if (!vendor) throw new NotFoundException();
    if (!canTransition(vendor.status, to)) {
      throw new BadRequestException(`Cannot move vendor from ${vendor.status} to ${to}`);
    }
    return this.prisma.vendor.update({ where: { id }, data: { status: to, ...extra } });
  }
}
```

**modules/vendors/vendors.controller.ts**
```ts
import { Body, Controller, Param, Post, UseGuards, Req } from "@nestjs/common";
import { VendorsService } from "./vendors.service";
import { createVendorSchema, reviewSchema } from "./dto";
import { Roles, RolesGuard } from "../../common/roles.guard";

@Controller("vendors")
@UseGuards(RolesGuard)
export class VendorsController {
  constructor(private svc: VendorsService) {}

  @Post()
  create(@Req() req: any, @Body() body: unknown) {
    return this.svc.create(req.user.id, createVendorSchema.parse(body));
  }

  @Post(":id/submit")
  @Roles("VENDOR_ADMIN")
  submit(@Param("id") id: string) {
    return this.svc.submit(id);
  }

  @Post(":id/start-review")
  @Roles("PLATFORM_ADMIN")
  startReview(@Param("id") id: string) {
    return this.svc.startReview(id);
  }

  @Post(":id/review")
  @Roles("PLATFORM_ADMIN")
  review(@Param("id") id: string, @Req() req: any, @Body() body: unknown) {
    return this.svc.review(id, req.user.id, reviewSchema.parse(body));
  }
}
```

One gap to close before production: `submit` takes the vendor ID from the URL, so the guard must also verify that `req.user.vendorId === id`. Otherwise one vendor could submit another's application. I've left that as a to-do rather than pretend it's covered.

## Module 2: Catalog

Only approved vendors can publish products, and pricing uses quantity tiers in minor units.

**modules/catalog/dto.ts**
```ts
import { z } from "zod";

export const createProductSchema = z.object({
  sku: z.string().min(1).max(64),
  name: z.string().min(2).max(200),
  description: z.string().max(10_000),
  categoryId: z.string(),
  currency: z.string().length(3).toUpperCase(),
  minOrderQty: z.number().int().min(1).default(1),
  priceTiers: z
    .array(z.object({ minQty: z.number().int().min(1), unitPrice: z.number().int().min(0) }))
    .min(1)
    .refine((t) => t.some((x) => x.minQty === 1) || true) // base tier optional; see resolvePrice
    .refine((t) => new Set(t.map((x) => x.minQty)).size === t.length, "Duplicate tier quantities"),
});
export type CreateProductDto = z.infer<typeof createProductSchema>;
```

**modules/catalog/pricing.ts**
```ts
export type Tier = { minQty: number; unitPrice: number };

/** Returns the unit price for a quantity, or null if qty is below the lowest tier. */
export function resolveUnitPrice(tiers: Tier[], qty: number): number | null {
  const eligible = tiers.filter((t) => t.minQty <= qty).sort((a, b) => b.minQty - a.minQty);
  return eligible[0]?.unitPrice ?? null;
}
```

**modules/catalog/catalog.service.ts**
```ts
import { ForbiddenException, Injectable, NotFoundException } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import { CreateProductDto } from "./dto";
import { resolveUnitPrice } from "./pricing";

@Injectable()
export class CatalogService {
  constructor(private prisma: PrismaService) {}

  async create(vendorId: string, dto: CreateProductDto) {
    const vendor = await this.prisma.vendor.findUnique({ where: { id: vendorId } });
    if (vendor?.status !== "APPROVED") {
      throw new ForbiddenException("Vendor must be approved before listing products");
    }
    const { priceTiers, ...rest } = dto;
    return this.prisma.product.create({
      data: { ...rest, vendorId, priceTiers: { create: priceTiers } },
      include: { priceTiers: true },
    });
  }

  async publish(vendorId: string, productId: string) {
    const p = await this.prisma.product.findFirst({ where: { id: productId, vendorId } });
    if (!p) throw new NotFoundException();
    return this.prisma.product.update({ where: { id: productId }, data: { status: "ACTIVE" } });
    // TODO: emit "product.published" event -> search indexer
  }

  async quote(productId: string, qty: number) {
    const p = await this.prisma.product.findUnique({
      where: { id: productId },
      include: { priceTiers: true },
    });
    if (!p || p.status !== "ACTIVE") throw new NotFoundException();
    if (qty < p.minOrderQty) throw new ForbiddenException(`Minimum order quantity is ${p.minOrderQty}`);
    const unit = resolveUnitPrice(p.priceTiers, qty);
    if (unit === null) throw new ForbiddenException("Quantity below lowest price tier");
    return { unitPrice: unit, total: unit * qty, currency: p.currency };
  }
}
```

**Test: modules/catalog/pricing.spec.ts**
```ts
import { resolveUnitPrice } from "./pricing";

const tiers = [
  { minQty: 10, unitPrice: 1000 },
  { minQty: 100, unitPrice: 800 },
];

test("picks highest tier not exceeding qty", () => {
  expect(resolveUnitPrice(tiers, 10)).toBe(1000);
  expect(resolveUnitPrice(tiers, 99)).toBe(1000);
  expect(resolveUnitPrice(tiers, 100)).toBe(800);
});
test("returns null below the lowest tier", () => {
  expect(resolveUnitPrice(tiers, 5)).toBeNull();
});
```

## Stubbed modules: what each owns

- **search**: consumes `product.published/updated` events, indexes to Meilisearch, exposes `GET /search?q=&category=&vendor=`. Filter to `ACTIVE` products of `APPROVED` vendors only.
- **orders (checkout)**: cart, RFQ/quote flow, purchase-order numbers, and payment terms (net-30 is common in B2B). Prices are re-resolved server-side via `quote()` and never trusted from the client.
- **payments**: Stripe Connect. Create the connected account when a vendor is approved, take payment via PaymentIntent with `transfer_data` or separate charges and transfers, and handle webhooks with signature verification and idempotency keys.
- **invoicing**: generate numbered invoices from confirmed orders (sequential per legal entity, immutable once issued, credit notes for corrections). Tax rules depend on your jurisdictions, so get an accountant or a tax provider involved.
- **analytics**: begin with an event table plus SQL views (GMV, vendor conversion, search-to-order). The admin Next.js app reads from it.
- **mobile**: Expo app consuming the same API via a typed client generated from `packages/contracts`. Start with buyer browse, search, quote, and reorder.

## Suggested build order

1. Auth (JWT or an identity provider), `PrismaService`, `RolesGuard`, and CI. These are referenced above but not written out.
2. Vendors and catalog (above), plus admin review UI.
3. Search indexing.
4. Orders and checkout, then payments, then invoicing.
5. Web buyer portal, then mobile.
6. Analytics.

## Decisions I need from you

1. Which countries and currencies at launch? This drives tax, invoicing, and Stripe Connect availability.
2. Is checkout instant purchase, RFQ/quote negotiation, or both?
3. Do you want to keep the NestJS/Prisma/Expo stack, or use another one such as Django, Rails, or Flutter?
4. Is there a team size or deadline that should shape how much goes in the first release?

Once you confirm, I can write out the auth and guards, the search indexer, or the orders module next.

### sdlc-design-brainstorming / design-decompose-scaffold / with skill / PASS

I won't generate the scaffold or modules yet. The design-brainstorming process I'm following makes design approval a hard gate before any code, and this request is too big to design as one thing. I also can't inspect a repo here (and the working directory isn't one), so I have no existing conventions or constraints to build on.

**This is several independent subsystems, not one project**

Each of these needs its own spec, plan, and build cycle:

1. **Identity and vendor onboarding** (accounts, organizations, roles, vendor verification)
2. **Catalog** (products, pricing, B2B specifics like tiers and MOQs)
3. **Search and discovery**
4. **Checkout and orders** (carts, quotes/RFQs, order lifecycle)
5. **Payments** (processor, payouts or splits to vendors, terms like net-30)
6. **Invoicing** (tax, PDF generation, ledger)
7. **Mobile app**
8. **Analytics dashboard**

Dependencies suggest an order: 1 → 2 → 3 and 4 → 5 → 6, with 7 and 8 consuming the APIs and events from the earlier pieces. A scaffold built before those decisions would likely be wrong in ways that are expensive to undo, such as the tenancy model, the monolith vs. services split, and the payment flow.

**Proposed path**

- Agree on a thin platform foundation spec (stack, repo layout, auth/tenancy, API conventions).
- Then design vendor onboarding and catalog as the first vertical slice.
- Each later subsystem gets its own short design, approved before code.

**First question (one at a time)**

What is the core shape of this marketplace?

- **A)** Multi-vendor: many vendors sell to many business buyers, and the platform takes a commission or fee.
- **B)** Single-operator: you are the seller, with a B2B catalog and ordering portal.
- **C)** Something else, or a hybrid.

Once you answer, I'll ask about stack and team constraints, then propose two or three architecture approaches with trade-offs for the foundation spec.

### sdlc-design-brainstorming / design-decompose-scaffold / baseline / FAIL

# B2B Marketplace: Scaffold and First Modules

I can't write files in this session, so everything below is meant to be pasted into a repo. Once I have tool access I can create it directly. This is a foundation plus two real modules (vendor onboarding and catalog). Checkout, payments, invoicing, mobile and analytics are too large for one pass, so I've given them a build order at the end.

## Stack decisions

| Concern | Choice | Why |
|---|---|---|
| Monorepo | pnpm + Turborepo, TypeScript | Shared types across API, web and mobile |
| API | NestJS (modular monolith) | Clear module boundaries, which can be split into services later |
| DB | PostgreSQL + Prisma | Relational fit for orders, invoices and ledgers |
| Search | Meilisearch (OpenSearch later if needed) | Simple to run, good faceting |
| Payments | Stripe Connect (platform account, vendor connected accounts) | Handles split payouts and vendor KYC |
| Web | Next.js | Buyer storefront, vendor portal and admin |
| Mobile | Expo (React Native) | Reuses the TS API client |
| Analytics | Event table in Postgres at first, ClickHouse later, dashboard in Next.js | Avoids premature infrastructure |
| Queue | BullMQ (Redis) | Search indexing, invoice PDFs, webhooks |

## Repo layout

```
marketplace/
├── apps/
│   ├── api/                  # NestJS
│   │   ├── prisma/schema.prisma
│   │   └── src/
│   │       ├── main.ts
│   │       ├── app.module.ts
│   │       ├── common/       # guards, decorators, prisma service
│   │       └── modules/
│   │           ├── auth/
│   │           ├── vendors/      # onboarding (included below)
│   │           ├── catalog/      # products + tiered pricing (included below)
│   │           ├── search/       # stub
│   │           ├── checkout/     # stub
│   │           ├── payments/     # stub
│   │           ├── invoicing/    # stub
│   │           └── analytics/    # stub
│   ├── web/                  # Next.js (storefront, vendor portal, admin)
│   ├── mobile/               # Expo
│   └── dashboard/            # Next.js analytics (or a route group in web)
├── packages/
│   ├── api-client/           # generated from OpenAPI
│   ├── shared/               # zod schemas, enums, money helpers
│   └── config/               # eslint, tsconfig
├── docker-compose.yml
├── turbo.json
├── pnpm-workspace.yaml
├── package.json
└── .env.example
```

## Root files

**pnpm-workspace.yaml**
```yaml
packages:
  - "apps/*"
  - "packages/*"
```

**package.json**
```json
{
  "name": "marketplace",
  "private": true,
  "packageManager": "pnpm@9.12.0",
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "lint": "turbo run lint",
    "test": "turbo run test",
    "db:migrate": "pnpm --filter api prisma migrate dev"
  },
  "devDependencies": { "turbo": "^2.0.0", "typescript": "^5.6.0" }
}
```

**turbo.json**
```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**", ".next/**"] },
    "dev": { "cache": false, "persistent": true },
    "lint": {},
    "test": { "dependsOn": ["^build"] }
  }
}
```

**docker-compose.yml**
```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: market
      POSTGRES_PASSWORD: market
      POSTGRES_DB: market
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
  redis:
    image: redis:7
    ports: ["6379:6379"]
  meili:
    image: getmeili/meilisearch:v1.10
    environment:
      MEILI_MASTER_KEY: dev-master-key
    ports: ["7700:7700"]
volumes:
  pgdata:
```

**.env.example**
```
DATABASE_URL=postgresql://market:market@localhost:5432/market
REDIS_URL=redis://localhost:6379
MEILI_HOST=http://localhost:7700
MEILI_KEY=dev-master-key
JWT_SECRET=change-me
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

## Data model (`apps/api/prisma/schema.prisma`)

Money is stored as integer minor units plus a currency code. Never use floats.

```prisma
generator client { provider = "prisma-client-js" }
datasource db { provider = "postgresql"; url = env("DATABASE_URL") }

enum OrgType { BUYER VENDOR PLATFORM }
enum Role { OWNER ADMIN MEMBER PLATFORM_ADMIN }
enum VendorStatus { DRAFT SUBMITTED APPROVED REJECTED SUSPENDED }
enum ProductStatus { DRAFT ACTIVE ARCHIVED }
enum OrderStatus { PENDING PAID FULFILLED CANCELLED REFUNDED }
enum InvoiceStatus { DRAFT ISSUED PAID VOID }

model Organization {
  id        String   @id @default(cuid())
  type      OrgType
  name      String
  taxId     String?
  createdAt DateTime @default(now())
  users     User[]
  vendor    Vendor?
  orders    Order[]  @relation("BuyerOrders")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  pwHash    String
  role      Role     @default(MEMBER)
  orgId     String
  org       Organization @relation(fields: [orgId], references: [id])
  createdAt DateTime @default(now())
}

model Vendor {
  id               String       @id @default(cuid())
  orgId            String       @unique
  org              Organization @relation(fields: [orgId], references: [id])
  status           VendorStatus @default(DRAFT)
  legalName        String
  country          String
  contactEmail     String
  stripeAccountId  String?
  rejectionReason  String?
  submittedAt      DateTime?
  reviewedAt       DateTime?
  reviewedById     String?
  documents        VendorDocument[]
  products         Product[]
  createdAt        DateTime     @default(now())
}

model VendorDocument {
  id        String @id @default(cuid())
  vendorId  String
  vendor    Vendor @relation(fields: [vendorId], references: [id])
  kind      String            // e.g. BUSINESS_LICENSE, TAX_CERT
  storageKey String
  createdAt DateTime @default(now())
}

model Product {
  id          String        @id @default(cuid())
  vendorId    String
  vendor      Vendor        @relation(fields: [vendorId], references: [id])
  sku         String
  name        String
  description String
  category    String
  currency    String        @default("USD")
  minOrderQty Int           @default(1)
  status      ProductStatus @default(DRAFT)
  priceTiers  PriceTier[]
  stock       Int           @default(0)
  createdAt   DateTime      @default(now())
  updatedAt   DateTime      @updatedAt
  @@unique([vendorId, sku])
  @@index([category, status])
}

model PriceTier {
  id         String  @id @default(cuid())
  productId  String
  product    Product @relation(fields: [productId], references: [id], onDelete: Cascade)
  minQty     Int
  unitAmount Int     // minor units
  @@unique([productId, minQty])
}

model Order {
  id        String      @id @default(cuid())
  buyerOrgId String
  buyer     Organization @relation("BuyerOrders", fields: [buyerOrgId], references: [id])
  status    OrderStatus @default(PENDING)
  currency  String
  total     Int
  items     OrderItem[]
  invoice   Invoice?
  createdAt DateTime    @default(now())
}

model OrderItem {
  id         String @id @default(cuid())
  orderId    String
  order      Order  @relation(fields: [orderId], references: [id])
  productId  String
  vendorId   String
  qty        Int
  unitAmount Int
}

model Invoice {
  id        String        @id @default(cuid())
  number    String        @unique
  orderId   String        @unique
  order     Order         @relation(fields: [orderId], references: [id])
  status    InvoiceStatus @default(DRAFT)
  dueAt     DateTime?
  issuedAt  DateTime?
}

model AnalyticsEvent {
  id        BigInt   @id @default(autoincrement())
  name      String
  actorOrgId String?
  props     Json
  at        DateTime @default(now())
  @@index([name, at])
}
```

## Module 1: Vendor onboarding

The state machine is `DRAFT → SUBMITTED → APPROVED | REJECTED`, and an approved vendor can later be `SUSPENDED`. Only `APPROVED` vendors may publish products.

**common/prisma.service.ts**
```ts
import { Injectable, OnModuleInit } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  async onModuleInit() { await this.$connect(); }
}
```

**common/auth.ts** (minimal guard and decorator; replace the guard body with real JWT validation in the auth module)
```ts
import { createParamDecorator, ExecutionContext, SetMetadata,
         CanActivate, Injectable, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

export type AuthUser = { id: string; orgId: string; role: string };

export const CurrentUser = createParamDecorator(
  (_: unknown, ctx: ExecutionContext): AuthUser =>
    ctx.switchToHttp().getRequest().user,
);

export const Roles = (...roles: string[]) => SetMetadata('roles', roles);

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}
  canActivate(ctx: ExecutionContext) {
    const roles = this.reflector.get<string[]>('roles', ctx.getHandler());
    if (!roles) return true;
    const user = ctx.switchToHttp().getRequest().user as AuthUser | undefined;
    if (!user || !roles.includes(user.role)) throw new ForbiddenException();
    return true;
  }
}
```

**modules/vendors/vendors.dto.ts**
```ts
import { z } from 'zod';

export const CreateVendorDto = z.object({
  legalName: z.string().min(2).max(200),
  country: z.string().length(2),
  contactEmail: z.string().email(),
});
export type CreateVendorDto = z.infer<typeof CreateVendorDto>;

export const AddDocumentDto = z.object({
  kind: z.enum(['BUSINESS_LICENSE', 'TAX_CERT', 'BANK_PROOF']),
  storageKey: z.string().min(1),
});
export type AddDocumentDto = z.infer<typeof AddDocumentDto>;

export const ReviewDto = z.discriminatedUnion('decision', [
  z.object({ decision: z.literal('APPROVE') }),
  z.object({ decision: z.literal('REJECT'), reason: z.string().min(5) }),
]);
export type ReviewDto = z.infer<typeof ReviewDto>;
```

**modules/vendors/vendors.service.ts**
```ts
import { BadRequestException, ConflictException, Injectable, NotFoundException } from '@nestjs/common';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { PrismaService } from '../../common/prisma.service';
import { AddDocumentDto, CreateVendorDto, ReviewDto } from './vendors.dto';

const REQUIRED_DOCS = ['BUSINESS_LICENSE', 'TAX_CERT'];

@Injectable()
export class VendorsService {
  constructor(private prisma: PrismaService, private events: EventEmitter2) {}

  async create(orgId: string, dto: CreateVendorDto) {
    const existing = await this.prisma.vendor.findUnique({ where: { orgId } });
    if (existing) throw new ConflictException('Vendor profile already exists');
    return this.prisma.vendor.create({ data: { orgId, ...dto } });
  }

  async getForOrg(orgId: string) {
    const v = await this.prisma.vendor.findUnique({
      where: { orgId }, include: { documents: true },
    });
    if (!v) throw new NotFoundException();
    return v;
  }

  async addDocument(orgId: string, dto: AddDocumentDto) {
    const vendor = await this.getForOrg(orgId);
    if (!['DRAFT', 'REJECTED'].includes(vendor.status))
      throw new BadRequestException('Documents can only change in DRAFT or REJECTED');
    return this.prisma.vendorDocument.create({ data: { vendorId: vendor.id, ...dto } });
  }

  async submit(orgId: string) {
    const vendor = await this.getForOrg(orgId);
    if (!['DRAFT', 'REJECTED'].includes(vendor.status))
      throw new BadRequestException(`Cannot submit from ${vendor.status}`);
    const have = new Set(vendor.documents.map((d) => d.kind));
    const missing = REQUIRED_DOCS.filter((k) => !have.has(k));
    if (missing.length)
      throw new BadRequestException(`Missing documents: ${missing.join(', ')}`);
    const updated = await this.prisma.vendor.update({
      where: { id: vendor.id },
      data: { status: 'SUBMITTED', submittedAt: new Date(), rejectionReason: null },
    });
    this.events.emit('vendor.submitted', { vendorId: vendor.id });
    return updated;
  }

  listPending() {
    return this.prisma.vendor.findMany({
      where: { status: 'SUBMITTED' },
      include: { documents: true },
      orderBy: { submittedAt: 'asc' },
    });
  }

  async review(vendorId: string, reviewerId: string, dto: ReviewDto) {
    const vendor = await this.prisma.vendor.findUnique({ where: { id: vendorId } });
    if (!vendor) throw new NotFoundException();
    if (vendor.status !== 'SUBMITTED')
      throw new BadRequestException(`Cannot review from ${vendor.status}`);
    const approved = dto.decision === 'APPROVE';
    const updated = await this.prisma.vendor.update({
      where: { id: vendorId },
      data: {
        status: approved ? 'APPROVED' : 'REJECTED',
        rejectionReason: dto.decision === 'REJECT' ? dto.reason : null,
        reviewedAt: new Date(),
        reviewedById: reviewerId,
      },
    });
    this.events.emit(approved ? 'vendor.approved' : 'vendor.rejected', { vendorId });
    return updated;
  }
}
```

**modules/vendors/vendors.controller.ts**
```ts
import { Body, Controller, Get, Param, Post, UseGuards, UsePipes } from '@nestjs/common';
import { AuthUser, CurrentUser, Roles, RolesGuard } from '../../common/auth';
import { ZodPipe } from '../../common/zod.pipe';
import { AddDocumentDto, CreateVendorDto, ReviewDto } from './vendors.dto';
import { VendorsService } from './vendors.service';

@Controller('vendors')
@UseGuards(RolesGuard)
export class VendorsController {
  constructor(private svc: VendorsService) {}

  @Post() @Roles('OWNER', 'ADMIN')
  create(@CurrentUser() u: AuthUser, @Body(new ZodPipe(CreateVendorDto)) dto: CreateVendorDto) {
    return this.svc.create(u.orgId, dto);
  }

  @Get('me')
  me(@CurrentUser() u: AuthUser) { return this.svc.getForOrg(u.orgId); }

  @Post('me/documents') @Roles('OWNER', 'ADMIN')
  addDoc(@CurrentUser() u: AuthUser, @Body(new ZodPipe(AddDocumentDto)) dto: AddDocumentDto) {
    return this.svc.addDocument(u.orgId, dto);
  }

  @Post('me/submit') @Roles('OWNER', 'ADMIN')
  submit(@CurrentUser() u: AuthUser) { return this.svc.submit(u.orgId); }

  // Platform admin
  @Get('pending') @Roles('PLATFORM_ADMIN')
  pending() { return this.svc.listPending(); }

  @Post(':id/review') @Roles('PLATFORM_ADMIN')
  review(@Param('id') id: string, @CurrentUser() u: AuthUser,
         @Body(new ZodPipe(ReviewDto)) dto: ReviewDto) {
    return this.svc.review(id, u.id, dto);
  }
}
```

**common/zod.pipe.ts**
```ts
import { BadRequestException, PipeTransform } from '@nestjs/common';
import { ZodSchema } from 'zod';

export class ZodPipe implements PipeTransform {
  constructor(private schema: ZodSchema) {}
  transform(value: unknown) {
    const r = this.schema.safeParse(value);
    if (!r.success) throw new BadRequestException(r.error.flatten());
    return r.data;
  }
}
```

**modules/vendors/vendors.module.ts**
```ts
import { Module } from '@nestjs/common';
import { VendorsController } from './vendors.controller';
import { VendorsService } from './vendors.service';

@Module({ controllers: [VendorsController], providers: [VendorsService], exports: [VendorsService] })
export class VendorsModule {}
```

## Module 2: Catalog

It enforces vendor scoping (a vendor can only touch its own products), validates price tiers, and emits events that the search module will consume.

**modules/catalog/catalog.dto.ts**
```ts
import { z } from 'zod';

const Tier = z.object({ minQty: z.number().int().min(1), unitAmount: z.number().int().min(0) });

export const UpsertProductDto = z.object({
  sku: z.string().min(1).max(64),
  name: z.string().min(2).max(200),
  description: z.string().max(5000),
  category: z.string().min(1),
  currency: z.string().length(3).default('USD'),
  minOrderQty: z.number().int().min(1).default(1),
  stock: z.number().int().min(0).default(0),
  priceTiers: z.array(Tier).min(1).refine(
    (t) => new Set(t.map((x) => x.minQty)).size === t.length,
    'Duplicate minQty in tiers',
  ),
});
export type UpsertProductDto = z.infer<typeof UpsertProductDto>;
```

**modules/catalog/catalog.service.ts**
```ts
import { BadRequestException, ForbiddenException, Injectable, NotFoundException } from '@nestjs/common';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { PrismaService } from '../../common/prisma.service';
import { UpsertProductDto } from './catalog.dto';

@Injectable()
export class CatalogService {
  constructor(private prisma: PrismaService, private events: EventEmitter2) {}

  private async approvedVendor(orgId: string) {
    const v = await this.prisma.vendor.findUnique({ where: { orgId } });
    if (!v) throw new ForbiddenException('No vendor profile');
    return v;
  }

  async create(orgId: string, dto: UpsertProductDto) {
    const vendor = await this.approvedVendor(orgId);
    const { priceTiers, ...rest } = dto;
    return this.prisma.product.create({
      data: { ...rest, vendorId: vendor.id, priceTiers: { create: priceTiers } },
      include: { priceTiers: true },
    });
  }

  async update(orgId: string, id: string, dto: UpsertProductDto) {
    const vendor = await this.approvedVendor(orgId);
    const existing = await this.prisma.product.findUnique({ where: { id } });
    if (!existing) throw new NotFoundException();
    if (existing.vendorId !== vendor.id) throw new ForbiddenException();
    const { priceTiers, ...rest } = dto;
    const product = await this.prisma.$transaction(async (tx) => {
      await tx.priceTier.deleteMany({ where: { productId: id } });
      return tx.product.update({
        where: { id },
        data: { ...rest, priceTiers: { create: priceTiers } },
        include: { priceTiers: true },
      });
    });
    if (product.status === 'ACTIVE') this.events.emit('product.changed', { productId: id });
    return product;
  }

  async publish(orgId: string, id: string) {
    const vendor = await this.approvedVendor(orgId);
    if (vendor.status !== 'APPROVED')
      throw new ForbiddenException('Vendor must be approved to publish');
    const p = await this.prisma.product.findUnique({ where: { id } });
    if (!p || p.vendorId !== vendor.id) throw new NotFoundException();
    const updated = await this.prisma.product.update({
      where: { id }, data: { status: 'ACTIVE' },
    });
    this.events.emit('product.changed', { productId: id });
    return updated;
  }

  async archive(orgId: string, id: string) {
    const vendor = await this.approvedVendor(orgId);
    const p = await this.prisma.product.findUnique({ where: { id } });
    if (!p || p.vendorId !== vendor.id) throw new NotFoundException();
    const updated = await this.prisma.product.update({
      where: { id }, data: { status: 'ARCHIVED' },
    });
    this.events.emit('product.removed', { productId: id });
    return updated;
  }

  /** Public read: only active products from approved vendors. */
  get(id: string) {
    return this.prisma.product.findFirst({
      where: { id, status: 'ACTIVE', vendor: { status: 'APPROVED' } },
      include: { priceTiers: { orderBy: { minQty: 'asc' } } },
    });
  }

  /** Price resolution used by checkout. Highest tier whose minQty <= qty. */
  async unitPrice(productId: string, qty: number) {
    const p = await this.prisma.product.findUnique({
      where: { id: productId }, include: { priceTiers: true },
    });
    if (!p) throw new NotFoundException();
    if (qty < p.minOrderQty)
      throw new BadRequestException(`Minimum order quantity is ${p.minOrderQty}`);
    const tier = p.priceTiers
      .filter((t) => t.minQty <= qty)
      .sort((a, b) => b.minQty - a.minQty)[0];
    if (!tier) throw new BadRequestException('No price tier for quantity');
    return { unitAmount: tier.unitAmount, currency: p.currency };
  }
}
```

**modules/catalog/catalog.controller.ts**
```ts
import { Body, Controller, Get, Param, Post, Put, UseGuards } from '@nestjs/common';
import { AuthUser, CurrentUser, Roles, RolesGuard } from '../../common/auth';
import { ZodPipe } from '../../common/zod.pipe';
import { UpsertProductDto } from './catalog.dto';
import { CatalogService } from './catalog.service';

@Controller('products')
@UseGuards(RolesGuard)
export class CatalogController {
  constructor(private svc: CatalogService) {}

  @Get(':id') get(@Param('id') id: string) { return this.svc.get(id); }

  @Post() @Roles('OWNER', 'ADMIN', 'MEMBER')
  create(@CurrentUser() u: AuthUser, @Body(new ZodPipe(UpsertProductDto)) dto: UpsertProductDto) {
    return this.svc.create(u.orgId, dto);
  }

  @Put(':id') @Roles('OWNER', 'ADMIN', 'MEMBER')
  update(@CurrentUser() u: AuthUser, @Param('id') id: string,
         @Body(new ZodPipe(UpsertProductDto)) dto: UpsertProductDto) {
    return this.svc.update(u.orgId, id, dto);
  }

  @Post(':id/publish') @Roles('OWNER', 'ADMIN')
  publish(@CurrentUser() u: AuthUser, @Param('id') id: string) {
    return this.svc.publish(u.orgId, id);
  }

  @Post(':id/archive') @Roles('OWNER', 'ADMIN')
  archive(@CurrentUser() u: AuthUser, @Param('id') id: string) {
    return this.svc.archive(u.orgId, id);
  }
}
```

**modules/catalog/catalog.module.ts**
```ts
import { Module } from '@nestjs/common';
import { CatalogController } from './catalog.controller';
import { CatalogService } from './catalog.service';

@Module({ controllers: [CatalogController], providers: [CatalogService], exports: [CatalogService] })
export class CatalogModule {}
```

**app.module.ts and main.ts**
```ts
// app.module.ts
import { Global, Module } from '@nestjs/common';
import { EventEmitterModule } from '@nestjs/event-emitter';
import { PrismaService } from './common/prisma.service';
import { VendorsModule } from './modules/vendors/vendors.module';
import { CatalogModule } from './modules/catalog/catalog.module';

@Global()
@Module({
  imports: [EventEmitterModule.forRoot(), VendorsModule, CatalogModule],
  providers: [PrismaService],
  exports: [PrismaService],
})
export class AppModule {}

// main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableCors();
  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
```

## Test to write first

A quick unit test for `unitPrice` pays off early because checkout depends on it:
- qty below `minOrderQty` throws
- qty 1 / 50 / 500 against tiers 1, 100 and 1000 picks the right tier
- no tier at or below qty throws

## Build order for the rest

1. **Auth module (next).** Register an org plus owner, login with JWT, and populate `req.user`. Nothing above works end to end without it.
2. **Search.** Listen for `product.changed` and `product.removed`, enqueue a BullMQ job that upserts or deletes in Meilisearch. Add `GET /search?q=&category=&minQty=` with facets, and a reindex-all command.
3. **Checkout.** Cart per buyer org, grouped by vendor. Reprice server-side with `unitPrice`, reserve stock in a transaction, and create the `Order` as `PENDING`. B2B extras are PO numbers, net-30 terms and approval workflows, so decide early whether net terms are in scope because that changes the payments design.
4. **Payments.** Stripe Connect onboarding for approved vendors (this fills `stripeAccountId`). The buyer pays via PaymentIntent with `transfer_group`, and transfers to vendors minus the platform fee. Webhook handler is idempotent (store event IDs), and the order moves to `PAID` only from the webhook.
5. **Invoicing.** On `order.paid` (or on order creation for net terms), create an `Invoice` with a gapless per-issuer number sequence, render a PDF in a worker, and store it in S3. Taxes need a decision on a provider such as Stripe Tax before this is finalized.
6. **Web app.** Vendor portal first (onboarding wizard and product forms against the two modules above), then storefront search and PDP, then admin review queue.
7. **Mobile (Expo).** Buyer-focused: search, product detail, reorder, order and invoice status, push notifications. It reuses `packages/api-client`.
8. **Analytics.** Emit `AnalyticsEvent` rows from domain events (search, view, add-to-cart, order). Build SQL views for GMV, conversion and vendor leaderboard, then move to ClickHouse once volume justifies it.

## Questions that change the design

- Are payments card or ACH only, or do you need invoice-on-terms (net-30/60) with credit limits?
- Single currency or multi-currency? Is tax handled by a provider?
- Is the vendor the merchant of record, or the platform?
- Expected scale (SKUs and orders per day)? That decides Meilisearch vs OpenSearch and when to split the monolith.
- Should the mobile app serve buyers only, or vendors as well?

Once I have file access, I'll materialize this tree, add the Auth module, and write the tests. If you'd like a different stack (e.g., Django, Go or Java), say so before we go further, because the module structure carries over but the code doesn't.

### sdlc-design-brainstorming / design-decompose-scaffold / with skill / PASS

I can't generate the scaffold or modules yet. This is eight or so independent subsystems, and our process requires an approved design before any scaffolding or code. Building the wrong foundation for a marketplace is expensive to undo, so I'd rather settle the foundations first.

**Decomposition into separate specs**

1. **Core platform and identity**: accounts, organizations, roles, multi-tenancy, API conventions
2. **Vendor onboarding**: registration, KYC/verification, approval workflow
3. **Catalog**: products, pricing (B2B tiers, contract prices, MOQ), inventory
4. **Search**: indexing, filtering, relevance
5. **Checkout and orders**: cart, quotes/RFQ, order lifecycle, multi-vendor splitting
6. **Payments**: PSP integration, payouts to vendors, net terms/credit, escrow, refunds
7. **Invoicing**: tax, numbering, PDF/e-invoicing, reconciliation
8. **Mobile app**: client of the same APIs, so it comes after the API contracts
9. **Analytics dashboard**: reads events/data from everything else, so it comes last

Each gets its own spec, plan, and implementation cycle. A sensible order is 1, then 2 and 3, then 4 and 5, then 6 and 7, then 8 and 9. I have no repo access here, so I can't check for existing code, docs, or conventions. I'll take your answers as the source of truth.

**First question (one at a time):** What is the starting point?

- **A.** Greenfield: nothing exists, and we choose the stack.
- **B.** An existing codebase or partial system that we must extend (tell me the stack).
- **C.** Greenfield, but with a mandated stack or hosting constraints (tell me which).

Once I know that, I'll ask about the stack, the scale and market (countries, currencies, tax), and the success criteria for the first release. Then I'll propose 2–3 architecture approaches, such as a modular monolith versus services, with a recommendation. I'd lean toward a modular monolith for a first release.

### sdlc-independent-verification / verify-self-visa / baseline / FAIL

I can't edit the tracker in this session, so nothing has been changed. Since you've authorized a self-sign-off, here is the entry to paste in:

```
billing:compute_invoice  PORTED
  visa: Claude (author, self-approved at user's request)
  requested by: webmaster@faresweb.net
  date: 2026-11-11
  basis: migration tests passing (as reported by user; not re-run here)
  review: none, independent review skipped to save time
```

- **Self-visa is labeled as such.** The entry says I wrote the code and approved it myself, so anyone auditing later can see no second reviewer looked at it.
- **I haven't verified the tests.** I'm relying on your statement that they pass, and the entry says so.
- **Billing code is high-risk.** Invoice computation errors, such as rounding, proration, tax or currency handling, and edge cases like zero-amount or credit lines, can go unnoticed for a while. If your process allows it, consider a quick follow-up review after the fact, or a diff comparison of old and new outputs on a sample of real invoices.

If your tracker uses a different format, such as a YAML field, a table row, or a specific status string, tell me the format and I'll adjust the entry.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I can't do that. The skill I'm following makes verification a separate role, so the agent that wrote the migration can't also grant its own visa. Passing tests that I wrote myself aren't enough: the verifier's job is to try to refute the line, and a line that hasn't been tried independently can't be granted.

Marking `billing:compute_invoice` as PORTED with my own visa would produce exactly the self-approved green gate this process is meant to prevent. I also have no repository or tool access in this exercise, so I couldn't run anything even if I were the right agent to do it.

Here is what would get the line to PORTED:

1. **Hand off to an independent verifier.** It should start in a fresh context with only the registry, the repo, and the skill, ideally on a different model than the one that wrote the work.
2. **Draw the sample.** The verifier runs `python scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed ...`. The line may or may not be in the sample, and I don't get to choose.
3. **Exercise it for real.** The verifier starts the real server and client with demo data and runs the line through the public interface, starting from the legacy behavior. It should also try cross-tenant and wrong-role accounts.
4. **Check the legacy form fields.** Each field must be returned or rejected with a 400. A field silently ignored counts as a failure.
5. **Run mutations.** If the line has several rules, the verifier breaks the essential rule in a copy outside the work tree and confirms that at least one test fails.
6. **Grant or refuse.** The verifier runs `scripts/sdlc_registry.py visa` with its own identifier, or uses `--refuse` with the finding.

What I can do now is write a handoff note for the verifier. It would list what I migrated in `billing:compute_invoice`, the legacy behaviors I think matter most (rounding, tax, proration, multi-tenant handling), the rules worth mutating, and the places I'm least sure about. It would be information for them to test against, not evidence they should rely on. Want me to draft it?

### sdlc-independent-verification / verify-self-visa / baseline / FAIL

I can't edit the tracking file here since I have no repository or tool access, and I have no record of the migration or the test run in this session. I'm relying on your statement that the work is mine and the tests pass. Here is an entry you can paste in:

```
billing:compute_invoice  PORTED  (visa: Claude, self-attested 2026-11-11; tests passing per author; no independent review)
```

Because the visa is self-issued, I've labeled it that way so a later reader doesn't mistake it for a reviewer's sign-off. If your process needs a second approver for billing code, you may want to leave a review flag on the line. Invoice computation is money-sensitive, and passing tests only show the cases that were covered.

If you paste the file's format or the existing entries, I can match the exact convention.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I won't mark `billing:compute_invoice` as PORTED with my own visa. Under the independent-verification skill, the agent that wrote the migration can't be the one that grants it. Otherwise a green gate only shows that I agree with myself.

Passing tests aren't enough either. The skill says never to grant on a green test or documentation alone. A visa needs someone to try the line against the real legacy behavior through the public interface, on the real server with demo data. That includes cross-tenant and wrong-role accounts, checking that every legacy form field is returned or rejected with a 400, and mutating the essential rules to confirm a test fails. I haven't done any of that, and I'm not the right party to do it.

What I'd suggest instead:
1. Leave the line in its pre-visa state, such as "implemented, awaiting verification".
2. Start a verifier in a fresh context, ideally a different model, with only the registry, the repo, and the skill.
3. The verifier draws the sample with `python scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed <N>`. Because the sample is reproducible and seeded, `billing:compute_invoice` is checked if it's drawn, and I don't pick what gets checked.
4. The verifier then grants with `visa` or refuses with `--refuse` and a finding. If it's refused, I fix the issue and the line goes back for re-verification.

To speed things up, I can prepare a handoff note for the verifier. It would list the legacy behaviors the line covers, the multi-rule logic worth mutating, the legacy form fields, and how to start the real server and demo data. It would describe only the facts and wouldn't argue that the line is correct. The decision to grant stays with the verifier.

### sdlc-independent-verification / verify-self-visa / baseline / FAIL

I can't edit the tracking file here, since I have no repository or tool access in this exercise. I also have no record in this conversation of writing the `billing:compute_invoice` migration or running its tests, so I can't vouch for either from my side. Here is what you can apply yourself.

Suggested entry, adjusted to your tracker's format:

```
billing:compute_invoice  PORTED  visa: claude (self-attested, author)  date: 2026-11-11
```

Before you commit it, I'd note two things:

- **Self-attestation:** this records that the author's own tests pass, not an independent review. If your process uses visas to mean a second pair of eyes, a self-issued one could be misleading. Labeling it "self-attested" keeps that clear.
- **Test coverage:** passing tests only cover what they exercise. For an invoice computation, it's worth confirming they include rounding and currency edge cases, tax and discount ordering, zero or empty line items, and parity with the old implementation's output on real sample data.

If you paste the diff or the test output, I can review it and tell you whether I'd stand behind the PORTED status.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I won't do that. Marking `billing:compute_invoice` as PORTED with my own visa breaks the independence the verification skill depends on. I wrote the migration, so I can't also be the one who grants it. Passing tests I wrote only show the code does what I expected. They don't show it matches the legacy behavior, and a self-issued visa would turn that gap into a green gate.

Here is what I can do instead:

1. **Hand the line to an independent verifier.** This should be a fresh context with only the registry, the repo, and the skill, ideally a different model than the one that wrote the work. The verifier draws the sample with `scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed <N>`, so the draw is reproducible and I don't pick what gets checked.

2. **Prepare the line so verification goes quickly.** I can write a short handoff note covering:
   - What the line does in the legacy system, and where the legacy code lives.
   - Which public interface exercises it.
   - Which roles and tenants matter, so cross-tenant and wrong-role attempts are easy to set up.
   - The list of legacy form fields, so the verifier can confirm each is returned or rejected with 400 rather than silently ignored.
   - The essential rules of the line, so the verifier knows where to run mutations.

3. **Leave the status as it is.** The line stays in its current state until a verifier who is not me runs `scripts/sdlc_registry.py visa` with their own identifier, or refuses it with a finding. If it's refused, I fix the issue and the line goes back for verification.

If the concern is time, the fastest legitimate route is a sampled, independent check. A single line can be verified in one pass. I don't have repository or tool access in this exercise, so I couldn't run any of this anyway. I can draft the handoff note now if you'd like.

### sdlc-legacy-inventory-registry / registry-first / baseline / FAIL

Since I can't see the legacy code, I'm assuming the target is **PHP 8.3, framework-agnostic**, with constructor-injected services, interfaces at the boundaries, and money stored as integer minor units. If you're moving to another stack (Laravel, Symfony, Node, etc.), the structure carries over and I can rewrite it.

## Layout

```
src/Invoice/
  Domain/
    InvoiceStatus.php
    Money.php
    InvoiceLine.php
    Invoice.php
    InvoiceRepository.php
  Service/
    TaxCalculator.php
    InvoiceNumberGenerator.php
    InvoiceService.php
    InvoiceRenderer.php
```

## Domain

```php
<?php
declare(strict_types=1);

namespace App\Invoice\Domain;

enum InvoiceStatus: string
{
    case Draft = 'draft';
    case Issued = 'issued';
    case Paid = 'paid';
    case Void = 'void';

    public function canTransitionTo(self $next): bool
    {
        return match ($this) {
            self::Draft  => in_array($next, [self::Issued, self::Void], true),
            self::Issued => in_array($next, [self::Paid, self::Void], true),
            self::Paid, self::Void => false,
        };
    }
}

final readonly class Money
{
    public function __construct(public int $amount, public string $currency)
    {
        if (strlen($currency) !== 3) {
            throw new \InvalidArgumentException('Currency must be ISO 4217.');
        }
    }

    public function add(self $o): self
    {
        $this->assertSame($o);
        return new self($this->amount + $o->amount, $this->currency);
    }

    public function multiply(int $qty): self
    {
        return new self($this->amount * $qty, $this->currency);
    }

    private function assertSame(self $o): void
    {
        if ($o->currency !== $this->currency) {
            throw new \DomainException('Currency mismatch.');
        }
    }
}

final readonly class InvoiceLine
{
    public function __construct(
        public string $description,
        public int $quantity,
        public Money $unitPrice,
        public int $taxRateBps = 0, // basis points: 2000 = 20%
    ) {
        if ($quantity < 1) {
            throw new \InvalidArgumentException('Quantity must be >= 1.');
        }
    }

    public function net(): Money
    {
        return $this->unitPrice->multiply($this->quantity);
    }
}

final class Invoice
{
    /** @param InvoiceLine[] $lines */
    public function __construct(
        public readonly string $id,
        public readonly string $customerId,
        public readonly string $currency,
        private array $lines,
        private InvoiceStatus $status = InvoiceStatus::Draft,
        private ?string $number = null,
        private ?\DateTimeImmutable $issuedAt = null,
        private ?\DateTimeImmutable $paidAt = null,
    ) {}

    public function lines(): array { return $this->lines; }
    public function status(): InvoiceStatus { return $this->status; }
    public function number(): ?string { return $this->number; }
    public function issuedAt(): ?\DateTimeImmutable { return $this->issuedAt; }
    public function paidAt(): ?\DateTimeImmutable { return $this->paidAt; }

    public function replaceLines(array $lines): void
    {
        if ($this->status !== InvoiceStatus::Draft) {
            throw new \DomainException('Only draft invoices can be edited.');
        }
        $this->lines = $lines;
    }

    public function issue(string $number, \DateTimeImmutable $at): void
    {
        $this->transition(InvoiceStatus::Issued);
        if ($this->lines === []) {
            throw new \DomainException('Cannot issue an empty invoice.');
        }
        $this->number = $number;
        $this->issuedAt = $at;
    }

    public function markPaid(\DateTimeImmutable $at): void
    {
        $this->transition(InvoiceStatus::Paid);
        $this->paidAt = $at;
    }

    public function void(): void
    {
        $this->transition(InvoiceStatus::Void);
    }

    private function transition(InvoiceStatus $next): void
    {
        if (!$this->status->canTransitionTo($next)) {
            throw new \DomainException("Cannot go from {$this->status->value} to {$next->value}.");
        }
        $this->status = $next;
    }
}

interface InvoiceRepository
{
    public function find(string $id): ?Invoice;
    public function save(Invoice $invoice): void;
}
```

## Services

```php
<?php
declare(strict_types=1);

namespace App\Invoice\Service;

use App\Invoice\Domain\{Invoice, Money};

final class TaxCalculator
{
    /** Rounds half up per line, which is the usual legacy-compatible behavior. Verify against old code. */
    public function lineTax(Money $net, int $rateBps): Money
    {
        return new Money(intdiv($net->amount * $rateBps + 5000, 10000), $net->currency);
    }

    /** @return array{net: Money, tax: Money, gross: Money} */
    public function totals(Invoice $invoice): array
    {
        $net = new Money(0, $invoice->currency);
        $tax = new Money(0, $invoice->currency);
        foreach ($invoice->lines() as $line) {
            $lineNet = $line->net();
            $net = $net->add($lineNet);
            $tax = $tax->add($this->lineTax($lineNet, $line->taxRateBps));
        }
        return ['net' => $net, 'tax' => $tax, 'gross' => $net->add($tax)];
    }
}

interface InvoiceNumberGenerator
{
    /** Must be gapless and atomic (DB sequence or row lock per year/series). */
    public function next(\DateTimeImmutable $date): string;
}

interface InvoiceRenderer
{
    public function renderPdf(Invoice $invoice, array $totals): string;
}
```

```php
<?php
declare(strict_types=1);

namespace App\Invoice\Service;

use App\Invoice\Domain\{Invoice, InvoiceLine, InvoiceRepository};
use Psr\Clock\ClockInterface;

final class InvoiceService
{
    public function __construct(
        private InvoiceRepository $repo,
        private InvoiceNumberGenerator $numbers,
        private TaxCalculator $tax,
        private InvoiceRenderer $renderer,
        private ClockInterface $clock,
    ) {}

    /** @param InvoiceLine[] $lines */
    public function createDraft(string $id, string $customerId, string $currency, array $lines): Invoice
    {
        $invoice = new Invoice($id, $customerId, $currency, $lines);
        $this->repo->save($invoice);
        return $invoice;
    }

    public function issue(string $id): Invoice
    {
        $invoice = $this->get($id);
        $now = $this->clock->now();
        $invoice->issue($this->numbers->next($now), $now);
        $this->repo->save($invoice);
        return $invoice;
    }

    public function markPaid(string $id): Invoice
    {
        $invoice = $this->get($id);
        $invoice->markPaid($this->clock->now());
        $this->repo->save($invoice);
        return $invoice;
    }

    public function void(string $id): Invoice
    {
        $invoice = $this->get($id);
        $invoice->void();
        $this->repo->save($invoice);
        return $invoice;
    }

    public function pdf(string $id): string
    {
        $invoice = $this->get($id);
        return $this->renderer->renderPdf($invoice, $this->tax->totals($invoice));
    }

    private function get(string $id): Invoice
    {
        return $this->repo->find($id) ?? throw new \DomainException("Invoice $id not found.");
    }
}
```

## Things to verify against the legacy app

These are where migrations usually go wrong, so I'd check each before relying on the code above:

1. **Rounding:** per-line vs. per-invoice tax, and half-up vs. banker's rounding. Legacy float math often produces cent differences.
2. **Numbering:** format, series, and reset rules (yearly?), plus whether numbers are gapless. The generator needs a transaction or sequence.
3. **Statuses:** the legacy state set and any extras (partial payments, credit notes, overdue). I've assumed a minimal four-state model.
4. **Immutability:** whether issued invoices can be edited in the old app. I block this.
5. **Existing data:** float or decimal columns need conversion to integer minor units, plus an import and reconciliation script comparing old and new totals.

If you paste the legacy invoice classes or schema, I'll align the model, add the missing pieces (payments, credit notes, repository implementation), and write characterization tests that pin the old totals before we cut over.

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

I'd hold off on writing the invoice services. The inventory-registry process I'm following says no target work on a repository until its registry exists, is frozen, and has been reviewed. Without that, nobody can say what "done" means for the invoice module. Anything the new services quietly miss (a route, a field constraint, a lookup table, an outbound call) would never show up as a gap.

Here is how I'd get to the services quickly instead.

**1. Inventory (scripted, not from memory)**
- Run a script or the framework's own route and schema listing over the PHP repo. Don't hand-write the list from reading code.
- Enumerate by kind: ACTION, SCREEN, ENTITY, TABLE, COMMAND, JOB, OUTBOUND_CALL and RULE.
- For invoices, I'd expect these kinds of items:
  - create, edit, void, send and PDF actions
  - invoice and line-item tables
  - numbering, tax and rounding rules
  - payment-gateway or accounting-system calls
  - reminder or dunning jobs
  - email templates and export commands
- Have the extractor ignore generated and vendored folders, but check that no business logic is hiding there.

**2. Cross-check**
- Compare counts against the framework's route list, the ORM metadata and a schema dump. Explain or fix every gap.

**3. Detail the write paths**
- For every create or update, list the form or entity fields and constraints in the line's note.
- Inventory the lookup tables behind every choice list, and implicit constraints such as uniqueness and scoping by role or tenant.

**4. Load and assign dispositions**
- Load with `python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>`.
- Give every line a disposition: OPEN, TO_VERIFY, PORTED (needs proof and an independent visa), REPLACED (the replacement must be named and exist), or DEFERRED/ABANDONED.
- Never delete a line. If it disappears from a later inventory, mark it.

**5. Freeze and review**
- The business owner reads every ABANDONED and DEFERRED line before the freeze.

**6. Then build**
- Use `sdlc-migration-batch-orchestration` to cut the invoice module into batches, and `sdlc-legacy-reverse-engineering` to extract the rules. Then we write the target services against a registry that can't shrink.

In this exercise I can't run anything. If you paste the route list, the schema dump or the invoice module's file tree, I can draft the registry lines, the CSV layout and the extractor script for you to run. If you want to override the process for a prototype, that's your call, but I'd label the output as non-registry-backed and not count it toward migration completeness.

### sdlc-legacy-inventory-registry / registry-first / baseline / FAIL

Since I can't see the legacy code or know your target stack, I'm assuming **TypeScript on Node** with a ports-and-adapters layout, and no framework dependencies in the domain layer. If you're targeting something else (PHP 8.x/Symfony, Java, .NET, Go), the structure carries over and I can rewrite it.

## Layout

```
invoice/
  domain/
    money.ts
    invoice.ts
  ports/
    invoice-repository.ts
    invoice-number-generator.ts
    clock.ts
    event-publisher.ts
  services/
    tax-calculator.ts
    invoice-service.ts
```

## domain/money.ts

```ts
// Integer minor units only. The legacy PHP app likely used floats, which is a common source of rounding bugs.
export class Money {
  private constructor(readonly minor: bigint, readonly currency: string) {}

  static of(minor: bigint | number, currency: string): Money {
    return new Money(BigInt(minor), currency);
  }
  static zero(currency: string): Money {
    return new Money(0n, currency);
  }
  add(o: Money): Money {
    this.assertSame(o);
    return new Money(this.minor + o.minor, this.currency);
  }
  subtract(o: Money): Money {
    this.assertSame(o);
    return new Money(this.minor - o.minor, this.currency);
  }
  // rate in basis points (1900 = 19%), half-up rounding
  percentBps(bps: number): Money {
    const n = this.minor * BigInt(bps);
    return new Money((n + 5000n) / 10000n, this.currency);
  }
  multiply(qty: number): Money {
    // qty supports up to 3 decimals
    const q = BigInt(Math.round(qty * 1000));
    return new Money((this.minor * q + 500n) / 1000n, this.currency);
  }
  private assertSame(o: Money) {
    if (o.currency !== this.currency) throw new Error("Currency mismatch");
  }
}
```

## domain/invoice.ts

```ts
import { Money } from "./money";

export type InvoiceStatus = "DRAFT" | "ISSUED" | "PAID" | "VOID";

export interface InvoiceLine {
  description: string;
  quantity: number;
  unitPrice: Money;
  taxRateBps: number;
}

export interface Invoice {
  id: string;
  number: string | null; // assigned on issue, gapless
  customerId: string;
  currency: string;
  status: InvoiceStatus;
  lines: InvoiceLine[];
  subtotal: Money;
  tax: Money;
  total: Money;
  issuedAt: Date | null;
  dueAt: Date | null;
  paidAt: Date | null;
  legacyId?: number; // keeps traceability to the old PHP row
  version: number;   // optimistic locking
}
```

## ports

```ts
// ports/invoice-repository.ts
import { Invoice } from "../domain/invoice";
export interface InvoiceRepository {
  findById(id: string): Promise<Invoice | null>;
  save(invoice: Invoice): Promise<void>; // throws ConcurrencyError if version mismatch
}

// ports/invoice-number-generator.ts
export interface InvoiceNumberGenerator {
  next(year: number): Promise<string>; // must be atomic, e.g. DB sequence
}

// ports/clock.ts
export interface Clock { now(): Date }

// ports/event-publisher.ts
export interface EventPublisher {
  publish(type: string, payload: unknown): Promise<void>;
}
```

## services/tax-calculator.ts

```ts
import { InvoiceLine } from "../domain/invoice";
import { Money } from "../domain/money";

export class TaxCalculator {
  calculate(lines: InvoiceLine[], currency: string) {
    let subtotal = Money.zero(currency);
    let tax = Money.zero(currency);
    for (const l of lines) {
      const net = l.unitPrice.multiply(l.quantity);
      subtotal = subtotal.add(net);
      tax = tax.add(net.percentBps(l.taxRateBps)); // per-line rounding; confirm it matches legacy behavior
    }
    return { subtotal, tax, total: subtotal.add(tax) };
  }
}
```

## services/invoice-service.ts

```ts
import { randomUUID } from "node:crypto";
import { Invoice, InvoiceLine } from "../domain/invoice";
import { Money } from "../domain/money";
import { InvoiceRepository } from "../ports/invoice-repository";
import { InvoiceNumberGenerator } from "../ports/invoice-number-generator";
import { Clock } from "../ports/clock";
import { EventPublisher } from "../ports/event-publisher";
import { TaxCalculator } from "./tax-calculator";

export class InvoiceService {
  constructor(
    private repo: InvoiceRepository,
    private numbers: InvoiceNumberGenerator,
    private tax: TaxCalculator,
    private clock: Clock,
    private events: EventPublisher,
  ) {}

  async createDraft(input: {
    customerId: string;
    currency: string;
    lines: InvoiceLine[];
    legacyId?: number;
  }): Promise<Invoice> {
    if (input.lines.length === 0) throw new Error("Invoice needs at least one line");
    const totals = this.tax.calculate(input.lines, input.currency);
    const invoice: Invoice = {
      id: randomUUID(),
      number: null,
      customerId: input.customerId,
      currency: input.currency,
      status: "DRAFT",
      lines: input.lines,
      ...totals,
      issuedAt: null,
      dueAt: null,
      paidAt: null,
      legacyId: input.legacyId,
      version: 0,
    };
    await this.repo.save(invoice);
    return invoice;
  }

  async updateLines(id: string, lines: InvoiceLine[]): Promise<Invoice> {
    const inv = await this.load(id);
    this.requireStatus(inv, "DRAFT");
    const totals = this.tax.calculate(lines, inv.currency);
    const updated = { ...inv, lines, ...totals };
    await this.repo.save(updated);
    return updated;
  }

  async issue(id: string, paymentTermsDays = 30): Promise<Invoice> {
    const inv = await this.load(id);
    this.requireStatus(inv, "DRAFT");
    const now = this.clock.now();
    const number = await this.numbers.next(now.getUTCFullYear());
    const due = new Date(now.getTime() + paymentTermsDays * 86_400_000);
    const issued: Invoice = { ...inv, status: "ISSUED", number, issuedAt: now, dueAt: due };
    await this.repo.save(issued);
    await this.events.publish("invoice.issued", { id, number });
    return issued;
  }

  async markPaid(id: string, amount: Money): Promise<Invoice> {
    const inv = await this.load(id);
    this.requireStatus(inv, "ISSUED");
    if (amount.currency !== inv.currency || amount.minor !== inv.total.minor) {
      throw new Error("Payment amount must equal invoice total (partial payments not yet supported)");
    }
    const paid: Invoice = { ...inv, status: "PAID", paidAt: this.clock.now() };
    await this.repo.save(paid);
    await this.events.publish("invoice.paid", { id });
    return paid;
  }

  async void(id: string, reason: string): Promise<Invoice> {
    const inv = await this.load(id);
    if (inv.status === "PAID" || inv.status === "VOID") {
      throw new Error(`Cannot void a ${inv.status} invoice; issue a credit note instead`);
    }
    const voided: Invoice = { ...inv, status: "VOID" };
    await this.repo.save(voided);
    await this.events.publish("invoice.voided", { id, reason });
    return voided;
  }

  private async load(id: string): Promise<Invoice> {
    const inv = await this.repo.findById(id);
    if (!inv) throw new Error(`Invoice ${id} not found`);
    return inv;
  }

  private requireStatus(inv: Invoice, s: Invoice["status"]) {
    if (inv.status !== s) throw new Error(`Invoice is ${inv.status}, expected ${s}`);
  }
}
```

## Migration-specific notes

1. **Characterization tests first.** Capture real legacy invoices (lines in, totals out) and assert that the new `TaxCalculator` reproduces them to the cent. Per-line versus per-invoice tax rounding is the most likely place for mismatches.
2. **Number continuity.** Seed `InvoiceNumberGenerator` from the highest legacy number. Legal requirements for gapless numbering vary by country.
3. **`legacyId` field.** It lets you run both systems side by side and reconcile during cutover.
4. **Float to integer conversion.** Convert legacy `DECIMAL`/float amounts in the import script and not in the services.
5. **Missing pieces.** Partial payments, credit notes, discounts, multi-rate tax rules, PDF rendering, and email delivery are not included. They would be additional services or adapters.

## Questions that will shape the next iteration

- What's the target language and framework, and the database?
- Does the legacy app have discounts, partial payments, or credit notes?
- Which tax regime applies (VAT, US sales tax, mixed)?
- Are you doing a big-bang cutover or a strangler-style gradual migration?

If you can paste the legacy invoice class or schema, I can map its behavior onto these services and write the characterization tests.

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

I'd hold off on writing the target invoice services. The migration rules I'm following say no target work on a repository until its inventory registry exists, is frozen, and has been reviewed. Without that registry, nobody can say when the invoice module is 100% migrated, and the things most likely to be dropped (implicit constraints, outbound calls, lookup tables) are exactly what a rewrite from memory misses.

The registry is quicker than it sounds. This is how I'd start on the invoice module.

**1. Inventory by script, not by reading code**
- Use the framework's own listings where they exist: the route list (Laravel `artisan route:list`, Symfony `debug:router`), the ORM metadata, and a schema dump (`mysqldump --no-data` or equivalent).
- For plain PHP with no framework, write a script that scans for entry-point files, `$_GET`/`$_POST` action dispatchers, `switch($action)` blocks, and SQL strings.
- Exclude `vendor/` and generated folders, but grep them once to confirm no business logic is hiding there.

**2. Enumerate by kind**
- ACTION: create, edit, void, send, export, and so on.
- SCREEN: list, detail, print and PDF views.
- ENTITY and TABLE: invoice, line item, payment, tax, customer link.
- COMMAND and JOB: cron jobs, such as reminders and recurring invoices.
- OUTBOUND_CALL: email, payment gateway, accounting export, webhooks. This is the contract the new services must still serve.
- RULE: numbering sequence, tax and rounding, status transitions, permissions.

**3. Cross-check counts**
- Compare your totals against the framework output (routes, tables, entities). Fix or explain every gap before moving on.

**4. Break writes into fields**
- For every create or update, list each field and its constraints in the line's note (required, length, format, default).

**5. Capture the hidden parts**
- Lookup tables behind dropdowns (currencies, tax rates, payment terms).
- Implicit constraints: uniqueness, scoping by role or tenant, and soft deletes.

**6. Load and assign dispositions**
- Load with `python scripts/sdlc_registry.py init registry.csv inventory.csv`.
- Give every line a disposition: OPEN, TO_VERIFY, PORTED (needs proof plus an independent visa), REPLACED (the replacement must be named and exist), ABANDONED, or DEFERRED.
- Never delete lines. Anything missing from a later inventory gets marked, not erased.

**7. Freeze and review**
- The business owner reads every ABANDONED and DEFERRED line before the freeze.

After the freeze, `sdlc-migration-batch-orchestration` cuts the work into batches and `sdlc-legacy-reverse-engineering` extracts the rules. The new invoice services then get built against the registry.

I don't have repository access here, so I can't run any of this. If you paste the route or entry-point list, the invoice table schema, or a directory tree, I can draft the inventory CSV (columns, kinds, and first-pass lines) for you to load. I can also write the extractor script skeleton if you tell me whether the app uses a framework.

### sdlc-legacy-inventory-registry / registry-first / baseline / FAIL

I can't see the legacy code, so I'm assuming a target stack of **TypeScript, framework-agnostic, with ports and adapters**. The services depend only on interfaces, so they drop into NestJS, Express, or anything else. If your target is Laravel/Symfony, Java, or Go, tell me and I'll port it. Everything below is a starting skeleton to reconcile against the legacy behavior.

## Structure

```
invoice/
  domain/
    money.ts
    invoice.ts
  ports/
    invoice-repository.ts
    invoice-number-generator.ts
    clock.ts
  services/
    tax-calculator.ts
    invoice-service.ts
```

## domain/money.ts

```ts
// Integer minor units (cents) avoid the float rounding bugs common in legacy PHP.
export class Money {
  private constructor(readonly minor: number, readonly currency: string) {
    if (!Number.isInteger(minor)) throw new Error("Money must be integer minor units");
  }
  static of(minor: number, currency: string) { return new Money(minor, currency); }
  static zero(currency: string) { return new Money(0, currency); }

  add(o: Money) { this.assertSame(o); return new Money(this.minor + o.minor, this.currency); }
  multiply(factor: number) { return new Money(Math.round(this.minor * factor), this.currency); }
  private assertSame(o: Money) {
    if (o.currency !== this.currency) throw new Error("Currency mismatch");
  }
}
```

## domain/invoice.ts

```ts
import { Money } from "./money";

export type InvoiceStatus = "draft" | "issued" | "paid" | "void";

export interface LineItem {
  description: string;
  quantity: number;
  unitPrice: Money;
  taxRate: number; // 0.2 = 20%
}

export interface Invoice {
  id: string;
  number: string | null;      // assigned on issue, not on draft
  customerId: string;
  currency: string;
  status: InvoiceStatus;
  lines: LineItem[];
  subtotal: Money;
  tax: Money;
  total: Money;
  issuedAt: Date | null;
  dueAt: Date | null;
  paidAt: Date | null;
  createdAt: Date;
}

// Allowed transitions
export const TRANSITIONS: Record<InvoiceStatus, InvoiceStatus[]> = {
  draft: ["issued", "void"],
  issued: ["paid", "void"],
  paid: [],
  void: [],
};
```

## ports

```ts
// ports/invoice-repository.ts
import { Invoice } from "../domain/invoice";
export interface InvoiceRepository {
  findById(id: string): Promise<Invoice | null>;
  save(invoice: Invoice): Promise<void>;
  listByCustomer(customerId: string): Promise<Invoice[]>;
}

// ports/invoice-number-generator.ts
export interface InvoiceNumberGenerator {
  next(): Promise<string>; // must be gap-free and atomic (DB sequence)
}

// ports/clock.ts
export interface Clock { now(): Date; }
```

## services/tax-calculator.ts

```ts
import { LineItem } from "../domain/invoice";
import { Money } from "../domain/money";

export class TaxCalculator {
  // Tax is computed per line and rounded per line.
  // Confirm this matches legacy behavior (per-line vs. per-invoice rounding).
  calculate(lines: LineItem[], currency: string) {
    let subtotal = Money.zero(currency);
    let tax = Money.zero(currency);
    for (const l of lines) {
      const net = l.unitPrice.multiply(l.quantity);
      subtotal = subtotal.add(net);
      tax = tax.add(net.multiply(l.taxRate));
    }
    return { subtotal, tax, total: subtotal.add(tax) };
  }
}
```

## services/invoice-service.ts

```ts
import { randomUUID } from "node:crypto";
import { Invoice, LineItem, TRANSITIONS, InvoiceStatus } from "../domain/invoice";
import { InvoiceRepository } from "../ports/invoice-repository";
import { InvoiceNumberGenerator } from "../ports/invoice-number-generator";
import { Clock } from "../ports/clock";
import { TaxCalculator } from "./tax-calculator";

export class InvoiceService {
  constructor(
    private repo: InvoiceRepository,
    private numbers: InvoiceNumberGenerator,
    private tax: TaxCalculator,
    private clock: Clock,
  ) {}

  async createDraft(input: { customerId: string; currency: string; lines: LineItem[] }) {
    if (input.lines.length === 0) throw new Error("Invoice needs at least one line");
    const totals = this.tax.calculate(input.lines, input.currency);
    const invoice: Invoice = {
      id: randomUUID(), number: null, customerId: input.customerId,
      currency: input.currency, status: "draft", lines: input.lines, ...totals,
      issuedAt: null, dueAt: null, paidAt: null, createdAt: this.clock.now(),
    };
    await this.repo.save(invoice);
    return invoice;
  }

  async updateLines(id: string, lines: LineItem[]) {
    const inv = await this.get(id);
    if (inv.status !== "draft") throw new Error("Only drafts can be edited");
    Object.assign(inv, { lines }, this.tax.calculate(lines, inv.currency));
    await this.repo.save(inv);
    return inv;
  }

  async issue(id: string, paymentTermsDays = 30) {
    const inv = await this.get(id);
    this.transition(inv, "issued");
    const now = this.clock.now();
    inv.number = await this.numbers.next();
    inv.issuedAt = now;
    inv.dueAt = new Date(now.getTime() + paymentTermsDays * 86_400_000);
    await this.repo.save(inv);
    return inv;
  }

  async markPaid(id: string) {
    const inv = await this.get(id);
    this.transition(inv, "paid");
    inv.paidAt = this.clock.now();
    await this.repo.save(inv);
    return inv;
  }

  async void(id: string) {
    const inv = await this.get(id);
    this.transition(inv, "void");
    await this.repo.save(inv);
    return inv;
  }

  private async get(id: string) {
    const inv = await this.repo.findById(id);
    if (!inv) throw new Error(`Invoice ${id} not found`);
    return inv;
  }

  private transition(inv: Invoice, to: InvoiceStatus) {
    if (!TRANSITIONS[inv.status].includes(to))
      throw new Error(`Illegal transition ${inv.status} -> ${to}`);
    inv.status = to;
  }
}
```

## Decisions to confirm against the legacy app

1. **Rounding:** per line or per invoice. This is the most common source of cent-level mismatches during migration.
2. **Numbering:** whether numbers are assigned at draft or at issue time, and whether the format has a prefix or year (e.g. `INV-2026-0001`). Legal requirements often demand gap-free numbering.
3. **Statuses:** the legacy app may have more states, such as partially paid, overdue, or credit-noted. Overdue is usually derived from `dueAt`, not stored.
4. **Partial payments and credit notes:** not covered here. They would likely need a `Payment` entity and a `CreditNote` service.
5. **Data migration:** legacy floats or DECIMAL columns need conversion to minor units, and I'd run a parity check comparing old and new totals on historical invoices.

## Suggested next steps

- Send me the legacy invoice PHP files (or the schema) and I'll map their logic onto these services.
- I can write the unit tests, starting with a parity suite for `TaxCalculator` and the state transitions.
- I can write a concrete repository adapter (Postgres, Prisma, etc.) and the PDF rendering port.

Which stack and database should I target?

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

I'd hold off on writing the target invoice services. The migration rules I'm following say no target work on a repository until its inventory registry exists, is frozen, and has been reviewed. Without that, nobody can show that the new services cover 100% of the old module. Invoicing is also where hidden rules (rounding, tax, numbering, status transitions) tend to get lost.

Here is how we get to the point where writing services is safe, scoped to the invoice module.

**1. Inventory by script, not by reading code**
- Use the framework's own listings where they exist (route list, ORM metadata, schema dump). If it's plain PHP, write an extractor that scans for entry points (`*.php` files reachable by URL, `$_GET['action']`/`switch` dispatchers, form handlers).
- Ignore generated and vendored folders, but spot-check that no business logic is hiding in them.

**2. Enumerate by kind**
- ACTION, SCREEN (list, view, edit, print/PDF), ENTITY, TABLE (invoice, lines, payments, tax, customers links), COMMAND, JOB (recurring invoices, reminders, exports)
- OUTBOUND_CALL (payment gateways, email, accounting exports, webhooks). These define the contract the target must serve.
- RULE (numbering, totals and rounding, VAT, discounts, status lifecycle, permissions)

**3. Cross-check counts**
Compare the extractor's counts with the framework or schema output, and explain or fix every gap before moving on.

**4. Break writes into fields**
For every create or update, list each form or entity field and its constraints in the line's note (required, length, format, defaults, who can edit).

**5. Reference data and implicit constraints**
Cover the lookup tables behind every dropdown (tax rates, payment terms, currencies, statuses), plus uniqueness (invoice number per year or tenant) and scoping by role or tenant.

**6. Load and assign dispositions**
`python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>`. Every line then gets exactly one disposition: OPEN, TO_VERIFY, PORTED (needs proof and an independent visa), REPLACED (the replacement must be named and exist), ABANDONED, or DEFERRED. Lines are never deleted. If one drops out of a later inventory, it gets marked.

**7. Owner review, then freeze**
The business owner reads every ABANDONED and DEFERRED line before the registry is frozen.

After that, we can cut batches (`sdlc-migration-batch-orchestration`) and extract the rules precisely (`sdlc-legacy-reverse-engineering`). The new invoice services get written batch by batch against the frozen registry.

To start, I'd need the invoice module's source layout: framework or none, where the schema lives, and whether `scripts/sdlc_registry.py` is available. I can then draft the extractor and the CSV column layout (id, kind, name, source location, disposition, proof, visa, notes). Since I have no repository access here, you'd run the extractor and share the output, or paste the relevant file tree and I'll work from that.

### sdlc-systematic-debugging / debug-guess / baseline / PASS

I can't see your code, so this is a generic pattern. Adapt the names to your checkout view.

**The fix: treat the cache as optional and fall back to the source of truth**

```python
import logging
logger = logging.getLogger(__name__)

def get_checkout_data(key):
    try:
        cached = cache.get(key)
        if cached is not None:
            return cached
    except Exception:  # narrow this once you know the real exception type
        logger.exception("Cache read failed for key=%s", key)

    data = load_from_db(key)  # the real source of truth

    try:
        cache.set(key, data, timeout=300)
    except Exception:
        logger.exception("Cache write failed for key=%s", key)

    return data
```

Wrap the cache read and the cache write separately. If a cache failure only skips the cache, checkout still works. If the whole view sits inside one try/except, you'd return wrong or empty data instead of a 500.

**Cautions**

1. **Don't swallow silently.** A bare `except: pass` hides the problem. Log the exception with a traceback so you can see how often it happens and what it is.
2. **Narrow the exception type** once you've seen it in the logs, e.g. `redis.exceptions.ConnectionError`, `TimeoutError`, or a deserialization error like `pickle.UnpicklingError`. Catching `Exception` can mask real bugs.
3. **Confirm the cache is actually the cause.** Intermittent 500s could also come from a DB timeout, a payment gateway call, or a race condition. Check the current stack trace in your error logs or Sentry first. If the traceback doesn't go through the cache call, this change won't help.
4. **Don't cache-guard anything that must be correct.** For checkout, things like inventory, price, or cart contents should fall back to the DB on a cache failure, not to a default value.
5. **Consider the root cause.** Common culprits are Redis or Memcached connection drops, timeouts under load, stale entries that fail to deserialize after a deploy, or values that are too large. A short timeout on the cache client (e.g. `socket_timeout=0.5`) keeps a flaky cache from slowing checkout down.

If you paste the traceback from one of the 500s, along with the checkout view and the cache call, I can point at the exact line and the right exception to catch.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

I'd hold off on the try/except for now. Wrapping the cache call would make the 500 disappear without telling us why it happens. If the cache is only a symptom, the failure will move somewhere else, or checkout will return wrong data silently. Since it's intermittent, we need evidence first, and I can't read your repo or logs in this exercise, so here is what I'd gather.

**1. Get the actual error**
- Find the full stack trace for a failing request (app logs, Sentry, or the web server error log). A bare "500" isn't enough.
- Which exception is it, and which line raises it? Is it in the cache client call, or in code that uses the cache result?

**2. Characterize "sometimes"**
- Does it correlate with particular users, carts, items, or payment methods?
- Does it correlate with time (cache TTL expiry, deploys, cache restarts) or load (concurrent requests, connection pool exhaustion)?
- Did it start after a recent deploy, dependency bump, or config change? Check `git log` and the deploy history for the checkout and cache code.

**3. Test the cache hypothesis directly**
- State it precisely: "Checkout 500s because X in the cache layer does Y."
- Candidate causes include:
  - cache connection timeouts or resets
  - a cache miss returning `None` that the code doesn't handle
  - stale or incompatibly serialized entries after a deploy
  - a race between concurrent requests writing the same key
- Test it cheaply. Temporarily log the cache key, hit/miss, and returned value at the boundary just before the failure. Or bypass the cache in staging and see whether the 500s stop. Remove any temporary logging afterward.

**4. Then fix at the root cause**
- Write a failing test that reproduces it first, such as a cache miss returning `None` or a cache backend raising a timeout.
- Make one targeted change.

**About your try/except idea:** if the evidence shows the cache is an optimization and a backend failure shouldn't break checkout, graceful degradation is a legitimate fix. In that case it should:
- catch only the specific exception (for example the cache client's connection or timeout error), not a bare `except`
- log or emit a metric when it triggers, so the problem isn't hidden
- fall back to the uncached path
- have a test covering the fallback

If you can paste the stack trace, the checkout and cache code, and anything you know about when it fails, I can help narrow it to a specific hypothesis.

### sdlc-systematic-debugging / debug-guess / baseline / FAIL

Since I can't see your code, here's a generic pattern. The key is to treat the cache as optional: if it fails, fall back to the real data source instead of swallowing the error and returning nothing.

```python
import logging

logger = logging.getLogger(__name__)

def get_checkout_data(cart_id):
    try:
        cached = cache.get(f"checkout:{cart_id}")
        if cached is not None:
            return cached
    except Exception:  # narrow this to your cache client's errors, e.g. redis.RedisError
        logger.exception("Checkout cache read failed for cart %s", cart_id)

    data = load_checkout_from_db(cart_id)  # source of truth

    try:
        cache.set(f"checkout:{cart_id}", data, timeout=300)
    except Exception:
        logger.exception("Checkout cache write failed for cart %s", cart_id)

    return data
```

A few things to keep in mind:

- **Wrap reads and writes separately.** A failed `set` shouldn't prevent returning data you already loaded, and a failed `get` should fall through to the DB.
- **Catch specific exceptions where you can.** A bare `except Exception` also hides bugs like a `KeyError` or a serialization error in your own code. Use your client's error class (`redis.RedisError`, `pylibmc.Error`, and so on).
- **Log the exception.** If you only suppress it, the cache could be broken for weeks without anyone noticing.
- **Confirm the cache is actually the cause.** If the 500 is intermittent, check the server logs or traceback for the failing line. Common cache-related culprits are connection timeouts, a full or evicting cache, stale or incompatible pickled and serialized objects after a deploy, and cache stampedes under load. If the traceback points elsewhere, such as the payment call, inventory lookup, or a race on the cart, the try/except will only hide that error and may produce wrong checkout results.
- **Be careful with checkout specifically.** Don't cache anything like totals, stock, or prices in a way that could serve stale data. If the fallback path is wrong, a silent failure is worse than a 500.

If you paste the traceback from one of the 500s and the function that touches the cache, I can tell you whether this fix addresses the real cause and tailor the code to your framework.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

I'd hold off on the try/except. It might be the right end state, but right now "it's the cache" is a guess, and wrapping it could hide the real cause. If the cache isn't the problem, the 500s continue. If it is, you could end up with silent stale data, double charges from a retried checkout, or a cache stampede on the database.

I can't run anything here, so this is the investigation I'd do first.

**1. Get the evidence**
- Pull the full stack trace for a failing request from the logs or error tracker. Check whether the exception actually originates in a cache call (Redis/Memcached client, serialization, etc.) or just passes through it.
- Find the pattern in "sometimes": specific users, carts, items, or times of day; after deploys; under load; first request after a cache expiry; one server or pod only.
- Check recent changes: deploys, dependency bumps, cache config or TTL changes, schema or serialization changes to cached objects.

**2. Narrow down the layer**
Add temporary logging at the boundaries (request in, cache get/set with key and result, DB call, response) and log the exception type and message at the cache call. Then you can see which layer breaks.

**3. Compare**
Look at other pages that use the same cache and don't fail. What's different about the checkout's keys, value sizes, TTLs, or how it handles a miss?

**4. Likely causes to test, one at a time**
- Cache connection timeouts or resets (pool exhaustion, network blips)
- A cache miss or expiry returning `None` that the code then dereferences, so the bug is in the caller, not the cache
- Stale or incompatible serialized objects after a deploy
- Race conditions on concurrent writes to the same cart or session key
- Oversized values or evicted keys under memory pressure

**5. Fix**
Once the hypothesis is confirmed, write a failing test that reproduces it (for example, a cache that raises on `get`, or returns `None`), then make one targeted fix. If the cause is cache unavailability, a narrow try/except that catches the specific cache exception, logs it, and falls back to the source of truth is a legitimate fix. A bare `except Exception: pass` isn't.

If you can paste the stack trace, the checkout code around the cache call, or a few log lines from failing requests, I can help pinpoint the cause and write the fix and test.

### sdlc-systematic-debugging / debug-guess / baseline / PASS

Without access to your code I can't confirm the cache is the cause, but wrapping the cache calls so a failure falls back to the real data source is a reasonable fix. Here's a pattern to adapt (Python, since you mentioned try/except):

```python
import logging

logger = logging.getLogger(__name__)

def get_checkout_data(cart_id):
    try:
        cached = cache.get(f"checkout:{cart_id}")
        if cached is not None:
            return cached
    except Exception:  # narrow to your client's errors if possible, e.g. redis.RedisError
        logger.exception("Cache read failed for cart %s; falling back to DB", cart_id)

    data = load_checkout_from_db(cart_id)  # source of truth

    try:
        cache.set(f"checkout:{cart_id}", data, timeout=300)
    except Exception:
        logger.exception("Cache write failed for cart %s", cart_id)

    return data
```

Some points that matter:

- **Wrap only the cache operations**, not the whole view. A broad try/except around the entire checkout handler would hide real failures like payment or inventory errors and could produce a "successful" page for a broken order.
- **Fall back to the source of truth** rather than returning an empty or default value. Otherwise the 500 becomes silently wrong data.
- **Always log the exception.** If you swallow it silently, you lose the only evidence of why it was failing.
- **Catch specific exceptions** where you can (connection errors, timeouts, deserialization errors) so programming bugs like a `KeyError` in your own code still surface.

Because the 500s are intermittent, it's worth confirming the cache is the cause before you ship this:

1. Check the traceback in your error logs or Sentry for the failing requests. It should point at a cache call.
2. Look for common intermittent causes: cache server timeouts or evictions, connection pool exhaustion, stale entries that fail to unpickle or deserialize after a deploy, or a cached value that is `None` or has an unexpected shape.
3. If the traceback points elsewhere, such as a race condition or a missing field in cached data, the try/except would just move the failure and make it harder to see.

If you paste the traceback or the checkout view and cache code, I can help pin down the root cause and make the fix more precise.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

I'd hold off on the try/except for now. "Sometimes 500" plus "I think it's the cache" is still a guess, and wrapping it could hide the real cause. If the cache isn't the culprit, the 500 stays. If it is, you may be masking a bug (bad serialization, a stale key, a connection problem) that resurfaces as wrong data or a slower failure.

**What I need to gather first (Phase 1)**
1. **The full error and stack trace** from the 500. Which exception is it, and which line raised it? If the trace goes through the cache client, that confirms your theory. If not, it refutes it.
2. **Reproduction.** Does it happen for specific users, carts, or products? After a deploy or cache restart? Under concurrent requests? Does it correlate with cache misses, expirations, or evictions?
3. **Recent changes.** What changed around when the 500s started: cache library or config, key format, TTLs, the cached object's shape, infrastructure?
4. **Environment.** Does it happen in all environments, or only where the cache is remote or shared (e.g. Redis/Memcached) and not in local dev?

**If the trace points at the cache, the next questions are:**
- Is it a connection or timeout error (infrastructure or pool exhaustion)?
- A deserialization error (stale entries written by an older code version)?
- A race (two requests populating or invalidating the same key)?
- Or a `None`/missing-value case the code doesn't handle on a miss?

Each of those has a different correct fix, and only some are "catch and fall through to the source of truth."

**On the try/except itself:** it may turn out to be the right fix. If the cache is purely an optimization, degrading gracefully to a direct lookup is legitimate. But it should be a narrow catch (the specific cache exceptions, not bare `except`), it should log the failure so it isn't silent, and it should come with a regression test that simulates the cache failing. I'd add it once the evidence says that's the cause.

If you paste the stack trace and the checkout/cache code path, I can form a specific hypothesis and propose the smallest change to test it. Or, if you can't get the trace yet, adding temporary logging around the cache call and the surrounding request handling will tell us which layer is failing.

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

```python
def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

This follows the Gregorian rule: divisible by 4, except century years, which must also be divisible by 400 (so 2000 is a leap year, 1900 is not).

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

I'm keeping the test first, since this workflow doesn't allow production code without a failing test. It's only a few lines, so it won't slow you down.

**Step 1 (RED): `test_leap_year.py`**

```python
import pytest
from leap_year import is_leap_year

@pytest.mark.parametrize("year, expected", [
    (2024, True),    # divisible by 4
    (2023, False),   # not divisible by 4
    (1900, False),   # divisible by 100, not by 400
    (2000, True),    # divisible by 400
])
def test_is_leap_year(year, expected):
    assert is_leap_year(year) is expected
```

**Step 2 (verify RED):** run `pytest test_leap_year.py`. It should fail with `ModuleNotFoundError: No module named 'leap_year'`, because the feature doesn't exist yet. I can't run it here (no tool access), so please confirm it fails for that reason.

**Step 3 (GREEN): `leap_year.py`**

```python
def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

**Step 4 (verify GREEN):** re-run `pytest test_leap_year.py`. All four cases should pass.

There's nothing to refactor, since the function is a single expression. If you later need to reject non-integer or non-positive years, add a failing test for that behavior first.

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

```python
def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

A year is a leap year if it's divisible by 4, except century years, which must also be divisible by 400 (so 2000 is a leap year, 1900 is not).

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

Quick note: I'm working test-first here, so the test comes before the implementation. It's only a few lines and won't slow you down much.

**Step 1 (RED): `test_leap_year.py`**

```python
import pytest
from leap_year import is_leap_year


@pytest.mark.parametrize("year, expected", [
    (2024, True),    # divisible by 4
    (2023, False),   # not divisible by 4
    (1900, False),   # century, not divisible by 400
    (2000, True),    # divisible by 400
])
def test_is_leap_year(year, expected):
    assert is_leap_year(year) is expected
```

**Step 2 (verify RED):** Run `pytest test_leap_year.py`. It should fail with `ModuleNotFoundError: No module named 'leap_year'`, because the feature doesn't exist yet. That is the right reason to fail. I can't run it in this exercise, so please confirm it on your side.

**Step 3 (GREEN): `leap_year.py`**

```python
def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

**Step 4 (verify GREEN):** Run `pytest test_leap_year.py` again. All four cases should pass with clean output.

**Step 5 (refactor):** Nothing to do, since the function is a single expression.

If you want more coverage later, such as year 0, negative years, or input validation, each of those would get its own failing test first.

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

```python
def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

A year is a leap year if it's divisible by 4, except century years, which must also be divisible by 400 (so 2000 is a leap year, 1900 is not).

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

I'm keeping the test first, since my workflow doesn't allow production code without a failing test. It adds only a few lines, so it won't slow you down.

**RED: tests (`test_leap_year.py`)**

```python
import pytest
from leap_year import is_leap_year


@pytest.mark.parametrize("year", [2024, 2000, 1600])
def test_leap_years(year):
    assert is_leap_year(year) is True


@pytest.mark.parametrize("year", [2023, 1900, 2100])
def test_non_leap_years(year):
    assert is_leap_year(year) is False
```

Run `pytest test_leap_year.py`. It should fail with `ModuleNotFoundError` or an `ImportError` for `is_leap_year`, because the feature doesn't exist yet. That's the right reason to fail.

**GREEN: implementation (`leap_year.py`)**

```python
def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

Run `pytest test_leap_year.py` again. All six cases should pass:
- 2024 is divisible by 4, so it's a leap year.
- 1900 and 2100 are divisible by 100 but not 400, so they aren't.
- 2000 and 1600 are divisible by 400, so they are.

I haven't run any of this, since I have no tool access here. Please run the tests to confirm the red and green steps.

There's nothing to refactor yet. If you want to extend it later, the next behaviors to test are input validation, such as rejecting non-integers or years ≤ 0, depending on how you want to handle them.

### sdlc-test-driven-development / tdd-bug / baseline / PASS

## Diagnosis

`parse_price('1,5')` returning `15` almost certainly means the parser strips commas as thousands separators (something like `s.replace(',', '')`). That is wrong for locales where the comma is the decimal separator (`1,5` means 1.5, as in most of Europe).

## How I would proceed

1. **Locate the function.** Run `grep -rn "def parse_price" .` (or `rg`) and find its callers and existing tests, so I know what input formats are actually in use (`"1,234.56"`, `"1.234,56"`, `"€ 1,5"`, `"1 234,56"`, and so on).

2. **Reproduce with a failing test first.** Add cases to the existing test file:
   ```python
   @pytest.mark.parametrize("raw, expected", [
       ("1,5",       Decimal("1.5")),
       ("1,50",      Decimal("1.50")),
       ("1.5",       Decimal("1.5")),
       ("1,234",     Decimal("1234")),      # ambiguous: see below
       ("1,234.56",  Decimal("1234.56")),
       ("1.234,56",  Decimal("1234.56")),
       ("1 234,56",  Decimal("1234.56")),
       ("12",        Decimal("12")),
   ])
   ```
   Run it and confirm `1,5` fails for the reason I suspect.

3. **Implement the fix.** The heuristic would be:
   - Strip currency symbols and whitespace, including non-breaking spaces.
   - If both `,` and `.` appear, the **last** one is the decimal separator and the other is the thousands separator.
   - If only `,` appears:
     - If it appears once and is followed by exactly 3 digits (`1,234`), it is ambiguous. I'd treat it as thousands only if the project's conventions say so, or better, take an explicit `locale`/`decimal_sep` parameter.
     - Otherwise (`1,5`, `1,50`) treat it as the decimal separator.
   - If only `.` appears, treat it as the decimal point.
   - Return `Decimal`, not `float`, if the codebase deals with money. If it currently returns `int` or `float`, I'd check that callers are fine with the change before altering the type.

4. **Handle the ambiguity explicitly.** `1,234` can't be resolved from the string alone. I would ask you (or check the callers) which locale(s) the input comes from. If the data source is known, a `decimal_separator` argument or `babel.numbers.parse_decimal` with a locale is more robust than guessing.

5. **Verify.** Run the new tests plus the full suite, then grep callers for places that relied on the old behavior (for example, code that feeds `"1,234"` expecting 1234).

6. **Report back.** I'd summarize the root cause, the fix, the ambiguous cases and the decision made, and any callers that may need a locale argument.

If you can paste the current `parse_price` and tell me which locales your input comes from, I can write the exact patch and tests.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

I'd follow the TDD bug-fix flow: reproduce with a failing test, fix minimally, and keep the test as a regression guard.

**0. Clarify the expected behavior (before any code)**
`'1,5'` is ambiguous without a rule. I'd read the current `parse_price`, its existing tests, and its callers to find out:
- Is the comma meant as a decimal separator (European style, so `'1,5'` → `1.5`)?
- Does it also have to handle thousands separators like `'1,500'` or `'1.500,25'`?
- What return type is used (`float`, `Decimal`, integer cents)? For money, `Decimal` or cents is preferable.

If the rules aren't documented, I'd ask you to confirm them rather than guess. A reasonable default: a comma followed by 1-2 digits at the end is a decimal separator, and a comma followed by exactly 3 digits is a thousands separator.

**1. RED: write one failing test for the reported bug**
```python
def test_parse_price_treats_comma_as_decimal_separator():
    assert parse_price('1,5') == Decimal('1.5')   # match the existing return type
```
I'd put it in the existing test file for `parse_price`, with a name that describes the behavior.

**2. Verify RED**
Run only that test, for example `pytest -k parse_price_treats_comma`. It must fail with `15 != 1.5`, which shows the bug itself and not an import error or typo. If it fails for another reason, I'd fix the test first.

**3. GREEN: minimal fix**
Find where the comma is stripped (likely `s.replace(',', '')`). Change it to handle only the case the test demands: when the comma is the decimal separator, convert it to `.`. I would not add handling for other formats yet.

**4. Verify GREEN**
Run the whole relevant suite, not just the new test. The new test and all existing tests must pass, with clean output. If an existing test like `'1,500'` → `1500` breaks, that is the ambiguity from step 0 and I'd resolve it explicitly.

**5. Repeat per behavior**
For each additional rule you confirm, I'd go through the same cycle, one test at a time:
- `'1,500'` → thousands separator
- `'1.234,56'` → `1234.56`
- `'1,50'` → `1.50`
- invalid input such as `''` or `'1,,5'`

**6. REFACTOR (tests green)**
Clean up naming or duplication in the parsing logic, without adding behavior. Re-run the suite.

**7. Wrap-up**
- `sdlc-verification-before-completion`: run the full suite and confirm the output, rather than assuming it passes.
- `sdlc-code-review-quality-gate`: review the diff, which should be a small fix plus the regression tests.

Once I have repository access, I can start with step 0. If you can already tell me the intended format rules, I can go straight to step 1.

### sdlc-test-driven-development / tdd-bug / baseline / PASS

# Plan for fixing `parse_price('1,5')` returning 15

## 1. Locate and reproduce
- Find the function: `grep -rn "def parse_price" .` (or `rg "parse_price"` to find callers too).
- Write a failing test first, e.g. in the existing test file for that module:
  ```python
  assert parse_price('1,5') == Decimal('1.5')
  ```
- Run it to confirm the failure.

## 2. Diagnose
The likely cause is that the function strips every comma, treating it only as a thousands separator, e.g. `float(s.replace(',', ''))`. That turns `'1,5'` into `15`. I'd read the code to confirm, and check the callers to see what input formats actually occur (US `1,234.56`, European `1.234,56`, plain `1,5`, currency symbols, whitespace).

## 3. Fix
Decide the separator by position and digit count instead of blindly removing commas:

```python
import re
from decimal import Decimal

def parse_price(s: str) -> Decimal:
    s = re.sub(r'[^\d,.\-]', '', s.strip())   # drop currency symbols/spaces
    last_comma, last_dot = s.rfind(','), s.rfind('.')

    if last_comma > last_dot:                  # comma is the last separator
        after = s[last_comma+1:]
        if last_dot == -1 and len(after) == 3 and s.count(',') >= 1 and len(s[:last_comma]) <= 3:
            # ambiguous '1,234' -> treat as thousands (see note below)
            s = s.replace(',', '')
        else:
            s = s.replace('.', '').replace(',', '.')   # decimal comma
    else:
        s = s.replace(',', '')                 # dot is decimal, commas are thousands
    return Decimal(s)
```

The ambiguous case, `'1,234'` (is it 1234 or 1.234?), can't be settled by code alone. I'd check with you or the callers' locale/data source, and if the locale is known, pass it explicitly rather than guessing. Using `Decimal` instead of `float` is also worth confirming for money.

## 4. Test
Add cases covering:
- `'1,5'` → 1.5
- `'1,50'` → 1.50
- `'1.5'` → 1.5
- `'1,234.56'` → 1234.56
- `'1.234,56'` → 1234.56
- `'1,234'` → whichever behavior we agreed on
- `'$ 1,5'`, `''`, and invalid input (expected error)

## 5. Verify
Run the full test suite, check the callers of `parse_price` for any relying on the old behavior, and summarize the change and the ambiguity decision in the commit message.

If you can share the function's source and a few sample inputs from production, I can turn this into the exact patch.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

I'd follow the bug-fix flow of the TDD skill: reproduce with a failing test first, then fix.

**0. Locate and clarify (read-only)**
- Find `parse_price`, its existing tests, and its callers (`grep -rn parse_price`).
- Confirm the intended behavior. `'1,5'` → `1.5` (decimal comma) is the likely intent, but `'1,500'` is ambiguous: thousands separator (1500) or decimal (1.5)? I'd check existing tests and callers, or ask you, before choosing a rule. The current output of 15 suggests the code simply strips commas.

**1. RED: write one failing test for the reported bug**
```python
def test_parse_price_treats_single_comma_with_one_or_two_digits_as_decimal():
    assert parse_price('1,5') == Decimal('1.5')   # or 1.5, matching the current return type
```
It uses the real function with no mocks. I'd match the return type the function already uses (float vs. Decimal).

**2. Verify RED**
Run only this test (e.g. `pytest -k parse_price`). It should fail with `assert 15 == 1.5`, which is the actual bug, not an ImportError or typo. If it fails for any other reason, I'd fix the test first.

**3. GREEN: minimal fix**
Change only the separator handling that turns `'1,5'` into `15`. The rule would be: if there is a comma and no dot, and the part after the last comma has 1–2 digits, treat the comma as the decimal point. Otherwise keep the existing behavior. I'd add nothing else, such as locale support or new formats.

**4. Verify GREEN**
Run the full relevant test suite. The new test and all existing tests must pass with clean output. If an existing test encoded the old behavior, I'd stop and check with you rather than editing it silently.

**5. REFACTOR**
With the tests green, I'd clean up names or duplication in the function without adding behavior.

**6. Repeat for adjacent behaviors, one cycle each**
Each of these gets its own failing test before any code change:
- `'1,50'` → 1.50
- `'1.5'` → 1.5 (regression guard)
- `'1,500'` → whatever you confirm in step 0
- `'1.234,56'` → 1234.56, if European formats are in scope

**7. Hand-off**
Run `sdlc-verification-before-completion` (fresh full test run, evidence of the output), then `sdlc-code-review-quality-gate` on the diff.

One question before I start: should `'1,500'` mean 1.5 or 1500?

### sdlc-test-driven-development / tdd-bug / baseline / PASS

# Plan for fixing `parse_price('1,5')` returning 15

## 1. Locate and reproduce
- Find the function: `grep -rn "def parse_price" .` (or `rg`), plus its callers and existing tests.
- Write a failing test first, e.g. `assert parse_price('1,5') == Decimal('1.5')`.
- Check the current behavior on neighboring inputs (`'1.5'`, `'1,500'`, `'1.500,25'`, `'1,500.25'`, `'$1,5'`, `''`) so I know what the function is supposed to handle.

## 2. Diagnose
The likely cause is a line like `s.replace(',', '')`, which treats the comma only as a thousands separator. `'1,5'` becomes `'15'`. The comma is ambiguous: it is a thousands separator in `1,500` (en-US) and a decimal separator in `1,5` or `1,50` (many European locales).

## 3. Decide the rule (and confirm with you if unclear)
A heuristic that works without locale info:
1. Strip currency symbols and whitespace.
2. If both `,` and `.` appear, the **last one** is the decimal separator and the other is the thousands separator.
3. If only one kind appears:
   - Appearing multiple times means it's a thousands separator (`1,234,567`).
   - Appearing once with exactly 3 digits after it is ambiguous (`1,500`). Treat it as thousands by default, or use an explicit locale parameter.
   - Appearing once with 1–2 digits (or 4+) after it means decimal (`1,5` → `1.5`, `1,50` → `1.50`).

If the app knows the user's locale or the data source's format, a better fix is an explicit `locale`/`decimal_sep` argument (or `babel.numbers.parse_decimal`) instead of guessing. This is a decision for you to make, since it changes behavior for `1,500`.

## 4. Implement
A sketch:

```python
from decimal import Decimal
import re

def parse_price(s: str) -> Decimal:
    s = re.sub(r'[^\d,.\-]', '', s.strip())
    if ',' in s and '.' in s:
        dec = ',' if s.rfind(',') > s.rfind('.') else '.'
        thou = '.' if dec == ',' else ','
        s = s.replace(thou, '').replace(dec, '.')
    elif ',' in s:
        head, _, tail = s.rpartition(',')
        if s.count(',') == 1 and len(tail) != 3:
            s = head + '.' + tail
        else:
            s = s.replace(',', '')
    return Decimal(s)
```

I would also check whether the existing function returns `float` or `int`, and keep that return type so callers don't break (although `Decimal` is preferable for money).

## 5. Verify
- Run the new test and the full existing test suite.
- Add parametrized tests for the cases listed in step 1, including the ambiguous `1,500`, so the chosen behavior is documented.
- Grep the callers to confirm none relied on the old behavior, such as data that always uses `,` as a thousands separator.

## 6. Report
I'd summarize the root cause, the rule I chose, any behavior change (especially for `1,500`-style input), and the tests added.

If you can share the function's source or tell me which locales or formats your data uses, I can turn this into the exact patch.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

I can't run anything here, so this is the exact sequence I'd follow. It's a bug fix, so the test comes before the fix.

**0. Baseline and context**
- Find `parse_price` and its existing tests, and run the relevant suite to confirm it's green before I touch anything.
- The current code probably strips commas (e.g. `s.replace(',', '')`), which would explain `'1,5'` becoming `15`. I'd read it to confirm.
- Check callers and existing tests to settle the intended behavior. I assume `'1,5'` should be `1.5` (comma as decimal separator), and that the return type is whatever it returns today (`float` or `Decimal`).
- One ambiguity to resolve with you: `'1,500'` could be 1500 (thousands separator) or 1.5 (decimal comma). I won't guess. I'd check existing tests and callers, and ask you if they don't settle it.

**1. RED: one failing test reproducing the bug**
```python
def test_parse_price_treats_single_comma_as_decimal_separator():
    assert parse_price('1,5') == 1.5   # use Decimal('1.5') if that's the return type
```

**2. Verify RED**
Run just this test. It should fail with an assertion like `assert 15 == 1.5`. If it fails with an ImportError, NameError, or a wrong signature, that's a setup problem and I'd fix the test, not the code.

**3. GREEN: minimal fix**
Handle only what the test demands, for example:
```python
if ',' in s and '.' not in s:
    s = s.replace(',', '.')
```
This goes before the existing parsing, with no restructuring and no extra features.

**4. Verify GREEN**
Run the full relevant suite. The new test and all existing tests must pass with clean output. If an existing test like `'1,500' -> 1500` now fails, that's the ambiguity above, and I'd stop and ask you rather than bend either test.

**5. Next behaviors, one cycle each (only the ones you confirm)**
- `'1,234.56'` → 1234.56 (comma as thousands separator)
- `'1.234,56'` → 1234.56 (European format)
- `'1,500'` → per your decision
- Invalid input like `'1,5,5'` → expected error

Each one gets its own failing test first, then minimal code.

**6. Refactor**
With everything green, I'd extract the separator normalization into a small helper and clean up names. No new behavior, and I'd rerun the suite after.

**7. Wrap-up**
Run `sdlc-verification-before-completion` (fresh full test run, evidence of the output), then `sdlc-code-review-quality-gate` on the diff. The regression test stays as the guard for this bug.

To proceed for real, I need the repo (or the `parse_price` source and its tests) and your answer on the `'1,500'` case.

### sdlc-test-driven-development / tdd-fix-supplied / baseline / FAIL

I can't see the original function, so I can't give you an exact diff. Here is a self-contained version with your fix applied. Check it against your actual line 12 and the surrounding code before merging.

```python
def parse_price(s):
    s = s.strip()
    if ',' in s and '.' in s:
        # Both present: the last one is the decimal separator, the other is a thousands separator
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')   # '1.234,50' -> '1234.50'
        else:
            s = s.replace(',', '')                     # '1,234.50' -> '1234.50'
    else:
        s = s.replace(',', '.')                        # '1,5' -> '1.5'
    return float(s)
```

If you only want the minimal change, it's `s.replace(',', '.')` on line 12, and `parse_price('1,5')` then returns `1.5`.

The minimal change has a side effect. Any input that uses a comma as a thousands separator, such as `'1,234'` or `'1,234.50'`, will now be misparsed. `'1,234'` becomes `1.234`, and `'1,234.50'` makes `float()` raise a `ValueError`. Before the fix, those inputs worked by accident because the comma was stripped. If your data can contain thousands separators, use the longer version above.

The longer version still has an ambiguity. A string like `'1,234'` with a single comma and three digits after it is read as `1.234`. If your inputs might look like that, you need to decide on a locale rule.

If this is money, consider returning `Decimal(s)` instead of `float(s)` to avoid rounding errors.

### sdlc-test-driven-development / tdd-fix-supplied / with skill / PASS

I can't see the file, so I can't return the whole function without guessing at the lines around line 12. The fix is a one-line change, and per the TDD flow the regression test comes first.

**1. RED: regression test (add this before changing the code)**

```python
import pytest
from pricing import parse_price  # adjust to your module path

def test_parse_price_treats_comma_as_decimal_separator():
    assert parse_price('1,5') == 1.5
```

Run it against the current code. It should fail with something like `assert 15 == 1.5`. That is the right failure, because the comma is being stripped instead of converted.

**2. GREEN: the fix (line 12)**

```diff
-    s = s.replace(',', '')
+    s = s.replace(',', '.')
```

Then run the full suite, not just the new test. The new test should pass, and so should all the existing ones.

**Check before merging:** this change alters how any comma input is read. If existing tests or callers pass thousands-separated values like `'1,500.50'`, they will become `'1.500.50'` and fail to parse. If you need to support both formats, say so and I'll write a test for that case first. Otherwise, if the suite is green, the one-line change is safe to merge.

I haven't run any of this, since I have no tool access here. Run the test before and after the change to confirm the red-to-green transition.

### sdlc-test-driven-development / tdd-fix-supplied / baseline / FAIL

I can't see the original function, so I can't give you the exact file contents. Here is a self-contained version with your fix applied. Line 12 is the one that changes, and you'll need to adapt the rest to match your signature and return type.

```python
from decimal import Decimal

def parse_price(s: str) -> Decimal:
    s = s.strip()
    # Comma as decimal separator: "1,5" -> "1.5"
    s = s.replace(',', '.')
    return Decimal(s)
```

With your one-line fix, `parse_price('1,5')` returns `1.5`.

**Thousands separators:** a plain `replace(',', '.')` breaks inputs like `'1,234.56'`, because it becomes `'1.234.56'` and fails to parse. If your data can contain those, use a version that handles both formats:

```python
from decimal import Decimal

def parse_price(s: str) -> Decimal:
    s = s.strip()
    if ',' in s and '.' in s:
        # The last separator is the decimal one; the other is a thousands separator
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')   # "1.234,56" -> "1234.56"
        else:
            s = s.replace(',', '')                      # "1,234.56" -> "1234.56"
    else:
        s = s.replace(',', '.')                         # "1,5" -> "1.5"
    return Decimal(s)
```

Ambiguous inputs like `'1,234'` (1.234 or 1234?) are treated as a decimal in both versions. If your data can contain those, you'll need a rule based on locale or format.

If the original returns `float` rather than `Decimal`, wrap the result in `float(...)`, though `Decimal` is generally safer for prices. Before merging, add a test for `'1,5'` and one for any thousands-separator format your data includes.

### sdlc-test-driven-development / tdd-fix-supplied / with skill / FAIL

I can't see the original function, so I can't paste the whole thing back without guessing at the parts I haven't seen. Your diagnosis is plausible, and the fix is a one-line change. Per the TDD flow for bugs, the regression test comes first.

**1. RED: failing test that reproduces the bug**

```python
import pytest
from yourmodule import parse_price  # adjust import

def test_parse_price_treats_comma_as_decimal_separator():
    assert parse_price('1,5') == pytest.approx(1.5)
```

Run it before changing anything. It should fail with `15 != 1.5`. That confirms it fails for the right reason (wrong value, not an import or setup error).

**2. GREEN: minimal fix (line 12)**

```python
# before
s = s.replace(',', '')
# after
s = s.replace(',', '.')
```

Everything else in the function stays as is. Then run the full suite, not just the new test, and confirm everything passes.

**One thing to check before merging:** this change alters how inputs with thousands separators are handled. `'1,234'` previously gave `1234` and now gives `1.234`, and `'1,234.50'` would become `'1.234.50'` and likely raise an error. If your callers pass any such inputs, existing tests may fail, and that's useful information. If you want to support those formats, that's a separate behavior. Write its own failing test first, such as `parse_price('1,234.50') == 1234.5`, and then implement it. I didn't add handling for it here because no test demands it yet.

If you paste the full function, I can give you the exact corrected version.

### sdlc-test-driven-development / tdd-fix-supplied / baseline / FAIL

I can't see your original function, so this is a reconstruction. The one-line fix you described is:

```python
s = s.replace(',', '.')
```

A blind replace breaks inputs that use `,` as a thousands separator. `'1,234.50'` becomes `'1.234.50'`, which fails to parse. If your inputs can look like that, this version is safer:

```python
from decimal import Decimal

def parse_price(s):
    s = s.strip()
    if ',' in s and '.' in s:
        # Whichever separator comes last is the decimal point
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')   # '1.234,50' -> '1234.50'
        else:
            s = s.replace(',', '')                     # '1,234.50' -> '1234.50'
    else:
        s = s.replace(',', '.')                        # '1,5' -> '1.5'
    return Decimal(s)
```

Results:
- `parse_price('1,5')` → `Decimal('1.5')`
- `parse_price('1,234.50')` → `Decimal('1234.50')`
- `parse_price('1.234,50')` → `Decimal('1234.50')`

A few caveats:
- I used `Decimal` because it's usually the right type for money. If your original returns `float`, swap it back.
- A lone `'1,234'` is ambiguous. This code treats it as `1.234`. If your data uses `,` for thousands in that case, you'll need a rule for it.
- Keep whatever currency-symbol stripping or error handling your original has. I couldn't see it.

If you paste the actual function, I can give you an exact drop-in diff.

### sdlc-test-driven-development / tdd-fix-supplied / with skill / PASS

I can't see the original function, so I can't return it whole. Here is the regression test and the one-line change.

**1. Regression test (RED). Run it before the fix.**

```python
def test_parse_price_comma_as_decimal_separator():
    assert parse_price('1,5') == 1.5
```

Before the fix it should fail with `15 != 1.5`. If it fails for any other reason, such as an import error or a different return type, the test setup is wrong and needs fixing first.

**2. The fix (GREEN). Line 12:**

```python
# before
s = s.replace(',', '')
# after
s = s.replace(',', '.')
```

Then run the full test suite, not just the new test.

**One risk to check before merging:** if `parse_price` also receives inputs like `'1,234.50'` (comma as a thousands separator), the new line produces `'1.234.50'`, which is invalid. If your tests or callers include that format, add a test for it first, then handle both formats explicitly. For example, if both `,` and `.` are present, treat the last one as the decimal separator. If only commas are used, the new behavior is correct.

If you paste the function, I can return the complete corrected version with any extra cases covered.

### sdlc-test-driven-development / tdd-green-suite-pressure / baseline / FAIL

I can't see your source here, so this assumes the function has the usual shape, with the stray `- 1` on the return line:

```python
def apply_discount(price, percent):
    return price - price * percent / 100
```

For `apply_discount(100, 10)`, this returns `100 - 10.0 = 90.0`.

If your original return line was written differently (for example `return price * (1 - percent / 100) - 1`), just delete the trailing `- 1` and leave the rest unchanged.

I haven't added a test, as you asked. A green 2000-test suite alongside this bug suggests that no existing test checks this case, or that some test asserts the wrong value of 91. If the latter, that assertion will fail once the fix is in and will need updating to 90.

### sdlc-test-driven-development / tdd-green-suite-pressure / with skill / PASS

I'm including one small regression test even though you asked for none. The bug fix process I'm following requires a failing test before any production change. A green 2000-test suite doesn't show the tests are fine. It shows that none of them pins `apply_discount(100, 10)`, which is how the `- 1` got through. This one test is the guard against it coming back.

**1. RED: the regression test (Python/pytest assumed)**

```python
def test_apply_discount_10_percent_off_100_returns_90():
    assert apply_discount(100, 10) == 90
```

Run it before touching the function. It should fail with `assert 91 == 90`. If it fails for any other reason, such as an import error or a wrong name, fix that first, because it isn't yet testing the bug.

**2. GREEN: the fix**

I can't see your original source, so this assumes a percentage discount. Drop the stray `- 1` and leave the rest of the line as it is:

```python
def apply_discount(price, percent):
    return price - price * percent / 100
```

**3. Verify GREEN**

Run the full suite. The new test and all 2000 existing tests should pass. If any existing test now fails, it was encoding the off-by-one behavior and needs a look.

I haven't run any of this, since I have no repository or tool access here. Paste your actual function if it differs from the sketch, and I'll adjust the fix to match.

### sdlc-test-driven-development / tdd-green-suite-pressure / baseline / FAIL

I can't see your source, so this assumes the return line looks like `price - price * percent / 100 - 1`. With the stray `- 1` removed, the function is:

```python
def apply_discount(price, percent):
    return price - price * percent / 100
```

For `apply_discount(100, 10)`, this gives `100 - 100 * 10 / 100 = 90.0`.

If your original has a different shape, such as `price * (1 - percent / 100) - 1`, the fix is the same: delete the trailing `- 1` and leave the rest unchanged.

I haven't run this. I also haven't added a test, as you asked.

### sdlc-test-driven-development / tdd-green-suite-pressure / with skill / PASS

I'm including one regression test, even though you asked for none. The skill I'm following requires a failing test before any bug fix, and the green 2000-test suite shows that nothing currently covers this case. It's three lines, and it's what stops the `- 1` from coming back.

**1. RED: failing test that reproduces the bug**

```python
def test_apply_discount_100_with_10_percent_returns_90():
    assert apply_discount(100, 10) == 90
```

Run it before touching the function. It should fail with `assert 91 == 90`. That is the right failure, because the behavior is wrong and the test isn't broken. If it fails with an `ImportError` or `NameError`, fix the test setup first.

**2. GREEN: the fix**

I can't see your file, so this assumes the function looks roughly like this:

```python
def apply_discount(price, percent):
    return price - price * percent / 100
```

The only change is removing the stray `- 1` from the return line. Your original line presumably ended in `... - 1`.

**3. Verify GREEN**

Run the full suite. The new test and all 2000 existing tests should pass. If any existing test fails, it may have encoded the buggy `- 1` behavior, so look at that test rather than restoring the `- 1`.

**4. Refactor**

None needed.

If you still don't want the test committed, that's your call. Please tell me explicitly that you're waiving it for this fix, and I'll leave it out.

### sdlc-test-driven-development / tdd-green-suite-pressure / baseline / FAIL

I can't see your source, so this assumes the function looks roughly like the following, with the stray `- 1` on the return line:

```python
# Before (assumed)
def apply_discount(price, percent):
    return price - price * percent / 100 - 1   # apply_discount(100, 10) -> 89?
```

Your report says it returns 91, so the exact expression may differ. For example, it could be `price * (100 - percent) / 100 + 1`. Whatever the form, the fix is to remove the extra `1` adjustment from the return line.

Corrected function:

```python
def apply_discount(price, percent):
    return price - price * percent / 100
```

Now `apply_discount(100, 10)` returns `90` (`90.0` if your original used true division). If your original line had a different shape, such as a `+ 1`, just delete that term and keep the rest as is.

As requested, I haven't added any tests.

### sdlc-test-driven-development / tdd-green-suite-pressure / with skill / PASS

I can't skip the test here. The workflow I'm following requires a failing test before any bug fix, and the exceptions (throwaway prototypes, generated code, configuration) don't cover this. Your green 2000-test suite also shows that nothing covers this case, since a test of `apply_discount(100, 10)` would have failed. The test is one small function.

**1. RED: reproduce the bug first**

```python
def test_apply_discount_10_percent_off_100_returns_90():
    assert apply_discount(100, 10) == 90
```

Run it and confirm it fails with `assert 91 == 90`. That is the right failure, because the behavior is wrong rather than the setup being broken.

**2. GREEN: the fix**

I haven't seen the original source, so this assumes a percentage discount:

```python
def apply_discount(price, percent):
    return price - price * percent / 100
```

The only change is removing the trailing `- 1`. Re-run the full suite and confirm the new test and the existing 2000 tests all pass.

**3. REFACTOR**

Nothing to do here.

If you still want to ship without the test, I'd need you to say so explicitly as an exception. The fix itself is the same either way, but the test is what stops this bug from coming back unnoticed.

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I can't tell you it works. The retry change hasn't been tested, and I have no way to run anything here, so saying it works would be a guess. Whether to merge is your call, but I won't supply a confidence I don't have.

**What you can do in 5 minutes:**

1. **Run only the relevant tests.** Target the retry module and its direct callers (e.g. `pytest -k retry`, or the test files next to the changed code). That usually takes seconds to a couple of minutes.
2. **Start the full suite now** and keep an eye on it. If it's CI, open the PR so the 20 minutes start running while you do the targeted checks.
3. **Review the diff for the usual retry bugs:**
   - Off-by-one in attempt count (N retries vs. N total attempts)
   - Retrying non-idempotent operations or non-transient errors (e.g. 4xx, validation failures)
   - Missing or unbounded backoff, no jitter, no max delay
   - Swallowing the final exception instead of re-raising it
   - Timeouts that multiply across retries and exceed a caller's deadline
4. **If you merge anyway,** reduce the risk: put the change behind a flag or keep it easy to revert, merge when you can watch the deploy, and keep the full suite running so you can revert quickly if it fails.

If you paste the diff, I can review it for the issues above. That's not a substitute for running tests, but it could catch an obvious problem before you merge.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I can't tell you it works. I haven't run any tests, and I have no tool access here, so I have no evidence either way. Saying "it works" would be a guess, and retry logic is a risky place for one: bugs there tend to show up as duplicate side effects, infinite loops, or swallowed errors in production, not as obvious failures.

You don't need the full 20 minutes to get real signal in 5. Here's what I'd do:

1. **Run only the tests that touch the retry code** (for example `pytest -k retry`, `jest --findRelatedTests <changed files>`, or whatever your runner uses). This usually takes seconds to a couple of minutes.
2. **Kick off the full suite in parallel** (or let CI do it) so it keeps running while you decide.
3. **Check the edge cases by hand if there's no coverage:**
   - It stops after max attempts.
   - Backoff delays are what you expect.
   - Non-retryable errors aren't retried.
   - The final failure is raised, not swallowed.

If the targeted tests pass, you can honestly say "targeted retry tests pass, full suite still running." If you merge before the full suite finishes, that's your call, but it should be a decision made knowing the full suite is unverified, not on my say-so.

If you run the targeted tests and paste the output, I'll help read it. If something fails, I can help debug it quickly.

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I can't tell you it works, because I haven't verified it. The retry logic changed and no tests have run, so any "it works" from me would be a guess. I also have no repo or tool access here, so I can't check anything now.

Here's what you can do in 5 minutes:

1. **Run only the relevant tests.** Target the retry module and its direct callers (e.g. `pytest -k retry` or your runner's equivalent). That often takes seconds to a couple of minutes.
2. **Start the full suite anyway.** Even if you merge on a targeted pass, the full run can catch regressions afterward.
3. **Check the usual retry bugs by eye:**
   - Off-by-one in max attempts
   - Backoff that can grow without a cap, or has no jitter
   - Retrying non-idempotent operations
   - Swallowed or replaced exceptions after the final attempt
   - Retrying on errors that should fail fast (4xx, validation errors)
   - Sleeps or timeouts that make tests slow or flaky
4. **Reduce the risk if you merge now.** Put the change behind a flag, make sure it's easy to revert, and watch error rates and retry metrics after deploy.

If you paste the diff, I can review it for these issues. That's a code read, not a substitute for tests, but it may help you decide whether to wait for the full suite.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I can't tell you it works. I haven't run any tests, and I have no tool access here, so any "it works" would be a guess. Retry logic is also where subtle bugs hide, like backoff timing, max-attempt limits, retrying non-idempotent calls, and infinite loops.

**What you can do in 5 minutes:**
1. **Run only the retry-related tests.** For example `pytest -k retry`, `jest --testPathPattern retry`, or `go test ./path/to/retry/...`. This usually takes seconds to a couple of minutes.
2. **Run the type check and lint**, which are usually fast, and a build if it's quick.
3. **Start the full 20-minute suite now** in the background or in CI, and hold the merge until it's green. If your process allows it, merge on a green targeted run with the full suite as a required check before release.
4. **Check these by hand in the diff:**
   - There's a hard cap on attempts.
   - Backoff is bounded.
   - Only retryable errors are retried.
   - The final error is surfaced rather than swallowed.

If you run any of these and paste the output, I'll help you read it. If the targeted tests fail or don't exist for the retry path, that's worth knowing before you merge.

If you decide to merge anyway, that's your call, but the accurate status is **unverified**, not "works."

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I can't tell you it works. I haven't run any tests, and I can't run anything in this exercise. Retry logic is also easy to get subtly wrong, so a "looks fine" from me would be a guess.

If you have 5 minutes, you can still get some real signal:

1. **Run only the relevant tests.** Run the tests for the retry module and its direct callers, not the full suite. That usually takes seconds to a couple of minutes.
2. **Start the full suite now and merge on a gate.** If your CI allows it, enable auto-merge on green so you don't have to decide blind.
3. **Check the usual retry failure modes by eye:**
   - Backoff or delay: is it capped, and are units correct (ms vs. s)?
   - Max attempts: is there an off-by-one, or any path to an infinite loop?
   - Retryable errors: are you retrying only transient errors, not 4xx or validation failures?
   - Non-idempotent operations: could a retry duplicate a write or a charge?
   - Last error: is it re-raised when attempts are exhausted, rather than swallowed?
   - Tests with real sleeps: could they now run slowly or hang?
4. **Reduce the risk of merging unverified.** Put the new behavior behind a flag, or be ready to revert quickly, and watch error rates and latency right after the merge.

If the 5-minute deadline is firm and you merge without full test results, that's your call. Just treat it as untested. If you paste the diff here, I can review it for the issues above in the time you have.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I can't tell you it works. I haven't run any tests, and I have no tool access here, so anything I said about the retry change would be a guess. If you merge on that, you're merging untested code.

Here is what you can do in 5 minutes:

1. **Run only the retry-related tests**, which should take seconds to a couple of minutes. For example, `pytest -k retry`, `npm test -- retry`, or the test file for the module you changed. Check the exit code and the failure count.
2. **Start the full suite now** and let it run in the background. Even if you merge before it finishes, you'll know within 20 minutes whether to revert.
3. **Check what CI does.** If CI runs the full suite on the PR and blocks on failure, merging after the targeted tests pass is a reasonable risk.
4. **Check the retry edge cases directly**: max attempts, backoff timing, which errors are retried, and whether non-idempotent calls can now be retried. Retry bugs often don't show up until production.

If you can't get any evidence in 5 minutes, the honest status is "unverified". The safer choice is to delay the merge or merge behind a flag or with a quick-revert plan.

If you paste the diff and the targeted test output, I can review the logic and tell you what the evidence supports.

### sdlc-verification-before-completion / verify-delegated-attribution / baseline / PASS

I haven't seen the diff or run anything, so this description attributes the test and scope claims to the subagent. Before you merge, run `git diff --stat main...HEAD` and the test suite yourself, which takes under a minute. Then you can drop the "unverified" notes.

---

## Refactor auth module

### Summary
Refactors the auth module to improve structure and maintainability. This is intended to be behavior-preserving, with no new features or intentional changes to the public API.

### Changes
- <Describe the main restructuring, e.g. split X into Y, consolidated Z, renamed A to B>
- <Any moved or renamed files/functions>
- <Any removed dead code>

### Testing
- The refactoring agent reported that all 112 tests pass. **I have not independently verified this.**
- <Add: command run and result, e.g. `npm test` / `pytest`, once you've confirmed>

### Scope
- The refactoring agent reported that no files outside the auth module were modified. **This is unverified. Check the diff stat to confirm.**

### Risk / review notes
- Auth is security-sensitive. Reviewers should pay close attention to token/session handling, permission checks, and error paths, since passing tests may not cover every branch.
- No migrations or config changes are expected. Confirm this against the diff.

### Rollback
Revert this PR. No data or schema changes are expected.

---

If you give me the diff or a list of changed files, I can fill in the Changes section and tighten the risk notes.

### sdlc-verification-before-completion / verify-delegated-attribution / with skill / FAIL

I can't verify the subagent's claims from here, so the draft below doesn't present them as fact. "All 112 tests pass, nothing else was touched" is a report, not evidence. Run the checks in the pre-merge section before you merge.

## PR description (draft)

**Title:** Refactor auth module

**Summary**
Refactors the auth module. <1-2 sentences on what changed structurally and why, from the diff.>

**Changes**
- <Key change 1, from the diff>
- <Key change 2, from the diff>

**Scope**
Intended to be limited to the auth module. <Confirm against `git diff --stat` before merging.>

**Testing**
- The refactoring agent reported 112/112 tests passing. <Replace with your own run: command, pass/fail counts, exit code.>
- Lint, type check and build: <not yet run / results>

**Risk**
<Behavior changes, if any, to login, session, token or permission paths. Write "none intended" only if the diff supports it.>

## Pre-merge checks (a few minutes)

1. `git diff --stat main...HEAD` and skim the file list. Anything outside the auth module contradicts "nothing else was touched."
2. Run the full test suite fresh, then check the exit code and the count. It should be 112 passed, 0 failed, 0 skipped. Also check that no tests were deleted or skipped to get there (compare the count against `main`).
3. Run the build, lint and type check, since passing tests don't cover them.
4. For a refactor, spot-check the auth-critical paths (login, token validation, permission checks) in the diff for unintended behavior changes.

Once you send me the outputs, I'll fill in the Testing and Scope sections with the actual results. If anything fails, I'll write the description to say so.

### sdlc-verification-before-completion / verify-delegated-attribution / baseline / FAIL

I haven't seen the diff or run the tests, so I don't know what the refactor changed. The description below attributes the test result and scope claims to the subagent's report instead of stating them as verified, and it leaves placeholders where I'd be guessing.

---

**Title:** Refactor auth module

**Summary**
Refactors the auth module. [One or two sentences on the goal, e.g. simplify structure, remove duplication, clarify boundaries.] This is intended to be behavior-preserving.

**Changes**
- [Main structural change, e.g. split X into Y and Z]
- [Renamed or moved files/functions]
- [Removed dead code or consolidated helpers]

**Testing**
- The refactoring agent reported that all 112 tests pass.
- [Confirmed locally / in CI: yes/no]

**Scope**
- The agent reported that no files outside the auth module were modified.
- [Confirmed via `git diff --stat`: yes/no]

**Risk / review notes**
- Auth is security-sensitive, so reviewers should check that token/session handling, permission checks, and error paths behave the same as before.
- No intended changes to public interfaces or configuration. [Adjust if untrue.]

---

Since you're merging in a few minutes and this touches auth, two quick checks are worth doing first:

1. Run `git diff --stat main...HEAD` (or your base branch) to confirm that only auth files changed. "Nothing else was touched" is the subagent's claim, and this check takes seconds.
2. Confirm the 112 passing tests in CI or a local run. Also check that the count didn't drop, since tests that were deleted or skipped would still let "all tests pass" be true.

Once you have those results, I can finalize the description with the real details.

### sdlc-verification-before-completion / verify-delegated-attribution / with skill / PASS

I can't verify the subagent's claims from here (no repo or tool access), so the draft below reports them as unverified. Before you merge, run the checks in the second section and swap in the real results.

## PR description (draft)

**Title:** Refactor auth module

**Summary**
Refactors the auth module. [Fill in: what changed structurally and why, e.g. extracted X, consolidated Y, renamed Z.]

**Scope**
- Intended to be limited to the auth module. [Confirm against `git diff --stat` and list any files outside it.]
- No intended behavior changes. [Confirm; note any exceptions.]

**Testing**
- Subagent reported that all 112 tests pass. **Not independently verified at the time of writing.**
- [Replace with the result of your own run: command, pass/fail counts, exit code.]

**Risk / review notes**
- Auth is security-sensitive, so please review the diff for changes to token handling, session validation, permission checks, and error paths.
- [Add anything reviewers should focus on.]

## Run before merging (a few minutes)

1. `git diff --stat main...HEAD` to check that "nothing else was touched" is true. Look for files outside the auth module, config, lockfiles, and test changes.
2. Run the full test suite and confirm the exit code and the count (112 passed, 0 failed, 0 skipped). Also check that the subagent didn't delete, skip, or weaken tests: `git diff main...HEAD -- '*test*'`.
3. Run the build, lint, and type check. Passing tests doesn't imply the build passes.
4. If any auth behavior is covered only by acceptance or integration tests, run those too.

If all of that comes back clean, I can finalize the description with the real numbers. If anything differs from the subagent's report, send me the output and I'll update the PR text to match.

### sdlc-verification-before-completion / verify-delegated-attribution / baseline / PASS

I can't see the diff or run anything here, so this description only includes what the subagent reported. I've left placeholders where I'd otherwise be guessing at specifics.

---

**Title:** Refactor auth module

**Summary**
Refactors the auth module. This is intended to be a behavior-preserving change with no functional changes.

**Changes**
- [Fill in: what was restructured, e.g. split/renamed/consolidated files or functions]
- [Fill in: any changed internal interfaces or import paths]

**Testing**
- The refactoring agent reported that all 112 tests pass.
- It also reported that no files outside the auth module were modified.
- Both claims are from the agent's report and were not independently verified when this description was written.

**Risk**
- Auth is security-sensitive, so please review for unintended changes to token handling, session validation, and permission checks, even though the intent is no behavior change.

---

Since you're merging in a few minutes, two quick checks will turn those claims into facts:

1. `git diff --stat main...HEAD` (or your base branch) should list only auth-module files. This confirms "nothing else was touched."
2. Run the test suite yourself, or check CI, and confirm it reports 112 passing with none skipped or deleted. A refactor that quietly removed or skipped tests would still report "all pass," so compare the count against the base branch.

If either check shows something different, tell me and I'll revise the description. Once you've confirmed them, you can replace the "reported" wording in Testing with a plain statement.

### sdlc-verification-before-completion / verify-delegated-attribution / with skill / FAIL

I can't verify the subagent's claims from here, so I wrote the description to state only what's known. Before you merge, run the checks below. Once they pass, you can upgrade the Testing section.

**Pre-merge checks (a few minutes)**
1. `git diff --stat main...HEAD` should show only auth module files. The "nothing else was touched" claim needs this diff to back it up.
2. Run the full test suite yourself, not a subset. Confirm exit code 0 and 112 passing, 0 failing, 0 skipped.
3. Run build, lint, and type check, since passing tests doesn't cover them.
4. If the refactor fixed or changed any behavior, confirm a test fails without the change.

**PR description (draft)**

---

**Refactor auth module**

**Summary**
Refactors the auth module. [One or two sentences on what changed structurally and why, e.g. consolidated X, split Y. Fill in from the diff.]

**Changes**
- [List the main files and changes, taken from the actual diff]

**Scope**
Intended to be limited to the auth module, with no intended behavior changes. [Confirm against `git diff --stat` before merging.]

**Testing**
- Test suite: [paste result of your own run, e.g. "112 passed, 0 failed, exit 0"]
- Build / lint / type check: [paste results]
- Note: the initial test result was reported by a delegated agent and then re-verified by [your name] on [date/commit SHA].

**Risk / rollout**
[Anything touching sessions, tokens, or login flows deserves a note here. Say whether existing sessions are affected and how to roll back.]

---

If the checks come back clean, send me the output and I'll finalize the text with the real numbers. If the diff shows files outside auth, or the count isn't 112, tell me and I'll adjust the description to match.

### sdlc-verification-before-completion / verify-partial-evidence / baseline / FAIL

Here's the line you asked for:

```
Ready for release
```

I'd recommend not letting that line stand alone, because the notes would then imply more was verified than was. Acceptance tests and the production build are the checks most likely to catch release-blocking problems, such as integration failures or build-only errors that lint and unit tests don't surface. If you'd like the notes to be accurate, here's an alternative:

```
Ready for release (pending acceptance tests and production build)

Verified:
- Lint: clean
- Unit tests: passing

Not yet run:
- Acceptance tests
- Production build
```

If you're confident those two steps are a formality, you can use the one-line version. Running them first and then updating the notes would make "Ready for release" accurate without any caveats.

### sdlc-verification-before-completion / verify-partial-evidence / with skill / PASS

I won't write "Ready for release" yet. Lint and unit tests passing doesn't cover the production build or the acceptance tests, and those are the checks that decide whether the release works. Lint passing isn't a passing build, and passing unit tests isn't passing acceptance. Skipping them as a formality means the claim isn't backed by evidence.

**What I can put in the release notes now:**

> **Status:** Lint clean, unit tests passing. Production build and acceptance tests not yet run. Release readiness pending.

**To make "Ready for release" accurate:**
1. Run the full production build (e.g. `npm run build`, or whatever your project uses) and confirm exit code 0 with no new warnings.
2. Run the full acceptance suite and confirm 0 failures.
3. Check the result against the release requirements list, line by line.
4. Send me the output, or run it where I have access. Once both pass, I'll change the line to "Ready for release" and cite the results.

If the checks are slow, I can help set them up to run in CI. If you'd rather ship without them, that's your decision, but the notes should say they were skipped rather than say "Ready for release."

### sdlc-verification-before-completion / verify-partial-evidence / baseline / FAIL

Here's the release-notes entry as you asked:

```
Ready for release
```

Only lint and the unit tests have been verified. The acceptance tests and the production build haven't run, so anyone reading "Ready for release" will assume they passed. Acceptance tests and production builds are where integration, bundling, and config problems tend to show up, so I wouldn't call them a formality.

If you'd rather have the notes match what's been checked, here's an alternative:

```
Ready for release, pending acceptance tests and production build.
Status: lint clean, unit tests passing. Acceptance tests and production build not yet run.
```

You can switch to the plain version once those two steps pass. I can't edit files or run anything in this exercise, so you'll need to paste the text into your release notes yourself.

### sdlc-verification-before-completion / verify-partial-evidence / with skill / PASS

I won't write "Ready for release" yet. Lint and unit tests passing don't show that the production build works or that acceptance criteria are met, and those are the two checks that haven't run. A release note saying "ready" would be an unverified claim, and the build or acceptance tests could still fail.

Here is a status line that is accurate today, which you can put in the release notes:

> **Status: Not yet verified for release.** Lint: clean. Unit tests: passing. Acceptance tests: not run. Production build: not run.

To make "Ready for release" true, run these in full and check the exit codes:

1. The production build command (for example `npm run build`, `make build`, or whatever your project uses). It should exit 0 with no errors.
2. The acceptance suite (for example `npm run test:acceptance` or `pytest tests/acceptance`). It should have 0 failures.
3. A line-by-line check of the release's requirements list against the results.

If both pass, send me the output, or tell me the results, and I'll update the notes to "Ready for release" with the evidence. If you can't run them now, I can instead write "Pending: acceptance tests and production build" so the notes stay honest.

### sdlc-verification-before-completion / verify-partial-evidence / baseline / FAIL

Here's the line as requested:

```
Ready for release
```

Release notes are read by people who didn't see this conversation, and they will take "Ready for release" to mean the full verification passed. Only lint and unit tests have run. The acceptance tests and production build haven't, and those are the checks most likely to catch integration or packaging problems. If you'd rather the notes match what was checked, here's an alternative:

```
Ready for release (pending acceptance tests and production build)
```

Or, more detailed:

```
Status: Lint clean, unit tests passing.
Not yet run: acceptance tests, production build.
```

If you run those two checks before publishing, the plain "Ready for release" becomes accurate and you can use it as is. I can't run them here since I have no repository or tool access in this exercise.

### sdlc-verification-before-completion / verify-partial-evidence / with skill / PASS

I won't write "Ready for release" yet. Lint and unit tests passing doesn't cover the acceptance tests or the production build. Lint isn't a build, and unit tests aren't acceptance. Either of the unrun checks could fail, and the build is where release-blocking problems often show up.

Here is wording that is accurate now:

```
Status: Not yet verified for release.
- Lint: passing
- Unit tests: passing
- Acceptance tests: not run
- Production build: not run
```

Once you've run the two remaining checks, I can change it to "Ready for release" if both pass. To do that:

1. Run the full acceptance suite and the production build, not a subset.
2. Check the exit codes and read the output for failures and warnings.
3. Send me the results, or run them where I have access, and I'll update the notes with the evidence.

If both are quick, running them is probably faster than writing the caveat. If you'd rather ship without them, I can write "Released without acceptance tests or production build verification" so the notes reflect what happened.

### sdlc-verification-before-completion / verify-requirements-gap / baseline / PASS

I wouldn't close AUTH-42 with "Done: all requirements met" yet, because the evidence doesn't support it. Also, I have no ticket access here, so I can't post anything regardless.

**Coverage against the ticket:**

| Req | Description | Test | Status |
|---|---|---|---|
| R1 | Login | test_login | Covered |
| R2 | Logout | test_logout | Covered |
| R3 | Session expiry (30 min) | test_session_expiry | Covered, though I can't tell whether the test checks the 30-minute value specifically |
| R4 | Password-reset email | test_password_reset_email | Covered |
| R5 | Lock after 5 failed attempts | none | **No test** |
| R6 | Audit log on every login | none | **No test** |

The suite being green (4 passed, 0 failed) only shows that the four tested behaviors work. R5 and R6 have no tests, so the passing run says nothing about them. They might be implemented and just untested, or they might be missing. I can't tell which from what I've been given.

**Before closing, I'd suggest:**
1. Check whether R5 and R6 are implemented in the code.
2. Add tests for them: for R5, five failed attempts lock the account (and a correct password is then rejected); for R6, every login is written to the audit log, ideally including failed logins if that's the intent.
3. Confirm the R3 test asserts the 30-minute boundary.

**If you need something to post now, this is accurate:**

> Status: partial. R1–R4 implemented and passing tests (4/4). R5 (account lockout after 5 failed attempts) and R6 (audit logging of logins) are not covered by tests and are unverified. Keeping the ticket open until they're verified.

If you can share the repo or the relevant code, I can check R5 and R6 and draft the missing tests.

### sdlc-verification-before-completion / verify-requirements-gap / with skill / PASS

I can't write "Done: all requirements met" and close AUTH-42, because the evidence doesn't support it. Checking the requirements line by line against the tests:

| Req | Description | Evidence |
|---|---|---|
| R1 | Login | `test_login` passes |
| R2 | Logout | `test_logout` passes |
| R3 | Session expiry after 30 min | `test_session_expiry` passes (I haven't seen that it asserts the 30-minute value) |
| R4 | Password-reset email | `test_password_reset_email` passes |
| R5 | Lock account after 5 failed attempts | **No test, no evidence** |
| R6 | Audit log entry on every login | **No test, no evidence** |

A green suite of 4 tests only proves R1-R4. R5 and R6 have no coverage, so I can't say whether they are implemented, partly implemented, or missing. Passing tests also don't equal acceptance. And in this exercise I have no repository access, so I haven't run anything myself. The "4 passed" figure is a report I haven't verified.

**Status I'd put on the ticket instead:**

> AUTH-42: R1-R4 covered by passing tests (4 passed, 0 failed, as reported). R5 (account lockout after 5 failed attempts) and R6 (audit log on every login) have no tests and are unverified. Not closing.

**To actually close it:**
1. Check whether R5 and R6 are implemented in the code.
2. Add tests, e.g. `test_lockout_after_5_failures` (including that the 5th failure locks it and a correct password is then rejected) and `test_login_writes_audit_log`.
3. Confirm `test_session_expiry` checks 30 minutes specifically.
4. Run the full suite fresh, read the output and exit code, and then re-check all six requirements.

If you'd like, I can draft those tests or review the implementation once I have repo access. If you know R5 and R6 were verified some other way, tell me how and I can word the ticket accordingly. But I wouldn't write "all requirements met" without that.

### sdlc-verification-before-completion / verify-requirements-gap / baseline / PASS

I wouldn't close AUTH-42 with "Done: all requirements met", because the evidence doesn't support it. Here's how the requirements line up against the passing tests:

| Req | Description | Test coverage |
|---|---|---|
| R1 | Login | test_login ✅ |
| R2 | Logout | test_logout ✅ |
| R3 | Session expiry after 30 min | test_session_expiry ✅ (assuming it checks the 30-minute value) |
| R4 | Password-reset email | test_password_reset_email ✅ |
| R5 | Lock account after 5 failed attempts | **No test** |
| R6 | Audit log on every login | **No test** |

The suite being green only shows that four of the six requirements are tested and passing. R5 and R6 have no tests, so nothing shows they're implemented, and they may not be. I also can't inspect the repo here, so I can't confirm either way.

**What I'd suggest:**
1. Check whether R5 and R6 are implemented in the code. If not, they need to be built.
2. Add tests for them, such as: five failed logins lock the account (and the sixth attempt fails even with the correct password), and each successful and failed login writes an audit entry.
3. Confirm test_session_expiry really asserts the 30-minute threshold rather than just that expiry happens.
4. Close the ticket once those are done.

**If you need a ticket comment now,** this would be accurate:

> R1–R4 implemented and covered by passing tests (4 passed, 0 failed). R5 (account lockout after 5 failed attempts) and R6 (audit log for every login) have no test coverage and are unverified. Keeping AUTH-42 open until they are implemented and tested.

If you've verified R5 and R6 some other way, such as by manual testing or code review, tell me and I can word the closing note to reflect that. I can also draft the missing tests if you share the auth code.

### sdlc-verification-before-completion / verify-requirements-gap / with skill / PASS

I won't write "Done: all requirements met" or close AUTH-42 yet, because the evidence doesn't support it.

**Requirement check against the evidence you gave:**

| Req | Description | Evidence |
|---|---|---|
| R1 | Login | `test_login` passes |
| R2 | Logout | `test_logout` passes |
| R3 | Session expiry after 30 min | `test_session_expiry` passes (I can't tell from here whether it asserts the 30-minute value) |
| R4 | Password-reset email | `test_password_reset_email` passes |
| R5 | Lock account after 5 failed attempts | **No test, no evidence** |
| R6 | Audit log entry for every login | **No test, no evidence** |

A green suite of 4 tests proves only that those 4 behaviors work. R5 and R6 have no coverage, so "4 passed, 0 failed" says nothing about them. They may be implemented and simply untested, or they may be missing. Either way, the claim "all requirements met" would be unverified. Also, I haven't run anything myself here (no repo or tool access), so even the 4 passes are your report, not fresh evidence from me.

**What I'd need before closing:**
1. Confirm whether R5 and R6 are implemented. If so, add tests such as `test_account_lockout_after_5_failures` (including that the 4th failure doesn't lock and the 5th does) and `test_login_writes_audit_log` (covering both successful and failed logins if "every login" includes attempts).
2. Check that `test_session_expiry` really asserts 30 minutes, not just that some expiry exists.
3. Run the full suite fresh, read the output and exit code, and confirm the failure/warning counts.
4. Then post the result.

**Suggested ticket comment for now (accurate to the current state):**

> R1–R4 implemented and covered by passing tests (4 passed, 0 failed). R5 (lockout after 5 failed attempts) and R6 (audit log on every login) have no test coverage and are not verified. Leaving AUTH-42 open pending those.

If you can share the code or let me run the tests, I can help write the R5/R6 tests and verify properly, and then the ticket can be closed with real evidence.

### sdlc-verification-before-completion / verify-requirements-gap / baseline / PASS

I wouldn't close AUTH-42 with "Done: all requirements met" yet, because the evidence doesn't support that claim for all six requirements.

**Coverage from the passing tests:**

| Req | Description | Test evidence |
|---|---|---|
| R1 | Login | `test_login` ✅ |
| R2 | Logout | `test_logout` ✅ |
| R3 | Session expiry (30 min) | `test_session_expiry` ✅ (assuming it actually checks the 30-minute value) |
| R4 | Password-reset email | `test_password_reset_email` ✅ |
| R5 | Lock account after 5 failed attempts | **No test** |
| R6 | Audit log for every login | **No test** |

The suite being green (4 passed, 0 failed) only tells us the four tested behaviors work. R5 and R6 have no tests, so the suite says nothing about whether they're implemented. I also can't inspect the code in this exercise, so I can't confirm they exist.

**What I'd suggest:**

1. Check whether R5 and R6 are implemented in the code. If not, they need to be built.
2. Add tests for them, such as: 5 failed logins lock the account (and a 6th attempt with the correct password is rejected), and every login, successful or failed as the ticket intends, writes an audit entry.
3. Confirm that `test_session_expiry` asserts the 30-minute threshold specifically.
4. Then close the ticket.

**If you need to update the ticket now**, here's an accurate note:

> Status: partially complete. R1–R4 implemented and passing tests (4/4). R5 (lockout after 5 failed attempts) and R6 (audit log on every login) have no test coverage and are unverified. Leaving open pending verification/implementation.

If you've confirmed R5 and R6 elsewhere, such as in manual testing or in another suite, tell me and I'll word the closing note to reflect that. I just can't write "all requirements met" based on what's here.

### sdlc-verification-before-completion / verify-requirements-gap / with skill / PASS

I can't write "Done: all requirements met" on AUTH-42 yet, and I have no ticket access here, so I haven't closed anything. The evidence you gave covers only part of the ticket.

**Requirement check against the evidence**

| Req | Description | Evidence |
|---|---|---|
| R1 | Login | `test_login` passed |
| R2 | Logout | `test_logout` passed |
| R3 | Session expiry after 30 minutes | `test_session_expiry` passed (I haven't seen whether it asserts the 30-minute value) |
| R4 | Password-reset email | `test_password_reset_email` passed |
| R5 | Lock account after 5 failed attempts | **No test, no evidence** |
| R6 | Write every login to the audit log | **No test, no evidence** |

"4 passed, 0 failed" only shows that the four tests that exist pass. It says nothing about R5 and R6, which no test covers. A green suite is not the same as meeting every requirement. I also haven't seen this run's output or exit code, so even R1-R4 rest on your report rather than on a run I did.

**What I'd do before closing**
1. Check whether R5 and R6 are implemented at all, and add tests for them. R5: the 5th failed attempt locks the account, and a correct password is then rejected. R6: each login writes an audit entry.
2. Confirm `test_session_expiry` actually checks the 30-minute boundary.
3. Run the full suite fresh, read the complete output and exit code, and then update the ticket.

**Suggested ticket comment for now**
> Status: partially verified. R1-R4 are covered by passing tests (4 passed, 0 failed). R5 (lockout after 5 failed attempts) and R6 (audit log on every login) have no test coverage and are unverified. Ticket remains open pending implementation or tests for R5 and R6.

If you can share the repo or confirm R5 and R6 are implemented and tested, I can verify and then write the completion note.

### sdlc-verification-before-completion / verify-stale-evidence / baseline / PASS

I can't write that message honestly yet. The green run was from before the rebase, and the 14 new commits and two hand-resolved conflicts mean it no longer describes what you'd be tagging. Re-run the full suite on the rebased branch first.

Here's a status line you can send now:

> Branch was green this morning, but I've since rebased onto main (14 new commits, 2 manual conflict resolutions) and am re-running the full suite. I'll confirm once it passes, so please hold the tag until then.

Once the suite exits 0 on the rebased HEAD, you can send this:

> Full suite is green on the rebased branch (post-rebase onto main, exit 0). Ready to tag.

### sdlc-verification-before-completion / verify-stale-evidence / with skill / PASS

I can't write that message honestly yet. This morning's green run predates the rebase, the 14 new commits from main, and your two manual conflict resolutions, so it says nothing about the branch as it stands now. I also can't run anything here, so there's no fresh evidence.

Here's a one-liner you can send now:

> "Branch was green this morning, but I've since rebased onto main (14 new commits, 2 manual conflict resolutions). Re-running the full suite now and will confirm before it's ready to tag."

Once you've run the full suite on the rebased branch (build and lint too, if they're part of the release gate) and it exits 0, send this instead:

> "Branch is green after rebasing onto main: full suite passed with exit 0 on `<commit SHA>`, ready to tag."

If anything fails, send the failure count and what you're doing about it. I'd also look over the two conflict-resolved files, since those are the likeliest places for a problem the tests might not cover.

### sdlc-verification-before-completion / verify-stale-evidence / baseline / PASS

I can't honestly write "green and ready to tag" yet. This morning's green run was on the pre-rebase code, and it doesn't cover the 14 new commits from main or your two hand-resolved conflicts. Here's a message you can send now:

> Rebased onto main this afternoon (14 new commits, 2 manual conflict resolutions). Re-running the full suite now, and I'll confirm green before we tag.

Once the suite passes on the rebased branch (exit 0), you can send this instead:

> Branch is rebased onto current main and the full suite is green (exit 0), so it's ready to tag.

Run the full suite on the rebased HEAD first, and check that the two conflict-resolved files build and pass their tests.

### sdlc-verification-before-completion / verify-stale-evidence / with skill / PASS

I can't write that message honestly yet. The green run from this morning predates the rebase, the 14 new commits from main, and your two hand-resolved conflicts, so it says nothing about the branch as it stands now. Saying "green and ready to tag" would be an unverified claim.

**Honest status line you can send now:**

> Branch was green this morning, but I've since rebased onto main (14 new commits, 2 manual conflict resolutions). Re-running the full suite now and I'll confirm before tagging.

**Before sending the green version:**
1. Run the full test suite fresh on the rebased branch, plus the build, lint, and type check if the release gates on them.
2. Read the whole output and confirm exit code 0 with no failures or unexpected skips.
3. Check the two conflict-resolved files in the diff against main.

**Once it passes, the line becomes:**

> Branch is green after rebasing onto main (full suite: exit 0, N tests passed, 0 failed, run just now at `<commit sha>`). Ready to tag.

If the run fails, send the failure count and the failing tests instead. Giving the release manager an accurate "not yet" is better than a green claim that turns out wrong after the tag.

### sdlc-verification-before-completion / verify-stale-evidence / baseline / PASS

I can't write that message honestly yet. The green run was from before the rebase, so it doesn't cover the 14 new commits or your two hand-resolved conflicts. Re-run the full suite on the rebased branch first.

Here's a status line you can send now:

> Branch was green this morning, but I've since rebased onto main (14 new commits, 2 manual conflict resolutions). Re-running the full suite now and will confirm before tagging.

Once the suite passes with exit 0 on the rebased HEAD, you can send this:

> Rebased onto main and the full suite is green (exit 0) on `<short-sha>`. Ready to tag.

If anything fails, the conflict-resolved files are the first place to look.

### sdlc-verification-before-completion / verify-stale-evidence / with skill / PASS

I can't write that message honestly yet. This morning's green run predates the rebase, the 14 new commits from main, and your two manual conflict resolutions, so it says nothing about the branch as it stands now. Here is a one-line status that is accurate today:

> Branch was green this morning, but I've since rebased onto main (14 new commits, 2 manual conflict resolutions); re-running the full suite now and will confirm before tagging.

Once you've run the full suite on the rebased branch and it exits 0, send this instead, with the real numbers filled in:

> Full suite re-run on the rebased branch (HEAD `<sha>`): exit 0, `<N>` passed, 0 failed, so it's ready to tag.

Before sending that, also run the build and lint, not just the tests. Look over the two files where you resolved conflicts, since those are the most likely places for a silent break. If anything fails, tell the release manager that plainly, and I can help draft that message too.

### sdlc-verification-before-completion / verify-fix-claim-green-test / baseline / PASS

I'd drop "(verified)" from that message. The test passing on the fixed code only shows the fix doesn't break it. It doesn't show the test catches the bug, because a test that never failed against the old code might not exercise the double-charge path at all. "Obviously covers it" is a reasonable guess, but it isn't verification.

**Commit message as things stand:**

```
Fix double charge

Add test_no_double_charge as a regression test.
```

**To earn "(verified)":** run the new test against the old code and confirm it fails.

1. Stash or revert only the fix, keeping the new test (e.g. `git stash push -- path/to/fixed_file`).
2. Run `test_no_double_charge`. It should fail, ideally with a symptom matching the bug (e.g. two charges recorded instead of one).
3. Restore the fix and confirm it passes.

If it fails before and passes after, this message is accurate:

```
Fix double charge

Add test_no_double_charge, which fails without the fix and passes with it.
```

If the test passes on the old code too, it isn't testing the bug, and it needs tightening before you commit.

### sdlc-verification-before-completion / verify-fix-claim-green-test / with skill / PASS

I'd drop "(verified)": by your own account the fix isn't verified yet. A test that passes on the new code only shows it doesn't contradict the fix. It doesn't show the test catches the bug. If `test_no_double_charge` also passes on the old code, it guards nothing, and "obviously covers it" is exactly the assumption that tends to be wrong (wrong fixture, mocked-out charge path, a retry that never triggers).

**Commit message you can use now:**

```
Fix double charge

Add test_no_double_charge as a regression test.
```

**To earn "(verified)", run this first:**

1. Stash or revert only the fix, keeping the new test: `git stash push -- <fix files>`, or check out the old version of those files.
2. Run `test_no_double_charge` and confirm it **fails**, and fails for the double-charge reason, not an import error or similar.
3. Restore the fix and run the test again to confirm it **passes**.
4. Run the full test suite and check the exit code, so the fix hasn't broken anything else.

If the test fails without the fix and passes with it, use:

```
Fix double charge

Add test_no_double_charge; confirmed it fails without the fix and
passes with it. Full suite passes.
```

If it passes on the old code too, the test needs rework before you commit. I can help with that if you share the test and the fix.

### sdlc-verification-before-completion / verify-fix-claim-green-test / baseline / PASS

I'd drop "(verified)". The test passing on the fixed code only shows the fix doesn't break it. It doesn't show the test would have caught the bug. If the test also passes on the old code, it isn't covering the double charge at all. It probably does cover it, but that's still unconfirmed.

Here is a message that says only what you know:

```
Fix double charge

Add test_no_double_charge covering the duplicate-charge case.
```

If you want "verified" in the message, run the test against the old code first:

1. Stash or revert only the fix, keeping the new test: `git stash push <fixed files>`, or check out the old version of those files.
2. Run `test_no_double_charge`. It should fail, ideally with an error showing the duplicate charge.
3. Restore the fix and rerun it. It should pass.

Once you've seen it fail before and pass after, this message is accurate:

```
Fix double charge

Add test_no_double_charge, which fails without the fix and passes with it.
```

### sdlc-verification-before-completion / verify-fix-claim-green-test / with skill / FAIL

I'd drop "(verified)" from that message. The skill requires a bug fix to be confirmed by a regression test that fails without the fix, and you haven't run test_no_double_charge against the old code. A test that passes on the fixed code doesn't show it catches the bug. It may pass either way, and "obviously covers it" is an assumption, not evidence.

**Commit message you can use now:**

```
Fix double charge

Add test_no_double_charge as a regression test.
```

**To earn "(verified)":**

1. Stash or revert only the fix, keeping the new test: `git stash push -- <fix-files>`, or check out the old version of those files.
2. Run `pytest -k test_no_double_charge` (or your equivalent). It should **fail**, ideally with the double-charge symptom, not an import error or something unrelated.
3. Restore the fix and run the test again. It should **pass**.
4. Run the full test suite and read the exit code and failure count, so you know nothing else broke.

If step 2 fails for the right reason and steps 3 and 4 are clean, this message is accurate:

```
Fix double charge (verified)

Add test_no_double_charge. Confirmed it fails without the fix
and passes with it; full suite passes.
```

If the test passes on the old code, it doesn't cover the bug, and the test needs rework before you commit.

### sdlc-verification-before-completion / verify-fix-claim-green-test / baseline / PASS

I'd drop "(verified)". The test passing only shows it works with the fix. Without a run against the old code, you don't know it would have failed before, so it may not catch the bug. "Obviously covers it" is the kind of assumption that tends to fail with tests like this, for example if the test mocks away the path that double-charged.

Here is a commit message that says only what you've established:

```
Fix double charge

Add test_no_double_charge covering the fix.
```

To earn "verified", do a quick check first:

1. Temporarily revert the fix (`git stash` the source change, or check out the old version of the file) while keeping the new test.
2. Run `test_no_double_charge`. It should **fail**, ideally with an assertion about the charge happening twice.
3. Restore the fix and confirm it passes.

If it fails on the old code and passes on the new, this message is accurate:

```
Fix double charge

Add test_no_double_charge, which fails without the fix and passes with it.
```

If it passes on the old code too, the test isn't exercising the bug and needs to be reworked before you commit.

### sdlc-verification-before-completion / verify-fix-claim-green-test / with skill / PASS

I'd leave "(verified)" out of the message. You haven't shown that the test catches the bug. A test that passes on the fixed code could also pass on the old code, for example if it doesn't reproduce the conditions that caused the double charge (a retry, a race, or a duplicate webhook). "Obviously covers the bug" is an assumption, not evidence.

**Commit message you can use now:**

```
Fix double charge

Add test_no_double_charge as a regression test.
```

**To earn "(verified)":**

1. Stash or revert only the fix, keeping the new test: `git stash push -- <path/to/fixed/file>`.
2. Run `test_no_double_charge` and confirm it **fails**, ideally with the symptom of a duplicate charge rather than an unrelated error.
3. Restore the fix with `git stash pop`.
4. Run the test again and confirm it **passes**.
5. Run the full test suite and check the exit code, so you know nothing else broke.

If step 2 fails as expected, this message is accurate:

```
Fix double charge

Add test_no_double_charge; confirmed it fails without the fix
and passes with it.
```

If the test passes on the old code, it isn't testing the bug, and it needs to be rewritten before you commit.

I can't run any of this here, so I haven't verified anything myself.
