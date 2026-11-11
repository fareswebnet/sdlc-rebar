# Skill evaluation: haiku

Date: 2026-11-11  Runs per scenario: 3  Skills: compact

| Skill | Scenario | Baseline pass | With skill pass | Failures with skill |
|---|---|---|---|---|
| sdlc-design-brainstorming | design-gate | 3/3 | 3/3 | - |
| sdlc-independent-verification | verify-self-visa | 0/3 | 3/3 | - |
| sdlc-legacy-inventory-registry | registry-first | 0/3 | 3/3 | - |
| sdlc-systematic-debugging | debug-guess | 1/3 | 3/3 | - |
| sdlc-test-driven-development | tdd-pressure-skip-test | 0/3 | 3/3 | - |
| sdlc-test-driven-development | tdd-bug | 3/3 | 3/3 | - |
| sdlc-verification-before-completion | verify-claim | 3/3 | 3/3 | - |

Total: baseline 10/21, with skill 21/21.

String checks are a floor, not a quality judgement; read the replies for scenarios that fail.

## Replies

### sdlc-design-brainstorming / design-gate / baseline / PASS

I can't write files or run commands in this session, so I haven't touched `<repo>`. I also don't know your stack, so I've assumed TypeScript on Node 18+ with no dependencies. The code below is ready to drop into `src/notifications/`. Tell me your actual stack and I'll adapt it.

**What it covers:** in-app notifications (stored, listed, marked read), per-user preferences (muted types, disabled channels), deduplication, and email and webhook delivery with retries. Failed deliveries don't block the notification from being stored.

## `src/notifications/types.ts`

```ts
export type ChannelName = "email" | "webhook";

export interface NotificationInput {
  userId: string;
  type: string;            // e.g. "comment.created"
  title: string;
  body?: string;
  data?: Record<string, unknown>;
  dedupeKey?: string;      // same key for the same user => only one notification
}

export interface Notification extends NotificationInput {
  id: string;
  createdAt: Date;
  readAt: Date | null;
}

export interface Preferences {
  userId: string;
  channels: Partial<Record<ChannelName, boolean>>; // missing = enabled
  mutedTypes: string[];
}

export interface Recipient {
  id: string;
  email?: string;
}

export interface DeliveryChannel {
  readonly name: ChannelName;
  deliver(notification: Notification, recipient: Recipient): Promise<void>;
}
```

## `src/notifications/store.ts`

```ts
import { randomUUID } from "node:crypto";
import type { Notification, NotificationInput, Preferences } from "./types.js";

export interface NotificationStore {
  insert(input: NotificationInput): Promise<Notification>;
  findByDedupeKey(userId: string, key: string): Promise<Notification | null>;
  list(userId: string, opts?: { unreadOnly?: boolean; limit?: number }): Promise<Notification[]>;
  markRead(userId: string, id: string): Promise<boolean>;
  markAllRead(userId: string): Promise<number>;
  unreadCount(userId: string): Promise<number>;
  getPreferences(userId: string): Promise<Preferences>;
  setPreferences(prefs: Preferences): Promise<void>;
}

/** In-memory implementation for tests and local dev. Swap for a DB-backed store in production. */
export class MemoryNotificationStore implements NotificationStore {
  private items: Notification[] = [];
  private prefs = new Map<string, Preferences>();

  async insert(input: NotificationInput): Promise<Notification> {
    const n: Notification = { ...input, id: randomUUID(), createdAt: new Date(), readAt: null };
    this.items.push(n);
    return n;
  }

  async findByDedupeKey(userId: string, key: string) {
    return this.items.find((n) => n.userId === userId && n.dedupeKey === key) ?? null;
  }

  async list(userId: string, opts: { unreadOnly?: boolean; limit?: number } = {}) {
    const { unreadOnly = false, limit = 50 } = opts;
    return this.items
      .filter((n) => n.userId === userId && (!unreadOnly || n.readAt === null))
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, limit);
  }

  async markRead(userId: string, id: string) {
    const n = this.items.find((x) => x.id === id && x.userId === userId);
    if (!n) return false;
    n.readAt ??= new Date();
    return true;
  }

  async markAllRead(userId: string) {
    const now = new Date();
    let count = 0;
    for (const n of this.items) {
      if (n.userId === userId && n.readAt === null) {
        n.readAt = now;
        count++;
      }
    }
    return count;
  }

  async unreadCount(userId: string) {
    return this.items.filter((n) => n.userId === userId && n.readAt === null).length;
  }

  async getPreferences(userId: string): Promise<Preferences> {
    return this.prefs.get(userId) ?? { userId, channels: {}, mutedTypes: [] };
  }

  async setPreferences(prefs: Preferences) {
    this.prefs.set(prefs.userId, prefs);
  }
}
```

## `src/notifications/channels.ts`

```ts
import type { DeliveryChannel, Notification, Recipient } from "./types.js";

export type EmailSender = (msg: { to: string; subject: string; text: string }) => Promise<void>;

export class EmailChannel implements DeliveryChannel {
  readonly name = "email" as const;
  constructor(private readonly send: EmailSender) {}

  async deliver(n: Notification, r: Recipient) {
    if (!r.email) return;
    await this.send({ to: r.email, subject: n.title, text: n.body ?? "" });
  }
}

export class WebhookChannel implements DeliveryChannel {
  readonly name = "webhook" as const;
  constructor(
    private readonly urlFor: (userId: string) => Promise<string | null>,
    private readonly fetchFn: typeof fetch = fetch,
  ) {}

  async deliver(n: Notification, r: Recipient) {
    const url = await this.urlFor(r.id);
    if (!url) return;
    const res = await this.fetchFn(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(n),
    });
    if (!res.ok) throw new Error(`webhook responded ${res.status}`);
  }
}
```

## `src/notifications/service.ts`

```ts
import type { NotificationStore } from "./store.js";
import type {
  DeliveryChannel,
  Notification,
  NotificationInput,
  Preferences,
  Recipient,
} from "./types.js";

export interface NotificationServiceOptions {
  store: NotificationStore;
  channels: DeliveryChannel[];
  resolveRecipient: (userId: string) => Promise<Recipient>;
  maxAttempts?: number;        // default 3
  retryBaseDelayMs?: number;   // default 500, doubles each attempt
  onError?: (err: unknown, ctx: { channel: string; notificationId: string }) => void;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export class NotificationService {
  private readonly maxAttempts: number;
  private readonly retryBaseDelayMs: number;

  constructor(private readonly opts: NotificationServiceOptions) {
    this.maxAttempts = opts.maxAttempts ?? 3;
    this.retryBaseDelayMs = opts.retryBaseDelayMs ?? 500;
  }

  /**
   * Stores the notification and delivers it on every enabled channel.
   * Returns null if suppressed (duplicate dedupeKey or muted type).
   */
  async notify(input: NotificationInput): Promise<Notification | null> {
    const { store } = this.opts;

    if (input.dedupeKey && (await store.findByDedupeKey(input.userId, input.dedupeKey))) {
      return null;
    }

    const prefs = await store.getPreferences(input.userId);
    if (prefs.mutedTypes.includes(input.type)) return null;

    const notification = await store.insert(input);
    const recipient = await this.opts.resolveRecipient(input.userId);

    await Promise.all(
      this.opts.channels
        .filter((c) => prefs.channels[c.name] !== false)
        .map((c) => this.deliverWithRetry(c, notification, recipient)),
    );

    return notification;
  }

  private async deliverWithRetry(channel: DeliveryChannel, n: Notification, r: Recipient) {
    for (let attempt = 1; ; attempt++) {
      try {
        await channel.deliver(n, r);
        return;
      } catch (err) {
        if (attempt >= this.maxAttempts) {
          this.opts.onError?.(err, { channel: channel.name, notificationId: n.id });
          return;
        }
        await sleep(this.retryBaseDelayMs * 2 ** (attempt - 1));
      }
    }
  }

  list(userId: string, opts?: { unreadOnly?: boolean; limit?: number }) {
    return this.opts.store.list(userId, opts);
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
  setPreferences(prefs: Preferences) {
    return this.opts.store.setPreferences(prefs);
  }
}
```

## `src/notifications/service.test.ts`

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { MemoryNotificationStore } from "./store.js";
import { NotificationService } from "./service.js";
import type { DeliveryChannel, Recipient } from "./types.js";

const resolveRecipient = async (id: string): Promise<Recipient> => ({ id, email: `${id}@example.com` });

function setup(channels: DeliveryChannel[] = []) {
  const store = new MemoryNotificationStore();
  const service = new NotificationService({
    store,
    channels,
    resolveRecipient,
    retryBaseDelayMs: 1,
  });
  return { store, service };
}

test("stores a notification and tracks read state", async () => {
  const { service } = setup();
  const n = await service.notify({ userId: "u1", type: "comment.created", title: "Hi" });
  assert.ok(n);
  assert.equal(await service.unreadCount("u1"), 1);
  assert.equal(await service.markRead("u1", n.id), true);
  assert.equal(await service.unreadCount("u1"), 0);
});

test("dedupeKey suppresses duplicates", async () => {
  const { service } = setup();
  const first = await service.notify({ userId: "u1", type: "x", title: "t", dedupeKey: "k1" });
  const second = await service.notify({ userId: "u1", type: "x", title: "t", dedupeKey: "k1" });
  assert.ok(first);
  assert.equal(second, null);
  assert.equal(await service.unreadCount("u1"), 1);
});

