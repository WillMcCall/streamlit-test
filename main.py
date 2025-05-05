import pandas as pd
from datetime import date
import streamlit as st
import db
from utils import clean_jobs, filter_jobs, get_jobs, to_excel


# Main Logic
with st.form("my_form"):
    data = db.github_read()
    
    locations_str = ", ".join(data["locations"])
    finance_jobs_str = ", ".join(data["finance_jobs"])
    bais_jobs_str = ", ".join(data["bais_jobs"])
    accounting_jobs_str = ", ".join(data["accounting_jobs"])
    
    days_old = st.slider("Days Old", 1, 90)
    num_jobs = st.slider("Max number of jobs to output", 1, 50)
    locations_input = st.text_area('Locations: (comma seperated)', locations_str)
    finance_jobs_input = st.text_area('Finance Jobs: (comma seperated)', finance_jobs_str)
    bais_jobs_input = st.text_area('BAIS Jobs: (comma seperated)', bais_jobs_str)
    accounting_jobs_input = st.text_area('Accounting Jobs: (comma seperated)', accounting_jobs_str)
    
    submitted = st.form_submit_button("Submit")
    
if submitted:
    locations = [loc.strip() for loc in locations_input.split(",")]
    finance_jobs = [job.strip() for job in finance_jobs_input.split(",")]
    bais_jobs = [job.strip() for job in bais_jobs_input.split(",")]
    accounting_jobs = [job.strip() for job in accounting_jobs_input.split(",")]
    
    data = {
        "locations": locations,
        "finance_jobs": finance_jobs,
        "bais_jobs": bais_jobs,
        "accounting_jobs": accounting_jobs
    }
    db.github_write(data)

    
    time_estimate_seconds = len(locations) * ((len(finance_jobs) + len(bais_jobs) + len(accounting_jobs)) * 7)
    time_estimate_minutes = time_estimate_seconds / 60
    
    time_estimate = st.write(f"Time Estimate: {time_estimate_minutes:.1f} minutes")
    my_bar = st.progress(0, text="Scraping in progress. Please wait.")
    counter = 0
    
    total_jobs = (len(finance_jobs) + len(bais_jobs) + len(accounting_jobs)) * len(locations)
    

    finance_jobs_output = get_jobs(finance_jobs, locations, days_old, my_bar, counter, total_jobs, num_jobs)
    finance_jobs_df = finance_jobs_output[0]
    counter = finance_jobs_output[1]
    
    bais_jobs_output = get_jobs(bais_jobs, locations, days_old, my_bar, counter, total_jobs, num_jobs)
    bais_jobs_df = bais_jobs_output[0]
    counter = bais_jobs_output[1]
    
    accounting_jobs_output = get_jobs(accounting_jobs, locations, days_old, my_bar, counter, total_jobs, num_jobs)
    accounting_jobs_df = accounting_jobs_output[0]
    counter = accounting_jobs_output[1]
    
    my_bar.progress(1, text="Finishing up!")
    
    jobs = pd.concat([finance_jobs_df, bais_jobs_df, accounting_jobs_df], ignore_index=True)
    
    jobs = jobs.drop_duplicates().reset_index(drop=True)
    my_bar.empty()

    st.dataframe(jobs)
    
    excel_data = to_excel(jobs)
    
    st.download_button(
        label="Download Excel file",
        data=excel_data,
        file_name=f"results_{date.today().strftime("%Y-%m-%d")}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
