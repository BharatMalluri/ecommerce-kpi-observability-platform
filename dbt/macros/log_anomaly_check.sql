-- macros/log_anomaly_check.sql
-- Post-hook macro: logs row count anomalies to monitoring.anomaly_log
-- Usage: {{ log_anomaly_check(this, 'row_count', 0) }}

{% macro log_anomaly_check(model, metric_name, threshold) %}
    insert into monitoring.anomaly_log (check_name, table_name, metric_value, threshold, status)
    select
        '{{ metric_name }}'                         as check_name,
        '{{ model.schema }}.{{ model.name }}'       as table_name,
        count(*)                                    as metric_value,
        {{ threshold }}                             as threshold,
        case when count(*) > {{ threshold }}
             then 'pass' else 'fail'
        end                                         as status
    from {{ model }}
{% endmacro %}
