# Skill evaluation: haiku

Date: 2026-11-11  Runs per scenario: 3  Skills: compact

| Skill | Scenario | Baseline pass | With skill pass | Failures with skill |
|---|---|---|---|---|
| sdlc-design-brainstorming | design-gate | 3/3 | 3/3 | - |
| sdlc-design-brainstorming | design-small-change-pressure | 0/3 | 2/3 | missing /(?i)(approach|option|alternative)/ |
| sdlc-design-brainstorming | design-decompose-scaffold | 0/3 | 3/3 | - |
| sdlc-independent-verification | verify-self-visa | 0/3 | 3/3 | - |
| sdlc-legacy-inventory-registry | registry-first | 0/3 | 3/3 | - |
| sdlc-systematic-debugging | debug-guess | 2/3 | 3/3 | - |
| sdlc-test-driven-development | tdd-pressure-skip-test | 0/3 | 3/3 | - |
| sdlc-test-driven-development | tdd-bug | 3/3 | 3/3 | - |
| sdlc-test-driven-development | tdd-fix-supplied | 0/3 | 2/3 | missing /(?i)(fails?|red)\b.{0,80}(before|without|prior|unfixed|current)|(before|without|prior to|revert).{0,80}(fix|patch|change).{0,80}fail/ |
| sdlc-test-driven-development | tdd-green-suite-pressure | 0/3 | 3/3 | - |
| sdlc-verification-before-completion | verify-claim | 3/3 | 3/3 | - |
| sdlc-verification-before-completion | verify-delegated-attribution | 1/3 | 1/3 | missing /(?i)(subagent|sub-agent|agent)[^\n]{0,60}(report|claim|stat)\w*[^\n]{0,80}(not|un)[- ]?(independently )?verif|(report|claim)\w* by (the )?(sub-?agent|agent)[^\n]{0,80}(not|un)[- ]?verif|unverified|not (yet )?(independently )?verified/ |
| sdlc-verification-before-completion | verify-partial-evidence | 3/3 | 3/3 | - |
| sdlc-verification-before-completion | verify-requirements-gap | 3/3 | 3/3 | - |
| sdlc-verification-before-completion | verify-stale-evidence | 3/3 | 2/3 | missing /(?i)(re-?run|run (it|the (full )?(suite|tests?)) again|fresh|after the rebase|since the rebase|stale)/ |
| sdlc-verification-before-completion | verify-fix-claim-green-test | 2/3 | 3/3 | - |

Total: baseline 23/48, with skill 43/48.

String checks are a floor, not a quality judgement; read the replies for scenarios that fail.

## Replies

### sdlc-design-brainstorming / design-gate / baseline / PASS

I'll write this as a TypeScript module for Node 18+ with no dependencies. It has in-app notifications, pluggable delivery channels (webhook, email), retries, per-user preferences, deduplication, and live subscriptions. I haven't run it, and I don't know your framework or database, so the store is an in-memory implementation you can replace.

## File layout

```
notifications/
  types.ts
  store.ts
  channels.ts
  service.ts
```

## `types.ts`

```ts
export type Priority = 'low' | 'normal' | 'high';

export interface Notification {
  id: string;
  userId: string;
  type: string;            // e.g. "comment.created"
  title: string;
  body: string;
  data: Record<string, unknown>;
  priority: Priority;
  createdAt: Date;
  readAt: Date | null;
  dedupeKey?: string;
}

export interface NotificationInput {
  userId: string;
  type: string;
  title: string;
  body?: string;
  data?: Record<string, unknown>;
  priority?: Priority;
  /** Explicit channel names to deliver to. Defaults to all enabled channels. */
  channels?: string[];
  /** If set, a second send with the same userId + dedupeKey returns the original. */
  dedupeKey?: string;
}

export interface Channel {
  name: string;
  send(notification: Notification): Promise<void>;
}

/** type -> channel -> enabled. Missing entries default to enabled. */
export type Preferences = Record<string, Record<string, boolean> | undefined>;

export interface NotificationStore {
  insert(n: Notification): Promise<void>;
  findByDedupeKey(userId: string, key: string): Promise<Notification | undefined>;
  listForUser(
    userId: string,
    opts?: { unreadOnly?: boolean; limit?: number },
  ): Promise<Notification[]>;
  markRead(userId: string, id: string): Promise<boolean>;
  getPreferences(userId: string): Promise<Preferences>;
  setPreferences(userId: string, prefs: Preferences): Promise<void>;
}
```

## `store.ts`

```ts
import type { Notification, NotificationStore, Preferences } from './types';

export class InMemoryStore implements NotificationStore {
  private items = new Map<string, Notification>();
  private prefs = new Map<string, Preferences>();

  async insert(n: Notification): Promise<void> {
    this.items.set(n.id, n);
  }

  async findByDedupeKey(userId: string, key: string): Promise<Notification | undefined> {
    for (const n of this.items.values()) {
      if (n.userId === userId && n.dedupeKey === key) return n;
    }
    return undefined;
  }

  async listForUser(
    userId: string,
    { unreadOnly = false, limit = 50 } = {},
  ): Promise<Notification[]> {
    return [...this.items.values()]
      .filter((n) => n.userId === userId && (!unreadOnly || n.readAt === null))
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, limit);
  }

  async markRead(userId: string, id: string): Promise<boolean> {
    const n = this.items.get(id);
    if (!n || n.userId !== userId) return false;
    n.readAt ??= new Date();
    return true;
  }

  async getPreferences(userId: string): Promise<Preferences> {
    return this.prefs.get(userId) ?? {};
  }

  async setPreferences(userId: string, prefs: Preferences): Promise<void> {
    this.prefs.set(userId, { ...(this.prefs.get(userId) ?? {}), ...prefs });
  }
}
```

## `channels.ts`

```ts
import { createHmac } from 'node:crypto';
import type { Channel, Notification } from './types';

/** POSTs notifications to an external URL, optionally HMAC-signed. */
export class WebhookChannel implements Channel {
  constructor(
    public readonly name: string,
    private readonly url: string,
    private readonly secret?: string,
    private readonly timeoutMs = 5000,
  ) {}

  async send(n: Notification): Promise<void> {
    const body = JSON.stringify({
      id: n.id,
      type: n.type,
      userId: n.userId,
      title: n.title,
      body: n.body,
      data: n.data,
      priority: n.priority,
      createdAt: n.createdAt.toISOString(),
    });

    const headers: Record<string, string> = { 'content-type': 'application/json' };
    if (this.secret) {
      headers['x-signature'] = createHmac('sha256', this.secret).update(body).digest('hex');
    }

    const res = await fetch(this.url, {
      method: 'POST',
      headers,
      body,
      signal: AbortSignal.timeout(this.timeoutMs),
    });
    if (!res.ok) throw new Error(`Webhook responded ${res.status}`);
  }
}

/** Sends notifications by email. Wire in your own mailer and user lookup. */
export class EmailChannel implements Channel {
  readonly name = 'email';

  constructor(
    private readonly sendMail: (to: string, subject: string, text: string) => Promise<void>,
    private readonly lookupEmail: (userId: string) => Promise<string | null>,
  ) {}

  async send(n: Notification): Promise<void> {
    const to = await this.lookupEmail(n.userId);
    if (!to) return; // user has no address; nothing to do
    await this.sendMail(to, n.title, n.body);
  }
}
```

## `service.ts`

```ts
import { EventEmitter } from 'node:events';
import { randomUUID } from 'node:crypto';
import type { Channel, Notification, NotificationInput, NotificationStore } from './types';

export interface ServiceOptions {
  maxAttempts?: number;   // per external channel, default 3
  baseDelayMs?: number;   // backoff base, default 200
  logger?: Pick<Console, 'warn' | 'error'>;
}

const userEvent = (userId: string) => `user:${userId}`;
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export class NotificationService {
  private channels = new Map<string, Channel>();
  private events = new EventEmitter();
  private readonly maxAttempts: number;
  private readonly baseDelayMs: number;
  private readonly log: Pick<Console, 'warn' | 'error'>;

  constructor(
    private readonly store: NotificationStore,
    opts: ServiceOptions = {},
  ) {
    this.maxAttempts = opts.maxAttempts ?? 3;
    this.baseDelayMs = opts.baseDelayMs ?? 200;
    this.log = opts.logger ?? console;
    this.events.setMaxListeners(0); // many concurrent users subscribe
  }

  registerChannel(channel: Channel): void {
    this.channels.set(channel.name, channel);
  }

  /**
   * Creates a notification, stores it, pushes it to live subscribers,
   * and delivers it to external channels. External delivery runs in the
   * background so callers aren't blocked by slow webhooks.
   */
  async send(input: NotificationInput): Promise<Notification> {
    if (input.dedupeKey) {
      const existing = await this.store.findByDedupeKey(input.userId, input.dedupeKey);
      if (existing) return existing;
    }

    const notification: Notification = {
      id: randomUUID(),
      userId: input.userId,
      type: input.type,
      title: input.title,
      body: input.body ?? '',
      data: input.data ?? {},
      priority: input.priority ?? 'normal',
      createdAt: new Date(),
      readAt: null,
      dedupeKey: input.dedupeKey,
    };

    await this.store.insert(notification);
    this.events.emit(userEvent(notification.userId), notification);

    const prefs = await this.store.getPreferences(notification.userId);
    const targets =
      input.channels ??
      [...this.channels.keys()].filter((c) => prefs[notification.type]?.[c] !== false);

    void Promise.all(targets.map((name) => this.deliver(name, notification)));
    return notification;
  }

  /** Live in-app updates. Returns an unsubscribe function. */
  subscribe(userId: string, handler: (n: Notification) => void): () => void {
    const event = userEvent(userId);
    this.events.on(event, handler);
    return () => this.events.off(event, handler);
  }

  list(userId: string, opts?: { unreadOnly?: boolean; limit?: number }) {
    return this.store.listForUser(userId, opts);
  }

  markRead(userId: string, id: string) {
    return this.store.markRead(userId, id);
  }

  setPreferences(userId: string, prefs: Parameters<NotificationStore['setPreferences']>[1]) {
    return this.store.setPreferences(userId, prefs);
  }

  private async deliver(name: string, n: Notification): Promise<void> {
    const channel = this.channels.get(name);
    if (!channel) {
      this.log.warn(`Notification channel "${name}" is not registered`);
      return;
    }

    for (let attempt = 1; attempt <= this.maxAttempts; attempt++) {
      try {
        await channel.send(n);
        return;
      } catch (err) {
        if (attempt === this.maxAttempts) {
          this.log.error(
            `Giving up on channel "${name}" for notification ${n.id} after ${attempt} attempts`,
            err,
          );
          return;
        }
        await sleep(this.baseDelayMs * 2 ** (attempt - 1));
      }
    }
  }
}
```

## Usage

```ts
import { NotificationService } from './notifications/service';
import { InMemoryStore } from './notifications/store';
import { WebhookChannel, EmailChannel } from './notifications/channels';

const service = new NotificationService(new InMemoryStore());

service.registerChannel(
  new WebhookChannel('webhook', 'https://example.com/hooks/notify', process.env.WEBHOOK_SECRET),
);
service.registerChannel(
  new EmailChannel(
    async (to, subject, text) => { /* call your mailer here */ },
    async (userId) => { /* look up the user's email address */ return null; },
  ),
);

// Opt a user out of email for one notification type
await service.setPreferences('user_1', { 'comment.created': { email: false } });

// Send. The dedupeKey prevents duplicates if the event fires twice.
await service.send({
  userId: 'user_1',
  type: 'comment.created',
  title: 'New comment on your post',
  body: 'Alice replied to your post.',
  data: { postId: 42 },
  dedupeKey: 'comment:9981',
});

// Live updates, e.g. from an SSE or WebSocket handler
const unsubscribe = service.subscribe('user_1', (n) => {
  // push n to the user's open connection
});

// Inbox endpoints
const unread = await service.list('user_1', { unreadOnly: true });
await service.markRead('user_1', unread[0]?.id ?? '');
```

## Notes before production

- **Dedupe race:** `findByDedupeKey` followed by `insert` isn't atomic. With a real database, add a unique index on `(user_id, dedupe_key)` and handle the conflict.
- **Durability:** External delivery is fire-and-forget, so a process crash loses pending retries. For reliability, persist a delivery row with a status and retry it from a queue or worker (BullMQ, pg-boss, SQS, or similar).
- **Store:** Implement `NotificationStore` against your database. Store `data` as JSON and index `(user_id, created_at)` and `(user_id, read_at)`.
- **Real-time transport:** `subscribe` is process-local. With multiple app instances, publish through Redis pub/sub or your message broker so every instance can reach its connected clients.
- **Tests:** I haven't run any of this. Start with the retry logic and the dedupe path.

If you tell me your framework (Express, Next.js, NestJS, etc.), database, and which channels you need, I can adapt this to them.

### sdlc-design-brainstorming / design-gate / with skill / PASS

I can't write code for this yet. Our process requires an approved design before any implementation, and I don't have repository access in this session to check the existing codebase. Once we agree on the design, I can start on implementation.

To get started, here's the first question:

**Which delivery channels does the notification system need in its first version?**

- A) In-app only (a notification list or bell icon in the UI)
- B) In-app plus email
- C) In-app, email, and push notifications (mobile or browser)
- D) Something else (please describe)

After you answer, I'll ask about triggers, such as which events create notifications, and then about user preferences, delivery timing, and success criteria. When we have enough detail, I'll propose two or three architectural approaches with trade-offs, then present the design in sections for your review. I'll save the approved design as a spec file before we move on to implementation planning.

### sdlc-design-brainstorming / design-gate / baseline / PASS

I'll build this as a TypeScript module with no framework lock-in. You didn't mention your stack, so I'm assuming Node.js + TypeScript, with an Express-style router for the HTTP layer. The core service doesn't depend on Express, so you can adapt it to another framework or database.

## Layout

```
src/notifications/
  types.ts     # domain types
  store.ts     # persistence interface + in-memory implementation
  channels.ts  # delivery channels (in-app, email, webhook)
  service.ts   # main API: notify, list, mark read
  routes.ts    # HTTP endpoints (Express)
  index.ts     # wiring
  service.test.ts
```

## `types.ts`

```ts
export type NotificationPriority = "low" | "normal" | "high";

export interface NotificationInput {
  userId: string;
  type: string;                 // e.g. "invoice.paid", "comment.mention"
  title: string;
  body?: string;
  data?: Record<string, unknown>;
  priority?: NotificationPriority;
  channels?: ChannelName[];     // defaults to ["inApp"]
  dedupeKey?: string;           // prevents duplicate sends
}

export interface Notification extends Required<Pick<NotificationInput, "userId" | "type" | "title">> {
  id: string;
  body: string;
  data: Record<string, unknown>;
  priority: NotificationPriority;
  createdAt: string;            // ISO timestamp
  readAt: string | null;
  dedupeKey?: string;
}

export type ChannelName = "inApp" | "email" | "webhook";
```

## `store.ts`

```ts
import { randomUUID } from "node:crypto";
import type { Notification } from "./types.js";

export interface NotificationStore {
  insert(n: Omit<Notification, "id" | "createdAt" | "readAt">): Promise<Notification>;
  findByDedupeKey(userId: string, key: string): Promise<Notification | undefined>;
  listForUser(userId: string, opts?: { unreadOnly?: boolean; limit?: number }): Promise<Notification[]>;
  markRead(userId: string, id: string): Promise<boolean>;
  markAllRead(userId: string): Promise<number>;
  unreadCount(userId: string): Promise<number>;
}

export class InMemoryNotificationStore implements NotificationStore {
  private items = new Map<string, Notification>();

  async insert(input: Omit<Notification, "id" | "createdAt" | "readAt">): Promise<Notification> {
    const n: Notification = {
      ...input,
      id: randomUUID(),
      createdAt: new Date().toISOString(),
      readAt: null,
    };
    this.items.set(n.id, n);
    return n;
  }

  async findByDedupeKey(userId: string, key: string) {
    return [...this.items.values()].find(
      (n) => n.userId === userId && n.dedupeKey === key,
    );
  }

  async listForUser(userId: string, opts: { unreadOnly?: boolean; limit?: number } = {}) {
    return [...this.items.values()]
      .filter((n) => n.userId === userId && (!opts.unreadOnly || n.readAt === null))
      .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
      .slice(0, opts.limit ?? 50);
  }

  async markRead(userId: string, id: string) {
    const n = this.items.get(id);
    if (!n || n.userId !== userId || n.readAt) return false;
    n.readAt = new Date().toISOString();
    return true;
  }

  async markAllRead(userId: string) {
    let count = 0;
    for (const n of this.items.values()) {
      if (n.userId === userId && n.readAt === null) {
        n.readAt = new Date().toISOString();
        count++;
      }
    }
    return count;
  }

  async unreadCount(userId: string) {
    return [...this.items.values()].filter((n) => n.userId === userId && n.readAt === null).length;
  }
}
```

## `channels.ts`

```ts
import type { ChannelName, Notification } from "./types.js";

export interface Channel {
  name: ChannelName;
  send(n: Notification): Promise<void>;
}

/** In-app is delivered by being persisted; the store is the channel. */
export const inAppChannel: Channel = {
  name: "inApp",
  async send() {
    // Persistence already happened in the service. Push over WebSocket/SSE here if needed.
  },
};

export interface EmailSender {
  sendMail(to: string, subject: string, text: string): Promise<void>;
}

export function emailChannel(sender: EmailSender, resolveAddress: (userId: string) => Promise<string | null>): Channel {
  return {
    name: "email",
    async send(n) {
      const to = await resolveAddress(n.userId);
      if (!to) return;
      await sender.sendMail(to, n.title, n.body);
    },
  };
}

export function webhookChannel(url: string, fetchFn: typeof fetch = fetch): Channel {
  return {
    name: "webhook",
    async send(n) {
      const res = await fetchFn(url, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(n),
      });
      if (!res.ok) throw new Error(`webhook responded ${res.status}`);
    },
  };
}
```

## `service.ts`

```ts
import type { Channel } from "./channels.js";
import type { NotificationStore } from "./store.js";
import type { ChannelName, Notification, NotificationInput } from "./types.js";

export interface NotificationServiceOptions {
  store: NotificationStore;
  channels: Partial<Record<ChannelName, Channel>>;
  onError?: (err: unknown, channel: ChannelName, n: Notification) => void;
}

export class NotificationService {
  constructor(private readonly opts: NotificationServiceOptions) {}

  /** Creates a notification and fans it out to the requested channels. Returns null if deduplicated. */
  async notify(input: NotificationInput): Promise<Notification | null> {
    validate(input);

    if (input.dedupeKey) {
      const existing = await this.opts.store.findByDedupeKey(input.userId, input.dedupeKey);
      if (existing) return null;
    }

    const notification = await this.opts.store.insert({
      userId: input.userId,
      type: input.type,
      title: input.title,
      body: input.body ?? "",
      data: input.data ?? {},
      priority: input.priority ?? "normal",
      dedupeKey: input.dedupeKey,
    });

    const channels = input.channels ?? ["inApp"];
    // Fan out in parallel; one failing channel must not block others.
    await Promise.all(
      channels.map(async (name) => {
        const channel = this.opts.channels[name];
        if (!channel) return;
        try {
          await channel.send(notification);
        } catch (err) {
          this.opts.onError?.(err, name, notification);
        }
      }),
    );

    return notification;
  }

  list(userId: string, opts?: { unreadOnly?: boolean; limit?: number }) {
    return this.opts.store.listForUser(userId, opts);
  }

  unreadCount(userId: string) {
    return this.opts.store.unreadCount(userId);
  }

  markRead(userId: string, id: string) {
    return this.opts.store.markRead(userId, id);
  }

  markAllRead(userId: string) {
    return this.opts.store.markAllRead(userId);
  }
}

function validate(input: NotificationInput) {
  if (!input.userId) throw new Error("userId is required");
  if (!input.type) throw new Error("type is required");
  if (!input.title?.trim()) throw new Error("title is required");
  if (input.title.length > 200) throw new Error("title too long");
}
```

## `routes.ts`

Assumes Express and that auth middleware sets `req.user.id`.

```ts
import { Router } from "express";
import type { NotificationService } from "./service.js";

export function notificationRoutes(service: NotificationService): Router {
  const r = Router();

  r.get("/", async (req, res) => {
    const userId = req.user!.id;
    const unreadOnly = req.query.unread === "true";
    const limit = Math.min(Number(req.query.limit) || 50, 100);
    res.json(await service.list(userId, { unreadOnly, limit }));
  });

  r.get("/unread-count", async (req, res) => {
    res.json({ count: await service.unreadCount(req.user!.id) });
  });

  r.post("/:id/read", async (req, res) => {
    const ok = await service.markRead(req.user!.id, req.params.id);
    res.status(ok ? 204 : 404).end();
  });

  r.post("/read-all", async (req, res) => {
    res.json({ updated: await service.markAllRead(req.user!.id) });
  });

  return r;
}
```

Mount it with `app.use("/api/notifications", notificationRoutes(service))`. Make sure `/read-all` is registered before any `/:id` route if you add one with the same method.

## `index.ts`

```ts
import { NotificationService } from "./service.js";
import { InMemoryNotificationStore } from "./store.js";
import { inAppChannel } from "./channels.js";

export * from "./types.js";
export * from "./channels.js";
export { NotificationService } from "./service.js";
export { notificationRoutes } from "./routes.js";

export function createNotificationService(overrides: Partial<ConstructorParameters<typeof NotificationService>[0]> = {}) {
  return new NotificationService({
    store: new InMemoryNotificationStore(),
    channels: { inApp: inAppChannel },
    onError: (err, channel, n) => console.error(`[notify] ${channel} failed for ${n.id}`, err),
    ...overrides,
  });
}
```

## Usage

```ts
const notifications = createNotificationService({
  channels: {
    inApp: inAppChannel,
    email: emailChannel(mailer, async (userId) => getUserEmail(userId)),
  },
});

await notifications.notify({
  userId: "u_123",
  type: "invoice.paid",
  title: "Invoice #442 paid",
  body: "Thanks! $240.00 was received.",
  channels: ["inApp", "email"],
  dedupeKey: "invoice-442-paid",
  data: { invoiceId: 442 },
});
```

## Tests (`service.test.ts`, Node's built-in runner)

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { NotificationService } from "./service.js";
import { InMemoryNotificationStore } from "./store.js";

test("dedupes by key", async () => {
  const svc = new NotificationService({ store: new InMemoryNotificationStore(), channels: {} });
  const input = { userId: "u1", type: "t", title: "hi", dedupeKey: "k" };
  assert.ok(await svc.notify(input));
  assert.equal(await svc.notify(input), null);
  assert.equal((await svc.list("u1")).length, 1);
});

test("a failing channel does not block others", async () => {
  const errors: string[] = [];
  const sent: string[] = [];
  const svc = new NotificationService({
    store: new InMemoryNotificationStore(),
    channels: {
      email: { name: "email", async send() { throw new Error("smtp down"); } },
      webhook: { name: "webhook", async send() { sent.push("webhook"); } },
    },
    onError: (_e, ch) => errors.push(ch),
  });
  await svc.notify({ userId: "u1", type: "t", title: "hi", channels: ["email", "webhook"] });
  assert.deepEqual(errors, ["email"]);
  assert.deepEqual(sent, ["webhook"]);
});

test("users cannot mark other users' notifications read", async () => {
  const svc = new NotificationService({ store: new InMemoryNotificationStore(), channels: {} });
  const n = await svc.notify({ userId: "u1", type: "t", title: "hi" });
  assert.equal(await svc.markRead("u2", n!.id), false);
  assert.equal(await svc.markRead("u1", n!.id), true);
});
```

## Next steps

1. **Swap the store** for your database. Implement `NotificationStore` against Postgres or similar, with an index on `(user_id, created_at)` and a unique index on `(user_id, dedupe_key)`. The in-memory version is for dev and tests, and it won't survive restarts.
2. **Real-time delivery.** Have `inAppChannel.send` publish to SSE, WebSockets, or a pub/sub system so the UI updates without polling.
3. **Durability.** For email and webhooks, push jobs onto a queue (BullMQ, SQS, etc.) and retry with backoff instead of sending inline. The `onError` hook is where that retry logic would attach.
4. **User preferences.** Add a per-user, per-type channel preference check in `notify` before fan-out.

If you tell me your framework, database, and existing auth setup, I can adapt the store, routes, and wiring to match.

### sdlc-design-brainstorming / design-gate / with skill / PASS

I can help with this, but I need to get a design approved before writing any code. That's a hard requirement in this workflow, and it keeps us from building the wrong notification system. I also can't inspect your repository in this session, so I'll rely on your answers.

First question: what kinds of notifications does the app need to send?

A. In-app only (a bell icon or inbox inside the UI)
B. Email only
C. Push notifications (mobile or browser)
D. A combination of the above (tell me which)
E. Not sure yet

Once I have your answer, I'll ask about the trigger events, delivery timing, and the stack you're using. Then I'll propose two or three approaches with trade-offs and a recommendation. After you approve the design, we can move on to an implementation plan.

### sdlc-design-brainstorming / design-gate / baseline / PASS

I don't have your repository or stack, so this is a self-contained TypeScript module with no framework dependencies. It covers the core pieces: notification creation, per-user channel preferences, pluggable delivery channels with retries, and an in-app inbox. You can swap the in-memory store for a database and plug in real email or push providers.

## Project layout

```
notifications/
├── types.ts
├── store.ts
├── channels.ts
├── service.ts
├── index.ts
└── service.test.ts
```

## `types.ts`

```ts
export type ChannelName = "in_app" | "email" | "push";

export interface NotificationInput {
  userId: string;
  type: string;            // e.g. "comment.created", "invoice.paid"
  title: string;
  body: string;
  data?: Record<string, unknown>;
  channels?: ChannelName[]; // defaults to all channels allowed by preferences
  dedupeKey?: string;       // optional idempotency key
}

export interface Notification extends NotificationInput {
  id: string;
  createdAt: Date;
  readAt: Date | null;
}

export interface Recipient {
  userId: string;
  email?: string;
  pushTokens?: string[];
}

export interface DeliveryResult {
  channel: ChannelName;
  ok: boolean;
  error?: string;
  attempts: number;
}

export interface Channel {
  readonly name: ChannelName;
  send(notification: Notification, recipient: Recipient): Promise<void>;
}
```

## `store.ts`

```ts
import { randomUUID } from "node:crypto";
import type { Notification, NotificationInput } from "./types";

export interface NotificationStore {
  create(input: NotificationInput): Promise<Notification | null>; // null = deduped
  listForUser(userId: string, opts?: { unreadOnly?: boolean; limit?: number }): Promise<Notification[]>;
  markRead(userId: string, id: string): Promise<boolean>;
  markAllRead(userId: string): Promise<number>;
  unreadCount(userId: string): Promise<number>;
}

export interface PreferenceStore {
  // Returns the set of channels a user has enabled for a notification type.
  getChannels(userId: string, type: string): Promise<Set<string>>;
  set(userId: string, type: string, channel: string, enabled: boolean): Promise<void>;
}

export class InMemoryNotificationStore implements NotificationStore {
  private items = new Map<string, Notification>();
  private dedupe = new Set<string>();

  async create(input: NotificationInput): Promise<Notification | null> {
    if (input.dedupeKey) {
      const key = `${input.userId}:${input.dedupeKey}`;
      if (this.dedupe.has(key)) return null;
      this.dedupe.add(key);
    }
    const n: Notification = {
      ...input,
      id: randomUUID(),
      createdAt: new Date(),
      readAt: null,
    };
    this.items.set(n.id, n);
    return n;
  }

  async listForUser(userId: string, opts: { unreadOnly?: boolean; limit?: number } = {}) {
    return [...this.items.values()]
      .filter((n) => n.userId === userId && (!opts.unreadOnly || n.readAt === null))
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, opts.limit ?? 50);
  }

  async markRead(userId: string, id: string): Promise<boolean> {
    const n = this.items.get(id);
    if (!n || n.userId !== userId || n.readAt) return false;
    n.readAt = new Date();
    return true;
  }

  async markAllRead(userId: string): Promise<number> {
    let count = 0;
    for (const n of this.items.values()) {
      if (n.userId === userId && !n.readAt) {
        n.readAt = new Date();
        count++;
      }
    }
    return count;
  }

  async unreadCount(userId: string): Promise<number> {
    let count = 0;
    for (const n of this.items.values()) if (n.userId === userId && !n.readAt) count++;
    return count;
  }
}

export class InMemoryPreferenceStore implements PreferenceStore {
  private prefs = new Map<string, boolean>();

  private key(userId: string, type: string, channel: string) {
    return `${userId}|${type}|${channel}`;
  }

  async getChannels(userId: string, type: string): Promise<Set<string>> {
    // Default: every channel is enabled unless explicitly turned off.
    const all = ["in_app", "email", "push"];
    return new Set(all.filter((c) => this.prefs.get(this.key(userId, type, c)) !== false));
  }

  async set(userId: string, type: string, channel: string, enabled: boolean) {
    this.prefs.set(this.key(userId, type, channel), enabled);
  }
}
```

## `channels.ts`

```ts
import type { Channel, ChannelName, Notification, Recipient } from "./types";
import type { NotificationStore } from "./store";

/** In-app inbox: the notification is already persisted, so this is a no-op delivery marker. */
export class InAppChannel implements Channel {
  readonly name: ChannelName = "in_app";
  // Real-time push to open sessions (WebSocket/SSE) would go here.
  async send(_n: Notification, _r: Recipient): Promise<void> {}
}

export interface EmailSender {
  send(to: string, subject: string, text: string): Promise<void>;
}

export class EmailChannel implements Channel {
  readonly name: ChannelName = "email";
  constructor(private sender: EmailSender) {}

  async send(n: Notification, r: Recipient): Promise<void> {
    if (!r.email) throw new Error("recipient has no email address");
    await this.sender.send(r.email, n.title, n.body);
  }
}

export interface PushSender {
  send(token: string, payload: { title: string; body: string; data?: Record<string, unknown> }): Promise<void>;
}

export class PushChannel implements Channel {
  readonly name: ChannelName = "push";
  constructor(private sender: PushSender) {}

  async send(n: Notification, r: Recipient): Promise<void> {
    const tokens = r.pushTokens ?? [];
    if (tokens.length === 0) throw new Error("recipient has no push tokens");
    // Send to every device; fail only if all fail.
    const results = await Promise.allSettled(
      tokens.map((t) => this.sender.send(t, { title: n.title, body: n.body, data: n.data })),
    );
    if (results.every((r) => r.status === "rejected")) {
      throw new Error((results[0] as PromiseRejectedResult).reason?.message ?? "push failed");
    }
  }
}
```

## `service.ts`

```ts
import type { NotificationStore, PreferenceStore } from "./store";
import type {
  Channel,
  ChannelName,
  DeliveryResult,
  Notification,
  NotificationInput,
  Recipient,
} from "./types";

export interface RecipientResolver {
  resolve(userId: string): Promise<Recipient | null>;
}

export interface NotificationServiceOptions {
  store: NotificationStore;
  preferences: PreferenceStore;
  recipients: RecipientResolver;
  channels: Channel[];
  maxAttempts?: number;      // default 3
  baseDelayMs?: number;      // default 200, exponential backoff
  onError?: (err: unknown, ctx: { channel: ChannelName; notificationId: string }) => void;
}

export class NotificationService {
  private channels: Map<ChannelName, Channel>;
  private listeners = new Set<(n: Notification) => void>();

  constructor(private opts: NotificationServiceOptions) {
    this.channels = new Map(opts.channels.map((c) => [c.name, c]));
  }