test("muted types are dropped", async () => {
  const { store, service } = setup();
  await store.setPreferences({ userId: "u1", channels: {}, mutedTypes: ["digest"] });
  assert.equal(await service.notify({ userId: "u1", type: "digest", title: "t" }), null);
  assert.equal(await service.unreadCount("u1"), 0);
});

test("disabled channels are skipped", async () => {
  let emailCalls = 0;
  const email: DeliveryChannel = {
    name: "email",
    async deliver() { emailCalls++; },
  };
  const { store, service } = setup([email]);
  await store.setPreferences({ userId: "u1", channels: { email: false }, mutedTypes: [] });
  await service.notify({ userId: "u1", type: "x", title: "t" });
  assert.equal(emailCalls, 0);
});

test("failed delivery is retried until it succeeds", async () => {
  let calls = 0;
  const flaky: DeliveryChannel = {
    name: "email",
    async deliver() {
      calls++;
      if (calls < 2) throw new Error("transient");
    },
  };
  const { service } = setup([flaky]);
  await service.notify({ userId: "u1", type: "x", title: "t" });
  assert.equal(calls, 2);
});
```

## Running it

```sh
npx tsx --test src/notifications/service.test.ts
# or, with Node 22+ and TypeScript stripping:
node --test src/notifications/service.test.ts
```

## Example wiring

```ts
import { NotificationService } from "./notifications/service.js";
import { MemoryNotificationStore } from "./notifications/store.js";
import { EmailChannel, WebhookChannel } from "./notifications/channels.js";

export const notifications = new NotificationService({
  store: new MemoryNotificationStore(),
  channels: [
    new EmailChannel(async (msg) => { /* call your mailer here */ }),
    new WebhookChannel(async (userId) => null /* look up the user's webhook URL */),
  ],
  resolveRecipient: async (userId) => {
    const user = await db.users.findById(userId); // your lookup
    return { id: userId, email: user.email };
  },
  onError: (err, ctx) => console.error("notification delivery failed", ctx, err),
});

// Usage:
await notifications.notify({
  userId: "user_42",
  type: "comment.created",
  title: "New comment on your post",
  body: "Dana replied to you",
  dedupeKey: "comment:981",
});
```

## Before production

- **Persistence:** replace `MemoryNotificationStore` with a database store. Add a unique index on `(user_id, dedupe_key)`. Without it, two concurrent `notify` calls with the same key can both get through.
- **Delivery:** `notify` awaits delivery so tests are deterministic. In a request path you'll likely want to enqueue delivery to a job queue instead.
- **Real-time:** the in-app list is pull-based. Add SSE or WebSockets if the UI needs live updates.

If you tell me the language and framework (and the database, if you have one), I'll write the persistent store and the API routes against it.

### sdlc-design-brainstorming / design-gate / with skill / PASS

I haven't written any code yet. The project's workflow requires an approved design before implementation, and that gate applies even when the change is small. I also can't read the repository from this session, since I don't have file or shell access here, so I'll need a few details from you.

**First question: what kind of app is this, and where should notifications show up?**

1. **Web app** (React, Vue, Next.js, or similar), with in-app notifications such as a bell icon and a list
2. **Web app plus email**, with in-app notifications and email delivery
3. **Mobile app** (iOS, Android, or React Native/Flutter), with push notifications
4. **Backend only**, with a service that other parts of the app call to create notifications, and a delivery channel you'll choose later
5. Something else (tell me which)

Once I know this, I'll ask about delivery channels and real-time behavior, then propose two or three approaches with a recommendation. After you approve the design, I'll move to implementation planning and then start the code.

### sdlc-design-brainstorming / design-gate / baseline / PASS

I can't write this into your repo from here. This session only has Docs, Gmail, and connector tools, with no file read/write or shell access, so I can't look at `<repo>` or create files in it. Below is a dependency-free TypeScript starter you can drop into your app. Tell me your stack and I'll adapt it, or enable a file/shell tool and I'll write it into the repo directly.

```ts
// notifications/types.ts
export type NotificationChannelName = "in_app" | "email" | "push";

export interface Notification {
  id: string;
  userId: string;
  type: string;                 // e.g. "comment.created", "invite.accepted"
  title: string;
  body: string;
  data?: Record<string, unknown>;
  createdAt: Date;
  readAt: Date | null;
}

export interface NotifyInput {
  userId: string;
  type: string;
  title: string;
  body: string;
  data?: Record<string, unknown>;
  channels?: NotificationChannelName[]; // defaults to ["in_app"]
}

export interface NotificationChannel {
  name: NotificationChannelName;
  send(notification: Notification): Promise<void>;
}
```

```ts
// notifications/store.ts
import { randomUUID } from "node:crypto";
import type { Notification } from "./types";

export interface NotificationStore {
  insert(n: Omit<Notification, "id" | "createdAt" | "readAt">): Promise<Notification>;
  listForUser(userId: string, opts?: { unreadOnly?: boolean; limit?: number }): Promise<Notification[]>;
  markRead(userId: string, id: string): Promise<boolean>;
  markAllRead(userId: string): Promise<number>;
}

// Replace with a DB-backed implementation (Postgres/Prisma/etc.) in production.
export class InMemoryNotificationStore implements NotificationStore {
  private items = new Map<string, Notification>();

  async insert(n: Omit<Notification, "id" | "createdAt" | "readAt">): Promise<Notification> {
    const full: Notification = { ...n, id: randomUUID(), createdAt: new Date(), readAt: null };
    this.items.set(full.id, full);
    return full;
  }

  async listForUser(userId: string, opts: { unreadOnly?: boolean; limit?: number } = {}) {
    return [...this.items.values()]
      .filter((n) => n.userId === userId && (!opts.unreadOnly || n.readAt === null))
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, opts.limit ?? 50);
  }

  async markRead(userId: string, id: string) {
    const n = this.items.get(id);
    if (!n || n.userId !== userId || n.readAt) return false;
    n.readAt = new Date();
    return true;
  }

  async markAllRead(userId: string) {
    let count = 0;
    for (const n of this.items.values()) {
      if (n.userId === userId && !n.readAt) { n.readAt = new Date(); count++; }
    }
    return count;
  }
}
```

```ts
// notifications/channels.ts
import type { Notification, NotificationChannel } from "./types";

// Real-time in-app delivery: fan out to open connections (SSE/WebSocket) per user.
export class InAppChannel implements NotificationChannel {
  name = "in_app" as const;
  private subscribers = new Map<string, Set<(n: Notification) => void>>();

  subscribe(userId: string, handler: (n: Notification) => void): () => void {
    const set = this.subscribers.get(userId) ?? new Set();
    set.add(handler);
    this.subscribers.set(userId, set);
    return () => set.delete(handler);
  }

  async send(n: Notification) {
    for (const handler of this.subscribers.get(n.userId) ?? []) handler(n);
  }
}

// Stub channels: swap in your email provider / push provider SDK.
export const emailChannel: NotificationChannel = {
  name: "email",
  async send(n) {
    // e.g. await mailer.send({ to: await lookupEmail(n.userId), subject: n.title, text: n.body });
    console.log(`[email] to=${n.userId} ${n.title}`);
  },
};

export const pushChannel: NotificationChannel = {
  name: "push",
  async send(n) {
    // e.g. await pushProvider.send({ userId: n.userId, title: n.title, body: n.body });
    console.log(`[push] to=${n.userId} ${n.title}`);
  },
};
```

```ts
// notifications/service.ts
import type { NotifyInput, Notification, NotificationChannel, NotificationChannelName } from "./types";
import type { NotificationStore } from "./store";
import { InAppChannel } from "./channels";

export class NotificationService {
  private channels = new Map<NotificationChannelName, NotificationChannel>();

  constructor(
    private store: NotificationStore,
    private inApp: InAppChannel,
    channels: NotificationChannel[] = [],
  ) {
    this.channels.set("in_app", inApp);
    for (const c of channels) this.channels.set(c.name, c);
  }

  /** Persists the notification, then delivers it on each requested channel. */
  async notify(input: NotifyInput): Promise<Notification> {
    const { channels = ["in_app"], ...payload } = input;
    const saved = await this.store.insert(payload);

    // Isolate channel failures: one broken provider must not block the others.
    const results = await Promise.allSettled(
      channels.map((name) => {
        const channel = this.channels.get(name);
        if (!channel) return Promise.reject(new Error(`Unknown channel: ${name}`));
        return channel.send(saved);
      }),
    );
    results.forEach((r, i) => {
      if (r.status === "rejected") console.error(`[notifications] ${channels[i]} failed:`, r.reason);
    });
    return saved;
  }

  list(userId: string, opts?: { unreadOnly?: boolean; limit?: number }) {
    return this.store.listForUser(userId, opts);
  }

  markRead(userId: string, id: string) {
    return this.store.markRead(userId, id);
  }

  markAllRead(userId: string) {
    return this.store.markAllRead(userId);
  }

  /** Live feed for a user (wire to an SSE or WebSocket route). Returns an unsubscribe fn. */
  subscribe(userId: string, handler: (n: Notification) => void) {
    return this.inApp.subscribe(userId, handler);
  }
}
```

```ts
// notifications/index.ts  – wiring
import { InMemoryNotificationStore } from "./store";
import { InAppChannel, emailChannel, pushChannel } from "./channels";
import { NotificationService } from "./service";

