import numpy as np
from sklearn.cluster import AffinityPropagation
import pandas as pd # DataFrames ke liye

class DecoyPicker:
    def __init__(self, damping=0.5, max_iter=200, convergence_iter=15, preference=None):
        """
        Affinity Propagation Decoy Picker ko initialize karta hai.
        Parameters AffinityPropagation algorithm ke hain:
        damping: Jitter ko control karta hai oscillations se bachne ke liye.
        max_iter: Maximum iterations kitne chalane hain.
        convergence_iter: Kitne iterations tak koi change na ho to converge maan liya jata hai.
        preference: Data points ke liye preference set karta hai exemplar banne ke liye.
                    None hone par median similarity use hoti hai.
        """
        self.damping = damping
        self.max_iter = max_iter
        self.convergence_iter = convergence_iter
        self.preference = preference # Ye auto-calculated bhi ho sakta hai, paper ke mutabik

        self.af = AffinityPropagation(
            damping=self.damping,
            max_iter=self.max_iter,
            convergence_iter=self.convergence_iter,
            preference=self.preference,
            random_state=0 # For reproducibility, can be removed in production
        )
        self.is_fitted = False # Track karne ke liye ki Affinity Propagation fit hua hai ya nahi

    def fit(self, transformed_data_df):
        """
        Dimension-reduced data par Affinity Propagation ko fit karta hai.
        transformed_data_df: Pandas DataFrame jismein PCA transformed features hain
                             (FeatureExtractor se aaya hua). Ismein original 'file_path' column bhi ho sakta hai.
        """
        if transformed_data_df.empty:
            print("Error: Input DataFrame for DecoyPicker is empty.")
            self.is_fitted = False
            return None # Indicate failure

        # Affinity Propagation ko fit karne ke liye sirf PCA component columns chahiye
        # Humein woh columns identify karne padenge jo PCA components hain (e.g., 'pc_1', 'pc_2', ...)
        # Assuming columns starting with 'pc_' are the PCA components
        pca_columns = [col for col in transformed_data_df.columns if col.startswith('pc_')]

        if not pca_columns:
            print("Error: No PCA component columns found in the input DataFrame for DecoyPicker.")
            self.is_fitted = False
            return None # Indicate failure

        # Data ko numpy array mein convert karein Affinity Propagation ke liye
        data_for_af = transformed_data_df[pca_columns].values

        # Paper mein similarity metric negative Euclidean distance hai.
        # scikit-learn ka AffinityPropagation default mein negative squared Euclidean distance use karta hai
        # Agar aap paper ke exact similarity function use karna chahte hain, toh aap precomputed similarity matrix de sakte hain.
        # Filhaal hum default use kar rahe hain.

        try:
            # Affinity Propagation ko data par fit karein
            # Agar preference None hai, toh scikit-learn default mein median similarity use kar leta hai.
            self.af.fit(data_for_af)
            self.is_fitted = True
            self.exemplar_indices = self.af.cluster_centers_indices_
            self.n_selected_decoys = len(self.exemplar_indices)

            print(f"Affinity Propagation fitted successfully.")
            print(f"Number of decoy candidates selected: {self.n_selected_decoys}")

            return self # Return self for chaining methods

        except Exception as e:
            print(f"Error fitting Affinity Propagation: {e}")
            self.is_fitted = False
            return None

    def get_decoy_candidates(self, original_data_df):
        """
        Fitted Affinity Propagation se selected decoy candidates ke original file paths return karta hai.
        original_data_df: Original DataFrame jismein 'file_path' column hai (jaise FileAttributesPreprocessor se mila tha).
                          Yeh ensure karne ke liye ki hum sahi files choose kar rahe hain unke index ke base par.
        """
        if not self.is_fitted:
            print("Error: Affinity Propagation is not fitted yet. Call .fit() first.")
            return [] # Return empty list

        if 'file_path' not in original_data_df.columns:
             print("Error: 'file_path' column not found in the original_data_df.")
             return []

        # Selected exemplar indices ka use karke original file paths nikalna
        # Humein original DataFrame ke indices use karne honge
        # Assuming the order of rows in transformed_data_df and original_data_df is the same
        # This is important! Ensure data is aligned throughout the pipeline.
        try:
            decoy_candidate_paths = original_data_df.iloc[self.exemplar_indices]['file_path'].tolist()
            print("Decoy candidates selected.")
            return decoy_candidate_paths

        except Exception as e:
            print(f"Error getting decoy candidates: {e}")
            return []

    def fit_and_get_candidates(self, transformed_data_df, original_data_df):
        """
        Affinity Propagation fit karta hai aur selected decoy candidates return karta hai.
        Convenience method.
        """
        if self.fit(transformed_data_df) is not None: # Check if fitting was successful
            return self.get_decoy_candidates(original_data_df)
        else:
            return []


