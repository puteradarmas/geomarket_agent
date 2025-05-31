#%%
import pandas as pd

#%%
df = pd.read_parquet("sample_cafe_data.parquet")

#%%
df.head()

#%%
df.columns

#%%
important_fields = [
    "types",
    "formattedAddress",
    "location",
    "rating",
    "websiteUri",
    
]
#%%
all_reviews = df["reviews"].to_list()
# %%
len(all_reviews[0])