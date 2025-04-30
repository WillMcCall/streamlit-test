import time
import pandas as pd
from io import BytesIO
from datetime import date
from jobspy import scrape_jobs
import streamlit as st

def get_jobs(job_titles: list[str], locations: list[str], days_old: int) -> pd.DataFrame:
    dfs: list[pd.DataFrame] = []
    
    for location in locations:
        for job_title in job_titles:
            dfs.append(scrape_jobs(
                site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
                search_term=job_title,
                location=location,
                results_wanted=2,
                hours_old=(days_old * 24),
                country_indeed='USA',
                verbose=1
            ))
            st.write(f"Searching for {job_title} jobs in {location}...")
            time.sleep(5) # Avoid rate limiting
    
    df = pd.concat(dfs, ignore_index=True)
    cleaned_df = clean_jobs(df)
    final_df = filter_jobs(cleaned_df)
    return final_df
    

def clean_jobs(jobs: pd.DataFrame) -> pd.DataFrame:
    # Removes Duplicates
    cleaned_jobs = jobs.drop_duplicates().reset_index(drop=True)
    
    # Removes all these unnecessary columns
    cleaned_jobs = cleaned_jobs.drop(
        ["id", "site", "job_url_direct", "job_type", "salary_source", "currency", "is_remote", "job_level", "job_function", 
         "listing_type", "emails", "description", "company_industry", "company_logo", "company_url", "company_addresses", 
         "company_description", "skills", "experience_range", "company_rating", "company_reviews_count", "vacancy_count", 
         "work_from_home_type", "interval"], axis=1, errors='ignore')
    
    return cleaned_jobs

def filter_jobs(jobs: pd.DataFrame) -> pd.DataFrame:
    jobs = jobs[(jobs['min_amount'] >= 50000) & (jobs['max_amount'] <= 80000)] # Only keep jobs paying $50,000+, remove jobs paying $80,000+
    jobs = jobs.sort_values("min_amount", ascending=False)
    jobs = jobs.head(num_jobs // 3)
    
    return jobs

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data


with st.form("my_form"):
    st.write("Form Title")
    days_old = st.slider("Days Old", 1, 90)
    num_jobs = st.slider("Max number of jobs to output", 1, 50)
    locations_input = st.text_input('Locations: (comma seperated)', 'Iowa City, Des Moines, Cedar Rapids, Chicago')
    finance_jobs_input = st.text_input('Finance Jobs: (comma seperated)', 'Wealth Manager, Financial Planner')
    bais_jobs_input = st.text_input('BAIS Jobs: (comma seperated)', 'Data Analyst, IT Consultant')
    accounting_jobs_input = st.text_input('Accounting Jobs: (comma seperated)', 'Master of Accountancy, Accountant')
    
    submitted = st.form_submit_button("Submit")
    
if submitted:
    start_time = time.time()
    
    locations = [loc.strip() for loc in locations_input.split(",")]
    finance_jobs = [job.strip() for job in finance_jobs_input.split(",")]
    bais_jobs = [job.strip() for job in bais_jobs_input.split(",")]
    accounting_jobs = [job.strip() for job in accounting_jobs_input.split(",")]

    
    time_estimate_seconds = len(locations) * ((len(finance_jobs) + len(bais_jobs) + len(accounting_jobs)) * 7)
    time_estimate_minutes = time_estimate_seconds / 60
    
    st.write(f"Time Estimate: {time_estimate_minutes:.1f} minutes")
    # st.write(finance_jobs)
    # st.write(bais_jobs)
    # st.write(accounting_jobs)

    finance_jobs_df = get_jobs(finance_jobs, locations, days_old)
    bais_jobs_df = get_jobs(bais_jobs, locations, days_old)
    accounting_jobs_df = get_jobs(accounting_jobs, locations, days_old)
    
    jobs = pd.concat([finance_jobs_df, bais_jobs_df, accounting_jobs_df], ignore_index=True)
    
    jobs = jobs.drop_duplicates().reset_index(drop=True)
    
    excel_data = to_excel(jobs)
    
    st.download_button(
        label="Download Excel file",
        data=excel_data,
        file_name=f"results_{date.today().strftime("%Y-%m-%d")}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    end_time = time.time()
    
    st.write(f"Finished in {(end_time - start_time) / 60:.1f} minutes")