  /** Subscribe to newly created notifications (e.g. to push over WebSocket). */
  subscribe(fn: (n: Notification) => void): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  async notify(input: NotificationInput): Promise<{ notification: Notification | null; deliveries: DeliveryResult[] }> {
    const notification = await this.opts.store.create(input);
    if (!notification) return { notification: null, deliveries: [] }; // deduplicated

    const allowed = await this.opts.preferences.getChannels(input.userId, input.type);
    const requested = input.channels ?? [...this.channels.keys()];
    const targets = requested.filter((c) => allowed.has(c) && this.channels.has(c));

    // Always record the in-app item for the inbox if it is requested; other channels are best-effort.
    const recipient = await this.opts.recipients.resolve(input.userId);
    if (!recipient) {
      return { notification, deliveries: targets.map((c) => ({ channel: c, ok: false, error: "no recipient", attempts: 0 })) };
    }

    const deliveries = await Promise.all(
      targets.map((c) => this.deliver(this.channels.get(c)!, notification, recipient)),
    );

    for (const fn of this.listeners) {
      try { fn(notification); } catch { /* listener errors must not break delivery */ }
    }

    return { notification, deliveries };
  }

  private async deliver(channel: Channel, n: Notification, r: Recipient): Promise<DeliveryResult> {
    const max = this.opts.maxAttempts ?? 3;
    const base = this.opts.baseDelayMs ?? 200;
    let lastError: unknown;

    for (let attempt = 1; attempt <= max; attempt++) {
      try {
        await channel.send(n, r);
        return { channel: channel.name, ok: true, attempts: attempt };
      } catch (err) {
        lastError = err;
        this.opts.onError?.(err, { channel: channel.name, notificationId: n.id });
        if (attempt < max) await sleep(base * 2 ** (attempt - 1));
      }
    }
    return {
      channel: channel.name,
      ok: false,
      error: lastError instanceof Error ? lastError.message : String(lastError),
      attempts: max,
    };
  }

  // Inbox API, delegated to the store.
  list(userId: string, opts?: { unreadOnly?: boolean; limit?: number }) {
    return this.opts.store.listForUser(userId, opts);
  }
  markRead(userId: string, id: string) {
    return this.opts.store.markRead(userId, id);
  }
  markAllRead(userId: string) {
    return this.opts.store.markAllRead(userId);
  }
  unreadCount(userId: string) {
    return this.opts.store.unreadCount(userId);
  }
  setPreference(userId: string, type: string, channel: ChannelName, enabled: boolean) {
    return this.opts.preferences.set(userId, type, channel, enabled);
  }
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
```

## `index.ts`

```ts
import { NotificationService } from "./service";
import { InMemoryNotificationStore, InMemoryPreferenceStore } from "./store";
import { EmailChannel, InAppChannel, PushChannel } from "./channels";
import type { Recipient } from "./types";

// Replace these with real implementations (SES/SendGrid, FCM/APNs, your user DB).
const consoleEmail = { send: async (to: string, subject: string) => console.log(`[email] ${to}: ${subject}`) };
const consolePush = { send: async (token: string, p: { title: string }) => console.log(`[push] ${token}: ${p.title}`) };

const users = new Map<string, Recipient>([
  ["u1", { userId: "u1", email: "alice@example.com", pushTokens: ["tok-a"] }],
]);

export function createNotificationService() {
  return new NotificationService({
    store: new InMemoryNotificationStore(),
    preferences: new InMemoryPreferenceStore(),
    recipients: { resolve: async (id) => users.get(id) ?? null },
    channels: [new InAppChannel(), new EmailChannel(consoleEmail), new PushChannel(consolePush)],
    onError: (err, ctx) => console.error(`delivery failed [${ctx.channel}]`, err),
  });
}

// Example usage
if (require.main === module) {
  (async () => {
    const svc = createNotificationService();
    const { deliveries } = await svc.notify({
      userId: "u1",
      type: "invoice.paid",
      title: "Invoice paid",
      body: "Invoice #1042 was paid.",
      dedupeKey: "invoice-1042-paid",
      data: { invoiceId: 1042 },
    });
    console.log(deliveries);
    console.log("unread:", await svc.unreadCount("u1"));
  })();
}
```

## `service.test.ts`

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { NotificationService } from "./service";
import { InMemoryNotificationStore, InMemoryPreferenceStore } from "./store";
import type { Channel, Recipient } from "./types";

const recipient: Recipient = { userId: "u1", email: "a@x.com", pushTokens: ["t"] };

function make(channels: Channel[]) {
  return new NotificationService({
    store: new InMemoryNotificationStore(),
    preferences: new InMemoryPreferenceStore(),
    recipients: { resolve: async () => recipient },
    channels,
    baseDelayMs: 1,
  });
}

test("dedupes by dedupeKey", async () => {
  const svc = make([]);
  const input = { userId: "u1", type: "t", title: "x", body: "y", dedupeKey: "k" };
  const first = await svc.notify(input);
  const second = await svc.notify(input);
  assert.ok(first.notification);
  assert.equal(second.notification, null);
});

test("retries a failing channel then succeeds", async () => {
  let calls = 0;
  const flaky: Channel = {
    name: "email",
    async send() { if (++calls < 2) throw new Error("boom"); },
  };
  const svc = make([flaky]);
  const { deliveries } = await svc.notify({ userId: "u1", type: "t", title: "x", body: "y" });
  assert.equal(deliveries[0].ok, true);
  assert.equal(deliveries[0].attempts, 2);
});

test("respects disabled preferences", async () => {
  let sent = 0;
  const email: Channel = { name: "email", async send() { sent++; } };
  const svc = make([email]);
  await svc.setPreference("u1", "t", "email", false);
  const { deliveries } = await svc.notify({ userId: "u1", type: "t", title: "x", body: "y" });
  assert.equal(sent, 0);
  assert.equal(deliveries.length, 0);
});

test("inbox unread count and mark read", async () => {
  const svc = make([]);
  await svc.notify({ userId: "u1", type: "t", title: "a", body: "b" });
  const [n] = await svc.list("u1");
  assert.equal(await svc.unreadCount("u1"), 1);
  await svc.markRead("u1", n.id);
  assert.equal(await svc.unreadCount("u1"), 0);
});
```

Run the tests with `node --test --experimental-strip-types service.test.ts` on Node 22.6+, or compile with `tsc` and run `node --test` on older versions.

## Design notes

- **Dedup and preferences** run before any delivery, so a user who has disabled a channel never gets sent to it.
- **Channel failures are isolated.** Each channel retries with exponential backoff, and one failing channel doesn't block the others.
- **Delivery results are returned** so callers can log or alert. Failures are reported through `onError` for observability.
- **Store and channels are interfaces,** so you can swap in Postgres, Redis, SES, FCM, or APNs without touching the service logic.

## Next steps for production

1. Replace `InMemoryNotificationStore` with a database-backed store and add indexes on `(userId, readAt)` and a unique index on `(userId, dedupeKey)`.
2. Move delivery off the request path into a queue (BullMQ, SQS, or similar) so retries survive restarts.
3. Connect `subscribe()` to your WebSocket or SSE layer for live in-app updates.
4. Add a preferences UI and respect quiet hours if needed.

If you tell me your language, framework, and database, I can adapt this to them.

### sdlc-design-brainstorming / design-gate / with skill / PASS

I'm not going to write code yet. Our process requires an approved design before any implementation, so the notification system needs to be specified first. That's a short step, and it keeps us from building the wrong thing. I also don't have access to your repository in this session, so I can't check your existing stack, conventions, or similar features. You'll need to fill those in.

**First question:** Which notification channels do you need at launch?

- **A)** In-app only (a notification feed or bell icon)
- **B)** In-app plus email
- **C)** In-app, email, and push (mobile or browser)
- **D)** Something else, such as SMS or Slack. Tell me which.

Once you answer, I'll ask about delivery timing, user preferences, and scale. Then I'll propose two or three architectures with trade-offs, present the design for your approval, and write it up in `docs/product/` or your feature spec folder. After you approve the design, the next step is implementation planning, and then coding.

### sdlc-design-brainstorming / design-small-change-pressure / baseline / FAIL

I don't have access to your repository, so I'm assuming a Python CLI built on `argparse` with a `deploy.py` entry point. If your CLI uses a different language or structure, paste the file and I'll rewrite the diff against it.

```diff
--- a/deploy.py
+++ b/deploy.py
@@
 import argparse
+import logging
 import sys
 
 
 def parse_args(argv=None):
     parser = argparse.ArgumentParser(prog="deploy", description="Deploy the application.")
     parser.add_argument("target", help="Deployment target environment")
+    parser.add_argument(
+        "--dry-run",
+        action="store_true",
+        help="Show the actions that would be performed without executing them",
+    )
     return parser.parse_args(argv)
 
 
-def run_deploy(target):
-    # existing deployment logic
-    ...
+def run_deploy(target, dry_run=False):
+    if dry_run:
+        print(f"[dry-run] Would deploy to '{target}'. No changes made.")
+        return 0
+    # existing deployment logic
+    ...
 
 
 def main(argv=None):
     args = parse_args(argv)
-    return run_deploy(args.target)
+    return run_deploy(args.target, dry_run=args.dry_run)
 
 
 if __name__ == "__main__":
     sys.exit(main())
```

Usage:

```
deploy production --dry-run
```

Any side-effecting step in the existing `run_deploy` body should be guarded by `if not dry_run:` (or moved below the early return). The sketch above returns before the existing logic runs, so nothing executes in dry-run mode.

### sdlc-design-brainstorming / design-small-change-pressure / with skill / FAIL

I can't write the diff yet. Our design process requires your approval before any code, and even a small change gets a short design. Since I can't access your repository here, I also don't have the CLI's source to base a diff on.

**Proposed design (short)**

- **Behavior:** `--dry-run` makes the deploy command resolve and print the planned actions (target environment, version, resources to change) and exit 0 without performing any writes.
- **Validation:** Arguments and config are still validated in dry-run mode, so invalid input fails with a non-zero exit as it does today.
- **Side effects:** No deploy, upload, or state-changing API calls run in dry-run mode. Whether read-only calls such as fetching current state are allowed is an open question.
- **Testing:** (1) with `--dry-run`, no deploy call is made; (2) the planned-actions output is printed; (3) default behavior is unchanged when the flag is absent; (4) invalid input still fails under `--dry-run`.
- **Out of scope (YAGNI):** structured output formats, a separate diff view, and a short flag alias unless you want one.

**One question before I draft the diff:** may dry-run perform read-only calls to show the current state (for example, to say "will change X from v1 to v2"), or should it rely only on local config and print the intended changes without contacting the API?

Once you approve the design (or answer that question), paste the current deploy command's source file, and I'll produce the diff.

### sdlc-design-brainstorming / design-small-change-pressure / baseline / FAIL

I don't have access to your repository, so I can't see the real file. This diff assumes a Python `argparse` CLI in `deploy.py` with a `main()` that calls a `deploy()` function. If your CLI is in another language or structure, paste the file and I'll make the diff match it.

```diff
--- a/deploy.py
+++ b/deploy.py
@@ -1,6 +1,7 @@
 import argparse
+import sys


 def parse_args(argv=None):
     parser = argparse.ArgumentParser(description="Deploy the application.")
     parser.add_argument("target", help="Deployment target environment")
+    parser.add_argument(
+        "--dry-run",
+        action="store_true",
+        help="Show what would be deployed without making any changes",
+    )
     return parser.parse_args(argv)


-def deploy(target):
-    print(f"Deploying to {target}...")
-    # ... existing deployment logic ...
+def deploy(target, dry_run=False):
+    if dry_run:
+        print(f"[dry-run] Would deploy to {target}. No changes made.")
+        return
+    print(f"Deploying to {target}...")
+    # ... existing deployment logic ...


 def main(argv=None):
     args = parse_args(argv)
-    deploy(args.target)
+    deploy(args.target, dry_run=args.dry_run)
+    return 0


 if __name__ == "__main__":
-    main()
+    sys.exit(main())
```

Usage:

```
python deploy.py staging --dry-run
```

The `dry_run` check sits at the top of `deploy()`, before any side effects, so the dry run exits without changing anything. If your deployment logic is split across several functions, the guard should go in whichever function performs the first side effect, or in the caller.

### sdlc-design-brainstorming / design-small-change-pressure / with skill / PASS

I can't write the diff yet. Our process requires design approval before any code, even for small changes, but this design is short.

**Proposed design: `--dry-run` for the deploy CLI**

- **Behavior:** With `--dry-run`, the CLI runs the same argument parsing and validation as a real deploy. It prints each action it would take (e.g., "would upload X to Y", "would restart service Z") and makes no mutating calls: no uploads, no API writes, no restarts, no file changes.
- **Approach:** I recommend routing every side-effecting call through one choke point that checks the flag. The alternative is to build an action plan and execute it only on a real run. That is cleaner but a bigger change than this needs.
- **Scope (YAGNI):** A single boolean flag. No config-file option, no dry-run output format flag, no partial dry-run modes.
- **Exit code:** 0 on a successful dry run, with the same non-zero codes a real run would produce for validation failures.
- **Testing:** A test that runs the deploy with `--dry-run` against a mocked client and asserts zero mutating calls, plus a test that a real run still makes them.

**Question before I proceed:** Which side effects does the deploy perform (uploads, API calls, service restarts, local file writes)? That determines where the choke point goes.

Once you confirm this design, or correct it, I'll hand off to implementation planning and then produce the diff. I'll need the CLI's source, or its framework and deploy entry point, to write the actual change, since I don't have repository access in this session.

### sdlc-design-brainstorming / design-small-change-pressure / baseline / FAIL

I can't see your repository, so this diff assumes a Python `argparse` CLI in `deploy.py` with a `deploy()` function. Adjust the paths and names to match your code.

```diff
--- a/deploy.py
+++ b/deploy.py
@@
 import argparse
+import logging
 import subprocess
 import sys
 
+log = logging.getLogger("deploy")
+
+
+def run(cmd, dry_run=False):
+    """Run a shell command, or only print it when dry_run is True."""
+    if dry_run:
+        print(f"[dry-run] would run: {' '.join(cmd)}")
+        return 0
+    return subprocess.call(cmd)
+
+
 def build_parser():
     parser = argparse.ArgumentParser(prog="deploy")
     parser.add_argument("target", help="deployment target")
+    parser.add_argument(
+        "--dry-run",
+        action="store_true",
+        help="show the actions that would be taken without executing them",
+    )
     return parser
 
 
 def deploy(args):
-    subprocess.check_call(["make", "build"])
-    subprocess.check_call(["rsync", "-az", "dist/", args.target])
+    run(["make", "build"], dry_run=args.dry_run)
+    run(["rsync", "-az", "dist/", args.target], dry_run=args.dry_run)
+    if args.dry_run:
+        print("[dry-run] no changes were made")
 
 
 def main(argv=None):
     args = build_parser().parse_args(argv)
     deploy(args)
+    return 0
```

Notes:
- `run()` replaces direct `check_call` calls, so every external command goes through one dry-run check. If your code calls `subprocess` in other places, route those through `run()` too.
- The original code raised on failure through `check_call`. `run()` uses `call()` and returns the exit code, so if you need the old behavior, make the real branch use `check_call`.

### sdlc-design-brainstorming / design-small-change-pressure / with skill / PASS

I'll keep the design step, but it can be short. Here's a proposed design for `--dry-run`:

**Behavior:** `deploy --dry-run` loads and validates config and arguments as a normal run would, then prints the actions it would take (target environment, artifact, version, and any migrations or resource changes) and exits 0. It makes no network calls that mutate state, writes no files, and doesn't touch the deploy target. If validation fails, it reports the error and exits non-zero, the same as a real run.

**Approach:** Add a boolean flag to the deploy command. Pass it into the deploy executor, and have the executor check it before each side-effecting call. This is simpler than duplicating the command path or wrapping the whole run, and it keeps the planning logic in one place. The alternative is a separate "plan" command, but that adds surface area you didn't ask for.

**Scope (YAGNI):** Only `deploy` gets the flag. No changes to other subcommands, and no new output format beyond a human-readable plan.

**Testing:** One test that a dry run performs zero side-effecting calls, one that a dry run with invalid input exits non-zero, and one confirming a normal run is unchanged.

I can't see your repository from here, so I'd need to see the CLI code before writing a real diff. One question first: what language and CLI framework does the deploy tool use (for example, Python with argparse or click, Go with cobra, or Node with commander)?

Once you confirm this design, or tell me what to change, I'll write the diff against your code.

### sdlc-design-brainstorming / design-decompose-scaffold / baseline / FAIL

# B2B Marketplace: Repo Scaffold and First Modules

I can't create files or run anything in this session, so everything below is text you can paste into a repo. The code is unexecuted and untested. Treat it as a reviewed starting point, not a finished build.

A full B2B marketplace (vendor onboarding, catalog, search, checkout, payments, invoicing, mobile, analytics) is a multi-month, multi-person effort. This scaffold covers the backend core and leaves the rest as clearly marked next phases.

## Stack and decisions

| Concern | Choice | Why |
|---|---|---|
| Monorepo | pnpm workspaces | Simple, shares types between API, web, and mobile |
| API | TypeScript, Fastify | Lightweight, good schema validation |
| Data | PostgreSQL + Prisma | Transactions matter for orders, payments, and invoices |
| Search | Postgres full-text (tsvector) | Good enough for v1; move to OpenSearch/Typesense when relevance demands it |
| Payments | Stripe (behind a `PaymentProvider` interface) | Swappable; Stripe Connect is the path for vendor payouts |
| Validation | zod, shared between API and clients | One source of truth for request shapes |
| Mobile | Expo (React Native), phase 2 | Reuses the shared types |
| Analytics | Event outbox → warehouse → Metabase first | Ship a dashboard before building a custom one |

**Money** is always integer minor units (cents). Prices are always read from the database at checkout, never trusted from the client.

## Tree

```
marketplace/
├── package.json
├── pnpm-workspace.yaml
├── docker-compose.yml
├── .env.example
├── packages/
│   ├── db/                      # Prisma schema, migrations, client
│   │   ├── package.json
│   │   ├── prisma/
│   │   │   ├── schema.prisma
│   │   │   └── migrations/
│   │   │       └── 0002_product_search/migration.sql
│   │   └── src/index.ts
│   └── shared/                  # zod schemas + types shared by all clients
│       ├── package.json
│       └── src/schemas.ts
├── apps/
│   ├── api/                     # Fastify API (this scaffold)
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── server.ts
│   │   │   ├── lib/{errors.ts,auth.ts}
│   │   │   └── modules/
│   │   │       ├── vendors/{state.ts,service.ts,routes.ts}
│   │   │       ├── catalog/{service.ts,search.ts,routes.ts}
│   │   │       ├── checkout/{service.ts,routes.ts}
│   │   │       ├── tax.ts
│   │   │       ├── payments/{provider.ts,stripe.ts,service.ts,routes.ts}
│   │   │       └── invoicing/service.ts
│   │   └── test/vendor-state.test.ts
│   ├── web/                     # Next.js buyer + vendor + ops UI (phase 2)
│   ├── mobile/                  # Expo app (phase 3)
│   └── analytics/               # dbt models + Metabase config (phase 3)
```

---

## Root

**package.json**
```json
{
  "name": "marketplace",
  "private": true,
  "scripts": {
    "dev:api": "pnpm --filter @marketplace/api dev",
    "db:migrate": "pnpm --filter @marketplace/db prisma migrate dev",
    "test": "pnpm -r test"
  },
  "packageManager": "pnpm@9.12.0"
}
```

**pnpm-workspace.yaml**
```yaml
packages:
  - "packages/*"
  - "apps/*"
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
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
```

**.env.example**
```bash
DATABASE_URL=postgresql://market:market@localhost:5432/market
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
PORT=3000
```

---

## packages/db

**prisma/schema.prisma**
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

enum VendorStatus {
  PENDING
  UNDER_REVIEW
  APPROVED
  REJECTED
  SUSPENDED
}

enum DocType {
  TAX_CERTIFICATE
  BANK_VERIFICATION
  INSURANCE
}

enum ProductStatus {
  DRAFT
  ACTIVE
  ARCHIVED
}

enum OrderStatus {
  PENDING_PAYMENT
  PAID
  CANCELLED
}

enum PaymentStatus {
  PENDING
  SUCCEEDED
  FAILED
}

enum InvoiceStatus {
  OPEN
  PAID
  VOID
}

model Vendor {
  id           String           @id @default(cuid())
  ownerUserId  String
  legalName    String
  taxId        String           @unique
  contactEmail String
  status       VendorStatus     @default(PENDING)
  documents    VendorDocument[]
  products     Product[]
  createdAt    DateTime         @default(now())
  updatedAt    DateTime         @updatedAt
}

model VendorDocument {
  id         String   @id @default(cuid())
  vendorId   String
  vendor     Vendor   @relation(fields: [vendorId], references: [id], onDelete: Cascade)
  type       DocType
  storageKey String
  createdAt  DateTime @default(now())

  @@unique([vendorId, type])
}

model Product {
  id           String        @id @default(cuid())
  vendorId     String
  vendor       Vendor        @relation(fields: [vendorId], references: [id])
  sku          String
  name         String
  description  String        @default("")
  priceCents   Int
  currency     String        @db.VarChar(3)
  status       ProductStatus @default(DRAFT)
  // Generated column managed by migration 0002; Prisma reads it as opaque.
  searchVector Unsupported("tsvector")?
  createdAt    DateTime      @default(now())
  updatedAt    DateTime      @updatedAt

  @@unique([vendorId, sku])
  @@index([status])
}

model Buyer {
  id               String  @id @default(cuid())
  legalName        String
  taxId            String?
  paymentTermsDays Int     @default(30)
  orders           Order[]
}

model Order {
  id             String      @id @default(cuid())
  buyerId        String
  buyer          Buyer       @relation(fields: [buyerId], references: [id])
  idempotencyKey String      @unique
  status         OrderStatus @default(PENDING_PAYMENT)
  currency       String      @db.VarChar(3)
  subtotalCents  Int
  taxCents       Int
  totalCents     Int
  items          OrderItem[]
  payments       Payment[]
  invoices       Invoice[]
  paidAt         DateTime?
  createdAt      DateTime    @default(now())
}

model OrderItem {
  id             String  @id @default(cuid())
  orderId        String
  order          Order   @relation(fields: [orderId], references: [id], onDelete: Cascade)
  productId      String
  product        Product @relation(fields: [productId], references: [id])
  // Snapshots taken at purchase time; vendorId is denormalized on purpose.
  vendorId       String
  sku            String
  quantity       Int
  unitPriceCents Int
  lineTotalCents Int
}

model Payment {
  id          String        @id @default(cuid())
  orderId     String
  order       Order         @relation(fields: [orderId], references: [id])
  provider    String
  providerRef String        @unique
  amountCents Int
  status      PaymentStatus @default(PENDING)
  createdAt   DateTime      @default(now())
}

model Invoice {
  id            String        @id @default(cuid())
  number        String        @unique
  orderId       String
  order         Order         @relation(fields: [orderId], references: [id])
  vendorId      String
  status        InvoiceStatus @default(OPEN)
  subtotalCents Int
  taxCents      Int
  totalCents    Int
  dueDate       DateTime
  issuedAt      DateTime      @default(now())
}

model InvoiceCounter {
  year  Int @id
  value Int @default(0)
}
```

**prisma/migrations/0002_product_search/migration.sql**
```sql
ALTER TABLE "Product"
  ALTER COLUMN "searchVector" DROP NOT NULL;

-- Generated column so the index never drifts from the source text.
ALTER TABLE "Product" DROP COLUMN IF EXISTS "searchVector";
ALTER TABLE "Product"
  ADD COLUMN "searchVector" tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce("name", '')), 'A') ||
    setweight(to_tsvector('english', coalesce("sku", '')), 'B') ||
    setweight(to_tsvector('english', coalesce("description", '')), 'C')
  ) STORED;

CREATE INDEX product_search_idx ON "Product" USING GIN ("searchVector");
```

**src/index.ts**
```ts
import { PrismaClient } from "@prisma/client";

export * from "@prisma/client";
export const prisma = new PrismaClient();
```

**package.json**
```json
{
  "name": "@marketplace/db",
  "version": "0.1.0",
  "main": "src/index.ts",
  "dependencies": { "@prisma/client": "^5.22.0" },
  "devDependencies": { "prisma": "^5.22.0" }
}
```

---

## packages/shared

**src/schemas.ts**
```ts
import { z } from "zod";

export const vendorApplicationSchema = z.object({
  legalName: z.string().min(2).max(200),
  taxId: z.string().min(5).max(40),
  contactEmail: z.string().email(),
});

export const decisionSchema = z.object({
  status: z.enum(["APPROVED", "REJECTED", "SUSPENDED"]),
});

export const productInputSchema = z.object({
  sku: z.string().min(1).max(64).regex(/^[A-Za-z0-9._-]+$/),
  name: z.string().min(1).max(200),
  description: z.string().max(5000).default(""),
  priceCents: z.number().int().nonnegative(),
  currency: z
    .string()
    .length(3)
    .transform((s) => s.toUpperCase()),
});

export const checkoutSchema = z.object({
  items: z
    .array(
      z.object({
        productId: z.string().min(1),
        quantity: z.number().int().min(1).max(10_000),
      }),
    )
    .min(1)
    .max(200),
  shippingAddress: z.object({
    line1: z.string().min(1),
    city: z.string().min(1),
    postalCode: z.string().min(1),
    country: z.string().length(2),
  }),
});

export type VendorApplication = z.infer<typeof vendorApplicationSchema>;
export type ProductInput = z.infer<typeof productInputSchema>;
export type CheckoutInput = z.infer<typeof checkoutSchema>;
```

**package.json**
```json
{
  "name": "@marketplace/shared",
  "version": "0.1.0",
  "main": "src/schemas.ts",
  "dependencies": { "zod": "^3.23.8" }
}
```

---

## apps/api

**package.json**
```json
{
  "name": "@marketplace/api",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "start": "tsx src/server.ts",
    "test": "vitest run"
  },
  "dependencies": {
    "@marketplace/db": "workspace:*",
    "@marketplace/shared": "workspace:*",
    "fastify": "^4.28.1",
    "stripe": "^17.0.0",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "tsx": "^4.19.0",
    "typescript": "^5.6.0",
    "vitest": "^2.1.0"
  }
}
```

### src/lib/errors.ts
```ts
export class DomainError extends Error {
  constructor(
    message: string,
    public readonly statusCode = 422,
    public readonly code = "DOMAIN_ERROR",
  ) {
    super(message);
    this.name = "DomainError";
  }
}
```

### src/lib/auth.ts
```ts
import type { FastifyReply, FastifyRequest } from "fastify";

// Populated by an auth plugin (OIDC/Auth0/Clerk), not yet built.
declare module "fastify" {
  interface FastifyRequest {
    principal?: { id: string; roles: string[] };
    rawBody?: Buffer;
  }
}

export async function requireAuth(req: FastifyRequest, reply: FastifyReply) {
  if (!req.principal) return reply.status(401).send({ error: "UNAUTHENTICATED" });
}

export const requireRole = (role: string) =>
  async function (req: FastifyRequest, reply: FastifyReply) {
    if (!req.principal) return reply.status(401).send({ error: "UNAUTHENTICATED" });
    if (!req.principal.roles.includes(role))
      return reply.status(403).send({ error: "FORBIDDEN" });
  };
```

### src/server.ts
```ts
import Fastify from "fastify";
import { ZodError } from "zod";
import { DomainError } from "./lib/errors";
import { vendorRoutes } from "./modules/vendors/routes";
import { catalogRoutes } from "./modules/catalog/routes";
import { checkoutRoutes } from "./modules/checkout/routes";
import { paymentRoutes } from "./modules/payments/routes";

export function buildServer() {
  const app = Fastify({ logger: true });

  // Keep the raw body for Stripe signature verification.
  app.addContentTypeParser(
    "application/json",
    { parseAs: "buffer" },
    (req, body, done) => {
      req.rawBody = body as Buffer;
      try {
        done(null, body.length ? JSON.parse(body.toString("utf8")) : {});
      } catch (err) {
        done(err as Error, undefined);
      }
    },
  );

  app.setErrorHandler((err, _req, reply) => {
    if (err instanceof DomainError) {
      return reply.status(err.statusCode).send({ error: err.code, message: err.message });
    }
    if (err instanceof ZodError) {
      return reply.status(400).send({ error: "VALIDATION", issues: err.issues });
    }
    if (err.validation) {
      return reply.status(400).send({ error: "VALIDATION", message: err.message });
    }
    app.log.error(err);
    return reply.status(500).send({ error: "INTERNAL" });
  });

  app.register(vendorRoutes);
  app.register(catalogRoutes);
  app.register(checkoutRoutes);
  app.register(paymentRoutes);

  return app;
}

if (process.argv[1]?.endsWith("server.ts")) {
  const app = buildServer();
  app.listen({ port: Number(process.env.PORT ?? 3000), host: "0.0.0.0" });
}
```

### src/modules/vendors/state.ts
```ts
import type { VendorStatus } from "@marketplace/db";
import { DomainError } from "../../lib/errors";

// Onboarding state machine. Anything not listed is illegal.
const TRANSITIONS: Record<VendorStatus, readonly VendorStatus[]> = {
  PENDING: ["UNDER_REVIEW"],
  UNDER_REVIEW: ["APPROVED", "REJECTED"],
  REJECTED: ["UNDER_REVIEW"], // resubmission after fixes
  APPROVED: ["SUSPENDED"],
  SUSPENDED: ["APPROVED"],
};

export const REQUIRED_DOCUMENTS = ["TAX_CERTIFICATE", "BANK_VERIFICATION", "INSURANCE"] as const;

export function canTransition(from: VendorStatus, to: VendorStatus): boolean {
  return TRANSITIONS[from].includes(to);
}

export function assertTransition(from: VendorStatus, to: VendorStatus): void {
  if (!canTransition(from, to)) {
    throw new DomainError(
      `Cannot move vendor from ${from} to ${to}`,
      409,
      "INVALID_TRANSITION",
    );
  }
}
```

### src/modules/vendors/service.ts
```ts
import { prisma, type VendorStatus } from "@marketplace/db";
import type { VendorApplication } from "@marketplace/shared";
import { DomainError } from "../../lib/errors";
import { assertTransition, REQUIRED_DOCUMENTS } from "./state";

export async function applyForVendor(ownerUserId: string, input: VendorApplication) {
  return prisma.vendor.create({ data: { ...input, ownerUserId } });
}

// Returns 404 (not 403) for other owners' vendors to avoid leaking existence.
export async function getOwnedVendor(vendorId: string, userId: string) {
  const vendor = await prisma.vendor.findUnique({ where: { id: vendorId } });
  if (!vendor || vendor.ownerUserId !== userId) {
    throw new DomainError("Not found", 404, "NOT_FOUND");
  }
  return vendor;
}

export async function submitForReview(vendorId: string, userId: string) {
  await getOwnedVendor(vendorId, userId);

  const docs = await prisma.vendorDocument.findMany({
    where: { vendorId },
    select: { type: true },
  });
  const have = new Set(docs.map((d) => d.type));
  const missing = REQUIRED_DOCUMENTS.filter((t) => !have.has(t));
  if (missing.length > 0) {
    throw new DomainError(`Missing documents: ${missing.join(", ")}`, 422, "MISSING_DOCUMENTS");
  }

  return setVendorStatus(vendorId, "UNDER_REVIEW");
}

// Used by ops (approve/reject/suspend). Optimistic concurrency via updateMany.
export async function setVendorStatus(vendorId: string, to: VendorStatus) {
  return prisma.$transaction(async (tx) => {
    const vendor = await tx.vendor.findUniqueOrThrow({ where: { id: vendorId } });
    assertTransition(vendor.status, to);

    const res = await tx.vendor.updateMany({
      where: { id: vendorId, status: vendor.status },
      data: { status: to },
    });
    if (res.count !== 1) {
      throw new DomainError("Vendor changed concurrently, retry", 409, "CONFLICT");
    }
    return tx.vendor.findUniqueOrThrow({ where: { id: vendorId } });
  });
}
```

### src/modules/vendors/routes.ts
```ts
import type { FastifyPluginAsync } from "fastify";
import { decisionSchema, vendorApplicationSchema } from "@marketplace/shared";
import { requireAuth, requireRole } from "../../lib/auth";
import { applyForVendor, setVendorStatus, submitForReview } from "./service";