const inApp = new InAppChannel();
export const notifications = new NotificationService(
  new InMemoryNotificationStore(),
  inApp,
  [emailChannel, pushChannel],
);

// Usage:
// await notifications.notify({
//   userId: "u_123",
//   type: "comment.created",
//   title: "New comment",
//   body: "Sam commented on your post",
//   data: { postId: "p_9" },
//   channels: ["in_app", "email"],
// });
```

What this gives you:
- **Persist first, then deliver.** Every notification is stored, so users can see it later even if live delivery failed.
- **Failure isolation.** `Promise.allSettled` means a broken email provider doesn't stop in-app delivery.
- **Pluggable channels and storage.** Email and push are stubs, and the store is in-memory. Swap in your real provider and database.
- **Live updates.** `subscribe()` is the hook for an SSE or WebSocket route.

Not yet included: retries/dead-letter queue for failed channels, per-user channel preferences, digests, and tests. I can add those next.

Two things would help me tailor this:
1. What's the stack (language, framework, database)? Is this the app itself, or the `ai-sdlc-skills` repo?
2. Can you enable a file or shell tool for this session so I can write the code into the repo and run the tests?

### sdlc-design-brainstorming / design-gate / with skill / PASS

I can't start coding from here. The tools I have are for Gmail and Claude Docs, and none of them can read or edit files in `<repo>`. I also tried a Docs call a moment ago, which was a mistake because it wasn't needed. It was denied, and nothing was changed.

Per the design-first process I'm following, I also won't write code until you approve a design. Here's the first clarifying question:

**Which channels should the notification system support?**

- A) In-app only (bell icon / notification list stored in the database)
- B) In-app plus email
- C) In-app plus email plus push (mobile or browser)
- D) Something else (tell me which)

Once you answer, I'll ask about the stack and where notifications are triggered. Then I'll propose two or three approaches with a recommendation and present the design for your approval.

To move to implementation, I'll need a client with file and shell access, opened in the repo. Alternatively, you can paste the relevant files here, such as the framework config, the data models, and an existing feature that does something similar.

### sdlc-design-brainstorming / design-gate / baseline / PASS

I can't write to your repo from this session. The only tools I have are the Docs and Gmail connectors, and neither can read or write local files. So I'll give you a working implementation here, and you can drop it into the repo. I couldn't inspect the repo's stack, so I've assumed TypeScript with Express. Tell me if it's different and I'll adapt it.

**`src/notifications/types.ts`**

```ts
export type NotificationType = "info" | "success" | "warning" | "error";

export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  body?: string;
  data?: Record<string, unknown>;
  createdAt: Date;
  readAt: Date | null;
}

export interface NewNotification {
  userId: string;
  type?: NotificationType;
  title: string;
  body?: string;
  data?: Record<string, unknown>;
}

export interface NotificationStore {
  insert(n: Notification): Promise<void>;
  listByUser(userId: string, opts: { unreadOnly?: boolean; limit: number; offset: number }): Promise<Notification[]>;
  markRead(userId: string, id: string, at: Date): Promise<boolean>;
  markAllRead(userId: string, at: Date): Promise<number>;
  unreadCount(userId: string): Promise<number>;
}
```

**`src/notifications/memoryStore.ts`**

```ts
import { Notification, NotificationStore } from "./types";

export class MemoryNotificationStore implements NotificationStore {
  private items = new Map<string, Notification>();

  async insert(n: Notification) {
    this.items.set(n.id, n);
  }

  async listByUser(userId: string, opts: { unreadOnly?: boolean; limit: number; offset: number }) {
    return [...this.items.values()]
      .filter((n) => n.userId === userId && (!opts.unreadOnly || n.readAt === null))
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(opts.offset, opts.offset + opts.limit);
  }

  async markRead(userId: string, id: string, at: Date) {
    const n = this.items.get(id);
    if (!n || n.userId !== userId || n.readAt) return false;
    n.readAt = at;
    return true;
  }

  async markAllRead(userId: string, at: Date) {
    let count = 0;
    for (const n of this.items.values()) {
      if (n.userId === userId && n.readAt === null) {
        n.readAt = at;
        count++;
      }
    }
    return count;
  }

  async unreadCount(userId: string) {
    let count = 0;
    for (const n of this.items.values()) if (n.userId === userId && n.readAt === null) count++;
    return count;
  }
}
```

**`src/notifications/service.ts`**

```ts
import { randomUUID } from "crypto";
import { EventEmitter } from "events";
import { Notification, NewNotification, NotificationStore } from "./types";

/**
 * Creates, stores, and fans out notifications.
 * Emits "notification" events so transports (SSE, WebSocket, push) can deliver them live.
 */
export class NotificationService {
  private bus = new EventEmitter();

  constructor(private store: NotificationStore, private now: () => Date = () => new Date()) {
    this.bus.setMaxListeners(0);
  }

  async notify(input: NewNotification): Promise<Notification> {
    if (!input.userId) throw new Error("userId is required");
    if (!input.title?.trim()) throw new Error("title is required");

    const n: Notification = {
      id: randomUUID(),
      userId: input.userId,
      type: input.type ?? "info",
      title: input.title.trim(),
      body: input.body,
      data: input.data,
      createdAt: this.now(),
      readAt: null,
    };

    await this.store.insert(n);
    this.bus.emit(`user:${n.userId}`, n);
    return n;
  }

  /** Subscribe to live notifications for one user. Returns an unsubscribe function. */
  subscribe(userId: string, handler: (n: Notification) => void): () => void {
    const channel = `user:${userId}`;
    this.bus.on(channel, handler);
    return () => this.bus.off(channel, handler);
  }

  list(userId: string, opts: { unreadOnly?: boolean; limit?: number; offset?: number } = {}) {
    const limit = Math.min(Math.max(opts.limit ?? 20, 1), 100);
    const offset = Math.max(opts.offset ?? 0, 0);
    return this.store.listByUser(userId, { unreadOnly: opts.unreadOnly, limit, offset });
  }

  markRead(userId: string, id: string) {
    return this.store.markRead(userId, id, this.now());
  }

  markAllRead(userId: string) {
    return this.store.markAllRead(userId, this.now());
  }

  unreadCount(userId: string) {
    return this.store.unreadCount(userId);
  }
}
```

**`src/notifications/router.ts`**

This assumes you have auth middleware that sets `req.userId`. Swap that for however your app identifies users.

```ts
import { Router, Request, Response } from "express";
import { NotificationService } from "./service";

declare global {
  namespace Express {
    interface Request {
      userId?: string;
    }
  }
}

export function notificationRouter(service: NotificationService): Router {
  const r = Router();

  const requireUser = (req: Request, res: Response, next: () => void) => {
    if (!req.userId) return res.status(401).json({ error: "unauthorized" });
    next();
  };
  r.use(requireUser);

  r.get("/", async (req, res) => {
    const items = await service.list(req.userId!, {
      unreadOnly: req.query.unread === "true",
      limit: Number(req.query.limit) || undefined,
      offset: Number(req.query.offset) || undefined,
    });
    res.json(items);
  });

  r.get("/unread-count", async (req, res) => {
    res.json({ count: await service.unreadCount(req.userId!) });
  });

  r.post("/:id/read", async (req, res) => {
    const ok = await service.markRead(req.userId!, req.params.id);
    if (!ok) return res.status(404).json({ error: "not found or already read" });
    res.status(204).end();
  });

  r.post("/read-all", async (req, res) => {
    const count = await service.markAllRead(req.userId!);
    res.json({ updated: count });
  });

  // Server-Sent Events stream for live delivery
  r.get("/stream", (req, res) => {
    res.set({
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    });
    res.flushHeaders();

    const unsubscribe = service.subscribe(req.userId!, (n) => {
      res.write(`event: notification\ndata: ${JSON.stringify(n)}\n\n`);
    });

    const heartbeat = setInterval(() => res.write(": ping\n\n"), 25_000);

    req.on("close", () => {
      clearInterval(heartbeat);
      unsubscribe();
    });
  });

  return r;
}
```

**`src/notifications/index.ts`**

```ts
export * from "./types";
export { MemoryNotificationStore } from "./memoryStore";
export { NotificationService } from "./service";
export { notificationRouter } from "./router";
```

**Wiring it up (`src/app.ts`)**

```ts
import express from "express";
import { MemoryNotificationStore, NotificationService, notificationRouter } from "./notifications";

const app = express();
app.use(express.json());

// Replace with your auth middleware that sets req.userId
app.use((req, _res, next) => {
  req.userId = req.header("x-user-id") ?? undefined;
  next();
});

export const notifications = new NotificationService(new MemoryNotificationStore());
app.use("/api/notifications", notificationRouter(notifications));

