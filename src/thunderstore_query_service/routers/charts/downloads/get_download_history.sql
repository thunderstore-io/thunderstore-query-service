WITH versions AS (
    SELECT id
    FROM analytics.thunderstore_${table_prefix}_model_package_version_update_v1 mpvu
    WHERE mpvu.namespace__name = {namespace:String}
    AND mpvu.name = {package:String}
)
SELECT
    toStartOfHour(toDateTime(apd.timestamp)) AS hour,
    count() AS downloads
FROM analytics.thunderstore_${table_prefix}_analytics_package_download_v1 apd
WHERE timestamp >= toStartOfHour(now()) - INTERVAL 7 DAY
  AND apd.version_id IN (SELECT id FROM versions)
GROUP BY hour
ORDER BY hour
