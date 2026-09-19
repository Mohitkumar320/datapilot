# Model Selection: Text-to-SQL Engine

## Context

This project needed a free, Groq-hosted LLM to power Text-to-SQL generation.
Rather than choosing based on published benchmarks alone, we ran a direct,
reproducible comparison on the actual database this project uses (MySQL
Sakila sample DB) — because writing syntactically valid SQL is not the hard
part; correctly extracting the *right* information for a given question is.

## Models compared

- `qwen/qwen3.8-27b`
- `openai/gpt-oss-120b`

Both hosted on Groq, both accessible via the same API key.

## Methodology

- 12 natural language questions, covering increasing difficulty: simple
  filters, joins, aggregations, `HAVING` clauses, date filtering, exclusion
  queries, and one deliberately ambiguous question.
- Each model was given the same schema description and question, and asked
  to return only SQL (no explanation).
- Critically: **we did not compare the SQL text.** Different, differently
  worded SQL can be equally correct, and superficially similar SQL can
  contain silent logic bugs. Instead, we **executed** each model's SQL
  against a live copy of the Sakila database and compared the actual
  returned data against a manually verified ground truth.

Full question list and raw results: [`evals/results.md`](../evals/results.md)

## Results summary

| # | Question type | Qwen | GPT-OSS |
|---|---|---|---|
| 1 | Simple filter | ✅ | ✅ |
| 2 | Sort + limit | ✅ | ✅ |
| 3 | Single join | ✅ | ✅ |
| 4 | Join + aggregation | ✅ | ✅ |
| 5 | Multi-join | ✅ | ✅ |
| 6 | Aggregation, ambiguous intent | ⚠️ | ⚠️ |
| 7 | Subquery / exclusion | ✅ | ✅ |
| 8 | Multi-join + ranking | ✅ | ✅ |
| 9 | Deliberately vague ("best customers") | ✅ | ✅ |
| 10 | `HAVING` clause | ✅ | ✅ |
| 11 | Date range filter | ✅ | ✅ |
| 12 | Exclusion, many-to-many relationship | ❌ | ✅ |

## Two findings worth detailing

### Finding 1 — Question 6 revealed genuine ambiguity, not a model failure

"Total revenue collected by each store" produced different totals from each
model:

- Qwen joined `store → customer → payment` (revenue attributed to a
  customer's home store)
- GPT-OSS joined `payment → rental → inventory → store` (revenue attributed
  to the store that owned the rented item)

We investigated further by checking a third interpretation
(`payment → staff → store`, i.e. revenue by the store of the staff who
processed the payment) — and got a **third, different number**.

Root cause: in Sakila, a staff member's home store does not always match
the store that owned the inventory they processed a rental for — confirmed
by checking:

```sql
SELECT COUNT(*)
FROM payment p
JOIN staff st ON p.staff_id = st.staff_id
JOIN rental r ON p.rental_id = r.rental_id
JOIN inventory i ON r.inventory_id = i.inventory_id
WHERE st.store_id != i.store_id;
```

which returned **8,007 mismatches** — roughly half of all payments.

**Takeaway:** this wasn't a case of one model being "wrong." The question
itself was under-specified, and both models silently picked a reasonable
but different interpretation instead of flagging the ambiguity. This is a
real production concern for Text-to-SQL systems, not a benchmark quirk —
and it's the reason this project's roadmap includes a human-in-the-loop
confirmation step for ambiguous queries (see Future Work).

### Finding 2 — Question 12 exposed a genuine logic bug in Qwen's output

"List films that have never been rented" returned 43 rows from Qwen and 42
from GPT-OSS. The extra row was `ACADEMY DINOSAUR` (film_id 1).

Qwen's query used a chained `LEFT JOIN` (`film → inventory → rental`) and
filtered `WHERE rental_id IS NULL`. Because films can have multiple
inventory copies, a film with 2+ copies — where only *some* copies were
rented — produces multiple rows in the join, and the never-rented copy's
row incorrectly makes the *film* appear never-rented, even though another
copy was.

Verified directly:

```sql
SELECT i.inventory_id, r.rental_id
FROM inventory i
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
WHERE i.film_id = 1;
```

This showed inventory copies of film 1 with non-null `rental_id`s, i.e. the
film *had* been rented — confirming Qwen's result was factually incorrect.

GPT-OSS used a `NOT EXISTS` subquery instead, which correctly checks
"has *any* copy of this film ever been rented," independent of how many
copies exist — and returned the correct 42 rows.

## Decision

**`openai/gpt-oss-120b`** is used as the primary Text-to-SQL model for this
project.

11 of 12 questions were a tie on correctness, but the one question
requiring correct handling of a many-to-many relationship (Q12) exposed a
real logic error in Qwen's generated SQL, while GPT-OSS handled it
correctly. GPT-OSS's SQL was also consistently more production-ready —
selecting only relevant columns and using descriptive aliases, rather than
`SELECT *`.

## Future work

- Add a human-in-the-loop confirmation step (LangGraph `interrupt`) for
  queries flagged as ambiguous, informed by the Question 6 finding.
- Expand the test set with more many-to-many and edge-case schema patterns,
  informed by the Question 12 finding.