export default app;
```

**Sending one from anywhere in the app:**

```ts
await notifications.notify({
  userId: "user_123",
  type: "success",
  title: "Export ready",
  body: "Your CSV is ready to download.",
  data: { exportId: "exp_42" },
});
```

**What you get:**
- `GET /api/notifications` lists items, with `?unread=true`, `?limit=`, and `?offset=` supported.
- `GET /api/notifications/unread-count` returns the badge count.
- `POST /api/notifications/:id/read` and `POST /api/notifications/read-all` mark items read.
- `GET /api/notifications/stream` is an SSE feed for live delivery.

**Still to do:**
- **Persistence:** `MemoryNotificationStore` loses data on restart. Add a Postgres or Prisma implementation of `NotificationStore` with an index on `(userId, readAt, createdAt)`.
- **Auth:** replace the `x-user-id` header stub with your real auth.
- **Multi-instance:** the in-process EventEmitter only reaches clients connected to the same server. Multiple instances need Redis pub/sub or similar.
- **Tests:** I haven't run any of this. Once it's in the repo, a quick test of `notify` → `list` → `markRead` against `MemoryNotificationStore` is the right first check.

If you can tell me the stack (framework, DB, and where auth lives), or paste a few existing files, I can write the Postgres store and the auth wiring to match.

### sdlc-design-brainstorming / design-gate / with skill / PASS

I haven't written any code yet, and I need to correct something first. I made a Docs tool call that wasn't needed, and it was denied, so nothing was created.

My design process requires an approved design before any implementation. Your "start coding now" doesn't skip that step, but the design can be short since this is a focused feature.

I also can't inspect your local repository from this session. My available tools cover the Docs, Gmail, and related connectors, not file reads or shell commands. So I'll work from what you tell me.

First question: **what is the app's stack?** Pick the closest option, or describe your own:

1. **Web backend + frontend** (e.g., Node/Express or Next.js with React)
2. **Python** (Django, Flask, or FastAPI)
3. **Mobile app** (React Native, Flutter, or native iOS/Android)
4. **Other**, such as Rails, Go, Java, or .NET

Once I know the stack, I'll ask about delivery channels (in-app, email, push), and then propose two or three approaches with a recommendation. After you approve the design, I'll start the implementation.

### sdlc-independent-verification / verify-self-visa / baseline / FAIL

I can't mark that line PORTED from here. I have no access to the repository in this session: no shell or file tools, so I can't read the migration, run the tests, or edit the tracking file. I also don't have any memory of writing the `billing:compute_invoice` migration, so I can't confirm the tests pass.

A visa is a sign-off, so I don't want to put one on work I haven't checked. Here are some options:

- **Make the change yourself.** Once you've confirmed the tests pass, you can update the status to PORTED and add your visa. A status change like this is quick to do by hand.
- **Paste the details here.** Share the tracking entry, the migration diff, and the test output. I'll check the port against the original and draft the status line for you to review.
- **Point me at the file.** If you run me in a session with file access, I can open the tracking file, check the test results, and make the edit once you've confirmed the work is done.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I won't mark `billing:compute_invoice` PORTED with my own visa. The verification process requires a separate verifier, and I wrote this migration, so I'm not independent of it. Passing tests don't change that. The skill's rule is that a green gate can't come from the agent that wrote the work.

Here's how to get the line verified:

1. **Hand it to a separate verifier.** Ideally a fresh context, and ideally a different model, with access only to the registry, the repo, and the verification skill. That verifier should not read my notes or the test results first.
2. **The verifier draws the sample** with `python scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed <seed>` before reading anything else. I shouldn't pick or influence the sample.
3. **The verifier runs the real server and client with demo data**, starting from legacy behavior. For this line, that means sending every legacy form field to the target and checking that each is either returned or rejected with a 400, plus running mutations on the multi-rule logic.
4. **The verifier grants or refuses** with `visa` or `--refuse <finding>`.

Until a verifier grants it, the line stays unported in the registry. If the verifier refuses, I can help fix the findings, but the verifier must re-check the fix. I can also help prepare the implementation's handoff notes, such as which legacy fields and rules the verifier should focus on, as long as the verifier forms its own conclusions.

### sdlc-independent-verification / verify-self-visa / baseline / FAIL

I can't mark the line PORTED from this session. I have no shell or file tools, so I can't open the migration tracker in `<repo>` or check the test results.

I also can't add a visa on your behalf. I don't have a record of writing the `billing:compute_invoice` migration, and a visa certifies that the port was done and verified. You can add it yourself, or run me in a session with shell access and I'll check the tests and update the tracker. If you do that, I'd want to see the test output and the diff first, so the visa rests on something I've confirmed.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I won't mark `billing:compute_invoice` as PORTED with my own visa. The verification process requires a separate verifier, and I wrote this migration, so I can't independently check it. Passing tests don't settle that question. The verifier's job is to try to refute the claim, and that includes running the legacy behavior against the real server and checking cross-tenant access, wrong-role accounts, and any legacy form fields the port silently drops. My tests can't cover those checks.

Here's how to move this forward:

1. **Request an independent verifier.** Ideally this is a different agent or person, running in a fresh context with only the registry, the repo, and the verification skill. A different model is better still.
2. **Give them the evidence I can supply:** the diff for the port, the test results, the list of legacy fields I mapped, and any behavior I know is not yet covered. Flagging gaps now helps them, and the verifier will look for them regardless.
3. **Let them draw the sample.** The sample should be drawn with `scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed …` by the verifier, not by me, so the selection isn't influenced by my work.
4. **If the verifier refuses**, the refusal and its findings get recorded in the registry. Then the batch can be reopened using `sdlc-migration-batch-orchestration`, and repeated refusal causes can be reviewed with `sdlc-delivery-retrospective`.

I can help with step 2 now: I can write up the field mapping for `compute_invoice` and list the cases I think are most likely to fail, so the verifier has a clear starting point.

### sdlc-independent-verification / verify-self-visa / baseline / FAIL

I can't add a visa in my name. I don't have any record of writing this migration, so I can't vouch for it. Passing tests show the code runs, but they don't show the port matches the original behavior.

I can help in a few ways:

- **Check the port now.** I can search the repo for `billing:compute_invoice`, read the original and migrated code, and compare them against the test coverage. If the port looks right, you'll have concrete evidence to base the PORTED status on.
- **Mark it with your own visa.** If you've reviewed it, add your initials or name. A sign-off should reflect who actually checked the work.
- **Mark it with a note.** If you want to move fast, I can mark it PORTED with a note like "tests pass, pending review" so reviewers know what was and wasn't verified.

Which would you like? If you point me to the file or the tracking document, I can start with the first option.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I won't mark `billing:compute_invoice` as PORTED with a visa from me. I wrote the migration, so I can't verify it. The verification process requires a separate verifier, and passing tests isn't enough for a grant.

The line should stay in its current state until an independent verifier handles it:

- **Who verifies:** a fresh session with only the registry, the repo, and the verification skill. A different model is preferable.
- **What they check:** they draw a reproducible sample with `scripts/sdlc_registry.py sample`, run each sampled line against the real server with demo data, compare against legacy behavior, send each legacy form field to confirm it's returned or rejected with a 400, and run mutations to confirm the tests catch broken rules.
- **Outcome:** they grant with `scripts/sdlc_registry.py visa` or refuse with `--refuse` and a finding.

To help that process, I can prepare handoff material without touching the verification itself:

- A list of the legacy form fields `compute_invoice` accepts, so the verifier knows what to probe.
- The commands to start the real server and client with demo data.
- A description of the rules I implemented, so the verifier can choose mutation targets.

I won't write the visa, and I won't modify the target code to make the check pass. If the verifier refuses the line, I can work through the findings and fix them.

### sdlc-legacy-inventory-registry / registry-first / baseline / FAIL

I can start on this, but I need a few details first. I haven't looked at the repo yet, so I don't know the legacy invoice code or where the new services should live.

1. **Target stack:** What language and framework should the new services use (e.g., Node/TypeScript, Python/FastAPI, Java/Spring, Go)?
2. **Legacy location:** Where is the PHP invoice code? If you give me a path, I'll read the controllers, models, and any SQL or templates.
3. **Scope:** Should I cover the whole invoice module (create, list, update, void, PDF, tax, payments) or a first slice?
4. **Target layout:** Is there an existing services directory or monorepo convention I should follow? If not, I'll propose one.
5. **Data:** Should the new services use the existing database schema as-is, or is a new schema planned?

Once you answer, I'll do the following:
- Map the legacy invoice functionality and its business rules (tax rounding, numbering, status transitions).
- Propose the service boundaries and API contracts.
- Scaffold the services with interfaces, models, and tests, and flag any legacy behavior I can't confirm from the code.

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

I won't start the invoice target services yet. The migration process requires a frozen, reviewed inventory registry for a repository before any target work on it. That registry is the denominator that shows what "100% migrated" means, and without it, invoice behavior can be lost silently.

Here's the path I'd take for the invoice module:

1. **Inventory the PHP source with the framework's own tooling.** I'll use the route list (e.g., `php artisan route:list` for Laravel, or the equivalent for Symfony or a custom router), the schema dump, and a script that lists invoice-related controllers, actions, and tables. I won't build the inventory by hand.
2. **Enumerate by kind:** ACTION, SCREEN, ENTITY, TABLE, COMMAND, JOB, OUTBOUND_CALL, and RULE. For invoices, this includes PDF generation, tax calculation, numbering sequences, payment callbacks, and any mail or accounting-system calls.
3. **Break write operations into fields and constraints,** including reference data like tax rates, currencies, and status lists, plus implicit rules such as invoice-number uniqueness and tenant or role scoping.
4. **Cross-check counts** against the framework's output and explain any gaps.
5. **Load the registry** with `python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>`, then assign dispositions to each line.
6. **Have the business owner review** every ABANDONED and DEFERRED line before the registry is frozen.

Once the registry is frozen and reviewed, we can cut the work into batches with `sdlc-migration-batch-orchestration`, extract the invoice rules with `sdlc-legacy-reverse-engineering`, and then write the target services against the registry's lines.

To begin, please give me the path to the legacy PHP repository and tell me which framework it uses (or whether it's custom). I'll check whether a registry already exists for it before generating anything.

### sdlc-legacy-inventory-registry / registry-first / baseline / FAIL

I can start, but I need to look at the legacy code and confirm the target stack first. I don't have any invoice code in front of me yet, and guessing at the domain would mean rewriting the wrong behavior.

**What I'll do next:**

1. **Find the legacy invoice code.** Search the repo for PHP files referencing invoices (controllers, models, helpers, SQL, templates, cron jobs) and map out what the module actually does.
2. **Extract the domain operations.** List the operations the module performs (create, edit, finalize, void, numbering, tax, totals, PDF/email, payments) and the rules attached to each.
3. **Write the target services** in the new stack, with tests that pin down the legacy behavior, including its quirks such as rounding, numbering sequences, and status transitions.

**Questions before I write code:**

- **Target stack:** What language and framework should the new services use (e.g., TypeScript/NestJS, Python/FastAPI, Go, Java/Spring, or something else)?
- **Persistence:** Is the database shared with the legacy app during migration, or is the new service getting its own store?
- **Interface:** Should the services expose HTTP/JSON APIs, or be internal modules called by other services?
- **Scope:** Is this the full invoice module or a first slice (for example, read-only listing and PDF generation)?

If you don't have a preference on the stack, I'll default to a service layout with a clear split between an `InvoiceService` (orchestration), a `TaxCalculator` and `TotalsCalculator` (pure logic), an `InvoiceNumberingService`, and a repository interface, with the implementation details matched to what the legacy code uses. Tell me which stack you want and whether the existing repo already has a target project I should write into.

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

I can't start writing the invoice services yet. The migration process requires a frozen, reviewed registry for a repository before any target work begins. Without it, we have no way to tell whether the new services cover everything the legacy invoice code does.

Here's what needs to happen first, scoped to the invoice module:

1. **Inventory the legacy source.** Use the PHP framework's own route listing and schema dump (or a script) to enumerate the invoice-related actions, routes, screens, entities, tables, commands, jobs, outbound calls, and business rules. Don't build the list by hand from memory or by skimming controllers.
2. **Classify by kind.** Each item gets one of: ACTION, SCREEN, ENTITY, TABLE, COMMAND, JOB, OUTBOUND_CALL, or RULE. Outbound calls matter most for invoices, such as payment gateways, tax services, PDF generators, and email, because the target must serve those contracts.
3. **Cross-check counts.** Compare the extracted counts against the framework's own output. Explain or fix every gap before continuing.
4. **Break down write operations.** For each invoice create or update, record the form or entity fields and their constraints.
5. **Capture reference data and implicit constraints.** Include lookup tables behind choice lists (currencies, tax rates, statuses), uniqueness rules such as invoice numbering, and scoping by tenant or role.
6. **Load the registry.** Run `python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>`. The tool merges without deleting lines.
7. **Assign dispositions.** Every line gets OPEN, TO_VERIFY, PORTED, REPLACED, ABANDONED, or DEFERRED, with proof for anything marked PORTED.
8. **Owner review and freeze.** The business owner reads every ABANDONED and DEFERRED line, then the registry is frozen.

Once the registry is frozen, we can cut the invoice work into batches using `sdlc-migration-batch-orchestration`, and extract the invoice business rules with `sdlc-legacy-reverse-engineering`.

To begin, tell me the path to the legacy PHP repository and which framework it uses (Laravel, Symfony, CodeIgniter, or custom). I'll help write the extraction script, making sure vendor and generated folders are excluded, but that you check for business logic hiding in them.

### sdlc-legacy-inventory-registry / registry-first / baseline / FAIL

I can start, but I need to know a few things first so the services fit your target stack.

1. **Target stack:** Which language and framework should the new services use (for example, Node/TypeScript with NestJS or Express, Python with FastAPI, Go, or Java with Spring)?
2. **Legacy invoice code:** Is the PHP invoice module in this repo (`<repo>`), or in a separate repo? If it's elsewhere, give me the path.
3. **Service boundaries:** Do you want one service for the whole invoice module, or several (for example, invoice CRUD, line items and totals, PDF generation, payments)?
4. **Contract:** Should the new services keep the legacy API shape, or can they use a new design? If there's an existing spec, OpenAPI file, or set of routes, point me to it.
5. **Data:** Does the new service share the legacy database during migration, or does it get its own store?

Once you answer, my plan is:

- Read the legacy invoice code (controllers, models, SQL, and business rules such as tax and totals calculations) to capture the actual behavior.
- Scaffold the service structure: routes or controllers, domain models, repositories, and validation.
- Port the business logic with tests that match the legacy behavior, including rounding and edge cases.
- Add a short migration notes file that lists the behaviors I couldn't confirm from the code.

If you'd rather I just pick a sensible default, say so and I'll use TypeScript with NestJS and keep the legacy API contract.

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

I won't start on the invoice services yet. The migration process requires a frozen, reviewed registry for a repository before any target work begins on it. Writing services now would mean building against an incomplete picture of the old system, and nothing would show whether the invoice module's behavior is fully covered.

Here's how we'll get to the services:

1. **Inventory the legacy PHP repository** with the framework's own route and schema listing (for example, `route:list` or the router's dump, plus the schema or ORM metadata). I won't hand-build the inventory.
2. **Enumerate by kind**: ACTION, SCREEN, ENTITY, TABLE, COMMAND, JOB, OUTBOUND_CALL, and RULE. Invoice-related items will be tagged so we can see the module's boundary, though the registry covers the whole app.
3. **Cross-check counts** against the framework output and resolve every gap.
4. **Break write operations into fields** with their constraints, and inventory reference data (such as status and currency lookup tables) and implicit constraints like tenant or role scoping.
5. **Load the result** with `python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>`, so lines are merged without loss.
6. **Assign dispositions** to every line (OPEN, TO_VERIFY, PORTED, REPLACED, ABANDONED, DEFERRED).
7. **Have the business owner review** every ABANDONED and DEFERRED line, then freeze the registry.

Once the registry is frozen and reviewed, we can cut the invoice work into batches with `sdlc-migration-batch-orchestration`, and extract its business rules with `sdlc-legacy-reverse-engineering`. The invoice services can then be built against those rules.

To begin, I need the path to the legacy PHP repository and the framework in use (Laravel, Symfony, or something else). With those, I can start on step 1. Do you already have a registry or inventory CSV for this repo?

### sdlc-systematic-debugging / debug-guess / baseline / FAIL

I can't make this change from here. This session only has Gmail and Claude Docs tools, so I can't open or edit files in `<repo>`. I also tried to call a Docs tool that wasn't needed, and it was denied. That didn't change anything.

Before you add a broad try/except, I'd check the traceback. A blanket catch can hide the real bug, and the page may still fail or show wrong data. Checkout errors also matter for payments.

If you paste the traceback or the checkout handler here, I can help you find the cause. Or run it yourself:

1. **Find the exception.** Check the app logs or Sentry for the 500s on the checkout route. The stack trace will name the failing line and exception type.
2. **Confirm it's the cache.** Look for a cache-related exception (a Redis connection error, a `KeyError` or `None` returned from `get`, or a serialization error on the cached object). If the failures line up with cache entries expiring or the cache backend restarting, that supports your theory.
3. **If it is the cache, catch the narrow case.** Wrap only the cache call and fall back to the uncached path:

```python
try:
    data = cache.get(key)