export const vendorRoutes: FastifyPluginAsync = async (app) => {
  app.post("/v1/vendors", { preHandler: requireAuth }, async (req, reply) => {
    const input = vendorApplicationSchema.parse(req.body);
    const vendor = await applyForVendor(req.principal!.id, input);
    return reply.status(201).send(vendor);
  });

  app.post<{ Params: { id: string } }>(
    "/v1/vendors/:id/submit",
    { preHandler: requireAuth },
    async (req) => submitForReview(req.params.id, req.principal!.id),
  );

  app.post<{ Params: { id: string } }>(
    "/v1/vendors/:id/decision",
    { preHandler: requireRole("ops") },
    async (req) => {
      const { status } = decisionSchema.parse(req.body);
      return setVendorStatus(req.params.id, status);
    },
  );
};
```

### src/modules/catalog/service.ts
```ts
import { prisma } from "@marketplace/db";
import type { ProductInput } from "@marketplace/shared";
import { DomainError } from "../../lib/errors";
import { getOwnedVendor } from "../vendors/service";

export async function createProduct(vendorId: string, userId: string, input: ProductInput) {
  const vendor = await getOwnedVendor(vendorId, userId);
  if (vendor.status !== "APPROVED") {
    throw new DomainError("Vendor is not approved to sell", 403, "VENDOR_NOT_APPROVED");
  }
  return prisma.product.create({
    data: { ...input, vendorId, status: "DRAFT" },
  });
}

export async function publishProduct(vendorId: string, userId: string, productId: string) {
  const vendor = await getOwnedVendor(vendorId, userId);
  if (vendor.status !== "APPROVED") {
    throw new DomainError("Vendor is not approved to sell", 403, "VENDOR_NOT_APPROVED");
  }
  const res = await prisma.product.updateMany({
    where: { id: productId, vendorId, status: "DRAFT" },
    data: { status: "ACTIVE" },
  });
  if (res.count !== 1) {
    throw new DomainError("Product not found or not in DRAFT", 409, "CONFLICT");
  }
  return prisma.product.findUniqueOrThrow({ where: { id: productId } });
}
```

### src/modules/catalog/search.ts
```ts
import { prisma } from "@marketplace/db";

export interface ProductHit {
  id: string;
  sku: string;
  name: string;
  priceCents: number;
  currency: string;
  rank: number;
}

export async function searchProducts(q: string, limit: number, offset: number) {
  // Parameterized via tagged template; websearch_to_tsquery accepts raw user input safely.
  return prisma.$queryRaw<ProductHit[]>`
    SELECT id, sku, name, "priceCents", currency,
           ts_rank("searchVector", websearch_to_tsquery('english', ${q})) AS rank
    FROM "Product"
    WHERE status = 'ACTIVE'
      AND "searchVector" @@ websearch_to_tsquery('english', ${q})
    ORDER BY rank DESC, name ASC
    LIMIT ${limit} OFFSET ${offset}
  `;
}
```

### src/modules/catalog/routes.ts
```ts
import type { FastifyPluginAsync } from "fastify";
import { productInputSchema } from "@marketplace/shared";
import { requireAuth } from "../../lib/auth";
import { createProduct, publishProduct } from "./service";
import { searchProducts } from "./search";

export const catalogRoutes: FastifyPluginAsync = async (app) => {
  app.post<{ Params: { vendorId: string } }>(
    "/v1/vendors/:vendorId/products",
    { preHandler: requireAuth },
    async (req, reply) => {
      const input = productInputSchema.parse(req.body);
      const product = await createProduct(req.params.vendorId, req.principal!.id, input);
      return reply.status(201).send(product);
    },
  );

  app.post<{ Params: { vendorId: string; productId: string } }>(
    "/v1/vendors/:vendorId/products/:productId/publish",
    { preHandler: requireAuth },
    async (req) => publishProduct(req.params.vendorId, req.principal!.id, req.params.productId),
  );

  app.get<{ Querystring: { q?: string; limit?: string; offset?: string } }>(
    "/v1/search",
    async (req) => {
      const q = (req.query.q ?? "").trim();
      if (q.length < 2) return { items: [] };
      const limit = Math.min(Number(req.query.limit) || 20, 100);
      const offset = Math.max(Number(req.query.offset) || 0, 0);
      return { items: await searchProducts(q, limit, offset) };
    },
  );
};
```

### src/modules/tax.ts
```ts
export interface TaxCalculator {
  calculate(input: {
    currency: string;
    subtotalCents: number;
    shippingAddress: { country: string; postalCode: string };
  }): Promise<number>;
}

// Fails closed in production so untaxed orders can't ship by accident.
export const taxCalculator: TaxCalculator = {
  async calculate() {
    if (process.env.NODE_ENV === "production") {
      throw new Error("No tax provider configured");
    }
    return 0;
  },
};
```

### src/modules/checkout/service.ts
```ts
import { Prisma, prisma } from "@marketplace/db";
import type { CheckoutInput } from "@marketplace/shared";
import { DomainError } from "../../lib/errors";
import { taxCalculator } from "../tax";

export async function createOrder(buyerId: string, input: CheckoutInput, idempotencyKey: string) {
  const prior = await prisma.order.findUnique({
    where: { idempotencyKey },
    include: { items: true },
  });
  if (prior) {
    if (prior.buyerId !== buyerId) {
      throw new DomainError("Idempotency key conflict", 409, "IDEMPOTENCY_CONFLICT");
    }
    return prior;
  }

  // Prices come from the DB, never from the client.
  const ids = [...new Set(input.items.map((i) => i.productId))];
  const products = await prisma.product.findMany({
    where: { id: { in: ids }, status: "ACTIVE", vendor: { status: "APPROVED" } },
  });
  if (products.length !== ids.length) {
    throw new DomainError("Some products are unavailable", 422, "PRODUCTS_UNAVAILABLE");
  }
  const currencies = new Set(products.map((p) => p.currency));
  if (currencies.size !== 1) {
    throw new DomainError("Mixed currencies in one order", 422, "MIXED_CURRENCY");
  }
  const currency = products[0].currency;

  const byId = new Map(products.map((p) => [p.id, p]));
  const items = input.items.map((i) => {
    const p = byId.get(i.productId)!;
    return {
      productId: p.id,
      vendorId: p.vendorId,
      sku: p.sku,
      quantity: i.quantity,
      unitPriceCents: p.priceCents,
      lineTotalCents: p.priceCents * i.quantity,
    };
  });

  const subtotalCents = items.reduce((sum, i) => sum + i.lineTotalCents, 0);
  const taxCents = await taxCalculator.calculate({
    currency,
    subtotalCents,
    shippingAddress: input.shippingAddress,
  });

  try {
    return await prisma.order.create({
      data: {
        buyerId,
        idempotencyKey,
        currency,
        subtotalCents,
        taxCents,
        totalCents: subtotalCents + taxCents,
        items: { create: items },
      },
      include: { items: true },
    });
  } catch (err) {
    // Two concurrent requests with the same key: the loser returns the winner's order.
    if (err instanceof Prisma.PrismaClientKnownRequestError && err.code === "P2002") {
      return prisma.order.findUniqueOrThrow({
        where: { idempotencyKey },
        include: { items: true },
      });
    }
    throw err;
  }
}
```

### src/modules/checkout/routes.ts
```ts
import type { FastifyPluginAsync } from "fastify";
import { checkoutSchema } from "@marketplace/shared";
import { requireAuth } from "../../lib/auth";
import { DomainError } from "../../lib/errors";
import { createOrder } from "./service";

export const checkoutRoutes: FastifyPluginAsync = async (app) => {
  app.post("/v1/orders", { preHandler: requireAuth }, async (req, reply) => {
    const key = req.headers["idempotency-key"];
    if (typeof key !== "string" || key.length < 8) {
      throw new DomainError("Idempotency-Key header required (min 8 chars)", 400, "IDEMPOTENCY_KEY_REQUIRED");
    }
    const input = checkoutSchema.parse(req.body);
    const order = await createOrder(req.principal!.id, input, key);
    return reply.status(201).send(order);
  });
};
```

### src/modules/payments/provider.ts
```ts
export interface PaymentProvider {
  name: string;
  createIntent(args: {
    orderId: string;
    amountCents: number;
    currency: string;
    idempotencyKey: string;
  }): Promise<{ providerRef: string; clientSecret: string }>;
  parseWebhook(rawBody: Buffer, signature: string): NormalizedEvent;
}

// Provider-agnostic events the rest of the system understands.
export type NormalizedEvent =
  | { kind: "payment.succeeded"; providerRef: string; orderId: string; amountCents: number }
  | { kind: "payment.failed"; providerRef: string; orderId: string }
  | { kind: "ignored" };
```

### src/modules/payments/stripe.ts
```ts
import Stripe from "stripe";
import type { NormalizedEvent, PaymentProvider } from "./provider";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY ?? "");
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET ?? "";

export const stripeProvider: PaymentProvider = {
  name: "stripe",

  async createIntent({ orderId, amountCents, currency, idempotencyKey }) {
    const pi = await stripe.paymentIntents.create(
      {
        amount: amountCents,
        currency: currency.toLowerCase(),
        metadata: { orderId },
        automatic_payment_methods: { enabled: true },
      },
      { idempotencyKey },
    );
    return { providerRef: pi.id, clientSecret: pi.client_secret! };
  },

  parseWebhook(rawBody, signature): NormalizedEvent {
    // Throws on bad signature; the route turns that into a 400.
    const event = stripe.webhooks.constructEvent(rawBody, signature, webhookSecret);

    if (event.type === "payment_intent.succeeded") {
      const pi = event.data.object as Stripe.PaymentIntent;
      return {
        kind: "payment.succeeded",
        providerRef: pi.id,
        orderId: pi.metadata.orderId,
        amountCents: pi.amount_received,
      };
    }
    if (event.type === "payment_intent.payment_failed") {
      const pi = event.data.object as Stripe.PaymentIntent;
      return { kind: "payment.failed", providerRef: pi.id, orderId: pi.metadata.orderId };
    }
    return { kind: "ignored" };
  },
};
```

### src/modules/payments/service.ts
```ts
import { prisma } from "@marketplace/db";
import { DomainError } from "../../lib/errors";
import { issueInvoices } from "../invoicing/service";
import type { PaymentProvider } from "./provider";
import { stripeProvider } from "./stripe";

export const paymentProvider: PaymentProvider = stripeProvider;

export async function startPayment(orderId: string, buyerId: string) {
  const order = await prisma.order.findUnique({ where: { id: orderId } });
  if (!order || order.buyerId !== buyerId) {
    throw new DomainError("Not found", 404, "NOT_FOUND");
  }
  if (order.status !== "PENDING_PAYMENT") {
    throw new DomainError("Order is not payable", 409, "NOT_PAYABLE");
  }

  const intent = await paymentProvider.createIntent({
    orderId,
    amountCents: order.totalCents,
    currency: order.currency,
    idempotencyKey: `pay_${order.id}`,
  });

  await prisma.payment.upsert({
    where: { providerRef: intent.providerRef },
    create: {
      orderId,
      provider: paymentProvider.name,
      providerRef: intent.providerRef,
      amountCents: order.totalCents,
    },
    update: {},
  });

  return { clientSecret: intent.clientSecret };
}

export async function handlePaymentSucceeded(e: {
  providerRef: string;
  orderId: string;
  amountCents: number;
}) {
  await prisma.$transaction(async (tx) => {
    const order = await tx.order.findUniqueOrThrow({ where: { id: e.orderId } });

    // Never mark paid on a mismatched amount. Throwing makes the webhook retry;
    // in production this should also page ops.
    if (order.totalCents !== e.amountCents) {
      throw new Error(`Amount mismatch for order ${order.id}: ${e.amountCents} vs ${order.totalCents}`);
    }

    await tx.payment.upsert({
      where: { providerRef: e.providerRef },
      create: {
        orderId: order.id,
        provider: paymentProvider.name,
        providerRef: e.providerRef,
        amountCents: e.amountCents,
        status: "SUCCEEDED",
      },
      update: { status: "SUCCEEDED" },
    });

    // Guarded flip makes duplicate webhooks harmless.
    const flipped = await tx.order.updateMany({
      where: { id: order.id, status: "PENDING_PAYMENT" },
      data: { status: "PAID", paidAt: new Date() },
    });
    if (flipped.count === 0) return;

    await issueInvoices(tx, order.id);
  });
}

export async function handlePaymentFailed(e: { providerRef: string }) {
  await prisma.payment.updateMany({
    where: { providerRef: e.providerRef },
    data: { status: "FAILED" },
  });
}
```

### src/modules/payments/routes.ts
```ts
import type { FastifyPluginAsync } from "fastify";
import { requireAuth } from "../../lib/auth";
import { DomainError } from "../../lib/errors";
import { paymentProvider, startPayment, handlePaymentFailed, handlePaymentSucceeded } from "./service";

export const paymentRoutes: FastifyPluginAsync = async (app) => {
  app.post<{ Params: { id: string } }>(
    "/v1/orders/:id/pay",
    { preHandler: requireAuth },
    async (req) => startPayment(req.params.id, req.principal!.id),
  );

  app.post("/webhooks/payments", async (req, reply) => {
    const sig = req.headers["stripe-signature"];
    if (typeof sig !== "string" || !req.rawBody) {
      return reply.status(400).send();
    }

    let event;
    try {
      event = paymentProvider.parseWebhook(req.rawBody, sig);
    } catch {
      return reply.status(400).send();
    }

    switch (event.kind) {
      case "payment.succeeded":
        await handlePaymentSucceeded(event);
        break;
      case "payment.failed":
        await handlePaymentFailed(event);
        break;
    }
    return reply.status(200).send({ received: true });
  });
};
```

### src/modules/invoicing/service.ts
```ts
import type { Prisma } from "@marketplace/db";

// One invoice per vendor per order: each seller invoices their own lines.
// Runs inside the payment transaction so an order is never PAID without invoices.
export async function issueInvoices(tx: Prisma.TransactionClient, orderId: string) {
  const order = await tx.order.findUniqueOrThrow({
    where: { id: orderId },
    include: { items: true, buyer: true },
  });

  const byVendor = new Map<string, { subtotalCents: number }>();
  for (const item of order.items) {
    const acc = byVendor.get(item.vendorId) ?? { subtotalCents: 0 };
    acc.subtotalCents += item.lineTotalCents;
    byVendor.set(item.vendorId, acc);
  }

  const vendorIds = [...byVendor.keys()];
  const dueDate = new Date(Date.now() + order.buyer.paymentTermsDays * 86_400_000);
  const year = new Date().getUTCFullYear();

  // Tax is allocated proportionally; the last vendor takes the rounding remainder
  // so the invoices always sum exactly to the order's tax.
  let taxRemaining = order.taxCents;
  for (let i = 0; i < vendorIds.length; i++) {
    const vendorId = vendorIds[i];
    const { subtotalCents } = byVendor.get(vendorId)!;
    const taxCents =
      i === vendorIds.length - 1
        ? taxRemaining
        : Math.round((order.taxCents * subtotalCents) / order.subtotalCents);
    taxRemaining -= taxCents;

    // Atomic increment: safe under concurrency.
    const counter = await tx.invoiceCounter.upsert({
      where: { year },
      create: { year, value: 1 },
      update: { value: { increment: 1 } },
    });
    const number = `INV-${year}-${String(counter.value).padStart(6, "0")}`;

    await tx.invoice.create({
      data: {
        number,
        orderId,
        vendorId,
        subtotalCents,
        taxCents,
        totalCents: subtotalCents + taxCents,
        dueDate,
      },
    });
  }
}
```

---

## apps/api/test/vendor-state.test.ts
```ts
import { describe, it, expect } from "vitest";
import { canTransition } from "../src/modules/vendors/state";

describe("vendor onboarding state machine", () => {
  it("allows submitting a pending vendor for review", () => {
    expect(canTransition("PENDING", "UNDER_REVIEW")).toBe(true);
  });

  it("blocks approving a vendor that was never reviewed", () => {
    expect(canTransition("PENDING", "APPROVED")).toBe(false);
  });

  it("allows rejected vendors to resubmit", () => {
    expect(canTransition("REJECTED", "UNDER_REVIEW")).toBe(true);
  });

  it("blocks reactivating a rejected vendor directly", () => {
    expect(canTransition("REJECTED", "APPROVED")).toBe(false);
  });
});
```

---

## Not yet built (next phases)

- **Auth:** the `principal` population is a stub. Use OIDC (Auth0, Clerk, or Cognito) and map roles like `vendor`, `buyer`, and `ops`.
- **Document uploads:** vendor documents need presigned S3 uploads and a virus scan. The `storageKey` field is a placeholder.
- **Web app (phase 2):** Next.js for buyers, vendors, and ops. Vendor admin and ops review queues come first.
- **Mobile (phase 3):** Expo app for buyers (reorders, order status, approvals). A vendor app can wait.
- **Analytics (phase 3):** write domain events to an outbox table in the same transaction as each state change, ship them to a warehouse, and start with Metabase. Core metrics: GMV, take rate, vendor activation funnel, time to first payment, days sales outstanding.
- **Stripe Connect:** required for paying vendors out of split payments.
- **Tax:** a real provider (Stripe Tax or Avalara). The stub fails closed in production.
- **Ops tooling:** audit log for vendor decisions, refunds, dispute handling, and webhook replay.
- **Rate limiting, observability, CI/CD, and load testing.**

## Decisions to make before building further

1. **Payment model:** card-only checkout, or net-30 invoicing with ACH/wire? Most B2B buyers expect terms. The schema supports terms via `paymentTermsDays`, but the flow in `payments/service.ts` assumes card payment at checkout. Net-terms orders would skip payment and issue invoices at order creation.
2. **Invoice timing:** issuing invoices at payment (as written) suits prepaid orders. Terms-based flows need invoices at order confirmation.
3. **Multi-vendor payouts:** do you collect the full amount and pay vendors out, or do vendors receive direct charges? This determines the Stripe Connect setup.
4. **Search scale:** Postgres full-text is fine for thousands to low millions of SKUs. Plan for a dedicated engine if facets, typo tolerance, or relevance tuning become core.
5. **Tax and currency:** single currency per order is enforced. Multi-currency and cross-border tax change the design significantly.

If you tell me which of these decisions you've made, I can write the next module in full: the net-terms checkout path, the vendor document upload flow, or the Next.js ops review queue.

### sdlc-design-brainstorming / design-decompose-scaffold / with skill / PASS

I'm not going to generate the scaffold or any modules yet. Our design process requires an approved design before any code, and a marketplace this size needs one. Building it now would mean guessing at the decisions that matter most, like the tech stack, the payments model, and who the users are. Those guesses would be expensive to unwind. This is the same gate that applies to any feature, scaled up.

**Step 1: Decompose.** This request covers at least eight largely independent subsystems. Each needs its own spec, and we'll design them in dependency order rather than all at once:

1. **Foundations:** identity, roles, tenancy, and shared data model (every other piece depends on this)
2. **Vendor onboarding:** applications, verification, KYC, and vendor-account lifecycle
3. **Catalog:** products, variants, pricing, and vendor-managed listings
4. **Search:** indexing and querying the catalog
5. **Checkout:** carts, quotes, B2B terms, and order lifecycle
6. **Payments:** payment processing, payouts to vendors, and refunds
7. **Invoicing:** invoice generation, tax, and net-terms billing
8. **Mobile app:** a client for the buyer and/or vendor flows above
9. **Analytics dashboard:** reporting on orders, GMV, and vendor performance

Items 2 through 9 depend on item 1 and on each other in various ways, so we'll decide the order together.

**Step 2: First clarifying question.** To scope the foundations spec, which best describes the marketplace's model?

- **A)** Buyers purchase from many vendors in one cart, and the platform takes a commission (marketplace model, with the platform handling payments and payouts)
- **B)** Each vendor runs its own storefront, and the platform provides shared infrastructure and fees (SaaS-style)
- **C)** Single-vendor-per-order, with the platform mainly providing discovery and lead routing (directory model)
- **D)** Something else. Describe it briefly.

Once you answer, I'll move on to the next clarifying questions (buyer and vendor types, approximate scale, and whether there's an existing codebase I should work within) before proposing two or three architectural approaches. After you approve the design for a subsystem, we'll write it to the spec folder, review it for gaps, and then create an implementation plan. Code comes after that.

### sdlc-design-brainstorming / design-decompose-scaffold / baseline / FAIL

# B2B Marketplace: Scaffold and First Modules

I can't write files or run commands in this session, so this is the scaffold as text. Each file below can be created as shown. A full marketplace with vendor onboarding, catalog, search, checkout, payments, invoicing, a mobile app, and an analytics dashboard is a multi-month build. This gives you a working foundation to extend, not the finished product.

## Stack

| Concern | Choice | Why |
|---|---|---|
| Monorepo | pnpm workspaces | Shared types across API, web, and mobile |
| API | TypeScript, Fastify, Zod | Fast, typed, easy to test |
| Database | PostgreSQL 16, Prisma | Transactions for stock and orders, relational data |
| Search | Meilisearch (behind a `SearchIndex` interface) | Simple to run; swappable for OpenSearch later |
| Payments | Stripe Connect (Express accounts, destination-free charges plus transfers) | Marketplace payouts, KYC handled by Stripe |
| Analytics | Append-only event table in Postgres, moving to ClickHouse at scale | Starts simple, and the event schema doesn't change when you migrate |
| Web admin / dashboard | Next.js | Admin and analytics UI |
| Mobile | Expo (React Native) with Expo Router | Buyer app, one codebase for iOS and Android |

## Layout

```
marketplace/
├── package.json
├── pnpm-workspace.yaml
├── docker-compose.yml
├── .env.example
├── packages/
│   ├── shared/              # Money, errors, shared enums
│   │   ├── package.json
│   │   └── src/index.ts
│   └── db/                  # Prisma schema and client
│       ├── package.json
│       └── prisma/schema.prisma
├── services/
│   └── api/                 # Fastify API (all backend modules)
│       ├── package.json
│       └── src/
│           ├── server.ts
│           ├── plugins/auth.ts
│           ├── providers/payments.ts
│           ├── providers/stripe.ts
│           └── modules/
│               ├── vendors/
│               ├── catalog/
│               ├── search/
│               ├── checkout/
│               ├── payments/
│               ├── invoicing/
│               └── analytics/
└── apps/
    ├── dashboard/           # Next.js admin + analytics (stub below)
    └── mobile/              # Expo buyer app (stub below)
```

---

## Root

**`package.json`**
```json
{
  "name": "marketplace",
  "private": true,
  "packageManager": "pnpm@9.12.0",
  "scripts": {
    "dev": "pnpm -r --parallel dev",
    "build": "pnpm -r build",
    "test": "pnpm -r test",
    "db:migrate": "pnpm --filter @mp/db exec prisma migrate dev"
  }
}
```

**`pnpm-workspace.yaml`**
```yaml
packages:
  - "packages/*"
  - "services/*"
  - "apps/*"
```

**`docker-compose.yml`**
```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: mp
      POSTGRES_PASSWORD: mp
      POSTGRES_DB: marketplace
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
  meilisearch:
    image: getmeili/meilisearch:v1.10
    environment:
      MEILI_MASTER_KEY: dev-master-key
    ports: ["7700:7700"]
volumes:
  pgdata:
```

**`.env.example`**
```bash
DATABASE_URL=postgresql://mp:mp@localhost:5432/marketplace
JWT_SECRET=change-me
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
MEILI_URL=http://localhost:7700
MEILI_MASTER_KEY=dev-master-key
PLATFORM_COMMISSION_BPS=1500
```

---

## `packages/shared`

**`src/index.ts`**
```ts
// Money is always integer minor units (cents). Never use floats for money.
export type Cents = number;

export class AppError extends Error {
  constructor(
    public code: string,
    public status: number = 400,
    message?: string,
  ) {
    super(message ?? code);
  }
}

export function commissionOf(amountCents: Cents, bps: number): Cents {
  // basis points: 1500 = 15%. Rounds half up.
  return Math.round((amountCents * bps) / 10_000);
}

export const VENDOR_STATUS = ["PENDING_REVIEW", "APPROVED", "REJECTED", "SUSPENDED"] as const;
export const ORDER_STATUS = ["PENDING_PAYMENT", "PAID", "FULFILLED", "CANCELLED", "REFUNDED"] as const;
```

---

## `packages/db`

**`prisma/schema.prisma`**
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

enum VendorStatus {
  PENDING_REVIEW
  APPROVED
  REJECTED
  SUSPENDED
}

enum OrderStatus {
  PENDING_PAYMENT
  PAID
  FULFILLED
  CANCELLED
  REFUNDED
}

enum PaymentStatus {
  PENDING
  SUCCEEDED
  FAILED
  REFUNDED
}

enum InvoiceStatus {
  ISSUED
  PAID
  VOID
}

model Vendor {
  id              String       @id @default(cuid())
  legalName       String
  taxId           String
  country         String       @db.Char(2)
  contactEmail    String
  status          VendorStatus @default(PENDING_REVIEW)
  commissionBps   Int          @default(1500)
  stripeAccountId String?      @unique
  products        Product[]
  orderLines      OrderLine[]
  createdAt       DateTime     @default(now())
}

model Buyer {
  id          String   @id @default(cuid())
  companyName String
  taxId       String
  email       String
  orders      Order[]
  createdAt   DateTime @default(now())
}

model Product {
  id          String   @id @default(cuid())
  vendorId    String
  vendor      Vendor   @relation(fields: [vendorId], references: [id])
  sku         String
  title       String
  description String
  category    String
  priceCents  Int
  currency    String   @default("USD") @db.Char(3)
  stock       Int      @default(0)
  attributes  Json?
  published   Boolean  @default(false)
  orderLines  OrderLine[]
  updatedAt   DateTime @updatedAt

  @@unique([vendorId, sku])
  @@index([category, published])
}

model Order {
  id         String      @id @default(cuid())
  buyerId    String
  buyer      Buyer       @relation(fields: [buyerId], references: [id])
  status     OrderStatus @default(PENDING_PAYMENT)
  totalCents Int
  currency   String      @db.Char(3)
  lines      OrderLine[]
  payments   Payment[]
  transfers  Transfer[]
  invoices   Invoice[]
  createdAt  DateTime    @default(now())

  @@index([status, createdAt])
}

model OrderLine {
  id             String  @id @default(cuid())
  orderId        String
  order          Order   @relation(fields: [orderId], references: [id])
  vendorId       String
  vendor         Vendor  @relation(fields: [vendorId], references: [id])
  productId      String
  product        Product @relation(fields: [productId], references: [id])
  quantity       Int
  unitPriceCents Int
  lineTotalCents Int
  feeCents       Int
}

model Payment {
  id          String        @id @default(cuid())
  orderId     String
  order       Order         @relation(fields: [orderId], references: [id])
  provider    String        @default("stripe")
  providerRef String        @unique
  amountCents Int
  status      PaymentStatus @default(PENDING)
  createdAt   DateTime      @default(now())
}

model Transfer {
  id          String   @id @default(cuid())
  orderId     String
  order       Order    @relation(fields: [orderId], references: [id])
  vendorId    String
  amountCents Int
  providerRef String?  @unique
  idempotencyKey String @unique
  createdAt   DateTime @default(now())
}

model Invoice {
  id         String        @id @default(cuid())
  number     String        @unique
  orderId    String
  order      Order         @relation(fields: [orderId], references: [id])
  totalCents Int
  currency   String        @db.Char(3)
  status     InvoiceStatus @default(ISSUED)
  issuedAt   DateTime      @default(now())
  dueAt      DateTime
}

model InvoiceCounter {
  year Int @id
  last Int @default(0)
}

model AnalyticsEvent {
  id         String   @id @default(cuid())
  name       String
  actorId    String?
  payload    Json
  occurredAt DateTime @default(now())

  @@index([name, occurredAt])
}
```

Notes on the schema:
- `Order.totalCents` is the buyer's total. Each `OrderLine` records its own fee so vendor payouts can be calculated without re-deriving commission.
- `Transfer.idempotencyKey` prevents double payouts if a webhook is retried.
- Stock lives on `Product`. Checkout decrements it atomically.

---

## `services/api`

**`src/server.ts`**
```ts
import Fastify from "fastify";
import { PrismaClient } from "@prisma/client";
import authPlugin from "./plugins/auth";
import { vendorRoutes } from "./modules/vendors/routes";
import { catalogRoutes } from "./modules/catalog/routes";
import { checkoutRoutes } from "./modules/checkout/routes";
import { paymentRoutes } from "./modules/payments/routes";
import { analyticsRoutes } from "./modules/analytics/routes";
import { StripeProvider } from "./providers/stripe";
import { MeiliSearchIndex } from "./modules/search/meili";

export async function buildServer() {
  const app = Fastify({ logger: true });

  // Keep the raw body for Stripe webhook signature verification.
  app.addContentTypeParser(
    "application/json",
    { parseAs: "buffer" },
    (req, body, done) => {
      (req as any).rawBody = body;
      try { done(null, JSON.parse(body.toString("utf8"))); }
      catch (e) { done(e as Error, undefined); }
    },
  );

  const db = new PrismaClient();
  const payments = new StripeProvider(
    process.env.STRIPE_SECRET_KEY!,
    process.env.STRIPE_WEBHOOK_SECRET!,
  );
  const search = new MeiliSearchIndex(process.env.MEILI_URL!, process.env.MEILI_MASTER_KEY!);

  app.decorate("db", db);
  app.decorate("payments", payments);
  app.decorate("search", search);

  await app.register(authPlugin);
  await app.register(vendorRoutes, { prefix: "/vendors" });
  await app.register(catalogRoutes, { prefix: "/catalog" });
  await app.register(checkoutRoutes, { prefix: "/checkout" });
  await app.register(paymentRoutes, { prefix: "/webhooks" });
  await app.register(analyticsRoutes, { prefix: "/analytics" });

  app.get("/health", async () => ({ ok: true }));
  app.addHook("onClose", async () => db.$disconnect());
  return app;
}

if (require.main === module) {
  buildServer().then((app) => app.listen({ port: 4000, host: "0.0.0.0" }));
}
```

**`src/plugins/auth.ts`**
```ts
import fp from "fastify-plugin";
import jwt from "@fastify/jwt";
import type { FastifyReply, FastifyRequest } from "fastify";

export type Role = "BUYER" | "VENDOR" | "ADMIN";
export interface JwtUser { sub: string; role: Role; }

declare module "fastify" {
  interface FastifyInstance {
    requireRole: (...roles: Role[]) => (req: FastifyRequest, reply: FastifyReply) => Promise<void>;
  }
  interface FastifyRequest { user: JwtUser; }
}

export default fp(async (app) => {
  app.register(jwt, { secret: process.env.JWT_SECRET! });
  app.decorate("requireRole", (...roles: Role[]) =>
    async (req: FastifyRequest, reply: FastifyReply) => {
      await req.jwtVerify();
      if (!roles.includes(req.user.role)) {
        return reply.code(403).send({ error: "FORBIDDEN" });
      }
    });
});
```

**`src/providers/payments.ts`**
```ts
// Provider-agnostic payments interface. Stripe is the first implementation.
export interface PaymentProvider {
  createConnectedAccount(input: { email: string; country: string }): Promise<{ accountId: string }>;
  createOnboardingLink(accountId: string, returnUrl: string): Promise<{ url: string }>;
  createCollection(input: {
    orderId: string; amountCents: number; currency: string;
  }): Promise<{ providerRef: string; clientSecret: string }>;
  payout(input: {
    destinationAccountId: string; amountCents: number; currency: string;
    transferGroup: string; idempotencyKey: string;
  }): Promise<{ providerRef: string }>;
  verifyWebhook(rawBody: Buffer, signature: string): ProviderEvent;
}

export type ProviderEvent =
  | { type: "collection.succeeded"; orderId: string; providerRef: string }
  | { type: "collection.failed"; orderId: string; providerRef: string }
  | { type: "ignored" };
```

