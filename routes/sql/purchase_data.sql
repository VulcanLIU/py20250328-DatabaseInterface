
SELECT
a.*,
b.MATERIALCODE AS 物料编码,
CASE
    WHEN b.KCYE IS NOT NULL AND b.KCYE > 0  THEN
    '是'
    ELSE
    '否'
END AS 是否到货,
COALESCE(b.KCYE ,0) AS 库存总量
FROM
{{ database_a }} a
LEFT JOIN {{ database_b }} b ON a.`图号` = b.CUSTOMFIELD9