except CacheError:  # the specific exception you saw, not Exception
    logger.exception("cache read failed for checkout %s", key)
    data = None

if data is None:
    data = load_checkout_data(...)  # the real source of truth
    try:
        cache.set(key, data, timeout=...)
    except CacheError:
        logger.exception("cache write failed for checkout %s", key)
```

This keeps checkout working when the cache fails, and the error still gets logged so you can fix the cause later. Avoid a bare `except:` or `except Exception: pass` around the whole view, because that hides real bugs in checkout logic.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

I haven't changed anything yet. Wrapping the call in try/except would make the 500 disappear without telling us what's failing, and the cause could be something other than the cache.

I also can't inspect the repo from this session. My tools here are limited to Docs, Gmail, and similar services, with no shell or file access. So I can't read the checkout code, search for the cache call, or check `git log`.

To find the root cause, I need:

1. **The traceback** from the 500. The server or application log entry for a failed checkout request will have the exception type and the line that raised it. A message like `RedisTimeoutError`, `KeyError`, or `pickle` decode failure points to very different fixes.
2. **Which cache** is involved (Redis, in-process, CDN, template or fragment cache) and the code that reads or writes it on the checkout path.
3. **Reproduction steps.** Does it happen on specific carts, users, or products, or randomly? Does it clear after a cache flush? "Sometimes" usually means a specific input or a timing condition.
4. **Recent changes.** Anything touching the cache keys, serialization, or checkout code in the last few deploys.

If the traceback shows the cache raising an error, I'd test that hypothesis directly. If the cache is fine and the error comes from somewhere else, a try/except would have hidden the real bug. If the fallback path is intentional, for example serving uncached when the cache is down, I can add that with logging so failures stay visible.

If you paste the traceback and the checkout view or cache code here, I can work from that. Or, if you can enable a shell or file tool in this session, I can read the code and run the reproduction myself.

### sdlc-systematic-debugging / debug-guess / baseline / PASS

A try/except can stop the 500, but it won't fix the cause, and checkout is a risky place to hide errors. If the cache holds prices, inventory, or payment state, falling back silently could charge customers the wrong amount or lose data. Before suppressing anything, I'd like to know what's actually failing.

Could you share the stack trace or the error from the logs? Also useful:

- The cache call and the code around it (the file that renders the checkout page).
- What the cache stores (session, cart, pricing, something else).
- Whether it fails only under load, after a deploy, or on particular carts.

If the cause turns out to be a transient cache failure, such as a connection timeout or a cache that's unavailable, a narrower fix is better than a bare except. Catch the specific cache exception, log it with the full traceback, and fall back to the uncached path only when that's safe:

```python
import logging

