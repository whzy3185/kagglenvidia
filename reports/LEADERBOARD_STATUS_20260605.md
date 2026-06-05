# Leaderboard Status 2026-06-05

- competition: `nvidia-nemotron-model-reasoning-challenge`
- team: `muelsyse111`
- team_id: `16158572`
- public_score: `0.86`
- public_rank: `399`
- submission_count_on_leaderboard: `7`
- latest_scored_submission_time_utc: `2026-06-05 07:00:55`
- leaderboard_snapshot: `logs/leaderboard_20260605/nvidia-nemotron-model-reasoning-challenge.zip`

## Score Tiers

| score | count | first_rank | last_rank |
| --- | ---: | ---: | ---: |
| 0.89 | 1 | 1 | 1 |
| 0.87 | 17 | 2 | 18 |
| 0.86 | 1358 | 19 | 1376 |
| 0.85 | 478 | 1377 | 1854 |

## Interpretation

The current score has reached the large `0.86` plateau. It is a valid public-score reproduction result, but it is not yet separated from the crowded 0.86 tier. The next useful objective is a route with credible evidence for `0.87+`, not another duplicate 0.86 package.

```yaml
NEXT_ACTION:
  status: stop_today
  action: "audit 0.87 and 0.89 public routes before opening the next submission window"
  reason: "The current public rank is 399 at 0.86; leaderboard separation starts at 0.87."
```