# Example usage (Testing) - Is code ko run karne ke liye aapko FileAttributesPreprocessor aur FeatureExtractor ki zaroorat padegi
if __name__ == "__main__":
    print("Testing DecoyPicker (Affinity Propagation)...")

    # Dummy directory aur files (same as previous examples)
    dummy_dir = "test_directory_ap"
    os.makedirs(dummy_dir, exist_ok=True)
    file_paths = []
    files_to_create = ["doc_A.txt", "doc_B.txt", "image_1.jpg", "image_2.jpg", "report_X.pdf", "report_Y.pdf", "data.csv", "script.py"]
    for i, file_name in enumerate(files_to_create):
         file_path = os.path.join(dummy_dir, file_name)
         with open(file_path, "w") as f:
              f.write(f"Content for {file_name}.")
         time.sleep(0.1) # Small delay to vary timestamps
         file_paths.append(file_path)


    # Step 1: Preprocess data using FileAttributesPreprocessor
    preprocessor = FileAttributesPreprocessor()
    original_and_processed_data_df = preprocessor.load_and_preprocess_directory(dummy_dir)

    if not original_and_processed_data_df.empty:
        print("\nStep 1: Data processed by FileAttributesPreprocessor.")
        # print(original_and_processed_data_df.head()) # Debugging line

        # Step 2: Extract features using FeatureExtractor (PCA)
        # Hum pehle se fit kiye hue preprocessor aur extractor use karne ka simulate kar rahe hain
        # Asli use case mein inko train karke state save/load kiya ja sakta hai.
        # Lekin testing example ke liye hum yahaan naya instance bana rahe hain.
        feature_extractor = FeatureExtractor(n_components=0.99) # Retain 99% variance

        # Fit and transform data - Iske liye processed_data_df ke sirf feature columns pass karne honge
        # Let's manually select feature columns from original_and_processed_data_df
        feature_columns_for_pca = [
             'extension_encoded',
            'size_scaled',
            'creation_hour_sin', 'creation_hour_cos',
            'modification_hour_sin', 'modification_hour_cos',
            'creation_dayofweek_sin', 'creation_dayofweek_cos',
            'modification_dayofweek_sin', 'modification_dayofweek_cos'
        ]
        # Ensure only valid columns are selected
        present_feature_columns = [col for col in feature_columns_for_pca if col in original_and_processed_data_df.columns]
        data_for_pca = original_and_processed_data_df[present_feature_columns]


        # Using fit_transform directly for simplicity in this test
        transformed_data_df = feature_extractor.fit_transform(original_and_processed_data_df)


        if not transformed_data_df.empty:
            print("\nStep 2: Data transformed by FeatureExtractor (PCA).")
            print(f"Shape after PCA: {transformed_data_df.shape}")
            print(transformed_data_df.head()) # Debugging line

            # Step 3: Pick decoy candidates using DecoyPicker (Affinity Propagation)
            decoy_picker = DecoyPicker()

            # Fit Affinity Propagation and get decoy candidates
            # Humein transformed data aur original data (file paths ke liye) dono chahiye
            decoy_candidates = decoy_picker.fit_and_get_candidates(transformed_data_df, original_and_processed_data_df)


            if decoy_candidates:
                print("\nStep 3: Selected Decoy Candidates (Original Paths):")
                for candidate in decoy_candidates:
                    print(candidate)
                print(f"Total selected decoy candidates: {len(decoy_candidates)}")
            else:
                 print("\nStep 3: No decoy candidates selected.")


        # Clean up dummy directory
        # import shutil
        # shutil.rmtree(dummy_dir)
        # print(f"\nCleaned up {dummy_dir}")
    else:
        print("No data to process for DecoyPicker.")