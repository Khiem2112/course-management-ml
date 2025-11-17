import pandas as pd
import numpy as np
import joblib
import umap
from sklearn.preprocessing import PowerTransformer, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.cluster import KMeans
from sklearn import set_config

from database.execute_service import DBExecuteService as db
from utils.logger import get_class_logger

# 1. Tell Scikit-Learn to output Pandas DataFrames instead of Numpy Arrays
# This allows us to select columns by name (e.g., df[engagement_columns]) after scaling.
set_config(transform_output="pandas")

logger = get_class_logger(__name__, "StudentClusterPipeline")

class StudentClusterPipeline:
    """
    Encapsulates the end-to-end logic:
    Raw CSV -> Preprocess -> Select Engagement Feats -> UMAP -> KMeans -> DB Update
    """
    
    # --- Configuration Constants ---
    NUMERICAL_COLS = [
        'sum', 'count', 'score', 'num_of_prev_attempts', 
        'assessment_engagement_score', 'submission_timeliness', 
        'score_per_weight', 'module_engagement_rate', 'repeat_student', 
        'performance_by_registration', 'weighted_engagement', 
        'cumulative_score', 'engagement_consistency', 'learning_pace', 
        'engagement_dropoff', 'activity_diversity', 'improvement_rate'
    ]

    CATEGORICAL_COLS = [
        'activity_type', 'gender', 'region', 'highest_education', 
        'imd_band', 'age_band', 'disability', 'final_result', 
        'study_status', 'withdrawal_status'
    ]

    # The specific subset of features used for UMAP -> Clustering
    ENGAGEMENT_COLUMNS = [
        'assessment_engagement_score',
        'module_engagement_rate',
        'weighted_engagement',
        'engagement_consistency',
        'learning_pace',
        'engagement_dropoff',
        'activity_diversity'
    ]

    def __init__(self, n_clusters=7, random_state=42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans = None

    def run_full_training_cycle(self, summary_csv_path: str):
        """
        Master method to orchestrate the entire flow.
        """
        logger.info("1. Loading Data...")
        df = self._load_data(summary_csv_path)
        # Sanitize data to handle those large values
        logger.info("1b. Sanitizing Data (Removing Infs/NaNs)...")
        df = self._sanitize_data(df)
        
        # Save IDs for later merge
        student_ids = df['id_student']
        train_data = df.drop(columns=['id_student'])
        
        logger.info("2. Preprocessing (Scaling & Encoding)...")
        # Returns a DataFrame with all columns scaled/encoded
        final_data_encoded_df = self._preprocess_data(train_data)
        
        logger.info("3. Running UMAP Reduction (Engagement Columns Only)...")
        # --- CRITICAL FIX: Select only specific engagement features ---
        try:
            umap_input = final_data_encoded_df[self.ENGAGEMENT_COLUMNS]
        except KeyError as e:
            logger.error(f"Missing engagement columns in processed data: {e}")
            return

        clusterable_embedding = umap.UMAP(
            n_neighbors=100,
            min_dist=0.0,
            n_components=2,
            random_state=self.random_state,
        ).fit_transform(umap_input)
        
        logger.info(f"4. Training K-Means (K={self.n_clusters})...")
        self.kmeans = KMeans(
            n_clusters=self.n_clusters, 
            random_state=self.random_state, 
            n_init=10
        )
        cluster_labels = self.kmeans.fit_predict(clusterable_embedding)
        
        logger.info("5. Preparing & Executing DB Update...")
        # Combine IDs, original preferences, and new clusters
        result_df = pd.DataFrame({
            'id_student': student_ids,
            'study_method_preference': df['study_method_preference'],
            'kmeans_cluster': cluster_labels
        })
        
        # Save artifact for reference
        # result_df.to_csv("../data/student_after_clustered.csv", index=False)
        
        # Perform the DB update
        self._bulk_update_database(result_df)
        
        logger.info("Pipeline Complete.")

    def _load_data(self, path: str) -> pd.DataFrame:
        # Load all necessary columns
        cols = ['id_student', 'study_method_preference'] + self.NUMERICAL_COLS + self.CATEGORICAL_COLS
        return pd.read_csv(path)[cols]

    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies PowerTransformer to numerical and OneHotEncoder to categorical.
        Returns a Pandas DataFrame (thanks to set_config).
        """
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', PowerTransformer(), self.NUMERICAL_COLS),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), self.CATEGORICAL_COLS)
            ],
            verbose_feature_names_out=False # Keeps column names clean (e.g., 'gender' instead of 'cat__gender')
        )
        
        # fit_transform will return a DataFrame now
        return preprocessor.fit_transform(df)
    def _sanitize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean infinite values and NaNs that crash sklearn.
        """
        # 1. Replace Infinity with NaN
        df = df.replace([np.inf, -np.inf], np.nan)

        # 2. Fill NaNs in Numeric Columns with Median
        # (Median is more robust to outliers than Mean)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Check if we actually have NaNs to fill
        if df[numeric_cols].isnull().any().any():
            logger.warning("Found NaNs/Infs in numeric data. Filling with median.")
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

        # 3. Fill NaNs in Categorical Columns with 'Missing'
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns
        if df[categorical_cols].isnull().any().any():
            df[categorical_cols] = df[categorical_cols].fillna("Missing")

        return df

    def _bulk_update_database(self, df: pd.DataFrame):
        """
        Generates the SQL CASE statement for batch updates.
        """
        if df.empty:
            return

        # De-duplicate: one prediction per student
        df = df.drop_duplicates(subset=['id_student'], keep='last')
        
        ids = df['id_student'].tolist()
        ids_str = ", ".join(map(str, ids))
        
        cluster_case = "CASE id_student\n"
        
        for _, row in df.iterrows():
            cluster_case += f"    WHEN {row['id_student']} THEN {row['kmeans_cluster']}\n"
            
        cluster_case += "    ELSE cluster_id\nEND"
        
        query = (
            f"UPDATE studentInfo\n"
            f"SET cluster_id = {cluster_case}\n"
            f"WHERE id_student IN ({ids_str});"
        )
        
        try:
            # Execute via your DB Service
            db.execute_query(query)
            logger.info(f"Successfully updated clusters for {len(df)} students.")
        except Exception as e:
            logger.error(f"Database update failed: {e}")

# --- Run ---
if __name__ == "__main__":
    pipeline = StudentClusterPipeline()
    pipeline.run_full_training_cycle("inference/summary.csv")