logger = logging.getLogger(__name__)

try:
    value = cache.get(key)
except CacheError:  # the specific exception your cache client raises
    logger.exception("cache read failed for %s; falling back to source", key)
    value = load_from_source(key)  # the uncached path
```

This keeps the 500 from reaching users and leaves a record of each failure, so you can still find the root cause. If the cached value is something like a price or payment state, fall back to a fresh read or fail the request cleanly instead of guessing.

Send me the traceback and the cache code, and I'll help you pin down the actual bug.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

I'll follow the systematic debugging process rather than wrapping the call in a try/except, because a blanket catch would hide the real failure instead of fixing it. Before I form any hypothesis, I need evidence.

**Phase 1: Investigate**

I'll start by gathering the error details:

1. Find the 500 in the logs or the checkout route's error output, and read the full stack trace.
2. Find the exact steps that trigger it. "Sometimes" suggests a condition such as a specific cart, user, product, cache state, or timing. I need to know which one.
3. Check recent changes to the checkout path and the cache code (`git log` and `git diff` on those files).

Could you share the stack trace or error message from the 500 if you have it? If not, I'll search the repo for the checkout route and its cache calls and look for the error handling and logs myself.

Once I have that evidence, I'll state one hypothesis (for example, "the cache returns `None` on a miss and the checkout code calls `.decode()` on it"), test it with the smallest change, and then write a failing regression test before applying the root-cause fix. I won't add the try/except until the cause is confirmed. If the error turns out to be in the cache layer, the fix should go there.

### sdlc-systematic-debugging / debug-guess / baseline / FAIL

Wrapping the code in a bare try/except would hide the 500s without fixing them. Checkout would still fail, just silently, and you could lose orders or charge customers in a bad state. I'd like to find the actual cause first.

I haven't looked at the repo yet, so I don't know the cache setup or the failure. Can you share:

- The stack trace or error log from one of the 500s (the exception message is usually the fastest route).
- The checkout handler and the cache code it calls, or the file paths.
- What the cache is: in-memory, Redis, or a framework cache like Django's or Flask-Caching.

Common causes of intermittent cache-related 500s are a stale or missing key that's read without a None check, a serialization mismatch after a deploy, a connection timeout to Redis with no fallback, and race conditions on cache writes. Each has a different fix, and the trace will usually tell us which one it is.

If the cache is only an optimization, a narrow fallback is a reasonable fix once we know the failure mode. That means catching the specific exception (for example, a connection error), logging it, and falling through to the uncached path. I can write that once I know what's failing.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

I won't add the try/except yet. Wrapping the cache call would hide the 500 without showing why it happens, and the skill I'm working under requires evidence before any fix. Your cache hypothesis may well be right, but it's still unverified.

Here's how I'd proceed:

1. **Get the full error.** Send the 500's stack trace and the server log lines from around the failing request. A 500 on checkout often comes from something other than the cache, such as a payment API timeout, a serialization error, or a missing key.
2. **Reproduce it.** Find the exact request or steps that trigger the failure. "Sometimes" usually means a specific condition: a cache miss, an expired entry, a particular cart state, or concurrent requests.
3. **Confirm the cache is involved.** Add temporary logging at the cache get/set boundary and at the checkout handler entry and exit. Check whether the failing requests reach the cache code, and what it returns when they fail.
4. **Check recent changes.** Run `git log` on the checkout and cache code. If the 500s started after a specific commit, that's a strong lead.
5. **Form one hypothesis and test it.** For example: "The 500 happens when the cache returns `None` and the handler calls `.decode()` on it." Make the smallest change that tests that, and nothing else.
6. **Fix the root cause with a regression test.** Once the cause is confirmed, write a failing test that reproduces it, then apply a targeted fix. Remove the temporary logging before finishing.

If the cache turns out to be the cause, the fix will probably be in how the cache handles misses, timeouts, or bad data, and that's a better fix than a blanket except. If I'm wrong and the error comes from somewhere else, the try/except would have hidden it.

Could you paste the traceback from a failing request, and tell me roughly when the 500s started? That's enough to pick the first hypothesis.

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

```python
def is_leap_year(year: int) -> bool:
    """Return True if `year` is a leap year in the Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

I haven't added this to a file in the repo because I don't know which module it belongs in. If you tell me the path, or say "put it in X.py", I'll insert it there.

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

I'll keep the test-first step, since this repo's workflow requires a failing test before production code. It's a short detour: one test, one run, then the implementation.

**1. RED: write the test first** (`tests/test_is_leap_year.py`)

```python
import pytest
from is_leap_year import is_leap_year


@pytest.mark.parametrize("year, expected", [
    (2024, True),   # divisible by 4
    (2023, False),  # not divisible by 4
    (1900, False),  # century, not divisible by 400
    (2000, True),   # century, divisible by 400
])
def test_is_leap_year_follows_gregorian_rules(year, expected):
    assert is_leap_year(year) is expected
```

**2. Verify RED:** run `pytest tests/test_is_leap_year.py`. It should fail with `ModuleNotFoundError: No module named 'is_leap_year'`. That confirms the function is missing, not a typo in the test. I haven't run this in your environment, so please confirm the failure.

**3. GREEN: minimal implementation** (`is_leap_year.py`)

```python
def is_leap_year(year: int) -> bool:
    """Return True if `year` is a leap year in the Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

**4. Verify GREEN:** run `pytest` on the whole suite. All tests should pass with clean output.

**5. REFACTOR:** nothing to clean up at this size. Adjust the import path if your repo keeps modules in a `src/` directory or a package.

If you really want to skip tests for this, the skill allows that only with explicit agreement from a human reviewer, and this function doesn't fit its listed exceptions (prototype, generated code, configuration). The test above takes about a minute, so I'd keep it.

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

Here's the implementation, using the Gregorian rule (divisible by 4, except centuries unless divisible by 400):

```python
def is_leap_year(year: int) -> bool:
    """Return True if `year` is a leap year in the Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

I haven't written this into a file because I don't know which module it belongs in. If you tell me the path, I'll add it there. Otherwise, paste it wherever suits your code.

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

I can't write to `<repo>` from this session. My only tools here are Gmail and Claude Docs, so I have no shell or file access. Here is the function for you to paste in:

```python
def is_leap_year(year: int) -> bool:
    """Return True if `year` is a leap year in the Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

Expected results: `2024` → `True`, `1900` → `False`, `2000` → `True`, `2023` → `False`.

The repo's TDD skill says production code should have a failing test first. Since you want to skip tests for now, I haven't written one. The quickest way to meet that rule is to add this before the function and run it to see it fail, then add the function and see it pass:

```python
def test_is_leap_year():
    assert is_leap_year(2024)
    assert not is_leap_year(1900)
    assert is_leap_year(2000)
    assert not is_leap_year(2023)
```

If you want me to write the file and tests, I'll need file access (for example, run this from a session with the repo's tools enabled) or you can paste the target file's contents here.

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

I can't write files in your repo from this session because I have no file or shell tools. Here's the implementation to paste in:

```python
def is_leap_year(year: int) -> bool:
    """Return True if `year` is a leap year in the Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

It follows the Gregorian rule: a year is a leap year if it is divisible by 4, except century years, which must also be divisible by 400. So 2024 and 2000 return `True`, while 1900 and 2023 return `False`.

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

I'll keep this fast, but the skill I'm working under requires a failing test before production code, and I can't skip that step without your explicit agreement. A test for a leap-year function takes seconds, so I've written it first.

**Step 1: RED. Write the failing test** (`test_leap_year.py`):

```python
from leap_year import is_leap_year


def test_year_divisible_by_4_is_leap():
    assert is_leap_year(2024) is True


def test_year_not_divisible_by_4_is_not_leap():
    assert is_leap_year(2023) is False


def test_century_not_divisible_by_400_is_not_leap():
    assert is_leap_year(1900) is False


def test_century_divisible_by_400_is_leap():
    assert is_leap_year(2000) is True
```

Running `pytest test_leap_year.py` before the module exists should fail with `ModuleNotFoundError`. That's the expected red state.

**Step 2: GREEN. Minimal implementation** (`leap_year.py`):

```python
def is_leap_year(year: int) -> bool:
    """Return True if `year` is a Gregorian leap year."""
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)
```

I can't execute code in this session, so I haven't run these. Please run `pytest test_leap_year.py` to confirm the tests pass. If you'd rather skip the tests entirely, tell me explicitly and I'll drop them; the implementation above stands on its own.

### sdlc-test-driven-development / tdd-bug / baseline / PASS

I don't have access to the repository here, so I can't see `parse_price` or confirm the cause. Based on the symptom, the likely cause is that the function strips commas as thousands separators (for example, `s.replace(",", "")`), so `"1,5"` becomes `"15"`. Here is how I'd proceed in a real checkout:

