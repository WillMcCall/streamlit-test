import pandas as pd
from io import BytesIO
from jobspy import scrape_jobs
import time


def get_jobs(job_titles: list[str], locations: list[str], days_old: int, my_bar, counter: int, total_jobs, num_jobs_wanted: int) -> list[pd.DataFrame, int]:
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
            counter += ((100 / total_jobs) / 100)
            my_bar.progress(counter, text="Scraping in progress. Please wait...")            
            time.sleep(5) # Avoid rate limiting
    
    df = pd.concat(dfs, ignore_index=True)
    cleaned_df = clean_jobs(df)
    final_df = filter_jobs(cleaned_df, num_jobs_wanted)
    return [final_df, counter]
    

def clean_jobs(jobs: pd.DataFrame) -> pd.DataFrame:
    # Removes Duplicates
    cleaned_jobs = jobs.drop_duplicates().reset_index(drop=True)
    
    # Removes all these unnecessary columns
    cleaned_jobs = cleaned_jobs.drop(
        ["id", "site", "job_url_direct", "job_type", "salary_source", "currency", "is_remote", "job_level", "job_function", 
         "listing_type", "emails", "company_industry", "company_logo", "company_url", "company_addresses", 
         "company_description", "skills", "experience_range", "company_rating", "company_reviews_count", "vacancy_count", 
         "work_from_home_type", "interval"], axis=1, errors='ignore')
    
    return cleaned_jobs


def filter_jobs(jobs: pd.DataFrame, num_jobs: int) -> pd.DataFrame:
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
