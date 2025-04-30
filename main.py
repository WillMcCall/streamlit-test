import time
import json
import pandas as pd
from io import BytesIO
from datetime import date
from jobspy import scrape_jobs
import streamlit as st


def read_config() -> dict:
    with open("config.json", "r") as file:
        data = json.load(file)
        
    return data


def write_config(data: dict) -> None:
    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4)  # indent makes the output nicely formatted
    
        
def get_jobs(job_titles: list[str], locations: list[str], days_old: int, my_bar, counter: int, total_jobs) -> pd.DataFrame:
    dfs: list[pd.DataFrame] = []
    
    for job_title in job_titles:
        for location in locations:
            dfs.append(scrape_jobs(
                site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
                search_term=job_title,
                location=location,
                results_wanted=2,
                hours_old=(days_old * 24),
                country_indeed='USA',
                verbose=1
            ))
            my_bar.progress(counter + ((100 / total_jobs) / 100), text="Scraping in progress. Please wait.")
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
    data = read_config()
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
    start_time = time.time()
    
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
    write_config(data)

    
    time_estimate_seconds = len(locations) * ((len(finance_jobs) + len(bais_jobs) + len(accounting_jobs)) * 7)
    time_estimate_minutes = time_estimate_seconds / 60
    
    st.write(f"Time Estimate: {time_estimate_minutes:.1f} minutes")
    my_bar = st.progress(0, text="Scraping in progress. Please wait.")
    counter = 0
    
    total_jobs = (finance_jobs + bais_jobs + accounting_jobs) * locations
    
    # st.write(finance_jobs)
    # st.write(bais_jobs)
    # st.write(accounting_jobs)

    finance_jobs_df = get_jobs(finance_jobs, locations, days_old, my_bar, counter, total_jobs)
    bais_jobs_df = get_jobs(bais_jobs, locations, days_old, my_bar, counter, total_jobs)
    accounting_jobs_df = get_jobs(accounting_jobs, locations, days_old, my_bar, counter, total_jobs)
    
    jobs = pd.concat([finance_jobs_df, bais_jobs_df, accounting_jobs_df], ignore_index=True)
    
    jobs = jobs.drop_duplicates().reset_index(drop=True)
    st.dataframe(jobs)
    
    excel_data = to_excel(jobs)
    
    st.download_button(
        label="Download Excel file",
        data=excel_data,
        file_name=f"results_{date.today().strftime("%Y-%m-%d")}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    end_time = time.time()
    
    st.write(f"Finished in {(end_time - start_time) / 60:.1f} minutes")