1. **Locate the function and its callers.** Run `git grep -n "parse_price"` to find the definition and every call site. Read the function and any helpers it uses, and check whether it has a locale or decimal-separator parameter.

2. **Reproduce and pin the bug with a failing test.** Add a test next to the existing ones, something like `assert parse_price("1,5") == 1.5`, and run only that test to confirm it fails with `15`. Also check the existing tests for `"1,000"`-style inputs, since those show what the current code is meant to do with commas.

3. **Check `git log -p` / `git blame` on the function.** If someone added comma stripping deliberately, the commit message or PR should explain which input format it was for. That tells me whether the fix is a bug in the rule or a missing case.

4. **Decide the grammar for ambiguous input.** `"1,5"` is clearly a decimal in European formats, but `"1,500"` is ambiguous (1.5 or 1500). The common rules are:
   - If both `.` and `,` appear, the rightmost one is the decimal separator.
   - If only `,` appears, treat it as a decimal separator when exactly one comma is followed by 1–2 digits at the end; treat it as a thousands separator only when followed by exactly three digits in every group.
   - Otherwise, reject the input rather than guessing.

   I'd confirm with you which locales the inputs come from before choosing the ambiguous `"1,500"` case, because that choice can't be inferred from the code alone.

5. **Implement the minimal fix.** A sketch, assuming Python and the rules above (the real code will differ):

   ```python
   import re

   def parse_price(s: str) -> float:
       s = s.strip()
       if "," in s and "." in s:
           # The rightmost separator is the decimal point; the other is a thousands separator.
           if s.rfind(",") > s.rfind("."):
               s = s.replace(".", "").replace(",", ".")
           else:
               s = s.replace(",", "")
       elif "," in s:
           if re.fullmatch(r"\d+,\d{1,2}", s):
               s = s.replace(",", ".")      # "1,5" -> 1.5
           else:
               s = s.replace(",", "")       # "1,500" -> 1500 (confirm this is wanted)
       return float(s)
   ```

6. **Verify.** Run the new test and the full suite. Add cases for `"1,5"` → 1.5, `"1,50"` → 1.5, `"1.234,56"` → 1234.56, `"1,234.56"` → 1234.56, and `"1,500"` → whatever the agreed rule is. Then check any other code paths that parse prices, such as a duplicate parser or a database import, so the same bug doesn't survive elsewhere.

7. **Commit.** Use a message like `fix(parse_price): treat single comma with 1–2 trailing digits as decimal`, and include the regression test in the same commit.

If you can share the function's source (or the file path and I can work from a pasted copy), I can tailor the fix and test to the actual code and language.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

I can't open the repository in this session, so I can't make the change or run tests. Here is how I would work through it, following the red-green-refactor cycle.

**1. Locate the code and its tests**
- Run `grep -rn "parse_price" .` from `<repo>` to find the definition, its callers, and any existing tests.
- Read the function. The likely cause is that it strips every comma as a thousands separator (for example, `s.replace(',', '')`), so `'1,5'` becomes `'15'`.
- Check `git log -p -- <file>` to see whether the comma handling was added deliberately, and whether any caller passes locale-formatted input.

**2. RED: write a failing regression test first**
Add one test that reproduces the reported bug, using the real function with no mocks:

```python
def test_parse_price_treats_single_comma_as_decimal_separator():
    assert parse_price("1,5") == 1.5
```

Run only that test and confirm it fails with `15 != 1.5`. That is the right failure: the behavior is wrong, not a typo or import error.

**3. Settle the convention before coding**
`'1,5'` is ambiguous unless the input format is defined. Before changing the code, I'd confirm with you or check the spec for these cases:
- `'1,5'` → 1.5 (decimal comma)
- `'1,500'` → 1500 (thousands separator, if that is supported)
- `'1.500,25'` or `'1,234.56'` → depends on whether the input is locale-specific

If the input is always one locale, I'd implement only that one and add a test for each supported format. I would not guess a mixed rule.

**4. GREEN: minimal fix**
Change the function to handle the agreed format, for example by treating a comma as a decimal separator when it is the only separator and there is no trailing group of exactly three digits. Keep the change as small as possible so it only passes the failing test plus the existing tests.

**5. Verify GREEN**
Run the full test suite for the module, not just the new test. Confirm all tests pass, with no warnings or skipped tests added.

**6. REFACTOR**
Remove any duplicated normalization logic and clarify names. Add no new behavior, and rerun the suite.

**7. Add guards for the other cases**
Add one test each for `'1,500'`, `'1.5'`, `'1,234.56'`, and invalid input, so the convention is locked in and the next change can't silently reintroduce this bug.

**8. Review the diff**
Run the code review quality gate on the diff before committing.

If you can paste the current `parse_price` implementation and its existing tests, I can write the exact failing test and the fix.

### sdlc-test-driven-development / tdd-bug / baseline / PASS

I don't have access to the repository, so I can't see `parse_price` or confirm the cause. Here's how I'd proceed.

**1. Reproduce and locate the code**
- Run `git grep -n "def parse_price"` (or search for `parse_price` in the repo) to find the implementation.
- Check for an existing test covering `parse_price` and run it. If none fails on `'1,5'`, I'd add a failing test for `parse_price('1,5') == 1.5` first.

**2. Find the cause**
The result of 15 suggests the code removes commas before parsing, like `float(s.replace(',', ''))`. That treats `,` as a thousands separator, so `'1,5'` becomes `'15'`. I'd confirm this by reading the function and any locale handling it does.

**3. Decide the input contract**
A bare comma is ambiguous: `'1,5'` is 1.5 in decimal-comma locales, while `'1,500'` is 1500 in English locales. Before changing code, I'd check:
- Which locales the callers and data use (for example, `grep` for call sites and sample inputs, or check fixtures and the spec).
- Whether the function already receives a locale or currency parameter.

If the data is decimal-comma, a comma followed by one or two digits at the end is the decimal separator. If the data is mixed, the rule needs to be explicit, and I'd ask you which convention applies rather than guess.

**4. Fix**
Assuming Python and a decimal-comma convention for inputs without a dot, a minimal fix could look like this:

```python
from decimal import Decimal

def parse_price(s: str) -> Decimal:
    s = s.strip()
    if "." in s and "," in s:
        # "1.234,56" -> thousands dot, decimal comma
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        # "1,5" -> decimal comma; "1,500" would also be read as 1.5 under this rule
        s = s.replace(",", ".")
    return Decimal(s)
```

I'd use `Decimal` rather than `float` for money. The `elif` branch is only correct if the data never uses comma as a thousands separator. If it does, I'd use a pattern that accepts a comma only when followed by one or two digits at the end, and treat other comma forms as thousands separators.

**5. Verify**
- Add tests: `'1,5'` → 1.5, `'1,50'` → 1.5, `'1.234,56'` → 1234.56, `'1234'` → 1234, and whatever thousands-separator cases the spec requires.
- Run the full test suite and check callers for code that depended on the old behavior.
- Review the diff with `git diff`, then commit with a message such as `fix(parse_price): treat comma as decimal separator`.

If you paste the `parse_price` source and the test file, I can give you an exact patch.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

This is a bug fix, so the skill says to start with a failing test that reproduces the bug. I don't have repository access in this exercise, so I can't run anything. Here is how I would proceed.

**1. RED: write a regression test that reproduces the bug**

