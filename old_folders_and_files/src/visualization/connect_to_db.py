import pandas as pd
import db_config
df = pd.read_sql('SELECT * FROM policies1',db_config.engine)