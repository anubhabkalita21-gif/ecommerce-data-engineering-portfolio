import pandas as pd
from src.quality import validate
def test_unique_fails_on_duplicates():
 r=validate(pd.DataFrame({"id":[1,1]}),[{"name":"unique","type":"unique","column":"id"}]); assert r["status"]=="FAIL"
def test_accepted_values_pass():
 r=validate(pd.DataFrame({"s":["paid"]}),[{"name":"status","type":"accepted_values","column":"s","values":["paid","refunded"]}]); assert r["status"]=="PASS"
