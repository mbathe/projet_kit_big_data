from dotenv import load_dotenv
from TP_BGDIA700.src.utils.streamlit import st
import pandas as pd
load_dotenv()


if __name__ == "__main__":
    st.write("wow")
    pass

"""
# My first app
Here's our first attempt at using data to create a table:
"""


df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
})

df
