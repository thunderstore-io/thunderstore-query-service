WITH versions AS (
    SELECT id
    FROM analytics.thunderstore_${table_prefix}_model_package_version_update_v1 mpvu
    WHERE mpvu.namespace__name = {namespace:String}
    AND mpvu.name = {package:String}
)
SELECT
    toStartOfHour(toDateTime(apd.timestamp, 'UTC')) AS hour,
    toUInt32(count()) AS downloads
FROM analytics.thunderstore_${table_prefix}_analytics_package_download_v1 apd
WHERE apd.timestamp >= toStartOfHour(now('UTC')) - INTERVAL 7 DAY
  AND apd.version_id IN (SELECT id FROM versions)
GROUP BY hour
ORDER BY hour WITH FILL
    FROM toStartOfHour(now('UTC')) - INTERVAL 7 DAY
    TO toStartOfHour(now('UTC')) + INTERVAL 1 HOUR
    STEP INTERVAL 1 HOUR