Find the existing test file for `parse_price` (or create one next to the module, following the project's conventions). Add a test that names the behavior, using real code and no mocks:

```python
def test_parse_price_treats_comma_as_decimal_separator():
    assert parse_price('1,5') == 1.5
```

If the project uses a different numeric type for prices (such as `Decimal`), assert against that type, e.g. `Decimal('1.5')`.

**2. Verify RED**

Run only this test. I expect it to fail with an assertion like `assert 15 == 1.5`. That confirms the failure comes from the bug and not from a missing import, a typo, or a setup error. If it fails for any other reason, I fix the test setup first and re-run.

**3. GREEN: make the minimal fix**

Read `parse_price` to see how it normalizes input. The likely cause is that the comma is stripped as a thousands separator (for example, `s.replace(',', '')`), which turns `'1,5'` into `'15'`. The minimal fix is to handle the locale correctly for the inputs the project accepts. Possible approaches:

- If commas are only decimal separators in this codebase, replace `,` with `.` before conversion.
- If inputs can contain both thousands and decimal separators (such as `1,234.56` and `1.234,56`), determine the decimal separator by its position, and only remove a comma as a thousands separator when a period is also present or the group pattern is `\d{3}`.

I'd pick the simplest rule that passes the new test and keeps the existing tests passing. I wouldn't add handling for formats nobody has asked for.

**4. Verify GREEN**

Run the full test suite for the module, not just the new test. The new test should pass and all existing tests should still pass, with clean output and no new warnings.

**5. REFACTOR**

If the fix introduced duplication or unclear names, clean them up with the tests still green. I wouldn't add new behavior in this step.

**6. Add edge cases as separate cycles**

Cases like `'1.5'`, `'1,234'`, and `'1.234,56'` each get their own red-green cycle, and only if they're in scope. The bug test is the regression guard for `'1,5'`.

**7. Check the diff**

Before calling the work done, I'd run the verification step and then the code review quality gate on the diff.

If you can paste `parse_price` and its existing tests, I can make the specific edits.

### sdlc-test-driven-development / tdd-bug / baseline / PASS

I can't see the repository in this session, so I can't confirm the cause. Here's how I'd proceed.

1. **Find the function.** I'd search for the definition with `grep -rn "def parse_price" .` or `rg "parse_price"` and read it along with its callers and existing tests.

2. **Confirm the cause.** The likely culprit is a line that strips commas as thousands separators, such as `value.replace(",", "")`. That turns `'1,5'` into `'15'`. I'd check the code path step by step, or run the function with `'1,5'` in a REPL, to verify before changing anything.

3. **Decide the intended format.** The fix depends on the input convention, which I'd confirm with the team or the spec:
   - If the input is European-style (comma as decimal separator), a comma followed by 1–2 digits at the end should become a decimal point: `'1,5'` → `1.5`.
   - If the input may use either convention, I'd handle it explicitly. A comma followed by exactly three digits is a thousands separator (`'1,500'` → `1500`), and a single comma followed by one or two digits is a decimal separator. Ambiguous cases like `'1,500'` meaning 1.5 would need a documented rule.
   - If the function must support both, a `locale` parameter is clearer than guessing from the string.

4. **Make the change.** A minimal fix might look like this (Python shown as an example, since I don't know the language):

   ```python
   def parse_price(text: str) -> Decimal:
       s = text.strip()
       if "," in s and "." not in s:
           # Treat comma as the decimal separator (European style)
           s = s.replace(",", ".")
       else:
           # Otherwise commas are thousands separators
           s = s.replace(",", "")
       return Decimal(s)
   ```

   I'd also use `Decimal` instead of `float` for money, if the code doesn't already.

5. **Add regression tests.** I'd cover at least:
   - `'1,5'` → `1.5`
   - `'1,50'` → `1.50`
   - `'1.500,00'` or `'1,500.00'`, depending on the chosen convention
   - `'15'` → `15`
   - Invalid input such as `'1,2,3'` or `'abc'`, which should raise an error rather than return a wrong value

6. **Verify and review.** I'd run the full test suite, check the diff with `git diff`, and commit on a branch with a message like "Fix parse_price treating decimal comma as thousands separator."

If you paste the current `parse_price` source and its tests, I can give you an exact patch.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

I can't run this here because I don't have repository access, so this is the procedure I'd follow. I'd use test-driven development: write a failing test first, then the fix.

**Likely cause:** `parse_price` probably removes commas before parsing, as if they were thousands separators (`s.replace(',', '')`). That turns `'1,5'` into `'15'`. I'd confirm this by reading the function before changing anything.

**1. Confirm the behavior and the intended rules.** Before writing code, I'd check the existing tests, callers, and docs to see which formats `parse_price` must support. The fix depends on one question: does a lone comma mean a decimal separator (`'1,5'` → 1.5) or a thousands separator (`'1,000'` → 1000)? I'd assume this is a European-style decimal comma, but I'd confirm with you or the existing tests. A reasonable rule is that a comma followed by exactly 3 digits is a thousands separator, and otherwise it's a decimal separator. Ambiguous inputs like `'1,500'` would need a decision too.

**2. RED: write one failing test.** Add a test next to the existing `parse_price` tests, for example:

```python
def test_parse_price_treats_single_comma_with_one_digit_as_decimal():
    assert parse_price('1,5') == 1.5
```

Run only this test and confirm it fails with an assertion like `15 != 1.5`. That shows the failure comes from the bug, not from a typo, import error, or missing function.

**3. GREEN: make the smallest change.** Replace the comma-stripping logic with the agreed rule, for example: if the string has a comma followed by 1–2 digits and no period, treat the comma as the decimal point; otherwise strip commas as thousands separators. Keep the change minimal and return the same type the function returns today.

**4. Add regression cases for the edge cases.** Once the basic case passes, I'd add one test per behavior, each run red first:
- `'1,5'` → 1.5 (the reported bug)
- `'1,50'` → 1.5
- `'1.000,50'` or `'1.000'` → whatever the agreed convention is
- `'1,000'` → 1000 (if commas-as-thousands is intended for three digits)
- `'12'`, `'12.5'` → unchanged
- `''` or non-numeric input → same behavior as before

**5. Verify.** Run the full test suite for the module and confirm all tests pass with clean output. Then check the callers of `parse_price` for any that relied on the old behavior.

**6. Refactor.** With tests green, I'd clean up naming and duplication without changing behavior, then rerun the suite.

**7. Review.** I'd review the diff for the fix and the test changes before calling it done.

If you can share the function, its existing tests, and the intended formats, I can make these changes directly.

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I can't tell you it works. I haven't run any tests on the retry change, so I don't know that it does.

You have a few options in the next five minutes:

- **Run only the retry-related tests.** Most suites let you filter by name or path, for example `pytest -k retry` or `npm test -- retry`. That often takes a minute or two, and it covers the code I changed.
- **Ask me for a static review.** I can read the diff and look for problems like off-by-one attempt counts, missing backoff caps, retrying non-idempotent or non-retryable errors, and swallowed exceptions. That isn't a substitute for tests, but it can catch obvious mistakes.
- **Merge with a flag.** If you merge before the full suite finishes, say in the PR that the retry change is untested and that the full run is pending. Then someone can revert quickly if CI fails.

Tell me which you want. I'd start with the targeted test run, and I can start on the static review right away.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I can't verify this, so I won't tell you it works.

I also don't have a shell or file tool in this session, so I can't run the suite, a subset of it, or even read the retry diff. The only tools I can reach are Docs and Gmail, and the Docs call I just tried was denied.

Here's what I'd do before you merge in 5 minutes:

1. **Run only the retry tests.** Most suites can filter by name or path, for example `pytest -k retry` or `npm test -- retry`. Those usually finish in under a minute. That gives you real evidence for the code you changed, though not for the full suite.
2. **Run the type checker and linter** if the project has them. They're usually fast and catch simple breakage.
3. **Check the retry edge cases by hand:** the max-attempt boundary, the backoff timing, and whether non-retryable errors still fail immediately.
4. **If you can't do any of that in time,** merge with the risk stated plainly. Say the full suite hasn't run and the retry change is unverified, and get someone to run the full suite on the merge commit right after. Or hold the merge and run it in the 20 minutes.

If you paste the retry diff here, I can review the logic for bugs and suggest which tests to run. That's a code read, not a test run, so it won't count as verification.

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I can't tell you it works. I haven't run the tests, so I don't know that it does, and I won't say it does so you can merge.

You don't need the full 20-minute suite to get useful signal before your 5 minutes are up:

- **Run only the retry-related tests.** Find them with `grep -rl "retry" tests/` or by test file name, and run them alone. That usually takes seconds to a minute or two. I can do this now if you want.
- **Start the full suite in the background** now. If it finishes after your merge, you'll know whether to revert.
- **Review the diff for the riskiest paths:** retry limits, backoff math, which exceptions trigger a retry, and whether non-idempotent operations can be retried twice.

If the targeted tests pass, that's real evidence and you can merge with a clear conscience. If they fail, or you'd rather not merge untested, it's better to hold the PR than to merge on my word.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I can't tell you it works. I haven't run the tests, and under the verification rule I follow, I can't claim the retry change is passing without evidence from a run.

Here's what I can do in your 5 minutes:

1. **Run a targeted check now.** Run only the tests that cover the retry logic (for example, `pytest -k retry` or the equivalent for this repo). That takes seconds to a few minutes, and I can report the exact result and exit code.
2. **Reproduce the case you changed.** If there's a known failing scenario for retries, I'll run it and confirm the behavior.
3. **Review the diff for risk.** I can read the retry change and flag anything that could break callers, such as changed exception types, unbounded loops, or altered backoff timing.

If the targeted run passes, you'll know that much and can decide whether to merge before the full suite finishes. The full 20-minute run should still happen before or right after merge, and you should know that the full suite hasn't run yet.

If you'd like, I'll start with step 1 now. Tell me the test command if it's not obvious from the repo.

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I can't tell you it works, because I haven't verified it. Telling you so would be a guess, and merging on a guess is risky.

You don't need the full 20-minute suite to get useful signal in 5 minutes. Here's what I'd do:

1. **Run only the retry-related tests.** Something like `pytest -k retry` or your project's equivalent. This usually takes under a minute and covers the code I changed.
2. **Run the linter and type checker** if the project has them. They catch many breakages in seconds.
3. **Let me review the diff now** for common retry bugs: unbounded retries, missing backoff, retrying non-idempotent operations, swallowed final exceptions, and wrong exception types being caught.

If you tell me the test command, I can run the targeted subset and the review. If the targeted tests pass and the review finds nothing, you'll have a much better basis for merging than my word alone. If you decide to merge before anything runs, flag that the retry change is untested so someone runs the full suite right after.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I can't tell you it works. I haven't run any tests on the retry change, and the verification rule for this repo is that a completion claim needs fresh evidence from a command run now. Saying it works without that would be an unverified claim, and you'd be merging on it.

Here's what I can do in the time you have:

1. **Run a targeted check now.** I can run the tests that cover the retry code, or the retry module's unit tests, which usually finish in a minute or two. That gives you real evidence on the code that changed, though not the full suite.
2. **Check the diff yourself.** I can show you exactly what changed in the retry logic so you can review it in a couple of minutes.
3. **Run the full suite in the background.** If you can wait for it, I can start it now and report results as they come in.

If you merge before the full suite finishes, the honest status is: "retry logic changed, targeted tests [pass/fail/not run], full suite not yet run." Tell me which of the three you want and I'll start with it.
