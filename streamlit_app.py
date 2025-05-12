#streamlit run streamlit_app.py
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from CH_Scrape import spider_scrape
from create_graph import create_CHgraph

# Example usage
base_url = "https://find-and-update.company-information.service.gov.uk"

st.title("Find the big cheese...")
st.markdown("Input a Company Number from the [Companies House website](https://find-and-update.company-information.service.gov.uk)")
company_number = st.text_input("Enter the company number:", value="07978187")
iterations = int(st.number_input("Enter max levels to scrape:", min_value=1, max_value=20, value=3))

if st.button("Scrape Data"):
    with st.spinner("Scraping data..."):
        results = spider_scrape(base_url, company_number, iterations)
        combined_df = pd.DataFrame(results)
        count_companies = combined_df['Entity2'].nunique()
        director_df = combined_df[combined_df['Role'] == 'Director']
        pwsc_df = combined_df[combined_df['Role'] == 'pwsc']
        director_count = director_df['Entity1'].nunique()
        pwsc_count = pwsc_df['Entity1'].nunique()
        st.success(f"{count_companies} Companies Identified: {director_count} unique directors & {pwsc_count} controlling interests")
        st.dataframe(combined_df)
        mynet = create_CHgraph(combined_df)
        net_html_path = f'temp_html/test_graph.html'
        with open(net_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=750)