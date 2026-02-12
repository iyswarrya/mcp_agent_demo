# n8n workflow setup

Use this when ReportAgent is configured with `N8N_WEBHOOK_URL` (see README).

## 1. Start services

```bash
docker compose up -d postgres mailhog n8n
```

Open n8n in the browser: **http://localhost:5678**

---

## 2. Create credentials in n8n

### Postgres (for the “Insert Report” node)

1. In n8n: **Settings** (gear) → **Credentials** → **Add credential**.
2. Search for **Postgres** and open it.
3. Fill in (values match `docker-compose`; use **postgres** as host when n8n runs in Docker):

   | Field      | Value      |
   |-----------|------------|
   | Host      | `postgres` |
   | Database  | `agentdb`  |
   | User      | `n8n`      |
   | Password  | `n8npassword` |
   | Port      | `5432`     |
   | SSL       | Disable    |

4. **Save** and name it e.g. **Local Postgres**.

### SMTP / MailHog (for the “Send Email” node)

1. **Add credential** again → search **SMTP**.
2. Fill in (MailHog in Docker):

   | Field   | Value      |
   |--------|------------|
   | Host   | `mailhog`  |
   | Port   | `1025`     |
   | Security | None (no TLS) |
   | User / Password | Leave empty |

3. **Save** and name it e.g. **MailHog SMTP**.

---

## 3. Import the workflow

1. In n8n: **Workflows** → **Add workflow** (or **Import from file** if your UI has it).
2. **Menu** (⋮) → **Import from File** (or **Import** tab when creating a workflow).
3. Choose:  
   `workflows/n8n_db_email_workflow.json`  
   from this repo.
4. The workflow **DB + Email Report (Webhook)** appears with 4 nodes: Webhook → Insert Report → Send Email → Respond.

---

## 4. Attach credentials to the nodes

The imported workflow has placeholder credential IDs; you must assign the credentials you created.

1. **Insert Report** (Postgres node)  
   - Open the node (double‑click).  
   - Under **Credential to connect with**, choose **Local Postgres** (or create new and use the Postgres values above).  
   - Save the node.

2. **Send Email**  
   - Open the node.  
   - Under **Credential to connect with**, choose **MailHog SMTP** (or create new with the SMTP values above).  
   - Save the node.

---

## 5. Activate the workflow

1. In the top-right of the workflow editor, turn the **Active** switch **ON** (enabled).
2. The webhook URL is shown on the **Webhook** node, e.g.:  
   `http://localhost:5678/webhook/db-email-report`  
   (or with a test URL; use the **Production** one that ends in `/webhook/db-email-report`.)

---

## 6. Test the workflow with curl (optional)

Before wiring ReportAgent, you can hit the webhook directly:

```bash
curl -X POST http://localhost:5678/webhook/db-email-report \
  -H "Content-Type: application/json" \
  -d '{"report_name":"Test Report","payload":{"sales":100,"region":"US"},"email_to":"user@example.com"}'
```

You should get a JSON response like `{"ok":true,"insertedId":1,"mail":"sent"}`. Check:

- **Postgres**: a new row in the `reports` table (e.g. `docker exec -it <postgres_container> psql -U n8n -d agentdb -c "SELECT * FROM reports;"` or any DB client).
- **MailHog**: http://localhost:8025 — the test email should appear.

---

## 7. Use it with ReportAgent

In your `.env`:

```bash
N8N_WEBHOOK_URL=http://localhost:5678/webhook/db-email-report
```

Restart ReportAgent, then run the client. ReportAgent will POST to this URL for “store report + notify”.

---

## If n8n runs on the host (not in Docker)

If you run n8n locally (e.g. `npx n8n`) instead of in Docker:

- **Postgres**: use host `localhost`, port `5432`, same database/user/password.
- **SMTP**: use host `localhost`, port `1025` (with MailHog still in Docker and port 1025 published).

The webhook URL stays `http://localhost:5678/webhook/db-email-report` if n8n is on port 5678.
