#streamlit run streamlit_app.py
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from CH_Scrape import spider_scrape
from create_graph import create_custom_graph

# 13150985 , 04663795
# Example usage
base_url = "https://find-and-update.company-information.service.gov.uk"

st.title("Find the big cheese...")
st.markdown("Input a Company Number from the [Companies House website](https://find-and-update.company-information.service.gov.uk)")
company_number = st.text_input("Enter the company number:").strip()
iterations = int(st.number_input("Enter max. number of levels trace up the hierarchy:", min_value=1, max_value=20, value=5))

if st.button("Scrape Data"):
    with st.spinner("Scraping data..."):
        try:
            results = spider_scrape(base_url, company_number, iterations)
            combined_df = pd.DataFrame(results)
            combined_df['BC_indicator'] = (combined_df['Role'] == 'pwsc') & (combined_df['Entity2Number'] == "N/A")
            combined_df.to_csv('test_output.csv', index=False)
            count_companies = combined_df['Entity2'].nunique()
            director_df = combined_df[combined_df['Role'] == 'Director']
            pwsc_df = combined_df[combined_df['Role'] == 'pwsc']
            director_count = director_df['Entity1'].nunique()
            pwsc_count = pwsc_df['Entity1'].nunique()
            st.success(f"{count_companies-1} Controlling Companies Identified & {director_count} unique directors")
            mynet = create_custom_graph(combined_df)
            html_content = mynet.generate_html()
            components.html(html_content, height=750)
        except Exception as e:
            st.error(f"Please check for valid company number = '{company_number}'")
            st.error(e)