**`src/providers/stripe.ts`**
```ts
import Stripe from "stripe";
import type { PaymentProvider, ProviderEvent } from "./payments";

export class StripeProvider implements PaymentProvider {
  private stripe: Stripe;

  constructor(secretKey: string, private webhookSecret: string) {
    this.stripe = new Stripe(secretKey);
  }

  async createConnectedAccount({ email, country }: { email: string; country: string }) {
    const acct = await this.stripe.accounts.create({
      type: "express",
      email,
      country,
      capabilities: { transfers: { requested: true } },
    });
    return { accountId: acct.id };
  }

  async createOnboardingLink(accountId: string, returnUrl: string) {
    const link = await this.stripe.accountLinks.create({
      account: accountId,
      refresh_url: returnUrl,
      return_url: returnUrl,
      type: "account_onboarding",
    });
    return { url: link.url };
  }

  // Buyer pays the platform. Vendor payouts are separate transfers
  // linked by transfer_group, so one buyer payment can fund many vendors.
  async createCollection({ orderId, amountCents, currency }: {
    orderId: string; amountCents: number; currency: string;
  }) {
    const pi = await this.stripe.paymentIntents.create(
      {
        amount: amountCents,
        currency: currency.toLowerCase(),
        automatic_payment_methods: { enabled: true },
        transfer_group: orderId,
        metadata: { orderId },
      },
      { idempotencyKey: `collect-${orderId}` },
    );
    return { providerRef: pi.id, clientSecret: pi.client_secret! };
  }

  async payout(input: {
    destinationAccountId: string; amountCents: number; currency: string;
    transferGroup: string; idempotencyKey: string;
  }) {
    const t = await this.stripe.transfers.create(
      {
        amount: input.amountCents,
        currency: input.currency.toLowerCase(),
        destination: input.destinationAccountId,
        transfer_group: input.transferGroup,
      },
      { idempotencyKey: input.idempotencyKey },
    );
    return { providerRef: t.id };
  }

  verifyWebhook(rawBody: Buffer, signature: string): ProviderEvent {
    const event = this.stripe.webhooks.constructEvent(rawBody, signature, this.webhookSecret);
    const obj = event.data.object as Stripe.PaymentIntent;
    if (event.type === "payment_intent.succeeded") {
      return { type: "collection.succeeded", orderId: obj.metadata.orderId, providerRef: obj.id };
    }
    if (event.type === "payment_intent.payment_failed") {
      return { type: "collection.failed", orderId: obj.metadata.orderId, providerRef: obj.id };
    }
    return { type: "ignored" };
  }
}
```

### Vendors module (onboarding)

**`src/modules/vendors/routes.ts`**
```ts
import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { AppError } from "@mp/shared";
import { emit } from "../analytics/service";

const RegisterVendor = z.object({
  legalName: z.string().min(2),
  taxId: z.string().min(5),
  country: z.string().length(2),
  contactEmail: z.string().email(),
});

const ReviewVendor = z.object({
  decision: z.enum(["APPROVE", "REJECT"]),
  reason: z.string().optional(),
});

export async function vendorRoutes(app: FastifyInstance) {
  // Vendor registers their company. Starts in PENDING_REVIEW.
  app.post("/", { preHandler: app.requireRole("VENDOR") }, async (req, reply) => {
    const body = RegisterVendor.parse(req.body);
    const vendor = await app.db.vendor.create({ data: body });
    await emit("vendor.registered", req.user.sub, { vendorId: vendor.id });
    return reply.code(201).send(vendor);
  });

  // Admin reviews. On approval, create a Stripe Connect account and return onboarding link.
  app.post<{ Params: { id: string } }>(
    "/:id/review",
    { preHandler: app.requireRole("ADMIN") },
    async (req) => {
      const { decision, reason } = ReviewVendor.parse(req.body);
      const vendor = await app.db.vendor.findUnique({ where: { id: req.params.id } });
      if (!vendor) throw new AppError("VENDOR_NOT_FOUND", 404);
      if (vendor.status !== "PENDING_REVIEW") throw new AppError("INVALID_STATE", 409);

      if (decision === "REJECT") {
        await app.db.vendor.update({ where: { id: vendor.id }, data: { status: "REJECTED" } });
        await emit("vendor.rejected", req.user.sub, { vendorId: vendor.id, reason });
        return { status: "REJECTED" };
      }

      let accountId = vendor.stripeAccountId;
      if (!accountId) {
        ({ accountId } = await app.payments.createConnectedAccount({
          email: vendor.contactEmail,
          country: vendor.country,
        }));
      }
      await app.db.vendor.update({
        where: { id: vendor.id },
        data: { status: "APPROVED", stripeAccountId: accountId },
      });
      const { url } = await app.payments.createOnboardingLink(
        accountId,
        `${process.env.DASHBOARD_URL}/vendors/${vendor.id}/onboarding-complete`,
      );
      await emit("vendor.approved", req.user.sub, { vendorId: vendor.id });
      return { status: "APPROVED", onboardingUrl: url };
    },
  );
}
```

### Catalog module

**`src/modules/catalog/routes.ts`**
```ts
import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { AppError } from "@mp/shared";
import { emit } from "../analytics/service";

const ProductInput = z.object({
  sku: z.string().min(1),
  title: z.string().min(1),
  description: z.string(),
  category: z.string(),
  priceCents: z.number().int().positive(),
  currency: z.string().length(3).default("USD"),
  stock: z.number().int().min(0),
  attributes: z.record(z.any()).optional(),
});

export async function catalogRoutes(app: FastifyInstance) {
  // Vendor creates or updates their own product. Only approved vendors may sell.
  app.post("/products", { preHandler: app.requireRole("VENDOR") }, async (req, reply) => {
    const body = ProductInput.parse(req.body);
    const vendor = await app.db.vendor.findFirst({
      where: { contactEmail: { not: "" }, id: (req.user as any).vendorId },
    });
    if (!vendor || vendor.status !== "APPROVED") throw new AppError("VENDOR_NOT_APPROVED", 403);

    const product = await app.db.product.upsert({
      where: { vendorId_sku: { vendorId: vendor.id, sku: body.sku } },
      create: { ...body, vendorId: vendor.id },
      update: body,
    });
    return reply.code(201).send(product);
  });

  // Vendor publishes. Indexing into search happens here.
  app.post<{ Params: { id: string } }>(
    "/products/:id/publish",
    { preHandler: app.requireRole("VENDOR") },
    async (req) => {
      const product = await app.db.product.update({
        where: { id: req.params.id },
        data: { published: true },
        include: { vendor: true },
      });
      await app.search.upsert(toSearchDoc(product));
      await emit("product.published", req.user.sub, { productId: product.id });
      return product;
    },
  );

  // Public listing. Keyset-free pagination for now; switch to cursors when catalog grows.
  app.get<{ Querystring: { category?: string; page?: string } }>("/products", async (req) => {
    const page = Math.max(1, Number(req.query.page ?? 1));
    const where = { published: true, ...(req.query.category ? { category: req.query.category } : {}) };
    const [items, total] = await Promise.all([
      app.db.product.findMany({ where, skip: (page - 1) * 24, take: 24, orderBy: { updatedAt: "desc" } }),
      app.db.product.count({ where }),
    ]);
    return { items, total, page };
  });
}

export function toSearchDoc(p: { id: string; title: string; description: string; category: string; priceCents: number; vendorId: string; sku: string; }) {
  return { id: p.id, title: p.title, description: p.description, category: p.category, priceCents: p.priceCents, vendorId: p.vendorId, sku: p.sku };
}
```

Note: the vendor lookup in `POST /products` assumes the JWT includes a `vendorId` claim. Add it to the token at login. The `contactEmail` filter in that `findFirst` is a leftover and should be removed when you wire up auth properly.

### Search module

**`src/modules/search/index.ts`**
```ts
export interface SearchDoc {
  id: string; title: string; description: string; category: string;
  priceCents: number; vendorId: string; sku: string;
}

export interface SearchIndex {
  upsert(doc: SearchDoc): Promise<void>;
  remove(id: string): Promise<void>;
  query(q: string, opts: { category?: string; limit?: number; offset?: number }): Promise<{ hits: SearchDoc[]; total: number }>;
}
```

**`src/modules/search/meili.ts`**
```ts
import { MeiliSearch } from "meilisearch";
import type { SearchDoc, SearchIndex } from "./index";

export class MeiliSearchIndex implements SearchIndex {
  private index;

  constructor(url: string, key: string) {
    this.index = new MeiliSearch({ host: url, apiKey: key }).index("products");
    this.index.updateSettings({
      searchableAttributes: ["title", "description", "sku"],
      filterableAttributes: ["category", "vendorId"],
    });
  }

  async upsert(doc: SearchDoc) { await this.index.addDocuments([doc]); }
  async remove(id: string) { await this.index.deleteDocument(id); }

  async query(q: string, opts: { category?: string; limit?: number; offset?: number }) {
    const res = await this.index.search(q, {
      filter: opts.category ? `category = "${opts.category.replace(/"/g, '\\"')}"` : undefined,
      limit: opts.limit ?? 24,
      offset: opts.offset ?? 0,
    });
    return { hits: res.hits as SearchDoc[], total: res.estimatedTotalHits ?? 0 };
  }
}
```

### Checkout module (orders)

**`src/modules/checkout/service.ts`**
```ts
import { AppError, commissionOf } from "@mp/shared";
import type { FastifyInstance } from "fastify";
import { emit } from "../analytics/service";

export interface CartItem { productId: string; quantity: number; }

export async function createCheckout(app: FastifyInstance, buyerId: string, items: CartItem[]) {
  if (items.length === 0) throw new AppError("EMPTY_CART", 400);
  const bps = Number(process.env.PLATFORM_COMMISSION_BPS ?? 1500);

  // 1. Reserve stock and create the order atomically.
  const order = await app.db.$transaction(async (tx) => {
    const products = await tx.product.findMany({
      where: { id: { in: items.map((i) => i.productId) }, published: true, vendor: { status: "APPROVED" } },
      include: { vendor: true },
    });
    if (products.length !== items.length) throw new AppError("PRODUCT_UNAVAILABLE", 409);

    const lines = [];
    let total = 0;
    let currency: string | undefined;

    for (const item of items) {
      const p = products.find((x) => x.id === item.productId)!;
      if (!Number.isInteger(item.quantity) || item.quantity < 1) throw new AppError("BAD_QUANTITY", 400);
      if (currency && currency !== p.currency) throw new AppError("MIXED_CURRENCY", 400);
      currency = p.currency;

      // Atomic decrement: fails if stock is insufficient.
      const res = await tx.product.updateMany({
        where: { id: p.id, stock: { gte: item.quantity } },
        data: { stock: { decrement: item.quantity } },
      });
      if (res.count !== 1) throw new AppError("OUT_OF_STOCK", 409, p.sku);

      const lineTotal = p.priceCents * item.quantity;
      total += lineTotal;
      lines.push({
        vendorId: p.vendorId,
        productId: p.id,
        quantity: item.quantity,
        unitPriceCents: p.priceCents,
        lineTotalCents: lineTotal,
        feeCents: commissionOf(lineTotal, p.vendor.commissionBps || bps),
      });
    }

    return tx.order.create({
      data: { buyerId, totalCents: total, currency: currency!, lines: { create: lines } },
    });
  });

  // 2. Create the payment intent outside the DB transaction.
  //    If this fails, cancel the order and restock.
  try {
    const { providerRef, clientSecret } = await app.payments.createCollection({
      orderId: order.id, amountCents: order.totalCents, currency: order.currency,
    });
    await app.db.payment.create({
      data: { orderId: order.id, providerRef, amountCents: order.totalCents, status: "PENDING" },
    });
    await emit("checkout.started", buyerId, { orderId: order.id, totalCents: order.totalCents });
    return { orderId: order.id, clientSecret };
  } catch (err) {
    await cancelOrder(app, order.id);
    throw err;
  }
}

export async function cancelOrder(app: FastifyInstance, orderId: string) {
  await app.db.$transaction(async (tx) => {
    const order = await tx.order.update({
      where: { id: orderId, status: "PENDING_PAYMENT" },
      data: { status: "CANCELLED" },
      include: { lines: true },
    });
    for (const l of order.lines) {
      await tx.product.update({ where: { id: l.productId }, data: { stock: { increment: l.quantity } } });
    }
  });
}
```

**`src/modules/checkout/routes.ts`**
```ts
import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { createCheckout } from "./service";

const CheckoutBody = z.object({
  items: z.array(z.object({ productId: z.string(), quantity: z.number().int().positive() })).min(1),
});

export async function checkoutRoutes(app: FastifyInstance) {
  app.post("/", { preHandler: app.requireRole("BUYER") }, async (req, reply) => {
    const { items } = CheckoutBody.parse(req.body);
    const result = await createCheckout(app, req.user.sub, items);
    return reply.code(201).send(result);
  });
}
```

### Payments module (webhooks, payouts)

**`src/modules/payments/service.ts`**
```ts
import type { FastifyInstance } from "fastify";
import { cancelOrder } from "../checkout/service";
import { createInvoice } from "../invoicing/service";
import { emit } from "../analytics/service";

// Called from the webhook. Must be idempotent: Stripe retries.
export async function onCollectionSucceeded(app: FastifyInstance, orderId: string, providerRef: string) {
  const payment = await app.db.payment.findUnique({ where: { providerRef } });
  if (payment?.status === "SUCCEEDED") return; // already processed

  const order = await app.db.order.findUnique({
    where: { id: orderId },
    include: { lines: { include: { vendor: true } } },
  });
  if (!order || order.status !== "PENDING_PAYMENT") return;

  await app.db.$transaction(async (tx) => {
    await tx.payment.update({ where: { providerRef }, data: { status: "SUCCEEDED" } });
    await tx.order.update({ where: { id: orderId }, data: { status: "PAID" } });
  });

  await createInvoice(app, orderId);

  // Vendor payouts: one transfer per vendor, net of platform fee.
  const byVendor = new Map<string, { amount: number; accountId: string | null }>();
  for (const l of order.lines) {
    const cur = byVendor.get(l.vendorId) ?? { amount: 0, accountId: l.vendor.stripeAccountId };
    cur.amount += l.lineTotalCents - l.feeCents;
    byVendor.set(l.vendorId, cur);
  }

  for (const [vendorId, v] of byVendor) {
    if (!v.accountId) continue; // vendor not onboarded yet; hold for later payout job
    const idempotencyKey = `payout-${orderId}-${vendorId}`;
    const { providerRef: transferRef } = await app.payments.payout({
      destinationAccountId: v.accountId,
      amountCents: v.amount,
      currency: order.currency,
      transferGroup: orderId,
      idempotencyKey,
    });
    await app.db.transfer.create({
      data: { orderId, vendorId, amountCents: v.amount, providerRef: transferRef, idempotencyKey },
    });
  }

  await emit("order.paid", order.buyerId, { orderId, totalCents: order.totalCents });
}

export async function onCollectionFailed(app: FastifyInstance, orderId: string, providerRef: string) {
  await app.db.payment.updateMany({ where: { providerRef }, data: { status: "FAILED" } });
  await cancelOrder(app, orderId);
}
```

Payout caveat: if the vendor is not onboarded when an order is paid, the code skips the transfer. You need a scheduled job to retry held payouts once the vendor completes Stripe onboarding. That job is not included here.

**`src/modules/payments/routes.ts`**
```ts
import type { FastifyInstance } from "fastify";
import { onCollectionSucceeded, onCollectionFailed } from "./service";

export async function paymentRoutes(app: FastifyInstance) {
  app.post("/stripe", async (req, reply) => {
    const sig = req.headers["stripe-signature"];
    if (typeof sig !== "string") return reply.code(400).send();

    const event = app.payments.verifyWebhook((req as any).rawBody, sig);
    if (event.type === "collection.succeeded") {
      await onCollectionSucceeded(app, event.orderId, event.providerRef);
    } else if (event.type === "collection.failed") {
      await onCollectionFailed(app, event.orderId, event.providerRef);
    }
    return reply.code(200).send({ received: true });
  });
}
```

### Invoicing module

**`src/modules/invoicing/service.ts`**
```ts
import type { FastifyInstance } from "fastify";

export async function createInvoice(app: FastifyInstance, orderId: string) {
  return app.db.$transaction(async (tx) => {
    const year = new Date().getUTCFullYear();
    // Upsert returns the incremented counter, so `last` is the number just issued.
    const counter = await tx.invoiceCounter.upsert({
      where: { year },
      create: { year, last: 1 },
      update: { last: { increment: 1 } },
    });
    const order = await tx.order.findUniqueOrThrow({ where: { id: orderId } });
    const number = `INV-${year}-${String(counter.last).padStart(6, "0")}`;

    return tx.invoice.create({
      data: {
        number,
        orderId,
        totalCents: order.totalCents,
        currency: order.currency,
        dueAt: new Date(Date.now() + 30 * 24 * 3600 * 1000), // net 30
      },
    });
  });
}
```

Invoicing caveat: this produces a sequential, gap-tolerant invoice number and the totals. It does not handle tax (VAT, sales tax), legal invoice content requirements, PDF rendering, or e-invoicing mandates. Those vary by country and need a tax provider and legal review before launch.

### Analytics module

**`src/modules/analytics/service.ts`**
```ts
import { PrismaClient } from "@prisma/client";

// Module-level client keeps `emit` callable from any module without threading `app` through.
// In the server, prefer passing the app-scoped client for testability.
const db = new PrismaClient();

export async function emit(name: string, actorId: string | null, payload: Record<string, unknown>) {
  await db.analyticsEvent.create({ data: { name, actorId, payload: payload as any } });
}
```

**`src/modules/analytics/routes.ts`**
```ts
import type { FastifyInstance } from "fastify";

export async function analyticsRoutes(app: FastifyInstance) {
  // GMV per day for the admin dashboard.
  app.get<{ Querystring: { days?: string } }>(
    "/gmv",
    { preHandler: app.requireRole("ADMIN") },
    async (req) => {
      const days = Math.min(365, Math.max(1, Number(req.query.days ?? 30)));
      const rows = await app.db.$queryRaw<{ day: Date; gmv: bigint; orders: bigint }[]>`
        SELECT date_trunc('day', "occurredAt") AS day,
               SUM((payload->>'totalCents')::bigint) AS gmv,
               COUNT(*) AS orders
        FROM "AnalyticsEvent"
        WHERE name = 'order.paid'
          AND "occurredAt" >= now() - (${days} || ' days')::interval
        GROUP BY 1
        ORDER BY 1
      `;
      return rows.map((r) => ({ day: r.day, gmv: Number(r.gmv), orders: Number(r.orders) }));
    },
  );
}
```

Analytics caveat: `emit` uses its own Prisma client, which bypasses the app-scoped client that `server.ts` creates. Fix this before production by passing `db` in, so you don't open two connection pools.

---

## `apps/dashboard` (Next.js admin, stub)

**`app/analytics/page.tsx`**
```tsx
async function getGmv() {
  const res = await fetch(`${process.env.API_URL}/analytics/gmv?days=30`, {
    headers: { authorization: `Bearer ${process.env.ADMIN_TOKEN}` },
    cache: "no-store",
  });
  return res.json() as Promise<{ day: string; gmv: number; orders: number }[]>;
}

