import pandas as pd

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