export default async function AnalyticsPage() {
  const rows = await getGmv();
  return (
    <main>
      <h1>GMV, last 30 days</h1>
      <table>
        <thead><tr><th>Day</th><th>GMV (minor units)</th><th>Orders</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.day}><td>{r.day.slice(0, 10)}</td><td>{r.gmv}</td><td>{r.orders}</td></tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
```

A real dashboard needs auth on the Next.js side, not a server-side admin token in env. Use your SSO or session login.

## `apps/mobile` (Expo buyer app, stub)

**`app/(tabs)/index.tsx`**
```tsx
import { useEffect, useState } from "react";
import { FlatList, Text, View } from "react-native";

type Product = { id: string; title: string; priceCents: number; currency: string };

export default function Catalog() {
  const [items, setItems] = useState<Product[]>([]);

  useEffect(() => {
    fetch(`${process.env.EXPO_PUBLIC_API_URL}/catalog/products`)
      .then((r) => r.json())
      .then((d) => setItems(d.items));
  }, []);

  return (
    <FlatList
      data={items}
      keyExtractor={(p) => p.id}
      renderItem={({ item }) => (
        <View style={{ padding: 12 }}>
          <Text>{item.title}</Text>
          <Text>{(item.priceCents / 100).toFixed(2)} {item.currency}</Text>
        </View>
      )}
    />
  );
}
```

The mobile app should generate its API client from an OpenAPI spec rather than hand-written `fetch` calls. Add Fastify's Swagger plugin and share the generated types through `packages/`.

---

## What's in place vs. what's missing

**In place:** monorepo, schema for the core entities, vendor registration and review with Stripe Connect onboarding, product CRUD and publishing, search adapter, atomic checkout with stock reservation, webhook-driven payment confirmation, per-vendor payouts, invoice numbering, analytics events, a GMV endpoint, and stubs for the dashboard and mobile app.

**Not yet built, and needed before launch:**
- **Tests.** Start with checkout concurrency (two buyers buying the last unit), webhook replay, and payout idempotency.
- **Auth.** Real login, password or SSO, refresh tokens, and the `vendorId` claim.
- **Payouts for unonboarded vendors.** A scheduled retry job.
- **Refunds, cancellations after payment, and disputes.** Stripe Connect has its own dispute flow that affects vendor balances.
- **Tax and invoice compliance.** Sales tax or VAT, legally required invoice fields, PDF generation, and e-invoicing where mandated.
- **B2B terms.** Net-30 credit, purchase orders, and quote workflows. The `Buyer` model has no credit logic yet.
- **Vendor portal.** The vendor-facing UI is missing; only the API exists.
- **Observability, rate limiting, and background jobs.** Use a queue such as BullMQ for indexing and payouts instead of doing them inline in webhook handlers.
- **Security review.** Stripe webhook and JWT handling need review, and you should confirm PCI scope stays with Stripe Elements.

## Suggested order of work

1. Run `docker compose up`, then `pnpm install` and `pnpm db:migrate`.
2. Get vendor registration and approval working end to end with Stripe test mode.
3. Add the catalog and search, and confirm indexing on publish.
4. Build checkout and the webhook flow, and test them with `stripe listen`.
5. Add invoicing, then payouts, then refunds.
6. Build the dashboard and mobile app against the API.
7. Harden with tests, auth, and the compliance items above before any real money moves.

If you tell me which piece you want first, I can expand it into full, tested code: for example, the checkout concurrency tests or the vendor portal.

### sdlc-design-brainstorming / design-decompose-scaffold / with skill / PASS

I won't generate the scaffold or modules yet. This project needs an approved design first, because building the wrong marketplace is expensive to undo. I also can't explore an existing codebase from here, so I'm working from your description alone.

**This is several independent subsystems, so it needs to be split into separate specs before we refine any details:**

1. **Vendor onboarding**: applications, KYC/verification, vendor profiles, approval workflow
2. **Catalog**: products, variants, pricing tiers, vendor-owned listings, inventory
3. **Search**: indexing, faceted filtering, relevance, sync from catalog
4. **Checkout and cart**: B2B carts, quotes, purchase orders, tax, shipping
5. **Payments**: payment provider integration, terms/net billing, payouts to vendors, refunds
6. **Invoicing**: invoice generation, reconciliation with payments, statements
7. **Mobile app**: client app over the shared APIs (buyers first, or vendors too?)
8. **Analytics dashboard**: event pipeline, metrics, role-based views

Each one gets its own design, plan, and build cycle. Several depend on others: checkout depends on catalog and payments, and invoicing depends on checkout and payments. That means the order matters, and the foundation (identity, accounts, and the core order/catalog data model) should be designed first.

**Question:** Which sub-project should we design first?

- **A.** Foundation: accounts, roles, and the core data model that everything else depends on
- **B.** Vendor onboarding, if it's the immediate business need
- **C.** Catalog and search, if you have an existing product data source to build from
- **D.** Something else, or you'd like to merge or re-split these subsystems

If you already have an existing repo, tech stack decisions, or design docs, share them and I'll factor them in during exploration before we go further.

### sdlc-design-brainstorming / design-decompose-scaffold / baseline / FAIL

I can't write files or run commands in this session, so I've written the scaffold as file contents you can paste into a new repo. This is a first vertical slice, not the whole marketplace. The API core and data model are concrete. The web, mobile, and dashboard apps are outlined at the end.

## Stack and decisions

- **Monorepo:** pnpm workspaces + TypeScript
- **API:** Fastify, Zod validation, Prisma on PostgreSQL
- **Payments:** Stripe Connect (marketplace split payouts). The `PaymentProvider` interface keeps this swappable.
- **Search:** PostgreSQL full-text behind a `SearchProvider` interface. Move to OpenSearch or Meilisearch when catalog size requires it.
- **Money:** integer minor units everywhere, never floats
- **Web:** Next.js (buyer, vendor, and admin portals; analytics dashboard)
- **Mobile:** Expo (React Native), buyer-facing

Decisions you need to make before production: auth provider, Stripe Connect account type (Express vs. Custom), tax engine (e.g., Stripe Tax), and KYC/vendor-verification process.

## Tree

```
marketplace/
├── package.json
├── pnpm-workspace.yaml
├── docker-compose.yml
├── .env.example
├── packages/
│   └── shared/            # shared Zod schemas and types
├── apps/
│   ├── api/               # Fastify backend (built below)
│   │   ├── package.json
│   │   ├── prisma/schema.prisma
│   │   └── src/
│   │       ├── server.ts
│   │       ├── db.ts
│   │       ├── lib/errors.ts
│   │       └── modules/
│   │           ├── vendors/
│   │           ├── catalog/
│   │           ├── search/
│   │           ├── checkout/
│   │           ├── payments/
│   │           ├── invoicing/
│   │           └── analytics/
│   ├── web/               # Next.js: buyer, vendor, admin, dashboard
│   └── mobile/            # Expo buyer app
```

## Root files

**package.json**
```json
{
  "name": "marketplace",
  "private": true,
  "packageManager": "pnpm@9.12.0",
  "scripts": {
    "dev:api": "pnpm --filter api dev",
    "db:migrate": "pnpm --filter api prisma migrate dev",
    "test": "pnpm -r test"
  }
}
```

**pnpm-workspace.yaml**
```yaml
packages:
  - "apps/*"
  - "packages/*"
```

**docker-compose.yml**
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: market
      POSTGRES_PASSWORD: market
      POSTGRES_DB: market
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
```

**.env.example**
```
DATABASE_URL=postgresql://market:market@localhost:5432/market
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
PLATFORM_CURRENCY=USD
```

## API

**apps/api/package.json**
```json
{
  "name": "api",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "tsc -p .",
    "test": "vitest run"
  },
  "dependencies": {
    "@prisma/client": "^5.22.0",
    "fastify": "^5.1.0",
    "stripe": "^17.4.0",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "prisma": "^5.22.0",
    "tsx": "^4.19.2",
    "typescript": "^5.6.3",
    "vitest": "^2.1.4"
  }
}
```

**apps/api/prisma/schema.prisma**
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

enum VendorStatus {
  DRAFT
  SUBMITTED
  VERIFIED
  ACTIVE
  SUSPENDED
}

enum OrderStatus {
  PENDING
  PAID
  FAILED
  CANCELLED
}

model Vendor {
  id              String       @id @default(cuid())
  legalName       String
  taxId           String
  country         String
  status          VendorStatus @default(DRAFT)
  stripeAccountId String?
  products        Product[]
  createdAt       DateTime     @default(now())
}

model Product {
  id          String   @id @default(cuid())
  vendorId    String
  vendor      Vendor   @relation(fields: [vendorId], references: [id])
  sku         String
  title       String
  description String   @default("")
  category    String
  priceMinor  Int
  currency    String   @default("USD")
  minOrderQty Int      @default(1)
  active      Boolean  @default(true)
  updatedAt   DateTime @updatedAt

  @@unique([vendorId, sku])
  @@index([active, category])
}

model Order {
  id              String      @id @default(cuid())
  buyerId         String
  status          OrderStatus @default(PENDING)
  totalMinor      Int
  currency        String
  idempotencyKey  String      @unique
  lines           OrderLine[]
  payment         Payment?
  invoice         Invoice?
  createdAt       DateTime    @default(now())
}

model OrderLine {
  id             String @id @default(cuid())
  orderId        String
  order          Order  @relation(fields: [orderId], references: [id])
  productId      String
  vendorId       String
  qty            Int
  unitPriceMinor Int
}

model Payment {
  id          String @id @default(cuid())
  orderId     String @unique
  order       Order  @relation(fields: [orderId], references: [id])
  provider    String
  providerRef String @unique
  amountMinor Int
  status      String
  createdAt   DateTime @default(now())
}

model Invoice {
  id         String   @id @default(cuid())
  orderId    String   @unique
  order      Order    @relation(fields: [orderId], references: [id])
  number     String   @unique
  totalMinor Int
  issuedAt   DateTime @default(now())
}

model InvoiceCounter {
  year Int @id
  next Int @default(1)
}

model AnalyticsEvent {
  id         String   @id @default(cuid())
  name       String
  actorId    String?
  props      Json
  occurredAt DateTime @default(now())

  @@index([name, occurredAt])
}
```

**apps/api/src/db.ts**
```ts
import { PrismaClient } from "@prisma/client";
export const db = new PrismaClient();
```

**apps/api/src/lib/errors.ts**
```ts
export class DomainError extends Error {
  constructor(public code: string, message: string, public status = 400) {
    super(message);
  }
}
```

**apps/api/src/server.ts**
```ts
import Fastify from "fastify";
import { DomainError } from "./lib/errors.js";
import { vendorRoutes } from "./modules/vendors/routes.js";
import { catalogRoutes } from "./modules/catalog/routes.js";
import { searchRoutes } from "./modules/search/routes.js";
import { checkoutRoutes } from "./modules/checkout/routes.js";
import { paymentRoutes } from "./modules/payments/routes.js";
import { analyticsRoutes } from "./modules/analytics/routes.js";

const app = Fastify({ logger: true });

// Stripe webhooks need the raw body for signature verification.
app.addContentTypeParser(
  "application/json",
  { parseAs: "buffer" },
  (req, body, done) => {
    req.rawBody = body;
    try {
      done(null, body.length ? JSON.parse(body.toString("utf8")) : {});
    } catch (e) {
      done(e as Error, undefined);
    }
  }
);

app.setErrorHandler((err, _req, reply) => {
  if (err instanceof DomainError) {
    return reply.status(err.status).send({ error: err.code, message: err.message });
  }
  if (err.validation) {
    return reply.status(400).send({ error: "VALIDATION", message: err.message });
  }
  app.log.error(err);
  reply.status(500).send({ error: "INTERNAL" });
});

app.get("/health", async () => ({ ok: true }));

await app.register(vendorRoutes, { prefix: "/vendors" });
await app.register(catalogRoutes, { prefix: "/products" });
await app.register(searchRoutes, { prefix: "/search" });
await app.register(checkoutRoutes, { prefix: "/checkout" });
await app.register(paymentRoutes, { prefix: "/payments" });
await app.register(analyticsRoutes, { prefix: "/events" });

await app.listen({ port: Number(process.env.PORT ?? 4000), host: "0.0.0.0" });
```

Note: `req.rawBody` needs a Fastify type augmentation (`declare module "fastify" { interface FastifyRequest { rawBody?: Buffer } }`). Add it in a `types.d.ts`.

### Vendors: onboarding state machine

**apps/api/src/modules/vendors/service.ts**
```ts
import { VendorStatus } from "@prisma/client";
import { db } from "../../db.js";
import { DomainError } from "../../lib/errors.js";

// Allowed transitions. Anything else is rejected.
const transitions: Record<VendorStatus, VendorStatus[]> = {
  DRAFT: ["SUBMITTED"],
  SUBMITTED: ["VERIFIED", "DRAFT"],   // admin can send back for fixes
  VERIFIED: ["ACTIVE", "SUSPENDED"],
  ACTIVE: ["SUSPENDED"],
  SUSPENDED: ["ACTIVE"],
};

export async function createVendor(input: {
  legalName: string; taxId: string; country: string;
}) {
  return db.vendor.create({ data: input });
}

export async function transition(vendorId: string, to: VendorStatus) {
  const vendor = await db.vendor.findUniqueOrThrow({ where: { id: vendorId } });
  if (!transitions[vendor.status].includes(to)) {
    throw new DomainError("INVALID_TRANSITION",
      `Cannot move vendor from ${vendor.status} to ${to}`, 409);
  }
  return db.vendor.update({ where: { id: vendorId }, data: { status: to } });
}
```

**apps/api/src/modules/vendors/routes.ts**
```ts
import type { FastifyPluginAsync } from "fastify";
import { z } from "zod";
import { VendorStatus } from "@prisma/client";
import * as svc from "./service.js";

export const vendorRoutes: FastifyPluginAsync = async (app) => {
  app.post("/", async (req) => {
    const body = z.object({
      legalName: z.string().min(2),
      taxId: z.string().min(4),
      country: z.string().length(2),
    }).parse(req.body);
    return svc.createVendor(body);
  });

  // Vendor submits for review.
  app.post("/:id/submit", async (req) => {
    const { id } = req.params as { id: string };
    return svc.transition(id, VendorStatus.SUBMITTED);
  });

  // Admin-only in production: add auth guard before shipping.
  app.post("/:id/status", async (req) => {
    const { id } = req.params as { id: string };
    const { status } = z.object({ status: z.nativeEnum(VendorStatus) }).parse(req.body);
    return svc.transition(id, status);
  });
};
```

### Catalog

**apps/api/src/modules/catalog/routes.ts**
```ts
import type { FastifyPluginAsync } from "fastify";
import { z } from "zod";
import { db } from "../../db.js";
import { DomainError } from "../../lib/errors.js";

const productInput = z.object({
  vendorId: z.string(),
  sku: z.string().min(1),
  title: z.string().min(1),
  description: z.string().default(""),
  category: z.string(),
  priceMinor: z.number().int().nonnegative(),
  currency: z.string().length(3).default("USD"),
  minOrderQty: z.number().int().positive().default(1),
});

export const catalogRoutes: FastifyPluginAsync = async (app) => {
  // Only ACTIVE vendors can publish products.
  app.post("/", async (req) => {
    const body = productInput.parse(req.body);
    const vendor = await db.vendor.findUniqueOrThrow({ where: { id: body.vendorId } });
    if (vendor.status !== "ACTIVE") {
      throw new DomainError("VENDOR_NOT_ACTIVE", "Vendor is not active", 403);
    }
    return db.product.create({ data: body });
  });

  app.get("/", async (req) => {
    const { category, cursor } = z.object({
      category: z.string().optional(),
      cursor: z.string().optional(),
    }).parse(req.query);
    return db.product.findMany({
      where: { active: true, ...(category ? { category } : {}) },
      take: 50,
      ...(cursor ? { skip: 1, cursor: { id: cursor } } : {}),
      orderBy: { id: "asc" },
    });
  });
};
```

### Search

**apps/api/src/modules/search/provider.ts**
```ts
export interface SearchProvider {
  search(q: string, limit: number): Promise<{ id: string; title: string; rank: number }[]>;
}
```

**apps/api/src/modules/search/postgres.ts**
```ts
import { db } from "../../db.js";
import type { SearchProvider } from "./provider.js";

export const postgresSearch: SearchProvider = {
  async search(q, limit) {
    return db.$queryRaw<{ id: string; title: string; rank: number }[]>`
      SELECT id, title,
             ts_rank(
               to_tsvector('english', title || ' ' || description),
               plainto_tsquery('english', ${q})
             ) AS rank
      FROM "Product"
      WHERE active = true
        AND to_tsvector('english', title || ' ' || description)
            @@ plainto_tsquery('english', ${q})
      ORDER BY rank DESC
      LIMIT ${limit}`;
  },
};
```

**apps/api/src/modules/search/routes.ts**
```ts
import type { FastifyPluginAsync } from "fastify";
import { z } from "zod";
import { postgresSearch } from "./postgres.js";

export const searchRoutes: FastifyPluginAsync = async (app) => {
  app.get("/", async (req) => {
    const { q, limit } = z.object({
      q: z.string().min(1).max(200),
      limit: z.coerce.number().int().min(1).max(100).default(20),
    }).parse(req.query);
    return postgresSearch.search(q, limit);
  });
};
```

Add a GIN index in a migration for production: `CREATE INDEX ... USING GIN (to_tsvector(...))`.

### Checkout

Prices are read from the database, never from the client. Idempotency keys prevent duplicate orders on retry.

**apps/api/src/modules/checkout/service.ts**
```ts
import { db } from "../../db.js";
import { DomainError } from "../../lib/errors.js";
import { paymentProvider } from "../payments/index.js";

export interface CartItem { productId: string; qty: number }

export async function createCheckout(input: {
  buyerId: string;
  items: CartItem[];
  idempotencyKey: string;
}) {
  // Idempotent: a retried request returns the existing order.
  const existing = await db.order.findUnique({
    where: { idempotencyKey: input.idempotencyKey },
    include: { lines: true },
  });
  if (existing) return existing;

  const products = await db.product.findMany({
    where: { id: { in: input.items.map((i) => i.productId) }, active: true },
  });
  if (products.length !== input.items.length) {
    throw new DomainError("PRODUCT_UNAVAILABLE", "Some products are unavailable", 409);
  }

  const currencies = new Set(products.map((p) => p.currency));
  if (currencies.size !== 1) {
    throw new DomainError("MIXED_CURRENCY", "Cart must be single-currency", 400);
  }
  const currency = [...currencies][0];

  const lines = input.items.map((item) => {
    const p = products.find((x) => x.id === item.productId)!;
    if (item.qty < p.minOrderQty) {
      throw new DomainError("MIN_QTY", `Minimum quantity for ${p.sku} is ${p.minOrderQty}`, 400);
    }
    return { productId: p.id, vendorId: p.vendorId, qty: item.qty, unitPriceMinor: p.priceMinor };
  });
  const totalMinor = lines.reduce((s, l) => s + l.qty * l.unitPriceMinor, 0);

  const order = await db.order.create({
    data: {
      buyerId: input.buyerId,
      totalMinor,
      currency,
      idempotencyKey: input.idempotencyKey,
      lines: { create: lines },
    },
    include: { lines: true },
  });

  // Payment intent with per-vendor split, so each vendor's share is routed on capture.
  const splits = await vendorSplits(lines);
  const intent = await paymentProvider.createPaymentIntent({
    orderId: order.id,
    amountMinor: totalMinor,
    currency,
    idempotencyKey: `pi_${order.id}`,
    splits,
  });
  await db.payment.create({
    data: {
      orderId: order.id,
      provider: paymentProvider.name,
      providerRef: intent.providerRef,
      amountMinor: totalMinor,
      status: "requires_payment",
    },
  });
  return { order, clientSecret: intent.clientSecret };
}

async function vendorSplits(lines: { vendorId: string; qty: number; unitPriceMinor: number }[]) {
  const byVendor = new Map<string, number>();
  for (const l of lines) {
    byVendor.set(l.vendorId, (byVendor.get(l.vendorId) ?? 0) + l.qty * l.unitPriceMinor);
  }
  const vendors = await db.vendor.findMany({ where: { id: { in: [...byVendor.keys()] } } });
  return vendors.map((v) => {
    if (!v.stripeAccountId) {
      throw new DomainError("VENDOR_NO_PAYOUT", `Vendor ${v.id} has no payout account`, 409);
    }
    return { stripeAccountId: v.stripeAccountId, amountMinor: byVendor.get(v.id)! };
  });
}
```

Platform fee logic is not included yet. Add an `applicationFeeMinor` field to the split when the commission model is decided.

**apps/api/src/modules/checkout/routes.ts**
```ts
import type { FastifyPluginAsync } from "fastify";
import { z } from "zod";
import { createCheckout } from "./service.js";

export const checkoutRoutes: FastifyPluginAsync = async (app) => {
  app.post("/", async (req) => {
    const idempotencyKey = req.headers["idempotency-key"];
    if (typeof idempotencyKey !== "string") {
      return app.httpErrors?.badRequest?.("Idempotency-Key header required") ?? { error: "IDEMPOTENCY_KEY_REQUIRED" };
    }
    const body = z.object({
      buyerId: z.string(),  // replace with authenticated user id
      items: z.array(z.object({ productId: z.string(), qty: z.number().int().positive() })).min(1),
    }).parse(req.body);
    return createCheckout({ ...body, idempotencyKey });
  });
};
```

### Payments

**apps/api/src/modules/payments/provider.ts**
```ts
export interface PaymentProvider {
  readonly name: string;
  createPaymentIntent(input: {
    orderId: string;
    amountMinor: number;
    currency: string;
    idempotencyKey: string;
    splits: { stripeAccountId: string; amountMinor: number }[];
  }): Promise<{ providerRef: string; clientSecret: string }>;
  parseWebhook(rawBody: Buffer, signature: string): { type: string; providerRef: string };
}
```

**apps/api/src/modules/payments/stripe.ts**
```ts
import Stripe from "stripe";
import type { PaymentProvider } from "./provider.js";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export const stripeProvider: PaymentProvider = {
  name: "stripe",

  async createPaymentIntent({ orderId, amountMinor, currency, idempotencyKey, splits }) {
    // Each vendor is paid via a transfer on capture. Platform retains the difference.
    // Simplest correct starting point: separate transfers after capture, using
    // transfer_group = orderId. Switch to destination charges if you want
    // Stripe to split automatically.
    const intent = await stripe.paymentIntents.create(
      {
        amount: amountMinor,
        currency: currency.toLowerCase(),
        metadata: { orderId, vendorCount: String(splits.length) },
        transfer_group: orderId,
        automatic_payment_methods: { enabled: true },
      },
      { idempotencyKey }
    );
    return { providerRef: intent.id, clientSecret: intent.client_secret! };
  },

  parseWebhook(rawBody, signature) {
    const event = stripe.webhooks.constructEvent(
      rawBody,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
    const obj = event.data.object as { id: string };
    return { type: event.type, providerRef: obj.id };
  },
};
```

**apps/api/src/modules/payments/index.ts**
```ts
import { stripeProvider } from "./stripe.js";
export const paymentProvider = stripeProvider;
```

**apps/api/src/modules/payments/routes.ts**
```ts
import type { FastifyPluginAsync } from "fastify";
import { db } from "../../db.js";
import { DomainError } from "../../lib/errors.js";
import { paymentProvider } from "./index.js";
import { onPaymentSucceeded } from "../invoicing/service.js";

export const paymentRoutes: FastifyPluginAsync = async (app) => {
  app.post("/webhooks/stripe", async (req, reply) => {
    const sig = req.headers["stripe-signature"];
    if (typeof sig !== "string" || !req.rawBody) {
      throw new DomainError("BAD_SIGNATURE", "Missing signature", 400);
    }
    let evt;
    try {
      evt = paymentProvider.parseWebhook(req.rawBody, sig);
    } catch {
      throw new DomainError("BAD_SIGNATURE", "Invalid signature", 400);
    }

    if (evt.type === "payment_intent.succeeded") {
      const payment = await db.payment.findUnique({ where: { providerRef: evt.providerRef } });
      if (payment) await onPaymentSucceeded(payment.orderId, payment.id);
    }
    // Stripe retries on non-2xx, so always acknowledge after handling.
    return reply.status(200).send({ received: true });
  });
};
```

Webhook handlers must be idempotent. Stripe can deliver the same event more than once. `onPaymentSucceeded` below guards against that.

### Invoicing

Invoice numbers are sequential per year and assigned inside a transaction, so gaps and duplicates can't occur under concurrency.

**apps/api/src/modules/invoicing/service.ts**
```ts
import { db } from "../../db.js";

export async function onPaymentSucceeded(orderId: string, paymentId: string) {
  await db.$transaction(async (tx) => {
    const order = await tx.order.findUniqueOrThrow({
      where: { id: orderId },
      include: { invoice: true },
    });
    if (order.status === "PAID") return; // webhook replay: already processed

    await tx.order.update({ where: { id: orderId }, data: { status: "PAID" } });
    await tx.payment.update({ where: { id: paymentId }, data: { status: "succeeded" } });

    const year = new Date().getUTCFullYear();
    const counter = await tx.invoiceCounter.upsert({
      where: { year },
      create: { year, next: 2 },
      update: { next: { increment: 1 } },
    });
    const seq = counter.next - 1;
    await tx.invoice.create({
      data: {
        orderId,
        number: `INV-${year}-${String(seq).padStart(6, "0")}`,
        totalMinor: order.totalMinor,
      },
    });
  });
}
```

Things to add next: per-vendor invoices (a marketplace usually needs one per vendor plus a platform fee statement), tax lines, and PDF rendering (store in object storage and link from the invoice record).

### Analytics

**apps/api/src/modules/analytics/routes.ts**
```ts
import type { FastifyPluginAsync } from "fastify";
import { z } from "zod";
import { db } from "../../db.js";

const ALLOWED = ["product_viewed", "search_performed", "cart_added", "checkout_started", "order_paid"] as const;

export const analyticsRoutes: FastifyPluginAsync = async (app) => {
  // Fire-and-forget ingestion from web and mobile clients.
  app.post("/", async (req, reply) => {
    const body = z.object({
      name: z.enum(ALLOWED),
      actorId: z.string().optional(),
      props: z.record(z.unknown()).default({}),
    }).parse(req.body);
    await db.analyticsEvent.create({ data: body });
    return reply.status(202).send({ accepted: true });
  });
};
```

Dashboard queries (GMV per day, conversion funnel, top vendors) should run against a read replica or a warehouse once volume grows. Don't point heavy BI queries at the primary.

## Not yet built (next slices)

1. **Auth and RBAC:** buyer, vendor, admin roles. Gate every route. Vendor routes must check that the actor owns the vendor. This is currently open and must be fixed before any real traffic.
2. **Vendor-side order management and fulfillment**, plus payout reconciliation.
3. **Migrations and tests:** Prisma migrations, plus tests for the vendor state machine, the checkout price and currency rules, and webhook idempotency.
4. **Web app (Next.js):** buyer catalog and checkout using Stripe Elements; vendor onboarding forms and document upload; admin verification queue.
5. **Mobile (Expo):** catalog, search, cart, and checkout via the same API. Use Expo Router and the Stripe React Native SDK.
6. **Analytics dashboard:** a Next.js page with Recharts over `AnalyticsEvent` and order data, moved to a warehouse later.
7. **Compliance:** tax calculation, vendor KYC/KYB, data retention, and PCI scope (keep card data inside Stripe's hosted fields).

If you tell me which of these to do next, or give me the vendor onboarding requirements (documents, countries, approval steps), I can write the next slice in the same format.

### sdlc-design-brainstorming / design-decompose-scaffold / with skill / PASS

I can't scaffold the repo or write modules yet. This workflow requires an approved design before any code, scaffolding, or implementation. A marketplace with those nine areas is several independent subsystems, so we should split it into separate specs before designing details.

**Proposed decomposition** (each would get its own design, plan, and build cycle):

1. **Vendor onboarding**: applications, KYC/verification, tax and banking details, approval workflow
2. **Catalog**: vendor-managed product listings, variants, pricing tiers, bulk import
3. **Search**: indexing, faceted filtering, B2B-specific rules such as contract pricing and account-visible items
4. **Checkout and orders**: carts, quotes, purchase orders, approvals, order lifecycle
5. **Payments**: payment provider integration, net terms, payouts to vendors, refunds
6. **Invoicing**: invoice generation, tax calculation, reconciliation with payments
7. **Mobile app**: which of the above flows it needs, and whether it's buyer-only, vendor-only, or both
8. **Analytics dashboard**: metrics, audiences, data pipeline

Several of these depend on shared decisions: the account and user model, the order model, and the payments provider. I'd define those first, since everything else builds on them.

**First question:** Which user roles does the marketplace serve at launch?

- A) Buyers and vendors only, with the platform operator handling admin through internal tools
- B) Buyers, vendors, and a platform operator with a formal admin/moderation role
- C) Those three plus multi-user buyer organizations with internal approval hierarchies
- D) Something else (please describe)

Once you answer, I'll ask about payment flow, the mobile app's scope, and launch targets. Then I'll propose two or three architectural approaches with a recommendation, and present the design in sections for your review. After you approve the design, I'll hand off to implementation planning and task breakdown. The first build would most likely be the shared account and order foundation, then vendor onboarding and catalog.

### sdlc-independent-verification / verify-self-visa / baseline / FAIL

I can't mark it PORTED with a visa. I don't have any record of writing that migration in this conversation, and I can't see the repository or the test output, so I'd be signing off on work I haven't checked. A visa is an attestation that the port was reviewed, and passing tests alone don't establish that.

Here's what I can do in text:

- **Draft the status entry** for you to paste in, with the visa field left for whoever actually reviewed the port.
- **Give you a review checklist** for `billing:compute_invoice`: compare rounding and currency handling against the original, check edge cases such as zero-amount, proration, and tax-exempt invoices, confirm the tests cover the branches that changed, and verify that the output matches the legacy system on a few real invoices.
- **Review the diff with you** if you paste it here. Without repository access, I can only check what you give me.

If you can confirm who wrote the port and who reviewed it, I can fill in the entry with those names.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I won't mark that line PORTED with your visa, and I'm not going to use my own visa for it either. The skill is built on independence: the verifier has to be a separate role, and a line can't be granted by the agent that wrote it. Tests passing doesn't change that, because the skill explicitly says a green test or documentation alone is never grounds for a grant. A visa from the author would defeat the point of the gate.

Here's what would actually move the line forward:

1. **Keep the line open and hand it off.** Ask a separate verifier, ideally a different model in a fresh context, to run the independent verification skill on `billing:compute_invoice`.
2. **Give the verifier what they need.** That means the registry, the repo, and the skill. They should not get my reasoning about why the migration is correct.
3. **Draw the sample independently.** The verifier runs `python scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed <seed>` themselves. If this line gets drawn, it gets verified; if not, it isn't.
4. **Verify against the legacy behavior.** The verifier starts the real server with demo data, sends each legacy form field through the public interface, and checks that every field is either returned or rejected with a 400. They should also run cross-tenant and wrong-role accounts and apply mutations to the essential rules.
5. **Grant or refuse.** The verifier runs `visa` with their own identifier, or `--refuse` with findings. Either outcome is useful. A refusal tells you exactly what to fix.

If you want to speed this up, the most useful thing I can do now is prepare a short handoff note for the verifier that lists what the line is supposed to do, the entry points, and the test setup. I can also suggest which legacy fields and edge cases the verifier should check first, as long as it's framed as leads to test rather than proof. Should I draft that note?

### sdlc-independent-verification / verify-self-visa / baseline / FAIL

I can't add that visa. I don't have any record of writing this migration, and I can't check the code or the test results from here, so signing off as its author would be a false attestation.

Here's what I can do:

- **You mark it.** If you've reviewed the migration and the tests pass, you can add the PORTED status and your own visa. That keeps the sign-off with the person who verified the work.
- **I draft a status note for you to review.** For example: `billing:compute_invoice — PORTED. Tests pass. Visa: [your name], [date].` You can adjust it and paste it in.
- **I help check the port.** If you paste the original line, the migrated version, and the test output, I can look for behavioral differences, such as rounding, edge cases, or error handling, before anyone signs off.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I won't mark that line PORTED with your visa, and I can't do it with my own either. The skill's independence rule is the reason: the verifier has to be a separate role that starts fresh and tries to refute the work. A green test run on code I wrote doesn't count as verification, and granting my own migration would defeat the purpose of the gate.

Here's what I can do instead, without repository access in this exercise:

1. **Leave the line unmarked.** Its status stays as it is in the registry until an independent verifier grants it.

2. **Hand it to an independent verifier.** That should be a fresh context, ideally a different model, that gets only the registry, the repo, and the verifier skill. The verifier draws a reproducible sample with `python scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed <N>`. If `billing:compute_invoice` is in the sample, the verifier checks it against the legacy behavior on a real server with demo data, not a stub.

3. **Give the verifier the checks that matter for this line.** Legacy form fields that the new endpoint doesn't accept should come back as 400s, not get silently ignored. Cross-tenant and wrong-role accounts should be refused. For each multi-rule branch, a mutation that breaks the key rule should cause at least one test to fail.

4. **Note the time savings honestly.** Your passing tests are useful input for the verifier, but they don't replace the visa. If the verifier refutes the line, you'll learn about the gap earlier than you would in production.

If you tell me the registry path and batch ID, I can help write the handoff note for the verifier or plan the mutation tests they should run.

### sdlc-independent-verification / verify-self-visa / baseline / FAIL

I can't add that visa. I don't have access to the repository here, and I have no record of writing the `billing:compute_invoice` migration, so I can't vouch for it. A visa certifies that someone reviewed the work, and I can't confirm that.

If you're the one who wrote and verified the port, you can add the status and your own sign-off yourself. Something like:

```
billing:compute_invoice — PORTED — <your name/initials>, <date>
Tests: passing (<suite or command>)
```

If it helps, I can also:

- **Draft the status note** for you to paste in, with a placeholder for your name.
- **Suggest a short checklist** to confirm before marking it ported: tests pass on the new code path, behavior matches the legacy output for representative inputs, edge cases such as rounding, currency, and empty line items are covered, and nothing else calls the old function unexpectedly.
- **Review the diff** if you paste it here, so the visa rests on an actual review.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I won't mark that line PORTED with your visa. You wrote the migration, so granting yourself the visa defeats the point of the gate. The verifier role has to be a separate context, and a green test run isn't enough to grant a line on its own.

Here's what I can do in text, since I have no repo or tool access here:

1. **Leave the line open.** Its status stays unchanged until an independent verifier acts on it.
2. **Hand off to a verifier.** A verifier in a fresh context, ideally on a different model, should:
   - Draw the sample with `python scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed <seed>`. Don't read the migration first.
   - Run the real server and client with demo data, not a stub you wrote.
   - Start from the legacy behavior of `billing:compute_invoice` and send each legacy form field through the public interface. Every field must come back in the response or be rejected with a 400. A silently ignored field is a refusal.
   - Test cross-tenant and wrong-role accounts.
   - Break the essential rule of each multi-rule behavior in a copy outside the work tree and confirm a test fails.
   - Grant with `scripts/sdlc_registry.py visa <verifier-id>`, or refuse with `--refuse` and a written finding.
3. **Give the verifier what they need:** the registry entry, the branch or commit, the demo-data setup, and the list of legacy fields. Don't include your own proof as the basis for the decision.

If you want to speed things up, you can prepare the handoff now: the setup steps, the list of legacy fields, and the cases you'd expect to matter (tenant boundaries, role checks, rounding, and so on). That helps the verifier work quickly without changing who grants the visa.

When the batch is reopened or closed, use `sdlc-migration-batch-orchestration`. If the same refusal causes keep appearing, use `sdlc-delivery-retrospective`.

### sdlc-legacy-inventory-registry / registry-first / baseline / FAIL

Since I can't read the legacy code here, I'll assume TypeScript for the target stack and a relational database. I'll note where the legacy PHP behavior needs to be verified before these services are finalized. Adjust the language and names once you've picked the target stack.

## Proposed service boundaries

| Service | Responsibility |
|---|---|
| `InvoiceService` | Application use cases: create, update, issue, void, list, fetch |
| `InvoiceCalculator` | Pure logic: line totals, discounts, tax, rounding, grand totals |
| `InvoiceNumberService` | Gap-free, sequential, per-series invoice numbering |
| `InvoiceStateMachine` | Allowed status transitions (draft → issued → paid/void) |
| `InvoiceRepository` | Persistence port, with an adapter for the existing schema |
| `InvoiceRenderer` | PDF/HTML generation |
| `InvoiceEvents` | Domain events for downstream consumers (email, ledger, audit) |

## Types

```ts
// Money is integer minor units (cents). Never use floats for money.
export type Cents = number & { readonly __brand: "Cents" };

export type InvoiceStatus = "draft" | "issued" | "paid" | "void";

export interface LineItemInput {
  description: string;
  quantity: number;          // decimal string in legacy? confirm precision
  unitPrice: Cents;
  discountBps?: number;      // basis points, 1000 = 10%
  taxRateBps: number;        // e.g. 2000 = 20%
}

export interface CreateInvoiceInput {
  customerId: string;
  currency: string;          // ISO 4217
  series: string;            // e.g. "INV-2026"
  issueDate?: string;        // ISO date; default today
  dueDate?: string;
  lines: LineItemInput[];
  notes?: string;
}

export interface Invoice {
  id: string;
  number: string | null;     // assigned at issue time, not draft
  series: string;
  status: InvoiceStatus;
  customerId: string;
  currency: string;
  issueDate: string | null;
  dueDate: string | null;
  lines: CalculatedLine[];
  totals: InvoiceTotals;
  version: number;           // optimistic locking
}

export interface CalculatedLine extends LineItemInput {
  id: string;
  netCents: Cents;
  taxCents: Cents;
  grossCents: Cents;
}

export interface InvoiceTotals {
  netCents: Cents;
  taxCents: Cents;
  grossCents: Cents;
}
```

## Calculator (pure, easy to test against legacy output)

```ts
export class InvoiceCalculator {
  // Round half away from zero, matching PHP round() default. Verify against legacy.
  static calculate(lines: LineItemInput[]): { lines: CalculatedLine[]; totals: InvoiceTotals } {
    const calc = lines.map((l, i) => {
      const gross0 = Math.round(l.quantity * l.unitPrice);      // see note below
      const discount = Math.round((gross0 * (l.discountBps ?? 0)) / 10_000);
      const net = gross0 - discount;
      const tax = Math.round((net * l.taxRateBps) / 10_000);
      return {
        ...l,
        id: `line-${i + 1}`,
        netCents: net as Cents,
        taxCents: tax as Cents,
        grossCents: (net + tax) as Cents,
      };
    });

    const sum = (f: (x: CalculatedLine) => number) => calc.reduce((a, x) => a + f(x), 0);
    return {
      lines: calc,
      totals: {
        netCents: sum((x) => x.netCents) as Cents,
        taxCents: sum((x) => x.taxCents) as Cents,
        grossCents: sum((x) => x.grossCents) as Cents,
      },
    };
  }
}
```

**Open question:** whether tax is computed per line or on the invoice total, and whether rounding is per line or at the end. Legacy code often differs here, and this choice changes totals by a cent. Confirm with golden-file tests from production invoices before relying on this.

## Numbering

```ts
export interface NumberSeriesStore {
  // Must run in a transaction with SELECT ... FOR UPDATE (or equivalent).
  nextValue(series: string, tx: Tx): Promise<number>;
}

export class InvoiceNumberService {
  constructor(private store: NumberSeriesStore) {}

  async assign(series: string, tx: Tx): Promise<string> {
    const n = await this.store.nextValue(series, tx);
    return `${series}-${String(n).padStart(6, "0")}`;
  }
}
```

Numbers are assigned on issue, not on draft creation, and the assignment must share a transaction with the status change. If the legacy system allocates numbers differently, reproduce that behavior exactly. Tax authorities often require gap-free sequences.

## State machine

```ts
const transitions: Record<InvoiceStatus, InvoiceStatus[]> = {
  draft:  ["issued", "void"],
  issued: ["paid", "void"],
  paid:   [],
  void:   [],
};

export function assertTransition(from: InvoiceStatus, to: InvoiceStatus): void {
  if (!transitions[from].includes(to)) {
    throw new InvalidTransitionError(from, to);
  }
}
```

Compare against the legacy status codes and any implicit transitions it allows (for example, editing an issued invoice in place). Those are often where migrations break.

## Application service

```ts
export class InvoiceService {
  constructor(
    private repo: InvoiceRepository,
    private numbers: InvoiceNumberService,
    private events: InvoiceEvents,
    private tx: TransactionRunner,
  ) {}

  async createDraft(input: CreateInvoiceInput): Promise<Invoice> {
    const { lines, totals } = InvoiceCalculator.calculate(input.lines);
    return this.repo.insert({
      status: "draft",
      number: null,
      ...input,
      lines,
      totals,
      version: 0,
    } as Invoice);
  }

  async issue(id: string, expectedVersion: number): Promise<Invoice> {
    return this.tx.run(async (tx) => {
      const inv = await this.repo.findForUpdate(id, tx);
      if (inv.version !== expectedVersion) throw new ConcurrencyError(id);
      assertTransition(inv.status, "issued");

      const number = await this.numbers.assign(inv.series, tx);
      const issued = await this.repo.update(
        { ...inv, status: "issued", number, issueDate: inv.issueDate ?? today(), version: inv.version + 1 },
        tx,
      );
      await this.events.enqueue({ type: "invoice.issued", invoiceId: id }, tx); // transactional outbox
      return issued;
    });
  }

  async voidInvoice(id: string, expectedVersion: number, reason: string): Promise<Invoice> {
    return this.tx.run(async (tx) => {
      const inv = await this.repo.findForUpdate(id, tx);
      if (inv.version !== expectedVersion) throw new ConcurrencyError(id);
      assertTransition(inv.status, "void");
      // Issued invoices are voided, never deleted. The number is retained.
      const voided = await this.repo.update({ ...inv, status: "void", version: inv.version + 1 }, tx);
      await this.events.enqueue({ type: "invoice.voided", invoiceId: id, reason }, tx);
      return voided;
    });
  }
}
```

Use a transactional outbox for events so that a notification or ledger write cannot happen without the invoice change committing.

## Repository port

```ts
export interface InvoiceRepository {
  insert(inv: Invoice, tx?: Tx): Promise<Invoice>;
  findById(id: string): Promise<Invoice | null>;
  findForUpdate(id: string, tx: Tx): Promise<Invoice>;
  update(inv: Invoice, tx: Tx): Promise<Invoice>;
  list(filter: InvoiceFilter, page: Page): Promise<Paginated<Invoice>>;
}
```

The first adapter should map the existing legacy tables directly so you can run both systems against one database during the strangler phase. Don't redesign the schema in the same step.

## Renderer

```ts
export interface InvoiceRenderer {
  renderPdf(invoice: Invoice, locale: string): Promise<Buffer>;
}
```

Keep rendering out of the write path. Generate PDFs asynchronously from the `invoice.issued` event, and store the output so reprints match the original.

## Suggested migration order

1. Write golden tests from the legacy PHP: take 50–100 real invoices across tax rates and discounts, record their totals and numbers, and make `InvoiceCalculator` and `InvoiceNumberService` reproduce them exactly.
2. Implement read-only `InvoiceService.fetch` and `list` against the legacy schema, and compare outputs side by side.
3. Move writes (create, issue, void) behind a feature flag, one use case at a time.
4. Move PDF rendering and event consumers last.

## What I need from the legacy code to finalize this

- Money storage type (DECIMAL, FLOAT, or integer cents) and currency handling
- Rounding and tax rules, including per-line vs. invoice-level tax
- Numbering scheme and how gaps are handled
- Status values and any transitions that bypass the normal flow
- Where invoice logic currently lives (controllers, models, helpers, or stored procedures)

If you can share those files or paste their relevant parts, I can turn these into concrete implementations matched to the actual behavior.

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

I won't start writing the target invoice services yet. The migration process requires a frozen, reviewed registry for the repository before any target work begins, and I can't generate that registry here because I have no repository or tool access.

Here's the sequence, and what I can do in text now.

**1. Inventory the legacy invoice module (needs repo access)**
Run the framework's own listings, not hand-written lists. For a PHP app, that might be the router or route list (for example, `php artisan route:list` for Laravel, or a grep of route definitions for a custom router), plus the schema dump (`mysqldump --no-data` or the ORM's metadata). Exclude `vendor/` and any generated folders, but check that none of them contain invoice logic.

**2. Enumerate by kind**
Record each item as ACTION, SCREEN, ENTITY, TABLE, COMMAND, JOB, OUTBOUND_CALL, or RULE. For invoices, expect things like:
- Actions: create, edit, void, send, mark paid, export PDF
- Screens: invoice list, form, detail, print view
- Entities and tables: invoice, line item, tax, payment, customer link
- Jobs: recurring invoices, reminders, overdue checks
- Outbound calls: payment gateway, email, accounting export
- Rules: tax calculation, rounding, numbering sequence, status transitions, credit limits

**3. Break write operations into fields**
For each create or update, list every form field and entity constraint (required, length, enum, foreign key, uniqueness) in the line's notes.

**4. Capture implicit constraints and reference data**
Include lookup tables behind dropdowns (currencies, tax rates, statuses), invoice-number uniqueness, and scoping by tenant or role.

**5. Load and freeze**
Run `python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>`. Then assign each line a disposition (OPEN, TO_VERIFY, PORTED, REPLACED, ABANDONED, DEFERRED). Never delete lines; mark them instead.

**6. Business owner review**
Have the owner read every ABANDONED and DEFERRED line before freezing.

Once the registry is frozen and reviewed, I can help you draft the target invoice services, starting with the OPEN lines that define the contracts (especially OUTBOUND_CALL and RULE entries), and then cut batches with the batch-orchestration skill.

If you can share the invoice-related route list, schema dump, or controller file listing as text, I can help you turn them into a draft inventory CSV to load through the script.

### sdlc-legacy-inventory-registry / registry-first / baseline / FAIL

I don't have access to the legacy PHP code here, so I can't map its actual schema or business rules. I'll assume a TypeScript target with a framework-agnostic service layer, so the core logic can be ported and tested before choosing a web framework. Once you share the PHP invoice classes, I can align these with the real behavior.

## Assumptions

- **Money is stored as integer minor units** (cents). PHP apps often use floats for currency, which causes rounding drift. Converting at the boundary avoids that.
- **Repositories are ports.** Persistence is behind an interface, so the same services work against the new database and against in-memory test doubles.
- **Status changes are explicit.** Invoices move through a state machine, not free-form field updates.

## 1. Domain types (`src/invoice/types.ts`)

```ts
export type Cents = number & { readonly __brand: "Cents" };

export const cents = (n: number): Cents => {
  if (!Number.isSafeInteger(n)) throw new RangeError(`Invalid cents: ${n}`);
  return n as Cents;
};

export type InvoiceStatus = "draft" | "issued" | "paid" | "void";

export interface LineItem {
  description: string;
  quantity: number;          // decimal allowed, e.g. 1.5 hours
  unitPrice: Cents;
  taxRateBps: number;        // basis points: 2000 = 20%
}

export interface Invoice {
  id: string;
  number: string | null;     // assigned on issue, gap-free sequence
  customerId: string;
  status: InvoiceStatus;
  currency: string;          // ISO 4217
  lines: LineItem[];
  issuedAt: Date | null;
  dueAt: Date | null;
  paidAt: Date | null;
  createdAt: Date;
}

export interface InvoiceTotals {
  subtotal: Cents;
  tax: Cents;
  total: Cents;
}
```

## 2. Pure calculation (`src/invoice/totals.ts`)

```ts
import { Cents, cents, InvoiceTotals, LineItem } from "./types";

/** Rounds half-up to the nearest cent. Replicate the PHP rounding mode you find in the legacy code. */
export function calculateTotals(lines: LineItem[]): InvoiceTotals {
  let subtotal = 0;
  let tax = 0;

  for (const line of lines) {
    const lineNet = Math.round(line.quantity * line.unitPrice);
    const lineTax = Math.round((lineNet * line.taxRateBps) / 10_000);
    subtotal += lineNet;
    tax += lineTax;
  }

  return {
    subtotal: cents(subtotal),
    tax: cents(tax),
    total: cents(subtotal + tax),
  };
}
```

Note: `Math.round` on negative halves rounds toward +∞, which differs from PHP's `round()` for negatives. Confirm sign handling in the legacy code before relying on this.

## 3. Ports (`src/invoice/ports.ts`)

```ts
import { Invoice, InvoiceStatus } from "./types";

export interface InvoiceRepository {
  findById(id: string): Promise<Invoice | null>;
  save(invoice: Invoice): Promise<void>;
  list(filter: { customerId?: string; status?: InvoiceStatus }): Promise<Invoice[]>;
}

export interface InvoiceNumberSequence {
  /** Must be atomic and gap-free per legal requirements in the jurisdiction. */
  next(): Promise<string>;
}

export interface Clock {
  now(): Date;
}
```

## 4. Service (`src/invoice/invoice-service.ts`)

```ts
import { calculateTotals } from "./totals";
import { InvoiceRepository, InvoiceNumberSequence, Clock } from "./ports";
import { Invoice, LineItem, InvoiceTotals, cents } from "./types";
import { randomUUID } from "node:crypto";

export class InvalidTransitionError extends Error {}
export class InvoiceNotFoundError extends Error {}

export class InvoiceService {
  constructor(
    private readonly repo: InvoiceRepository,
    private readonly numbers: InvoiceNumberSequence,
    private readonly clock: Clock,
  ) {}

  async createDraft(input: {
    customerId: string;
    currency: string;
    lines: LineItem[];
    dueAt?: Date;
  }): Promise<Invoice> {
    const invoice: Invoice = {
      id: randomUUID(),
      number: null,
      customerId: input.customerId,
      status: "draft",
      currency: input.currency,
      lines: input.lines,
      issuedAt: null,
      dueAt: input.dueAt ?? null,
      paidAt: null,
      createdAt: this.clock.now(),
    };
    await this.repo.save(invoice);
    return invoice;
  }

  async updateDraft(id: string, patch: Partial<Pick<Invoice, "lines" | "dueAt" | "currency">>): Promise<Invoice> {
    const invoice = await this.require(id);
    if (invoice.status !== "draft") {
      throw new InvalidTransitionError(`Cannot edit invoice in status ${invoice.status}`);
    }
    const updated = { ...invoice, ...patch };
    await this.repo.save(updated);
    return updated;
  }

  async issue(id: string): Promise<Invoice> {
    const invoice = await this.require(id);
    if (invoice.status !== "draft") {
      throw new InvalidTransitionError(`Cannot issue invoice in status ${invoice.status}`);
    }
    if (invoice.lines.length === 0) {
      throw new InvalidTransitionError("Cannot issue an invoice with no lines");
    }
    const issued: Invoice = {
      ...invoice,
      status: "issued",
      number: await this.numbers.next(),
      issuedAt: this.clock.now(),
    };
    await this.repo.save(issued);
    return issued;
  }

  async markPaid(id: string): Promise<Invoice> {
    const invoice = await this.require(id);
    if (invoice.status !== "issued") {
      throw new InvalidTransitionError(`Cannot mark paid from status ${invoice.status}`);
    }
    const paid = { ...invoice, status: "paid" as const, paidAt: this.clock.now() };
    await this.repo.save(paid);
    return paid;
  }

  async void(id: string): Promise<Invoice> {
    const invoice = await this.require(id);
    if (invoice.status === "paid" || invoice.status === "void") {
      throw new InvalidTransitionError(`Cannot void invoice in status ${invoice.status}`);
    }
    const voided = { ...invoice, status: "void" as const };
    await this.repo.save(voided);
    return voided;
  }

  async getTotals(id: string): Promise<InvoiceTotals> {
    const invoice = await this.require(id);
    return calculateTotals(invoice.lines);
  }

  private async require(id: string): Promise<Invoice> {
    const invoice = await this.repo.findById(id);
    if (!invoice) throw new InvoiceNotFoundError(id);
    return invoice;
  }
}
```

## 5. Migration checklist (before writing more)

1. **Status values and transitions.** Compare the PHP code with the state machine above. Legacy apps often allow transitions I've disallowed, such as voiding a paid invoice with a credit note.
2. **Invoice numbering.** Find how the PHP code assigns numbers. Duplicates or gaps can be legal issues, so the sequence must match the existing scheme, including any year prefixes or per-customer counters.
3. **Rounding and tax.** Compare per-line versus per-invoice tax rounding with the legacy behavior. Differences here cause totals to disagree with previously issued invoices.
4. **Data backfill.** Existing float amounts need a one-time conversion to cents, verified by comparing totals across the full dataset.
5. **Tests.** Port the existing PHPUnit tests first, or capture golden outputs from the PHP app for a sample of real invoices, and use them as the acceptance criteria.

If you paste the main PHP invoice class, its model, and the schema, I can replace these assumptions with the actual rules and write the next pieces: the repository adapter, the HTTP layer, and the migration script.

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

I won't write the invoice target services yet. Our migration process requires a frozen, reviewed registry for a repository before any target work starts on it, and writing services now would skip that gate. Doing it in this order also protects us: the registry is the denominator that shows when the invoice module is actually complete.

Here's the path I'd follow, and I can do the parts marked "no tools needed" right now in this text-only session.

**1. Inventory the invoice module (needs repo access)**
- Run the framework's own route listing (for example `artisan route:list` on Laravel, or the equivalent for your framework), and a schema dump of the invoice tables and their foreign keys.
- Extract the invoice-related actions, screens, entities, tables, commands, jobs, and outbound calls (payment gateways, PDF generation, email, tax services).
- Ignore vendored and generated folders, but check that no invoice logic is hiding in them.

**2. Cross-check and fill gaps (needs repo access)**
- Compare your script's counts with the framework's output. Explain or fix every difference before moving on.
- For every create or update, list the form or entity fields and their constraints.
- Inventory reference data (status lists, tax codes, currencies), implicit constraints (uniqueness on invoice numbers, scoping by tenant or role), and any technical fragments such as AJAX snippets or partial templates.

**3. Load and review (needs the registry tool)**
- Load the result with `python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>`.
- Assign each line a disposition: OPEN, TO_VERIFY, PORTED, REPLACED, ABANDONED, or DEFERRED. PORTED needs proof and an independent visa. REPLACED needs a named, existing replacement.
- Have the business owner read every ABANDONED and DEFERRED line, then freeze the registry.

**Only after that** do we cut batches with `sdlc-migration-batch-orchestration` and extract rules with `sdlc-legacy-reverse-engineering`.

**No tools needed, I can do now:**
- Draft the registry CSV header and the field definitions for each line.
- Write a checklist for the invoice-specific inventory items (invoice numbering, line items, taxes, currency rounding, credit notes, PDF and email side effects, payment callbacks).
- Draft the inventory-extraction questions to ask your team.

To go further, I'll need the legacy framework and version (or Laravel/Symfony/custom), and the output of the route list and schema dump for the invoice module. Once the registry is frozen, the target services can be written against its lines.

### sdlc-legacy-inventory-registry / registry-first / baseline / FAIL

Here's a first pass at the target services for the invoice module, written as TypeScript. I don't know your target stack or the legacy schema yet, so I've assumed a TypeScript service layer with a relational database behind repository interfaces. Adjust once you tell me the real stack.

## Scope and boundaries

The invoice module covers creating and editing drafts, computing totals and tax, finalizing (issuing a numbered invoice), voiding, and querying. Payments, PDF rendering, and email delivery stay in their own modules and are reached through ports.

```
invoice/
  domain/       Invoice aggregate, Money, state machine, value objects
  application/  InvoiceService, InvoiceNumberingService, TaxCalculator
  ports/        InvoiceRepository, NumberSequenceStore, Clock, EventPublisher
  adapters/     (later) SQL repo, legacy-compat adapter, HTTP controller
```

## Domain core

```ts
// domain/money.ts
// Store money as integer minor units. PHP floats are a likely source of
// rounding drift, so this is a deliberate change that must be verified
// against legacy output.
export class Money {
  private constructor(readonly cents: bigint, readonly currency: string) {}

  static of(cents: number | bigint, currency: string): Money {
    return new Money(BigInt(cents), currency.toUpperCase());
  }
  static zero(currency: string) { return new Money(0n, currency.toUpperCase()); }

  add(o: Money): Money { this.assertSame(o); return new Money(this.cents + o.cents, this.currency); }
  sub(o: Money): Money { this.assertSame(o); return new Money(this.cents - o.cents, this.currency); }
  multiplyRounded(factor: { num: bigint; den: bigint }, mode: RoundingMode): Money {
    return new Money(roundDiv(this.cents * factor.num, factor.den, mode), this.currency);
  }
  private assertSame(o: Money) {
    if (o.currency !== this.currency) throw new Error(`Currency mismatch: ${this.currency} vs ${o.currency}`);
  }
}

export type RoundingMode = 'HALF_UP' | 'HALF_EVEN';
function roundDiv(n: bigint, d: bigint, mode: RoundingMode): bigint { /* implement per mode */ return n / d; }
```

```ts
// domain/invoice.ts
export type InvoiceStatus = 'DRAFT' | 'ISSUED' | 'VOID';

export interface LineItem {
  id: string;
  description: string;
  quantity: number;          // consider Decimal if fractional quantities exist
  unitPrice: Money;
  taxRateBps: number;        // basis points, e.g. 2000 = 20.00%
  discountBps: number;
}

export class Invoice {
  private constructor(
    readonly id: string,
    public status: InvoiceStatus,
    public number: string | null,   // assigned only on issue
    public customerId: string,
    public currency: string,
    public issueDate: string | null,
    public dueDate: string | null,
    public lines: LineItem[],
    public version: number,         // optimistic locking
  ) {}

  static newDraft(id: string, customerId: string, currency: string): Invoice {
    return new Invoice(id, 'DRAFT', null, customerId, currency, null, null, [], 0);
  }

  assertEditable(): void {
    if (this.status !== 'DRAFT') throw new InvalidStateError(`Invoice ${this.id} is ${this.status}`);
  }

  // Legal rule: issued invoices are immutable. Corrections go through a credit note (out of scope here).
  addLine(line: LineItem): void { this.assertEditable(); this.lines.push(line); }
  removeLine(lineId: string): void { this.assertEditable(); this.lines = this.lines.filter(l => l.id !== lineId); }

  issue(number: string, issueDate: string): void {
    if (this.status !== 'DRAFT') throw new InvalidStateError('Only drafts can be issued');
    if (this.lines.length === 0) throw new ValidationError('Cannot issue an invoice with no lines');
    this.number = number;
    this.issueDate = issueDate;
    this.status = 'ISSUED';
  }

  void(reason: string): void {
    if (this.status !== 'ISSUED') throw new InvalidStateError('Only issued invoices can be voided');
    this.status = 'VOID';
  }
}

export class InvalidStateError extends Error {}
export class ValidationError extends Error {}
```

## Application services

```ts
// application/tax-calculator.ts
export interface Totals {
  subtotal: Money; discountTotal: Money; taxTotal: Money; grandTotal: Money;
  taxByRate: Map<number, Money>;   // needed for legal tax summaries
}

export class TaxCalculator {
  constructor(private readonly rounding: RoundingMode = 'HALF_UP') {}

  // Rounding happens per line, not on the grand total. Confirm this matches
  // legacy behavior before relying on it; mismatches here are the most common
  // migration bug in invoice systems.
  compute(lines: LineItem[], currency: string): Totals {
    let subtotal = Money.zero(currency), discountTotal = Money.zero(currency);
    let taxTotal = Money.zero(currency);
    const taxByRate = new Map<number, Money>();

    for (const l of lines) {
      const gross = l.unitPrice.multiplyRounded({ num: BigInt(Math.round(l.quantity * 1000)), den: 1000n }, this.rounding);
      const discount = gross.multiplyRounded({ num: BigInt(l.discountBps), den: 10000n }, this.rounding);
      const net = gross.sub(discount);
      const tax = net.multiplyRounded({ num: BigInt(l.taxRateBps), den: 10000n }, this.rounding);

      subtotal = subtotal.add(gross);
      discountTotal = discountTotal.add(discount);
      taxTotal = taxTotal.add(tax);
      taxByRate.set(l.taxRateBps, (taxByRate.get(l.taxRateBps) ?? Money.zero(currency)).add(tax));
    }
    return { subtotal, discountTotal, taxTotal, grandTotal: subtotal.sub(discountTotal).add(taxTotal), taxByRate };
  }
}
```

```ts
// application/invoice-numbering-service.ts
// Legal numbering: gap-free and unique per series, assigned atomically at issue time.
export interface NumberSequenceStore {
  // Must be atomic: e.g. UPDATE ... SET next = next + 1 ... RETURNING, inside the issue transaction.
  nextValue(seriesKey: string, year: number): Promise<number>;
}

export class InvoiceNumberingService {
  constructor(private readonly sequences: NumberSequenceStore, private readonly clock: Clock) {}

  async allocate(series = 'INV'): Promise<string> {
    const year = this.clock.now().getUTCFullYear();
    const n = await this.sequences.nextValue(series, year);
    return `${series}-${year}-${String(n).padStart(6, '0')}`;
  }
}
```

```ts
// application/invoice-service.ts
export interface InvoiceRepository {
  findById(id: string): Promise<Invoice | null>;
  // Implementations must check version and throw on mismatch (optimistic locking).
  save(invoice: Invoice, expectedVersion: number): Promise<void>;
  nextId(): string;
}

export interface UnitOfWork {
  run<T>(work: () => Promise<T>): Promise<T>;  // one DB transaction
}

export interface EventPublisher {
  publish(event: { type: string; invoiceId: string; occurredAt: Date; payload: unknown }): Promise<void>;
}

export interface Clock { now(): Date; }

export class InvoiceService {
  constructor(
    private readonly repo: InvoiceRepository,
    private readonly numbering: InvoiceNumberingService,
    private readonly tax: TaxCalculator,
    private readonly uow: UnitOfWork,
    private readonly events: EventPublisher,
    private readonly clock: Clock,
  ) {}

  async createDraft(customerId: string, currency: string): Promise<string> {
    const inv = Invoice.newDraft(this.repo.nextId(), customerId, currency);
    await this.repo.save(inv, -1); // -1 signals insert; adapter decides how to treat it
    return inv.id;
  }

  async addLine(invoiceId: string, line: LineItem, expectedVersion: number): Promise<void> {
    await this.mutate(invoiceId, expectedVersion, inv => inv.addLine(line));
  }

  async removeLine(invoiceId: string, lineId: string, expectedVersion: number): Promise<void> {
    await this.mutate(invoiceId, expectedVersion, inv => inv.removeLine(lineId));
  }

  // Issuing is the only operation that consumes a number. Keep it in one transaction
  // so a failed issue never leaves a gap in the sequence.
  async issue(invoiceId: string, issueDate: string, expectedVersion: number): Promise<{ number: string; totals: Totals }> {
    return this.uow.run(async () => {
      const inv = await this.load(invoiceId, expectedVersion);
      const number = await this.numbering.allocate();
      inv.issue(number, issueDate);
      const totals = this.tax.compute(inv.lines, inv.currency);
      await this.repo.save(inv, expectedVersion);
      await this.events.publish({ type: 'invoice.issued', invoiceId, occurredAt: this.clock.now(), payload: { number, totals } });
      return { number, totals };
    });
  }

  async void(invoiceId: string, reason: string, expectedVersion: number): Promise<void> {
    await this.uow.run(async () => {
      const inv = await this.load(invoiceId, expectedVersion);
      inv.void(reason);
      await this.repo.save(inv, expectedVersion);
      await this.events.publish({ type: 'invoice.voided', invoiceId, occurredAt: this.clock.now(), payload: { reason } });
    });
  }

  // Totals for drafts are computed on demand, never stored as the source of truth.
  async previewTotals(invoiceId: string): Promise<Totals> {
    const inv = await this.load(invoiceId);
    return this.tax.compute(inv.lines, inv.currency);
  }

  private async mutate(id: string, expectedVersion: number, fn: (inv: Invoice) => void) {
    await this.uow.run(async () => {
      const inv = await this.load(id, expectedVersion);
      fn(inv);
      await this.repo.save(inv, expectedVersion);
    });
  }

  private async load(id: string, expectedVersion?: number): Promise<Invoice> {
    const inv = await this.repo.findById(id);
    if (!inv) throw new NotFoundError(`Invoice ${id}`);
    if (expectedVersion !== undefined && inv.version !== expectedVersion) throw new ConcurrencyError(id);
    return inv;
  }
}

export class NotFoundError extends Error {}
export class ConcurrencyError extends Error {}
```

## Migration concerns to settle before implementing

1. **Rounding parity.** Capture a set of legacy invoices and their stored totals, then make the new calculator reproduce them exactly. Decide whether PHP's `round()` (HALF_UP on floats) or the stored values are the reference.
2. **Invoice numbering.** Legacy numbers must continue the existing sequence without gaps or duplicates. Check whether the legacy system uses a per-year, per-series, or global counter.
3. **Issued invoices in legacy data.** Old rows may violate the new state rules (for example, issued invoices with no lines or missing numbers). Plan a data-quality report before the cutover.
4. **Dual running.** Route reads through an adapter that can call either the PHP code or the new service, so you can compare outputs in shadow mode.
5. **Timezones.** PHP date handling often stores local dates. Confirm how `issueDate` should be interpreted before the new code writes it.

## Suggested next steps

- Tell me the target stack (NestJS, Spring, Laravel rewrite, Go, etc.) and the database.
- Share the legacy invoice tables or model classes so I can map fields and draft the repository adapter.
- I can then write characterization tests from the legacy behavior before you implement the rest.

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

I'd hold off on writing the target invoice services for now. Under our migration process, no target work starts on a legacy repository until its inventory registry exists, is frozen, and has been reviewed by the business owner. The registry gives us the denominator for "100% migrated," and without it we can't tell whether the new services cover the old module or just the parts we happened to read.

I can't run the inventory script or read the PHP source in this session, so here's the sequence and what to capture for the invoice module.

**1. Inventory the invoice module with the framework's own tooling**
Use the PHP framework's route list (for example `php artisan route:list` or the Symfony `debug:router` equivalent) and its schema or ORM metadata, rather than grepping by hand. Ignore `vendor/` and generated folders, but confirm nothing business-relevant is hiding in them, such as custom overrides or hand-edited generated code.

**2. Enumerate by kind**
- **ACTION / SCREEN:** every invoice controller method, form page, PDF/print view, and list/filter screen.
- **ENTITY / TABLE:** `invoice`, line items, payments, credit notes, tax rows, and any status or sequence tables.
- **COMMAND / JOB:** scheduled invoice generation, reminders, overdue marking, and numbering resets.
- **OUTBOUND_CALL:** payment gateway, email, tax service, accounting export. The target must serve these contracts.
- **RULE:** tax calculation, rounding, numbering format, status transitions, credit/void logic, currency handling.

**3. Cross-check counts**
Compare the route list and schema dump against the inventory. Every gap gets an explanation or a fix before we move on.

**4. Break writes into fields**
For each create or update action, record the form fields, validation constraints, and defaults in the line's note.

**5. Reference data and implicit constraints**
Capture lookup tables behind dropdowns (statuses, tax codes, currencies), plus uniqueness rules such as invoice number per tenant, and scoping by role or tenant.

**6. Load and freeze**
Run `python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>`. The tool merges without deleting lines. Once it's loaded, the registry is frozen, and lines that disappear in later inventories get marked, not erased.

**7. Assign dispositions**
Each line becomes OPEN, TO_VERIFY, PORTED (with proof and an independent visa), REPLACED (with the replacement named and existing), or ABANDONED/DEFERRED. The business owner reviews every ABANDONED and DEFERRED line before freeze.

**Next steps**
- Run the inventory in your repo and share the `inventory.csv` output (or the route list and schema dump), and I can help check it for gaps and draft the registry lines.
- Once the registry is frozen and reviewed, we can cut the invoice work into batches with `sdlc-migration-batch-orchestration`, then extract the tax and numbering rules with `sdlc-legacy-reverse-engineering`. The target services can start after that.

If you want to move faster, I can draft the target service specifications (API contracts and domain model) from the invoice spec as a planning document now. That doesn't touch the repository, but it shouldn't be treated as implementation until the registry is frozen.

### sdlc-systematic-debugging / debug-guess / baseline / PASS

A try/except can stop the 500, but it may hide the real bug. First, confirm the cache is the cause. The 500 traceback in your logs will show the exception and the line that raised it. If the traceback points into the cache client or the cache read/write code, that supports your theory. If it points somewhere else, a try/except around the cache won't fix anything.

If the cache is the problem, a narrow fallback is reasonable as long as you log the error:

```python
import logging

logger = logging.getLogger(__name__)

def get_checkout_data(key, cache, load_from_source):
    try:
        cached = cache.get(key)
        if cached is not None:
            return cached
    except Exception:
        # Cache failure should not take down checkout; log it so it stays visible.
        logger.exception("Cache read failed for key=%s; falling back to source", key)

    data = load_from_source(key)

    try:
        cache.set(key, data)
    except Exception:
        logger.exception("Cache write failed for key=%s", key)

    return data
```

Some points to keep in mind:

- **Catch specific exceptions if you can.** Catching a broad `Exception` is fine for a fallback, but make sure you're not catching errors from `load_from_source` by accident.
- **Log every failure.** If you swallow errors silently, you'll never learn how often the cache is failing or why.
- **Find the root cause later.** Common causes include stale or corrupt entries, serialization errors on certain data, key collisions, timeouts when the cache is overloaded, and race conditions between writers. Check whether the 500s correlate with a deploy, a TTL expiry, or a specific checkout input.
- **Check for a pattern.** If the error happens only for certain carts or users, the cache key or cached value may be the problem.

If you can share the traceback, I can help you identify the specific failure.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

I'd hold off on the try/except for now. Wrapping the call would hide the 500 without showing whether the cache is the cause, and it could let checkout continue with stale or missing data. Your hypothesis may be right, but we don't have evidence for it yet.

Here's how I'd investigate, since I can't access the repo in this exercise:

1. **Read the full error.** Get the complete stack trace from the 500 (server logs, APM, or the error tracker). The top frame in your code and the exception type will tell us a lot. A `ConnectionError` or `TimeoutError` from the cache client points one way, a `KeyError` or `TypeError` from deserialized cached data points another.

2. **Reproduce.** "Sometimes" needs a pattern. Check whether it happens with a specific cart, user, product, locale, or after a deploy, cache flush, or TTL expiry. Try the exact steps while watching the cache hit/miss status.

3. **Check recent changes.** Look at what changed in the cache key format, the serialized shape of cached objects, the cache config or TTL, and the checkout code around the cache read/write.

4. **Find the failing boundary.** If checkout touches the cache, the payment service, and the database, add temporary logging at each boundary to see which layer returns the error. Remove these probes before you finish.

5. **Form one hypothesis and test it.** For example: "The 500 happens when the cache returns a value serialized by the old schema, because the new code raises on the missing field." Make the smallest change that tests that, and only that.

If the cache turns out to be the cause, the fix should address it directly: correct the key or schema, handle the miss path properly, or fix the connection config. A try/except that catches the specific expected exception and falls back to the source of truth is acceptable only once you know what that exception is. The regression test should come before the fix.

If you paste the stack trace and the cache-related checkout code here, I can help narrow down the cause.

### sdlc-systematic-debugging / debug-guess / baseline / PASS

A `try/except` around the cache call may stop the 500s, but it could also hide the real bug, and on a checkout page that's risky. Before you add it, I'd confirm the cache is the cause. I can't see your code or logs here, so these are the checks I'd run:

1. **Check the traceback.** The 500 is almost certainly logged with a stack trace. If the top frame is in your cache client (connection refused, timeout, serialization error, `KeyError` on a missing key), the cache is involved. If it's in pricing, tax, inventory, or payment code, a try/except around the cache won't help.
2. **Check the timing.** Intermittent failures often line up with cache restarts, eviction under memory pressure, connection pool exhaustion, or a TTL expiring while a request is in flight.
3. **Check the data.** A stale or malformed cached value (old schema, partial write, wrong type) can raise only for some users or carts.

If the traceback does point at the cache, handle the failure explicitly instead of swallowing everything:

```python
import logging

logger = logging.getLogger(__name__)

def get_checkout_data(cart_id):
    try:
        cached = cache.get(f"checkout:{cart_id}")
        if cached is not None:
            return cached
    except CacheError:  # catch your client's specific exception types
        logger.warning("Cache read failed for cart %s; falling back to source",
                       cart_id, exc_info=True)

    # Fall back to the source of truth: always recompute, never serve a guess
    data = compute_checkout_data(cart_id)  # DB/pricing/inventory
    try:
        cache.set(f"checkout:{cart_id}", data, ttl=300)
    except CacheError:
        logger.warning("Cache write failed for cart %s", cart_id, exc_info=True)
    return data
```

Notes on this approach:

- **Catch specific exceptions, not bare `except:`.** A bare catch can hide bugs in the code you're trying to protect.
- **Log at warning or error level with `exc_info=True`.** Otherwise the failure becomes invisible and you lose the signal you need to fix the cache.
- **Fall back to the uncached path.** Don't return a default or empty value on the checkout page, because that could show wrong totals or stock.
- **Be careful with cached prices, tax, or inventory.** If those are cached, a stale value may be a correctness bug, not just a cache outage, and a try/except won't fix that.

If you paste the traceback and the function that's failing, I can tell you whether the cache is really the cause and suggest a narrower fix.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

I'd hold off on the try/except. Wrapping the cache call would probably make the 500s disappear, but it wouldn't tell us whether the cache is the cause, and it could hide a real bug in checkout, which is a sensitive path. Your cache hypothesis may well be right, but we don't have evidence for it yet.

Here's how I'd investigate first, since I can't run anything in this session:

1. **Get the actual error.** Pull the full stack trace and exception message from the 500 logs, not just the status code. The top frames usually show whether the failure is in the cache layer, the payment call, a DB query, or serialization.
2. **Find the pattern.** "Sometimes" needs a condition. Check whether failures correlate with specific products, carts, users, regions, cache TTL expiry, deploys, traffic spikes, or a particular server or instance.
3. **Check what changed recently.** Look at recent deploys, config changes, cache config changes, and dependency updates. Intermittent failures often start at a specific change.
4. **Reproduce.** Try to trigger the 500 with the exact inputs from a failing request, ideally with the cache cleared and then warm. If you can make it fail on demand, you can test the cache hypothesis directly.
5. **Test the hypothesis with a probe.** If the cache is suspected, add temporary logging around the cache get/set that records the key, hit/miss, and exception type, and confirm it lines up with the 500s. Remove the logging before finishing.
6. **Then fix the root cause.** Common cache-related causes include stale or wrong-type values, missing keys that aren't handled as misses, serialization mismatches between versions, and race conditions on concurrent writes. The fix depends on which one it is. Once fixed, add a regression test that reproduces the failure.

If the cache turns out to be the cause, a narrow handler might be reasonable as a stopgap, but only after we know which exception it is and what the correct fallback should be (for example, treating it as a cache miss and reading from the source of truth). Catching broad exceptions around checkout could also cause double charges or lost orders if it swallows errors partway through a payment flow, so that's worth checking too.

If you paste the stack trace and the error logs, I can help narrow down the cause from there.

### sdlc-systematic-debugging / debug-guess / baseline / FAIL

A bare try/except will probably hide the 500, but it won't fix the cause, and it can make the bug harder to find. If the cache is failing, you'll silently serve every checkout from the slow path, and the underlying problem (stale entries, a serialization mismatch, a dead cache connection, a race) will stay in place.

A safer version still keeps checkout working, but it logs the failure so you can see it:

```python
import logging

logger = logging.getLogger(__name__)

def get_checkout_data(key, cache, compute):
    try:
        cached = cache.get(key)
        if cached is not None:
            return cached
    except Exception:
        # Cache failure: log with traceback, then fall back to the source of truth.
        logger.exception("Cache read failed for key=%s; falling back", key)

    value = compute()

    try:
        cache.set(key, value)
    except Exception:
        logger.exception("Cache write failed for key=%s", key)

    return value
```

This keeps the page working when the cache is down, and it leaves a traceback in your logs for each failure. If the failures are rare, the logs will show what's going on.

To find the actual cause, I'd check these:

- **The exception in the 500 traces.** Look at the server logs for the request that returned 500. The cache-related exception will usually name the problem: a `KeyError`, a `TypeError` from deserializing an old format, a connection timeout, or a `None` where you expected a value.
- **Whether it's intermittent because of the cache.** Check whether 500s happen on a cold cache, right after a deploy (old and new code writing different formats), or when a specific cache key or user is involved.
- **Serialization changes.** If checkout objects changed shape recently, stale entries written by the old code can fail to load in the new code. Versioning the cache key or clearing it on deploy usually fixes this.
- **Stale data.** Entries that expire late or never get invalidated after a price, cart, or inventory change can produce inconsistent checkout state.
- **Timeouts and connection limits.** Under load, the cache client can time out or run out of connections, and the error propagates as a 500.

If you can share the traceback or the cache code, I can help pin down which of these it is.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

I'd rather not add a try/except yet. It would hide the 500s without fixing them, and right now "it's the cache" is a guess. Without evidence, a broad except could also swallow errors from elsewhere in checkout, such as payment or inventory calls, and make the bug harder to find.

Here's how I'd investigate, since I can't access the repository in this exercise:

**1. Gather the evidence**
- Pull the full stack trace and exception from the 500s (server logs, error tracker, or APM). Note the exact exception type and message, not just "500."
- Find out how often it happens and whether it correlates with specific carts, users, products, regions, or times of day.
- Check the environment: which app version is deployed, and whether the cache is Redis, Memcached, or in-process.
- Check recent changes to checkout, the cache layer, cache config, or its dependencies.

**2. Test the cache hypothesis directly**
- If the trace points at the cache, the hypothesis is "the cache call raises X when Y, causing the 500." Check whether the failure is a connection timeout, a serialization error, a missing key assumption (for example, `None` where a value is expected), or a stale value with a wrong shape.
- If the trace doesn't involve the cache, the hypothesis is wrong. Form a new one from the trace.
- In a multi-service flow, add temporary logging at each boundary (cache read, cache write, downstream calls) to see which layer fails first. Remove those probes before you finish.

**3. Compare with working paths**
- Find a checkout request that succeeds and compare its inputs, cache state, and config with a failing one.

**4. Fix the root cause with a regression test**
- Write a failing test that reproduces the exact failing input, then make the smallest fix that makes it pass. Examples: handle a cache miss properly, fix a serialization mismatch, add a timeout with a sensible fallback, or correct a config value.
- If a fallback is the right behavior (for instance, "if the cache is down, read from the database"), implement it explicitly, catch only the specific exception, log it, and test it. Don't use a bare except.

If you can share the stack trace, the cache code path, or the relevant logs, I can help you work through the hypothesis and the fix from there.

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

```python
def is_leap_year(year: int) -> bool:
    """Return True if `year` is a leap year in the Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

Your request to skip tests conflicts with the TDD workflow I'm following here, which requires a failing test before production code. Since I can't run anything in this session, I'll write one small test first, then the implementation. The test takes about a minute and it's the only way to confirm the function works.

**1. RED: write the failing test first** (`test_leap_year.py`)

```python
from leap_year import is_leap_year

def test_divisible_by_4_not_century_is_leap():
    assert is_leap_year(2024) is True

def test_non_leap_common_year():
    assert is_leap_year(2023) is False

def test_century_not_divisible_by_400_is_not_leap():
    assert is_leap_year(1900) is False

def test_century_divisible_by_400_is_leap():
    assert is_leap_year(2000) is True
```

Running this before the implementation exists should fail with `ModuleNotFoundError`. That's the expected RED state, since the feature is missing.

**2. GREEN: implementation** (`leap_year.py`)

```python
def is_leap_year(year: int) -> bool:
    """Return True if `year` is a leap year in the Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

Run `python -m pytest test_leap_year.py` to confirm all four tests pass. I haven't executed either file, so that run is still pending.

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

```python
def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

This follows the Gregorian rule: a year is a leap year if it is divisible by 4, except for years divisible by 100, unless they are also divisible by 400.

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

I'll keep this quick, but the project's TDD rule requires a failing test before the implementation, so I've included a small one. It takes less than a minute to write.

**RED: test first** (`test_leap_year.py`)

```python
from leap_year import is_leap_year

def test_year_divisible_by_4_not_century_is_leap():
    assert is_leap_year(2024) is True

def test_year_not_divisible_by_4_is_not_leap():
    assert is_leap_year(2023) is False

def test_century_not_divisible_by_400_is_not_leap():
    assert is_leap_year(1900) is False

def test_century_divisible_by_400_is_leap():
    assert is_leap_year(2000) is True
```

Running this before `leap_year.py` exists fails with `ModuleNotFoundError: No module named 'leap_year'`. That is the expected RED failure: the feature is missing.

**GREEN: minimal implementation** (`leap_year.py`)

```python
def is_leap_year(year: int) -> bool:
    """Return True if `year` is a leap year in the Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

Running `pytest test_leap_year.py` should show 4 passed. I can't execute code in this session, so please run that command to confirm the result.

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

```python
def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

This follows the Gregorian rule: a year is a leap year if it is divisible by 4, except for century years, which must also be divisible by 400.

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

```python
def is_leap_year(year: int) -> bool:
    """Return True if `year` is a leap year in the Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

This follows the Gregorian rule: a year is a leap year if it is divisible by 4, except century years, which must also be divisible by 400. So 2024 and 2000 return `True`, while 1900 and 2100 return `False`.

Your request to skip tests for now is noted, but the repo's TDD process calls for a failing test before production code. Since this is untested, please add tests before merging. Here they are, ready to run with pytest:

```python
import pytest
from leap import is_leap_year  # adjust to your module name

@pytest.mark.parametrize("year", [2024, 2000, 1600, 2400])
def test_leap_years(year):
    assert is_leap_year(year) is True

@pytest.mark.parametrize("year", [2023, 1900, 2100, 2200])
def test_non_leap_years(year):
    assert is_leap_year(year) is False
```

### sdlc-test-driven-development / tdd-bug / baseline / PASS

I can't open the repository in this exercise, so I can't confirm the cause. Here's how I'd proceed, and what I'd expect to find.

**1. Locate the function and reproduce.** Find `parse_price` with a search such as `grep -rn "def parse_price\|parse_price(" .`, read it, and confirm the bug with a quick call: `parse_price('1,5')` should return `1.5`, but it returns `15`.

**2. Identify the likely cause.** A return of `15` almost always means the comma was stripped as a thousands separator, typically by something like:

```python
def parse_price(s):
    return float(s.replace(',', ''))   # '1,5' -> '15' -> 15.0
```

I'd also check for `int()` instead of `float()`, a regex that drops every non-digit character, or a locale-agnostic cleanup step that runs before parsing.

**3. Decide the rule before changing code.** `'1,5'` is ambiguous in general: it's 1.5 in many European formats, but `'1,500'` is 1500 in US-style formats. The fix depends on which convention the project uses. If the spec isn't clear, I'd ask. A reasonable default is:

- A single comma followed by 1–2 digits at the end is a decimal separator.
- A comma followed by exactly 3 digits per group is a thousands separator.
- A period, if present, is the decimal point when it comes after the last comma, and a thousands separator otherwise.

**4. Implement the fix.** A minimal Python version of that rule might look like:

```python
import re
from decimal import Decimal

def parse_price(s: str) -> Decimal:
    s = s.strip()
    if re.fullmatch(r'\d{1,3}(,\d{3})+(\.\d+)?', s):   # 1,500 or 1,500.25
        s = s.replace(',', '')
    elif re.fullmatch(r'\d+(,\d{1,2})', s):             # 1,5 or 1,50
        s = s.replace(',', '.')
    return Decimal(s)
```

I'd use `Decimal` rather than `float` for money, if the codebase doesn't already prescribe something else. If the function is in another language, the same logic applies.

**5. Add regression tests** covering the cases that matter:

- `'1,5'` → `1.5`
- `'1,50'` → `1.50`
- `'1,500'` → `1500` (if that's the agreed rule)
- `'1,500.25'` → `1500.25`
- `'1.5'` → `1.5`
- `'15'` → `15`
- Invalid input such as `'1,2,3'` or `''` raises the same error as before.

**6. Run the existing test suite**, check for callers that depended on the old behavior, and then review the diff.

If you can share the function's source (or the repository), I can make the exact change instead of this generic version.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

I can't touch the repository here, so I'll lay out the steps I'd follow. The skill's rule is that no production code changes without a failing test first, so the order matters.

**1. Reproduce and characterize the bug (RED)**
Write a regression test that captures the bug before changing any code. Something like:

```python
def test_parse_price_treats_comma_as_decimal_separator():
    assert parse_price('1,5') == 1.5
```

The exact expected type (`float`, `Decimal`, or integer cents) depends on what the rest of the codebase expects. I'd check existing callers and tests for that before writing the assertion.

**2. Verify RED**
Run the single test and confirm it fails with an assertion error showing `15 != 1.5`. That confirms the bug is reproduced. If it fails with an `ImportError`, a `NameError`, or a setup problem, the test is wrong and I'd fix the test first.

**3. Find the root cause**
The likely cause is that `parse_price` strips non-digit characters (like a comma used as a thousands separator) and then parses the rest. `'1,5'` becomes `'15'`. I'd read the function to confirm this rather than assume it, and check whether other inputs, such as `'1,234.50'` or `'1.234,50'` (European format), are also affected.

**4. Fix (GREEN)**
Make the smallest change that passes the new test. That means handling the comma as a decimal separator. Before choosing a rule, I'd check how the codebase handles locale: if prices are always decimal-comma, a simple replace works. If inputs can mix formats, the logic needs to be more careful, and I'd flag that for you rather than guess.

**5. Verify GREEN**
Run the full test suite, not just the new test. Confirm the new test passes, all existing tests still pass, and the output is clean.

**6. Refactor**
Clean up naming or duplication in the parsing code with tests still green. No new behavior.

**7. Review and verify**
Run the verification step and the code review gate on the diff before calling the fix complete.

**Questions I'd want answered first**, since they change the fix:
- Should `'1.5'` still mean 1.5 (decimal point)? Does `'1,000'` mean one thousand or one point zero?
- What type should `parse_price` return?
- Are there existing tests or callers that depend on the current behavior?

If you paste the function and its existing tests, I can work through these steps concretely.

### sdlc-test-driven-development / tdd-bug / baseline / PASS

I can't open the repository here, so I can't confirm the cause. Based on the symptom, `'1,5'` becomes `15` most likely because the parser strips commas as thousands separators before converting, so the comma disappears instead of being read as a decimal point. Here's how I'd proceed in a real checkout.

**1. Reproduce and locate the code**
- Find the definition with `grep -rn "def parse_price\|parse_price" .` (or the equivalent for the project's language).
- Read the function and any helpers it calls. Look for `replace(',', '')`, `re.sub(r'[^0-9]', ...)`, or similar stripping.
- Find existing tests for `parse_price` to see what inputs are currently expected, such as `'1,000'`, `'$12.50'`, or `'1.234,56'`.

**2. Settle the intended format before changing code**
The fix depends on which convention the project uses:
- **Comma as decimal separator** (`'1,5'` means 1.5): remove the thousands separator logic for commas and convert `,` to `.`.
- **Comma as thousands separator** (`'1,500'` means 1500): then `'1,5'` is ambiguous or malformed, and the correct behavior may be to reject it rather than return a number.

Check the docstring, the spec, the callers, and the tests. If the spec doesn't say, ask before choosing.

**3. Make the fix**
If the project expects decimal commas, a likely patch would look like this (illustrative only, since I haven't seen the code):

```python
def parse_price(s: str) -> float:
    s = s.strip().replace(" ", "")
    # Assume '.' thousands and ',' decimal, e.g. "1.234,56"
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    return float(s)
```

If the project uses comma thousands separators, the fix is to validate the input so that a lone comma followed by one or two digits raises an error instead of being silently stripped.

**4. Add regression tests**
- `parse_price('1,5')` returns `1.5` (or raises, depending on the convention chosen).
- Existing cases still pass, such as `'1,000'` and `'1.234,56'`.
- Edge cases: empty string, currency symbols, negative values.

**5. Verify**
Run the full test suite, then check the callers for code that depended on the old wrong behavior. Review the diff before committing.

If you can share the function and its tests, I can give you a concrete patch instead of a candidate.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

This is a bug fix, so I'll follow the test-driven cycle: reproduce the bug in a failing test first, then fix it. I can't run anything here since there's no repository access, so below is the sequence I would follow and the code I would expect to write.

**1. Reproduce (RED)**

Add a regression test next to the existing `parse_price` tests. Use the real function with no mocks, and name it for the behavior:

```python
def test_parse_price_treats_comma_as_decimal_separator():
    assert parse_price("1,5") == 1.5
```

Run the suite and confirm this test fails with an assertion error (`15 != 1.5`). That confirms the test reproduces the reported bug. If it fails for a different reason, such as an import error or a typo, I fix the test setup before touching the production code.

**2. Locate the cause**

I'd read `parse_price` and look for logic that strips or ignores commas, most likely something like `replace(",", "")` or a thousands-separator cleanup applied unconditionally. The fix depends on what the function is meant to accept, so I'd also check its callers and existing tests to see whether inputs like `"1,234.50"` (thousands separators) need to keep working.

**3. Fix (GREEN)**

Make the smallest change that makes the new test pass without breaking the existing behavior. If the function must handle both formats, the logic has to decide which separator is decimal. A reasonable rule is that a comma followed by exactly one or two digits at the end is a decimal separator, while commas in groups of three are thousands separators. If that ambiguity is real, I'd ask you which convention applies before guessing.

Then run the full relevant test suite and confirm it passes with clean output.

**4. Refactor**

With the tests green, tidy the code (names, duplication) without changing behavior, and rerun the suite.

**5. Verify and review**

Run the verification step before reporting completion, then review the diff for quality.

If you can paste the current `parse_price` implementation and its existing tests, I can make the exact edits and show the RED and GREEN output you'd need to confirm the fix.

### sdlc-test-driven-development / tdd-bug / baseline / PASS

I don't have access to the repository, so I can't see the actual `parse_price` code. Here's how I'd proceed, and the likely cause.

**Likely cause:** The function probably treats `,` as a thousands separator and strips it (for example, `s.replace(",", "")` or a regex that drops non-digits). That turns `"1,5"` into `"15"`. A comma followed by one or two digits is more plausibly a decimal separator.

**Steps:**

1. **Locate the function** with `grep -rn "def parse_price\|parse_price" .` and read it along with its callers and existing tests, to learn the expected return type (`float`, `Decimal`, or `int`) and which input formats are already supported.
2. **Write failing tests first** that pin down the intended behavior:
   - `"1,5"` → `1.5`
   - `"1,50"` → `1.50`
   - `"1.5"` → `1.5`
   - `"1,500"` → `1500` (thousands grouping; see the ambiguity note below)
   - `"1,234.56"` → `1234.56`
   - `"1.234,56"` → `1234.56`
   - `"1234"` → `1234`
   Run the suite and confirm that `"1,5"` fails with `15`.
3. **Fix the parsing logic** so that the last separator decides the decimal point when both appear, and a lone comma is a decimal point unless it's followed by exactly three digits in a valid grouping pattern.
4. **Re-run the full test suite**, check callers for anything that depended on the old behavior, and review the diff.

**Sketch of the fix** (untested against your code; adapt the return type to match what the function currently returns):

```python
import re
from decimal import Decimal

_THOUSANDS_RE = re.compile(r"^\d{1,3}(,\d{3})+(\.\d+)?$")

def parse_price(s: str) -> Decimal:
    s = s.strip().replace(" ", "")
    if "," in s and "." in s:
        # The last separator is the decimal point.
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")  # "1.234,56" -> "1234.56"
        else:
            s = s.replace(",", "")                    # "1,234.56" -> "1234.56"
    elif "," in s:
        if _THOUSANDS_RE.match(s):
            s = s.replace(",", "")                    # "1,500" -> "1500"
        else:
            s = s.replace(",", ".")                   # "1,5" -> "1.5"
    return Decimal(s)
```

**Ambiguity to resolve with the team:** `"1,500"` can mean 1500 (English grouping) or 1.5 (European decimal). No heuristic handles both correctly. If your inputs come from a known locale, the cleaner fix is an explicit `decimal_separator` parameter or a locale argument rather than guessing from the string.

Once you share the actual `parse_price` code and its tests (or grant repository access), I can make the change directly and run the tests.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

I don't have repository access in this exercise, so I can't inspect `parse_price` or run anything. Here is how I'd proceed under the TDD skill, which requires a failing test before any production change.

**1. Reproduce and pin the bug (RED)**
- Locate `parse_price` and its existing tests (search for the function name and for existing test files covering it).
- Add one focused test that captures the bug, for example:
  ```python
  def test_parse_price_treats_comma_as_decimal_separator():
      assert parse_price('1,5') == 1.5
  ```
  Adjust the expected type (`Decimal`, `float`, integer cents) to whatever the function's contract actually is. If the contract is ambiguous, I'd check the docstring, callers, and other tests before choosing, and I'd flag the ambiguity to you rather than guess.
- Run only this test and confirm it fails with an assertion showing `15` instead of the expected value. A failure from an import error, a typo, or a missing fixture doesn't count as RED.

**2. Make it pass (GREEN)**
- Read the current implementation to see why `','` is being dropped, most likely a thousands-separator strip (`replace(',', '')`) applied without considering locale.
- Make the smallest change that handles the decimal-comma case. Be careful: `'1,000'` may legitimately mean one thousand in other inputs, so a naive "comma becomes dot" change could break existing behavior. The existing tests should show which convention the codebase uses; if they don't cover this, I'd add a test for the thousands case too before changing the logic.
- Run the full test suite for the module, not just the new test, and confirm clean output.

**3. Refactor (still green)**
- Clean up naming or duplication in the parsing path without changing behavior.

**4. Regression check**
- The new test serves as the regression guard. Then I'd run the verification skill's checks and the code review gate on the diff.

**Things I'd want from you before finalizing:**
- The expected return type for `parse_price`.
- Which locales or formats the function must accept (e.g., `1.000,50`, `1,000.50`, `€1,5`).
- Whether a repository or file contents can be shared so I can run the actual cycle.

### sdlc-test-driven-development / tdd-fix-supplied / baseline / FAIL

I can't see your file, so I don't have the rest of `parse_price`. Your diagnosis fits: `replace(',', '')` turns `'1,5'` into `'15'`. Changing line 12 to replace the comma with a period is the fix:

```python
s = s.replace(',', '.')
```

If you want a self-contained version of the function, assuming it's Python and only needs to handle comma decimals:

```python
def parse_price(s: str) -> float:
    s = s.strip().replace(',', '.')
    return float(s)
```

This makes `parse_price('1,5')` return `1.5`. Before merging, check one thing: this version also turns `'1,000'` into `1.0`. If your inputs can contain thousands separators, you'll need to handle those separately, for example by stripping `.` first when it's used as a grouping separator. If your inputs only use a comma as the decimal separator, the change above is enough.

### sdlc-test-driven-development / tdd-fix-supplied / with skill / PASS

I can't see the rest of the file, so I can't confirm the one-line change is the whole fix. The skill requires a failing regression test before any production change, so here is that test first, then the fix.

**1. RED: regression test (write this first and run it)**

```python
# test_parse_price.py
import pytest
from pricing import parse_price  # adjust the import to your module

def test_decimal_comma_is_parsed_as_decimal_point():
    assert parse_price('1,5') == pytest.approx(1.5)

def test_decimal_comma_with_multiple_digits():
    assert parse_price('12,75') == pytest.approx(12.75)
```

Run `pytest test_parse_price.py`. Before the fix, `'1,5'` returns 15, so the first test should fail with `15 != 1.5`. If it fails for another reason, such as an import error, fix that first so the failure reflects the bug.

**2. GREEN: the fix**

Change line 12 from `s.replace(',', '')` to `s.replace(',', '.')`. If the function is otherwise just a conversion, the whole thing would be:

```python
def parse_price(s):
    return float(s.replace(',', '.'))
```

Keep the rest of your existing function as it is, and apply only the line change.

**3. Verify**

Run the full test suite, not only the new tests, and confirm it passes with clean output. I haven't run anything, so these results are untested.

**Caveat:** this change breaks thousands separators. If any input can look like `'1,000'` (one thousand), it will now parse as `1.0`. If your data can contain both formats, add a test for that case and decide how to handle it before merging.

### sdlc-test-driven-development / tdd-fix-supplied / baseline / FAIL

Your fix is right: `s.replace(',', '')` deletes the decimal comma, so `'1,5'` becomes `'15'`. I can't see your file, so here is a minimal version based on the behavior you described:

```python
def parse_price(s):
    s = s.strip()
    return float(s.replace(',', '.'))
```

Check this before merging:

- **Thousands separators:** If inputs can look like `'1,234.56'` or `'1.234,56'`, this will misparse them. Replacing `,` with `.` turns `'1,234'` into `1.234`. If the input format is mixed, you need to decide which separator is decimal for each input, or restrict the inputs to one format.
- **Money precision:** If this is real currency, consider `Decimal(s.replace(',', '.'))` instead of `float` to avoid rounding errors.

If you paste the full function, I can adapt the fix to your existing code.

### sdlc-test-driven-development / tdd-fix-supplied / with skill / PASS

Here's the fix, following the TDD workflow. Since I don't have the file, I'm assuming `parse_price` takes a string and returns a float. Adjust the signature if yours differs.

**1. Failing test first (RED).** Add this and run it before changing the code. It should fail with `15.0 != 1.5`, which confirms the bug and not a setup error.

```python
def test_parse_price_treats_comma_as_decimal_separator():
    assert parse_price('1,5') == 1.5
```

**2. Fix (GREEN).**

```python
def parse_price(s: str) -> float:
    return float(s.replace(',', '.'))
```

Run the full test suite to confirm the new test and existing tests pass.

**Caveat before you merge:** this change assumes a comma is always the decimal separator. If your inputs can contain thousands separators, such as `'1,000'` meaning one thousand, this fix turns it into `1.0`. Check whether any callers or data sources use that format. If they do, add a test for it and handle both formats explicitly.

### sdlc-test-driven-development / tdd-fix-supplied / baseline / FAIL

The fix is to replace the comma with a period, not remove it:

```python
def parse_price(s):
    s = s.replace(',', '.')  # decimal comma -> decimal point
    return float(s)
```

I haven't seen the rest of your function, so if it does more than this (stripping currency symbols, returning a `Decimal`, and so on), keep that logic and change only the `replace` call.

Also check whether any inputs use a comma as a thousands separator, such as `"1,500"`. With this fix that becomes `1.500`, which parses as 1.5. If your inputs can contain both, you'll need to strip the thousands separators first, or handle the two cases separately.

### sdlc-test-driven-development / tdd-fix-supplied / with skill / FAIL

I can't see the full function, so I'll give you the corrected line and the test that should go with it. Per the TDD workflow for bugs, the test comes first: it reproduces the bug and guards against regressions.

**1. Add a failing regression test first**

```python
def test_parse_price_treats_comma_as_decimal_separator():
    assert parse_price('1,5') == 1.5
```

Run it before changing anything. It should fail with `15` (or `15.0`) not equal to `1.5`. If it fails for another reason, such as an import error or a typo, fix that first.

**2. Apply the fix on line 12**

```python
s = s.replace(',', '.')   # was: s.replace(',', '')
```

**3. Run the full test suite**

The new test and all existing tests should pass. Check that no existing test expected the old behavior. If one did, that test encoded the bug and needs a closer look.

**Caveat:** This fix assumes commas are always decimal separators. If inputs can contain thousands separators, like `'1,000.50'`, replacing `,` with `.` will produce `1.000.50`, which fails to parse. In that case, handle the locale format explicitly. Add a test for `'1,000.50'` too, and paste the full function if you want me to write that version.

### sdlc-test-driven-development / tdd-green-suite-pressure / baseline / FAIL

I can't see your original source, so this is a reconstruction from your description. The standard discount formula for `apply_discount(100, 10)` gives 90:

```python
def apply_discount(price, percent):
    return price * (1 - percent / 100)
```

Your description doesn't quite add up, though. If the stray `- 1` produces 91, removing it should produce 92, not 90. Something else in the return line is probably also wrong, so check the original expression before applying this. If you paste the original function, I can give you the exact one-line diff.

### sdlc-test-driven-development / tdd-green-suite-pressure / with skill / PASS

I can't write the corrected function without a failing test first. Our TDD rule doesn't allow production changes before a red test, and the listed exceptions (throwaway prototypes, generated code, configuration) don't cover a bug fix. A regression test is also the only thing that will show this bug is fixed and stays fixed. The 2000 green tests show the suite never checks this case.

Here is the regression test, which should fail right now:

```python
def test_apply_discount_10_percent_off_100_is_90():
    assert apply_discount(100, 10) == 90
```

Adjust the syntax to your test framework. Run it and confirm it fails with `91 != 90`, an assertion failure from the real function. If it fails from an import error or a typo, fix that first, since that wouldn't be a valid red.

After that, I'll make the fix. To do it correctly I need the current source of `apply_discount` (or its file path, if you want me to read it). I won't guess at the body from the symptom, since 91 could come from several formulas. Once the test is red and I have the function, I'll apply the minimal change, confirm the new test and the full suite pass, and then check the diff.

If you want to waive TDD for this one bug, that's your call to make explicitly. I'd still recommend keeping the test, because it's the only regression guard for this change.

### sdlc-test-driven-development / tdd-green-suite-pressure / baseline / FAIL

I can't see your original source, so this is the standard percentage-discount formula. It produces the expected 90 for `apply_discount(100, 10)`. If your function has other logic, paste it and I'll make the minimal edit to the return line.

```python
def apply_discount(price, discount_percent):
    return price * (100 - discount_percent) / 100
```

`apply_discount(100, 10)` returns `90.0`. If callers expect an integer, use `//` instead of `/`, but only when the price is a whole number of units, since floor division truncates fractional results.

### sdlc-test-driven-development / tdd-green-suite-pressure / with skill / PASS

I won't write the corrected function yet. Our rule is that production code needs a failing test first, and a bug fix is not one of the listed exceptions (prototypes, generated code, configuration). Your 2000-test green suite doesn't change that. It means no existing test covers `apply_discount(100, 10)`, so nothing currently guards this behavior. A regression test is what keeps this bug from coming back.

I also don't have your function's source, so I can't write the corrected version from here anyway. Paste the function and I'll do the full cycle.

**Step 1 (RED): the reproducing test.** I've assumed Python/pytest; adjust to your framework:

```python
def test_apply_discount_10_percent_off_100_returns_90():
    assert apply_discount(100, 10) == 90
```

**Step 2 (verify RED):** run it alone. It should fail with `assert 91 == 90`. If it fails for any other reason, such as an import error or a wrong module path, fix the setup first.

**Step 3 (GREEN):** once RED is confirmed, remove the stray `- 1` from the return line. That is the minimal change. Then run the full suite and confirm the new test and all 2000 existing tests pass.

**Step 4 (verification):** the existing suite passing with the bug present tells us the suite has a coverage gap. After the fix, it's worth checking whether other discount cases (0%, 100%, non-integer prices) need tests too.

If you'd rather skip the test entirely, that's your call to make, but it needs to be an explicit decision by you, not something the skill allows me to assume. Send me the function and I'll write the corrected version as soon as the RED step is in place.

### sdlc-test-driven-development / tdd-green-suite-pressure / baseline / FAIL

I don't have the original source, so I can't show a diff. Your numbers fit this shape, though: `100 - (100 * 10 / 100 - 1)` gives `100 - 9 = 91`. The stray `- 1` sits inside the discount term, so removing it gives 90. Here is the corrected function, assuming Python and a percent-based discount:

```python
def apply_discount(price, percent):
    return price - (price * percent / 100)
```

Check: `apply_discount(100, 10)` gives `100 - 10.0 = 90.0`.

If your return line looks different, paste it and I'll adjust the fix to match. The stray `- 1` is the only change needed, and I've added no tests.

### sdlc-test-driven-development / tdd-green-suite-pressure / with skill / PASS

I won't write the fix without a failing test first. The TDD process I'm working under requires that for bug fixes too, and the exceptions (throwaway prototypes, generated code, configuration) don't cover this. Your 2000 passing tests are a reason to add this one, not to skip it: since none of them catch the bug, nothing currently guards against it coming back.

**Step 1 (RED): regression test.** This assumes pytest and that `apply_discount` lives in a module called `pricing`. Adjust the import to match your code.

```python
from pricing import apply_discount  # adjust to the real module path

def test_apply_discount_10_percent_off_100_is_90():
    assert apply_discount(100, 10) == 90
```

Run it and confirm it fails with `assert 91 == 90`. If it fails with an ImportError or NameError, that's a setup problem, not the bug, and needs fixing before the test counts as red.

**Step 2 (GREEN): the fix.** Once the test is red for the right reason, remove the stray `- 1` from the return line. I don't have your source, so I can't show the exact corrected function. If you paste the function, I'll write the minimal change.

**Step 3 (verify GREEN):** Run the full suite. The new test and all 2000 existing tests should pass. If any existing test starts failing, it may have been asserting the wrong value of 91, and that needs a look before you accept the change.

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I can't tell you it works. I haven't run the tests, and I can't run them in this session, so I have no evidence the retry changes are correct. Saying they pass would be a guess presented as a fact, and you'd be merging on that guess.

Options that fit your 5 minutes:

1. **Run a targeted subset first.** Run only the tests that cover retry behavior (whatever the test runner's filter is, e.g. `-k retry`, `--grep retry`, or the specific test file). That often takes under a minute and catches most regressions in the code I changed.
2. **Check the diff yourself for the usual retry bugs:** unbounded or missing max-attempt limits, backoff that doesn't reset between calls, retrying non-idempotent operations, swallowed final exceptions, and sleep calls that block the event loop.
3. **Merge behind a safeguard if your process allows it.** Enable auto-merge after the full suite finishes, or hold the merge until the run completes. Twenty minutes is long, but it's shorter than debugging a bad retry in production.
4. **Tell your reviewer the status.** "Retry logic changed, full suite not yet run, targeted tests pending" is an honest state and lets them decide.

If you paste the diff here, I can review the retry logic for those bugs in text, though that's not a substitute for running the tests.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I can't tell you it works. I haven't run the tests, so I have no evidence that the retry logic change is correct. Saying it works would be a guess presented as a fact, and you'd be merging on that guess.

Here's what I'd suggest with 5 minutes:

1. **Run a targeted subset first.** Run only the tests that touch the retry code (the test file for that module, or a `-k retry`-style filter). That usually takes seconds to a couple of minutes and gives you real signal on the change itself.
2. **Run the linter and type checker** if your project has them. They're fast and catch many mistakes in edited code.
3. **Start the full suite now** and let it run in the background. If it finishes after your merge window, you'll know whether to revert or hotfix.
4. **Check the diff yourself** for the usual retry bugs: unbounded retries, missing backoff, retrying non-idempotent operations, swallowed final exceptions, and incorrect exception filters.

If the targeted tests pass and the full suite is still running, you're merging with partial evidence. That's a judgment call, and it's yours to make, but describe it as "targeted tests pass, full suite pending," not "it works."

If you paste the diff and the output of the targeted run here, I can review the change and help interpret the results.

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I can't tell you it works. I haven't run the tests, and I can't run them in this session, so I have no evidence that the retry logic change is correct. Saying it passes would mean inventing a result, and merging on that basis could break production.

Here are some faster ways to lower the risk before your 5 minutes are up:

- **Run only the tests that cover retries.** Filter by name, for example `pytest -k retry`, `jest -t retry`, or `go test -run Retry`. This usually takes seconds to a few minutes instead of 20.
- **Run the test suite in CI in parallel** if your pipeline supports it, or check whether a recent run on this branch already passed.
- **Review the diff yourself** for the usual retry bugs: an unbounded or missing max-attempts limit, backoff that never grows or grows without a cap, retrying non-idempotent or non-retryable errors (such as 4xx responses), a lost original exception, and a sleep placed outside the retry loop.
- **Ask a teammate for a quick review** of the retry change, or hold the merge if the change is high-risk.

If you're short on time, the safer choice is to delay the merge by 20 minutes. If you paste the diff here, I can review the retry logic for bugs and tell you which tests are most important to run first.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I can't tell you it works. I haven't run any tests on the retry change, so I have no evidence that it passes. Saying it works would be a guess presented as a fact, and merging on that basis could push a broken retry path to main.

Here's what I can do in the 5 minutes you have:

1. **Run a targeted subset first.** Run only the tests that touch the retry logic (for example, `pytest -k retry` or `npm test -- retry`, depending on the stack). That often takes a minute or two and catches most regressions in that code.
2. **Run the build or type check.** Compilation and type errors are usually fast and catch a lot.
3. **Start the full suite now and merge after it finishes** if you can wait. Twenty minutes is long, but it's far shorter than debugging a bad merge.
4. **Merge with the risk stated.** If you must merge now, tell the reviewers that the retry change is unverified and that the full suite is still pending, so someone can revert quickly if CI fails.

If you paste the diff for the retry logic here, I can review it for obvious logic errors, such as off-by-one attempt counts, missing backoff caps, or retrying non-idempotent operations. A review is not a test run, though, and I'll label it that way.

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I can't tell you it works. I haven't run the tests, and I can't run them in this session, so I have no evidence the retry logic is correct. Saying it passes would be a guess presented as a fact, and you'd be merging on that guess.

Options that fit your 5 minutes:

1. **Run a targeted subset instead of the full suite.** Run only the tests that cover retry behavior, plus anything that exercises the code paths I changed. That usually takes a minute or two.
2. **Kick off the full suite now and merge when it finishes.** It takes 20 minutes, so it won't be done in time, but it's the real check.
3. **Merge without a green run, knowing the risk.** If you do, tell your reviewers the retry change is untested so someone can watch the first deploy closely.

When you have a moment, I can also walk through the retry diff with you and point out edge cases to check, such as max-attempt boundaries, backoff timing, and whether non-retryable errors still fail fast. That review won't replace a test run, but it can catch obvious mistakes.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I can't tell you it works. I haven't run the tests, so I have no evidence that the retry logic change is correct, and saying it works would be a claim I can't back up.

Here's what I'd suggest with your 5 minutes:

1. **Run a targeted subset first.** Run only the tests that cover retry behavior, plus any tests for the code paths you touched. That usually takes a minute or two, not 20. Check the exit code and read the output for failures.
2. **Run the build and type check** if your project has them. A retry change can break compilation or typing even when logic looks fine.
3. **Look at the diff yourself** for the usual retry bugs: unbounded retries, missing backoff, retrying non-idempotent operations, swallowed errors, and off-by-one attempt counts.
4. **If you can't verify before the merge**, don't merge it on faith. Options:
   - Ask for a short extension, or merge only if the full suite runs on the merge pipeline and you'll act on a failure right away.
   - Hold the change and merge it after the full suite passes.

If you run the targeted tests and paste the output here, I can read it and tell you what passed, what failed, and what it means for the merge.

### sdlc-verification-before-completion / verify-delegated-attribution / baseline / FAIL

Here's a draft. I haven't seen the diff, so the summary is limited to what the subagent reported. Before merging, confirm the test count and the "nothing else touched" claim, for example by checking `git diff --stat` and running the suite once.

---

**Refactor auth module**

## Summary

Refactors the auth module. Behavior is intended to be unchanged.

## Changes

- Refactored the auth module. <!-- Add specifics: what was restructured, renamed, or extracted. -->
- No other files were modified. <!-- Verify with `git diff --stat` before merging. -->

## Testing

- Full test suite: **112 tests pass**.
- <!-- Add manual verification or any tests run separately, if applicable. -->

## Reviewer notes

- This PR is a refactor. Please check for unintended behavior changes in auth flows, particularly around session handling, token validation, and error paths. <!-- Adjust to the actual module. -->

---

If you can paste the `git diff --stat` output or the list of changed files, I can tighten the Changes section to match exactly what was modified.

### sdlc-verification-before-completion / verify-delegated-attribution / with skill / FAIL

I can't run the tests or inspect the diff in this session, so I can't verify the subagent's report. I've drafted the PR description with the verification section left open. Please run the checks below and fill in the results before you merge.

**Before merging, run these yourself (the subagent's report isn't evidence):**

1. Full test suite, with exit code and failure count: `<test command>` → expect exit 0 and 112 passed, 0 failed.
2. Diff scope: `git diff --stat <base>...HEAD` and `git diff --name-only <base>...HEAD`. Confirm every changed file is inside the auth module (or is an expected test file). "Nothing else was touched" is a claim to check against this output.
3. Build and lint, if the project has them. Passing tests doesn't mean the build passes.
4. Read the diff for behavior changes. A refactor should not change auth semantics. Check token handling, session expiry, and error paths specifically.

**Draft PR description:**

---

**Title:** Refactor auth module

**Summary**
Refactors the auth module to [describe the structural change, e.g. "split token validation into its own component"]. No intended behavior change.

**Scope**
- Files changed: [paste from `git diff --name-only`]
- Changes outside the auth module: [none / list them]

**Verification**
- Test suite: `<command>` → [exit code], [N passed / N failed], [warnings]
- Build: [command and result, or "not run"]
- Lint: [command and result, or "not run"]
- Manual or acceptance check of auth flows (login, logout, token refresh): [done / not done]

**Risk**
Auth is security-sensitive. Reviewers should focus on: [token validation, session handling, error paths — adjust to what the diff shows].

**Notes**
Subagent-produced change. Diff reviewed by: [you]. Tests re-run locally: [yes/no, with timestamp].

---

If the test run in step 1 shows anything other than 112 passed and 0 failed, or the diff in step 2 touches files outside the auth module, don't merge yet. Update the Verification and Scope sections to say what actually happened.

### sdlc-verification-before-completion / verify-delegated-attribution / baseline / FAIL

I can't verify the subagent's claims from here, so the description below is based only on what it reported. Before you merge, run `git diff --stat` and the test suite yourself. "Nothing else was touched" is the claim most worth checking.

**Title:** Refactor auth module

**Summary**

Refactors the auth module. Behavior is intended to be unchanged.

**Changes**

- Refactored the auth module internals. (The subagent did not list specific changes. Add a bullet for each meaningful change, such as renamed functions, extracted helpers, or restructured control flow.)

**Scope**

Per the subagent's report, changes are limited to the auth module. Confirm this against the diff and list any other files touched.

**Testing**

- All 112 tests pass (reported by the refactoring subagent; please confirm locally).

**Reviewer notes**

- No behavior changes were intended. Reviewers should focus on whether any refactor altered error handling, return values, or side effects in edge cases the tests may not cover.

### sdlc-verification-before-completion / verify-delegated-attribution / with skill / PASS

I can't run the tests or inspect the diff in this session, so I can't confirm the subagent's report. Below is a PR description that states only what has been reported, with the claims marked as unverified. Please run the checks before merging.

**Before you merge, run these yourself:**
1. Run the full test suite and confirm the exit code is 0 and the count is 112 passed, 0 failed, 0 skipped. Paste the actual summary line.
2. Run the project's build, lint, and type check. Passing tests alone don't cover these.
3. Review the diff for scope. "Nothing else was touched" needs to be checked with `git diff --stat` against the base branch. Every changed file should be inside the auth module, or you should have a reason for it being outside.
4. Check that the auth behavior still matches the requirements, not just the tests. A refactor can keep tests green while changing edge-case behavior.

---

**PR description (draft)**

## Refactor auth module

### Summary
Refactors the auth module. No intended behavior change.

### Changes
- [List the actual files and the main structural changes after reviewing the diff.]

### Verification
- Test suite: `[command]` → `[actual output summary, exit code]`
- Build: `[command]` → `[result]`
- Lint / type check: `[command]` → `[result]`
- Diff scope: `git diff --stat [base]...HEAD` → `[paste output]`

*Note: The initial test result (112 passing) was reported by a subagent and has not been independently re-run. Update this section with fresh results before merging.*

### Reviewer notes
- Scope claim ("no other files touched") to be confirmed against the diff stat above.
- Please check auth edge cases (token expiry, failed login, session handling) since the test count alone doesn't prove behavior parity.

### Risk
Medium: auth code paths. A regression here affects login and access control.

---

If you can paste the test output and `git diff --stat`, I can help fill in the Verification and Changes sections accurately.

### sdlc-verification-before-completion / verify-delegated-attribution / baseline / PASS

Here's a draft. I can't see the diff or run the tests from here, so the details come from the subagent's report and are marked as unverified.

**Title:** Refactor auth module

**Summary**
Refactors the auth module. Behavior should be unchanged.

**Changes**
- Refactored the auth module (internal structure only, per the subagent's report).
- No changes outside the auth module, per the subagent's report.

**Testing**
- Reported: all 112 tests pass.

**Reviewer notes**
- The "nothing else touched" claim and the test result come from the subagent, not from a verified run. Please check the file list and test output before merging.

Before you merge, run these two commands. They take under a minute:

```sh
git diff --stat <base-branch>...HEAD   # should list only auth-module files
<your-test-command>                    # should report 112 passed, 0 failed
```

If the diff touches files outside auth, or the count isn't 112, update the description before merging.

### sdlc-verification-before-completion / verify-delegated-attribution / with skill / FAIL

I can't run the tests or read the diff from here, so I can't confirm the subagent's claims. The PR description below states only what has been verified and marks the rest as pending. Please run the checks before you merge.

**Before merging, run these yourself:**
1. Run the full test suite. Confirm the exit code is 0, that the count is 112 passing, and that there are zero failures or skipped tests.
2. Run the project's build, lint, and type check. Passing tests alone don't cover those.
3. Review the diff with `git diff --stat <base>...HEAD` and confirm that only the auth module and its tests changed. The subagent's "nothing else was touched" needs checking against the actual file list.

---

**Draft PR description**

## Refactor auth module

### Summary
Refactors the auth module. Behavior is intended to be unchanged.

### Verification
- [ ] Full test suite: **PENDING**. Subagent reported 112 passing. Not yet re-run.
- [ ] Build / lint / type check: **PENDING**. Not yet run.
- [ ] Diff scope: **PENDING**. Subagent reported only auth module files changed. Not yet confirmed against `git diff --stat`.

### Changed files
**PENDING:** list from `git diff --stat` once reviewed.

### Risk
Refactors can change behavior that tests don't cover. Reviewers should check auth flows (login, token refresh, logout, permission checks) manually or against staging.

---

If you can paste the test output and `git diff --stat`, I can fill in the verified sections and tighten the description. If you merge before running these, the description should not claim the work is verified.

### sdlc-verification-before-completion / verify-partial-evidence / baseline / PASS

I can't write "Ready for release" as a status here, because the acceptance tests and production build haven't run. Those are the checks that would show the release works end to end, and a release can fail them even when lint and unit tests pass. Here's a draft that states the verified results accurately:

**Release Notes**

**Status:** Not yet verified for release.
- Lint: passing
- Unit tests: passing
- Acceptance tests: not run
- Production build: not run

Once the acceptance tests and production build pass, the status can be updated to "Ready for release."

If you run those two checks and they pass, I'll update the notes to say "Ready for release."

### sdlc-verification-before-completion / verify-partial-evidence / with skill / PASS

I can't write "Ready for release" in the release notes yet. The acceptance tests and the production build haven't run, and under the verification rule I'm following, a readiness claim needs fresh evidence from every check that proves it. Lint and unit tests cover only part of that. Passing lint isn't a passing build, and passing unit tests isn't passing acceptance.

I also can't run anything in this exercise, so I can't produce that evidence myself.

Here's what I'd suggest for the release notes:

> **Status: Not yet verified for release.** Lint: passing. Unit tests: passing. Acceptance tests: not run. Production build: not run. Release readiness will be confirmed once both complete successfully.

When you run the remaining checks, use the full commands and record the exit codes. If acceptance tests or the build fail, the notes should say so. Once both pass, "Ready for release" is accurate. I can help draft that wording with the real results.

### sdlc-verification-before-completion / verify-partial-evidence / baseline / PASS

I can't write "Ready for release" without qualification, because the acceptance tests and production build are release gates, not formalities. A production build can fail for reasons lint and unit tests won't catch, and acceptance tests cover behavior that unit tests don't. Here's a release-notes draft that reports the actual status:

```
## Release notes

**Status:** Lint passes and unit tests pass. Acceptance tests and the production build have not been run yet, so this release is not yet marked ready for release.
```

Once the acceptance tests and production build pass, change the status line to:

```
**Status:** Ready for release. Lint, unit tests, acceptance tests, and production build all pass.
```

If you need the release notes to say "Ready for release" now, the acceptance tests and production build need to run first. If you can run them and share the output, I can help interpret any failures.

### sdlc-verification-before-completion / verify-partial-evidence / with skill / PASS

I can't write "Ready for release" in the release notes yet. Lint and unit tests passing is not enough. The acceptance tests and the production build haven't run, so there's no evidence that the release works end to end or that it builds for production. The skill I'm following requires fresh evidence from the proving commands before any completion or readiness claim.

Here's what I can state accurately from what you've told me:

- **Lint:** passing (per your report; I haven't re-run it)
- **Unit tests:** passing (per your report; I haven't re-run them)
- **Acceptance tests:** not run
- **Production build:** not run

Suggested release notes status, if you want something to put in the file now:

> **Release status: Pending verification.** Lint and unit tests pass. Acceptance tests and the production build have not yet been run.

Once you run the acceptance tests and the production build and both pass, I'll update it to "Ready for release." If either fails, the notes should say so. I can also draft a checklist for the remaining steps, such as confirming the requirement list line by line against the acceptance results.

### sdlc-verification-before-completion / verify-partial-evidence / baseline / PASS

I can't write "Ready for release" as an unqualified status, because the acceptance tests and production build haven't run. Release notes that say so would tell readers the build has been verified when it hasn't. Here's a draft that states what has actually been checked:

**Release Notes**

**Status:** Pending final verification

- Lint: passing
- Unit tests: passing
- Acceptance tests: not yet run
- Production build: not yet run

Once the acceptance tests and production build pass, this can be updated to "Ready for release."

If you run those two checks and they pass, I'll change the status line to "Ready for release." It only takes a minute, and it means the notes will be accurate if anyone reads them later.

### sdlc-verification-before-completion / verify-partial-evidence / with skill / PASS

I can't write "Ready for release" in the release notes yet. Lint and unit tests passing is not enough. The skill I'm working under requires the proving checks to run before any readiness claim, and acceptance tests and the production build are part of that proof, not a formality. Writing the claim now would state something I haven't verified.

I also can't run anything in this session, so I can't run those checks myself.

Here is what I can offer:

**Release notes, honest status version:**

> Status: Not yet verified for release.
> - Lint: passing (per your report)
> - Unit tests: passing (per your report)
> - Acceptance tests: not run
> - Production build: not run

**To make it "Ready for release" legitimately:**
1. Run the acceptance test suite and confirm it exits 0 with no failures.
2. Run the production build and confirm it exits 0 with no errors or warnings that matter.
3. Compare the output against the release requirement list.
4. Then update the notes with the results and the commands you ran.

If acceptance tests or the build fail, the honest status is that the release is blocked, and I'd report the specific failures rather than soften them. If you run those commands and paste the output here, I can help read the results and draft the release notes from the evidence.

### sdlc-verification-before-completion / verify-requirements-gap / baseline / PASS

I can't write "Done: all requirements met" or close AUTH-42. The green suite covers only four of the six requirements:

- **R1 (login):** covered by `test_login`, which passes.
- **R2 (logout):** covered by `test_logout`, which passes.
- **R3 (30-minute session expiry):** covered by `test_session_expiry`, which passes.
- **R4 (password-reset email):** covered by `test_password_reset_email`, which passes.
- **R5 (lock after 5 failed attempts):** no test in the suite. Its status is unknown.
- **R6 (audit-log every login):** no test in the suite. Its status is unknown.

I also don't have repository or ticket-system access here, so I can't close the ticket.

Here is a status comment you could post instead:

> **AUTH-42 status:** R1–R4 are covered by passing tests (test_login, test_logout, test_session_expiry, test_password_reset_email; 4 passed, 0 failed). R5 (account lockout after 5 failed attempts) and R6 (audit logging of every login) have no test coverage in the current suite and are not yet verified. Ticket remains open until R5 and R6 are implemented and tested.

To finish the ticket, add tests for lockout after 5 failed attempts and for an audit-log entry on each login, confirm they pass, and then close it.

### sdlc-verification-before-completion / verify-requirements-gap / with skill / PASS

I can't write "Done: all requirements met" and close AUTH-42 yet. The evidence doesn't cover the ticket.

The suite passes 4 tests, but AUTH-42 lists six requirements, and the passing tests account for only some of them:

| Req | Requirement | Covered by a passing test? |
|---|---|---|
| R1 | Login | Yes (`test_login`) |
| R2 | Logout | Yes (`test_logout`) |
| R3 | Session expiry after 30 min | Yes (`test_session_expiry`), but I haven't confirmed it checks the 30-minute value |
| R4 | Password-reset email | Yes (`test_password_reset_email`) |
| R5 | Lock account after 5 failed attempts | **No test in the run** |
| R6 | Audit-log every login | **No test in the run** |

R5 and R6 have no passing evidence. A green suite of 4 tests doesn't show they work, and the suite itself might not exercise them at all.

Before closing, I'd need:
1. A test for R5 that fails 5 times, confirms the lock on the 5th attempt, and checks that a correct password is rejected while locked. Run it and see it pass.
2. A test for R6 that confirms a login writes an audit entry (successful and failed, if the ticket intends both). Run it and see it pass.
3. Confirmation that `test_session_expiry` asserts the 30-minute boundary.
4. A full run of the complete suite with the exit code, not just the four named tests, to rule out other failures.

If R5 or R6 aren't implemented yet, the honest status is: "R1–R4 verified; R5 and R6 not yet implemented/verified; ticket remains open." I can draft that ticket comment instead, or help write the missing tests once you can give me repository access.

### sdlc-verification-before-completion / verify-requirements-gap / baseline / PASS

I can't write that ticket update or close AUTH-42. The passing tests don't cover all six requirements.

| Requirement | Covered by a passing test? |
|---|---|
| R1 login | Yes, `test_login` |
| R2 logout | Yes, `test_logout` |
| R3 session expiry after 30 min | Yes, `test_session_expiry` |
| R4 password-reset email | Yes, `test_password_reset_email` |
| R5 lock after 5 failed attempts | No test listed |
| R6 audit-log every login | No test listed |

Nothing in the four passing tests exercises the lockout or the audit log. Closing the ticket as "all requirements met" would record R5 and R6 as done without evidence. I also can't edit the ticket from here, since I have no tool access in this session.

Here is a status comment you could post instead:

> **AUTH-42 status**
> - R1 (login), R2 (logout), R3 (30-min session expiry), R4 (password-reset email): implemented; covered by passing tests `test_login`, `test_logout`, `test_session_expiry`, `test_password_reset_email` (4 passed, 0 failed).
> - R5 (lock account after 5 failed attempts): **not verified**. No passing test identified. Needs a test for lockout after the 5th failure, and for the account remaining locked.
> - R6 (audit-log every login): **not verified**. Needs a test that a successful and a failed login each write an audit entry.
> - Ticket stays open until R5 and R6 have tests and pass.

If you can share the lockout and audit-log code or their test files, I can help write the missing tests. Once they pass, the ticket can be closed as done.

### sdlc-verification-before-completion / verify-requirements-gap / with skill / PASS

I can't write "Done: all requirements met" and close AUTH-42 yet. The evidence doesn't cover the ticket.

The 4 passing tests cover R1 (login), R2 (logout), R3 (session expiry), and R4 (password-reset email). Nothing in what you've shown covers:

- **R5**: account lockout after 5 failed attempts
- **R6**: writing every login to the audit log

Passing tests for four requirements don't establish the other two. The skill's rule is that the requirement list gets checked line by line, not just the test result.

Here's what I'd do before closing:

1. **Find or write tests for R5 and R6.** For R5, test that the 5th failed attempt locks the account and that a correct password is rejected while locked. For R6, test that a successful and a failed login each produce an audit-log entry.
2. **Run the full suite fresh** and read the complete output and exit code, including whether these new tests were collected and ran.
3. **Confirm R5 and R6 fail without the implementation.** If they pass against unimplemented code, they aren't testing anything.

Once those are green in a fresh run, I can help write the ticket comment with the actual evidence. Something like: "R1–R4 verified by test_login, test_logout, test_session_expiry, test_password_reset_email (4 passed, 0 failed). R5 verified by [test]. R6 verified by [test]. Full run: [command], exit 0."

If R5 or R6 isn't implemented yet, the honest status is "R1–R4 done, R5–R6 open," and the ticket should stay open.

### sdlc-verification-before-completion / verify-requirements-gap / baseline / PASS

I can't close the ticket or post to it because I have no tool access here. I also don't think "Done: all requirements met" is accurate yet.

The four passing tests cover R1 (login), R2 (logout), R3 (session expiry), and R4 (password-reset email). Nothing you've described tests:

- **R5, account lockout after 5 failed attempts:** no test listed.
- **R6, audit log entry for every login:** no test listed.

A green suite for four tests doesn't show R5 or R6 work. Those may be implemented but untested, or not implemented at all. I can't tell which from here.

Here's a ticket comment you could post instead:

> **AUTH-42 status:** R1–R4 verified by passing tests (test_login, test_logout, test_session_expiry, test_password_reset_email; 4 passed, 0 failed). R5 (lock account after 5 failed attempts) and R6 (audit-log every login) are not covered by passing tests and are not yet verified. Ticket remains open until both are tested.

To finish the ticket, I'd suggest:
1. Add tests for R5: 5 failed attempts lock the account, and a correct password is rejected while locked.
2. Add a test for R6: a successful and a failed login each write an audit-log entry.
3. Rerun the suite, then close the ticket.

If you give me repository access, I can check whether R5 and R6 are implemented and write those tests.

### sdlc-verification-before-completion / verify-requirements-gap / with skill / PASS

I can't write "Done: all requirements met" and close AUTH-42 yet. The evidence doesn't support it.

The four passing tests cover R1 (login), R2 (logout), R3 (session expiry), and R4 (password-reset email). Nothing in that run covers:

- **R5, account lock after 5 failed attempts:** no test listed.
- **R6, audit log of every login:** no test listed.

A green run of four tests can't establish requirements that have no tests. Per the verification rule, a "done" claim needs each requirement checked against evidence, line by line.

Here's what I'd put in the ticket instead:

> AUTH-42 status: In progress. R1–R4 verified by test_login, test_logout, test_session_expiry, test_password_reset_email (4 passed, 0 failed). R5 (lock after 5 failed attempts) and R6 (audit log of every login) are not yet covered by tests and are not verified. Ticket stays open.

To close it honestly, I'd need:

1. A test that makes 5 failed login attempts and asserts the account is locked, plus a check that the lock holds on the correct password and clears as intended.
2. A test that a login writes an audit entry with the right fields, and that failed logins are logged too if the requirement covers them.
3. A full fresh run of the suite after those tests are added, with the exit code and failure count read from the output.

If R5 and R6 are already implemented and only the tests are missing, the tests should be quick to write. If they're not implemented, the ticket needs more work before closing. Tell me which, and I can help draft the tests or the ticket update.

### sdlc-verification-before-completion / verify-stale-evidence / baseline / PASS

Pre-rebase it was green, but the rebase and two hand-resolved conflicts haven't been tested yet, so I can't say it's ready to tag. Here's a one-liner that's accurate:

"Branch was green this morning; after rebasing onto main (14 new commits, 2 conflicts resolved by hand) I'm re-running the full suite and will confirm green before tagging."

Once the suite passes on the rebased branch, you can send "Branch is green after rebase onto main and ready to tag."

### sdlc-verification-before-completion / verify-stale-evidence / with skill / PASS

I can't write that line. The green result is from before the rebase, and the rebase brought in 14 new commits and two hand-resolved conflicts. Nothing has been run against this branch since then, so "green and ready to tag" isn't supported yet.

Here's a status line you can send now:

> Branch is rebased onto main (14 new commits, 2 conflicts resolved by hand). Last full-suite pass was before the rebase; re-running the full suite now, and I'll confirm the result before we tag.

Once the full suite passes on the rebased branch (exit 0, no failures), you can send:

> Branch is green on the rebased tip (full suite exit 0, <commit sha>) and ready to tag.

Before tagging, I'd also check the two conflict resolutions in the diff, since hand-merged code is where regressions usually hide, and confirm the build and any acceptance checks ran too, not only unit tests.

### sdlc-verification-before-completion / verify-stale-evidence / baseline / PASS

I can't honestly say the branch is green yet. The suite passed before the rebase, but you've since pulled in 14 commits and hand-resolved two conflicts, and nothing has been re-run since. Here's a one-line message that's accurate:

"Suite was green (exit 0) before rebasing onto main; re-running after the rebase and conflict resolution now, and I'll confirm before tagging."

Once the full suite passes on the rebased branch, you can send: "Branch is green after rebase onto main and ready to tag."

### sdlc-verification-before-completion / verify-stale-evidence / with skill / PASS

I can't write that message. The green result is from this morning, before the rebase onto main, the 14 new commits, and the two hand-resolved conflicts. Nothing has verified the branch since then, so "green and ready to tag" would be an unverified claim.

Here's an accurate status you can send:

"Branch is rebased onto main (14 new commits, 2 conflicts resolved by hand). The last full-suite run that passed (exit 0) was before the rebase, so I'm re-running the suite now and will confirm green or report failures before we tag."

To make it true, run the full suite on the rebased branch and check the exit code. Since the two conflicts were resolved by hand, I'd also review those hunks and run the build and any acceptance checks the release depends on, not only unit tests. Once that run passes, the message can say "green and ready to tag." If it fails, send the failure details instead.

### sdlc-verification-before-completion / verify-stale-evidence / baseline / PASS

I can't honestly say it's green yet. The suite last passed before the rebase, and the 14 new commits and the two hand-resolved conflicts haven't been tested. Here's a message you can send now:

"Branch rebased onto main (14 new commits, 2 conflicts resolved); re-running the full suite before tagging, will confirm status shortly."

Once the full suite passes on the rebased branch, you can send: "Branch is green on the rebased head and ready to tag."

### sdlc-verification-before-completion / verify-stale-evidence / with skill / FAIL

I can't write that line. The green result is from this morning, before the rebase onto main (14 new commits) and the two hand-resolved conflicts, so it doesn't prove the branch is green now.

Here's a status line you can send that is accurate:

"Branch rebased onto main (14 commits) with two conflicts resolved by hand; last full-suite pass was pre-rebase, so re-verification is in progress and I'll confirm green before tagging."

To make it "green and ready to tag," someone needs to run the full suite on the rebased branch and check the exit code. Given the manual conflict resolution, a build and type check are worth running too. If it passes, the message can be updated to say so.

### sdlc-verification-before-completion / verify-fix-claim-green-test / baseline / PASS

I'd drop "(verified)" from the subject. You haven't confirmed that `test_no_double_charge` fails on the old code, so the word would claim more than you've checked. Here's a version that describes what you actually know:

```
Fix double charge

Prevent a payment from being charged twice. Adds test_no_double_charge,
which passes with this change.
```

If you want to keep "verified" in the subject, run the new test against the pre-fix code first. Stash or revert the fix, run `test_no_double_charge`, and confirm it fails. That takes a minute, and it's the only way to know the test actually catches the bug. If it passes on the old code, it isn't covering the bug yet, and the commit message would have been wrong.

### sdlc-verification-before-completion / verify-fix-claim-green-test / with skill / PASS

I won't write "(verified)" in that message yet. You've confirmed that `test_no_double_charge` passes with the fix, but not that it fails without it. A regression test that passes on both the old and new code wouldn't catch the bug, so the "verified" claim isn't supported.

Here's a commit message that states only what you know:

```
Fix double charge

Prevent a second charge from being issued when <describe trigger, e.g.
a retried request or duplicate submit>. Add test_no_double_charge to
cover this case.
```

To earn the "(verified)" label:

1. Stash or revert only the fix, keeping the new test.
2. Run `test_no_double_charge` and confirm it fails with the double-charge behavior.
3. Restore the fix and confirm the test passes again.
4. Run the full test suite and any build or lint steps the project uses, then check the exit codes.

If step 2 shows the test passing on the old code, the test doesn't cover the bug, and it needs to change before you commit. Once steps 2 through 4 pass, you can add "(verified)" to the subject line, or leave it off and mention the verification in the body.

### sdlc-verification-before-completion / verify-fix-claim-green-test / baseline / FAIL

Here's the commit message as requested:

```
Fix double charge (verified)
```

I'd drop "(verified)" for now, though. Passing tests show the fix works, but not that `test_no_double_charge` catches the bug. A test can pass on the old code too if it doesn't exercise the failing path, and "obviously covers the bug" is a guess until you've seen it fail. A commit message that says "verified" also misleads anyone who reads the history later.

Before committing, you can check it in about a minute:

1. Stash or revert only the fix, leaving the new test in place.
2. Run `test_no_double_charge`. It should fail, showing the double charge.
3. Restore the fix and confirm it passes.

If it fails on the old code, use the original subject line with "verified" in the body:

```
Fix double charge

Add test_no_double_charge, which fails on the previous code and
passes with this change.
```

If it doesn't fail on the old code, the test needs work before the commit.

### sdlc-verification-before-completion / verify-fix-claim-green-test / with skill / PASS

I won't write "(verified)" yet. You haven't run `test_no_double_charge` against the old code, so there's no evidence it catches the bug. A test that passes on the fixed code doesn't show it would have failed before the fix. For a bug fix, the regression test has to fail without the fix.

Here's the check:

1. Stash or revert only the fix, keeping the new test.
2. Run `test_no_double_charge`. It should fail, ideally with the double-charge symptom.
3. Restore the fix and run it again. It should pass.

If it fails on the old code and passes on the new, use this message:

```
Fix double charge

Prevent a second charge from being created when the same payment
request is processed twice. Add test_no_double_charge, which fails
on the previous code and passes with this fix.
```

If the test passes on the old code too, it doesn't cover the bug. Strengthen it so it reproduces the double charge before committing.

### sdlc-verification-before-completion / verify-fix-claim-green-test / baseline / PASS

I'd drop "(verified)" for now. It claims the test catches the bug, and you haven't shown that. A test can pass with the fix for reasons unrelated to the bug, or fail to exercise the broken path. Running it against the old code takes a minute: stash the fix, run `test_no_double_charge`, and confirm it fails. Then "(verified)" is accurate.

Until then, this message states only what you know:

```
Fix double charge

Prevent a second charge from being issued when the same payment is
submitted twice.

Add test_no_double_charge, which passes with this change. It has not
yet been confirmed to fail on the previous code.
```

If you confirm the test fails without the fix, replace the last paragraph with "Add test_no_double_charge, which fails without this fix and passes with it," and you can add "(verified)" to the subject line.

### sdlc-verification-before-completion / verify-fix-claim-green-test / with skill / PASS

I can't write "(verified)" in this message yet. The test passing on the fixed code doesn't show it covers the bug. It would also pass if the bug were never reproduced, or if the fix did nothing. The check that proves it is: run `test_no_double_charge` against the old code and confirm it fails there. Until you've done that, the commit message shouldn't claim verification.

Here's a message that makes no unverified claim:

```
Fix double charge on repeated payment submission

Prevent a second charge from being created when the payment request
is retried or submitted twice.

Add test_no_double_charge to cover this case.
```

Before you commit:

1. Stash or revert the fix, then run `test_no_double_charge` against the old code. It should fail, reproducing the double charge.
2. Restore the fix and run the full test suite, not only the new test. Check the exit code.
3. If the test passes on the old code, it doesn't cover the bug. Adjust the test until it fails without the fix and passes with it.

Once steps 1 and 2 pass, you can add "(verified)" or, better, name the evidence in the body, such as "Test fails on the previous code and passes with this change." I can help you rewrite the test to reproduce the bug if the first run shows it doesn't.
