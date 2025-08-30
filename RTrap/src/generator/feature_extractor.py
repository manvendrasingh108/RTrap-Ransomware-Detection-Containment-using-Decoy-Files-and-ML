import numpy as np
from sklearn.decomposition import PCA
import pandas as pd # DataFrames ke liye

class FeatureExtractor:
    def __init__(self, n_components=0.99):
        """
        PCA Feature Extractor ko initialize karta hai.
        n_components: Kitna variance explain karna hai (float) ya kitne components rakhne hain (int).
                      Default 0.99 matlab 99% variance retain karna hai.
        """
        self.n_components = n_components
        self.pca = PCA(n_components=self.n_components)
        self.is_fitted = False # Track karne ke liye ki PCA fit hua hai ya nahi

    def fit(self, data_df):
        """
        Data par PCA ko fit karta hai.
        data_df: Pandas DataFrame jismein preprocessed numerical features hain.
                 FileAttributesPreprocessor se aaya hua DataFrame.
        """
        # PCA ko fit karne ke liye sirf feature columns chahiye
        # Yahaan hum मान रहे हैं ki input DataFrame mein woh columns hain jo preprocessing ke baad ML ready hain.
        # FileAttributesPreprocessor mein humne 'processed_df' select kiya tha, ab hum usko use karenge.
        # Let's assume the input data_df has the feature columns needed for PCA
        # We need to make sure the columns passed to fit are ONLY the numerical/encoded features
        # NOT the original file paths, extensions, etc.

        # Ek list define karte hain expected feature columns ki
        feature_columns_for_pca = [
            'extension_encoded',
            'size_scaled',
            'creation_hour_sin', 'creation_hour_cos',
            'modification_hour_sin', 'modification_hour_cos',
            'creation_dayofweek_sin', 'creation_dayofweek_cos',
            'modification_dayofweek_sin', 'modification_dayofweek_cos'
        ]

        # Sirf un columns ko select karein jo input DataFrame mein hain aur PCA ke liye zaroori hain
        # Agar koi column missing hai toh handle kar sakte hain
        present_feature_columns = [col for col in feature_columns_for_pca if col in data_df.columns]

        if not present_feature_columns:
            print("Error: No valid feature columns found in the input DataFrame for PCA.")
            self.is_fitted = False
            return None # Indicate failure

        # Data ko numpy array mein convert karein PCA ke liye
        data_for_pca = data_df[present_feature_columns].values

        try:
            # PCA ko data par fit karein
            self.pca.fit(data_for_pca)
            self.is_fitted = True
            print(f"PCA fitted successfully. Number of components selected: {self.pca.n_components_}")
            return self # Return self for chaining methods
        except Exception as e:
            print(f"Error fitting PCA: {e}")
            self.is_fitted = False
            return None

    def transform(self, data_df):
        """
        Data ko dimension-reduced space mein transform karta hai using the fitted PCA.
        data_df: Pandas DataFrame jismein preprocessed numerical features hain.
                 Yeh wahi format mein hona chahiye jaisa fit karte waqt tha.
        """
        if not self.is_fitted:
            print("Error: PCA is not fitted yet. Call .fit() first.")
            return pd.DataFrame() # Return empty DataFrame

        # Sirf feature columns ko select karein transform karne ke liye
        feature_columns_for_pca = [
             'extension_encoded',
            'size_scaled',
            'creation_hour_sin', 'creation_hour_cos',
            'modification_hour_sin', 'modification_hour_cos',
            'creation_dayofweek_sin', 'creation_dayofweek_cos',
            'modification_dayofweek_sin', 'modification_dayofweek_cos'
        ]

        present_feature_columns = [col for col in feature_columns_for_pca if col in data_df.columns]

        if not present_feature_columns:
             print("Error: No valid feature columns found in the input DataFrame for PCA transformation.")
             return pd.DataFrame()

        data_for_pca = data_df[present_feature_columns].values


        try:
            # Data ko transform karein
            transformed_data = self.pca.transform(data_for_pca)

            # Transformed data ko wapas DataFrame mein convert karein
            # Columns ke naam 'principal_component_1', 'principal_component_2' etc. rakhte hain
            transformed_df = pd.DataFrame(transformed_data, columns=[f'pc_{i+1}' for i in range(transformed_data.shape[1])])

            # Original file paths ko bhi add kar sakte hain wapas reference ke liye
            # Iske liye hum original data_df ka 'file_path' column join kar sakte hain
            if 'file_path' in data_df.columns:
                 transformed_df['file_path'] = data_df['file_path'].values


            print("Data transformed using PCA.")
            return transformed_df # Return transformed data as DataFrame

        except Exception as e:
            print(f"Error transforming data using PCA: {e}")
            return pd.DataFrame()


    def fit_transform(self, data_df):
        """
        Data par PCA fit karta hai aur phir usse transform bhi karta hai.
        Convenience method.
        """
        if self.fit(data_df) is not None: # Check if fitting was successful
            return self.transform(data_df)
        else:
            return pd.DataFrame()


    def get_pca_state(self):
        """
        Fitted PCA ki state return karta hai (components, mean, etc.).
        """
        if self.is_fitted:
            return {
                'n_components_': self.pca.n_components_,
                'explained_variance_ratio_': self.pca.explained_variance_ratio_.tolist(), # Convert to list for easier saving (e.g., JSON)
                'mean_': self.pca.mean_.tolist(),
                'components_': self.pca.components_.tolist()
                # Aap aur bhi relevant attributes add kar sakte hain agar zaroorat ho
            }
        return None

    def load_pca_state(self, state):
        """
        Saved state se PCA ko load karta hai.
        """
        if state:
            self.pca = PCA(n_components=state['n_components_'])
            self.pca.mean_ = np.array(state['mean_'])
            self.pca.components_ = np.array(state['components_'])
            self.pca.explained_variance_ratio_ = np.array(state['explained_variance_ratio_'])
            self.is_fitted = True
            print("PCA state loaded.")
        else:
            print("No PCA state provided.")


# Example usage (Testing) - Is code ko run karne ke liye aapko FileAttributesPreprocessor ki zaroorat padegi
if __name__ == "__main__":
    # Is example ko run karne ke liye, humein FileAttributesPreprocessor se processed data chahiye hoga.
    # Hum pichhle example code se dummy data generate karke use kar sakte hain.

    print("Testing FeatureExtractor (PCA)...")

    # Dummy directory aur files (same as previous example)
    dummy_dir = "test_directory_pca"
    os.makedirs(dummy_dir, exist_ok=True)
    with open(os.path.join(dummy_dir, "document1.txt"), "w") as f:
        f.write("This is a test document.")
    time.sleep(0.1)
    with open(os.path.join(dummy_dir, "image.jpg"), "w") as f:
        f.write("Fake image content.")
    time.sleep(0.1)
    with open(os.path.join(dummy_dir, "report.pdf"), "w") as f:
        f.write("Fake pdf content.")
    time.sleep(0.1)
    with open(os.path.join(dummy_dir, "another_doc.txt"), "w") as f:
        f.write("Another text file.")
    time.sleep(0.1)
    with open(os.path.join(dummy_dir, "spreadsheet.csv"), "w") as f:
        f.write("col1,col2\n1,2\n3,4")


    # FileAttributesPreprocessor ka instance banayein aur data process karein
    preprocessor = FileAttributesPreprocessor()
    processed_data_df = preprocessor.load_and_preprocess_directory(dummy_dir)

    if not processed_data_df.empty:
        print("\nData processed by FileAttributesPreprocessor:")
        print(processed_data_df[['extension_encoded', 'size_scaled', 'creation_hour_sin', 'modification_dayofweek_cos']].head()) # Example columns

        # FeatureExtractor (PCA) ka instance banayein
        # Hum yahaan 99% variance retain kar rahe hain (default)
        feature_extractor = FeatureExtractor(n_components=0.99)

        # Data par PCA fit aur transform karein
        transformed_data_df = feature_extractor.fit_transform(processed_data_df)

        if not transformed_data_df.empty:
            print("\nData transformed by FeatureExtractor (PCA):")
            print(transformed_data_df.head())
            print(f"\nOriginal dimensions: {processed_data_df.shape[1]} (including original columns like file_path)")
            print(f"Dimensions after PCA: {transformed_data_df.shape[1]} (including file_path if added back)")
            # Note: PCA output dimensions will be less than the input numerical features,
            # but the final DataFrame might have more if original columns are added back.
            print(f"Number of principal components: {feature_extractor.pca.n_components_}")
            print(f"Explained variance ratio: {feature_extractor.pca.explained_variance_ratio_.sum():.4f}")


        # Clean up dummy directory
        # import shutil
        # shutil.rmtree(dummy_dir)
        # print(f"\nCleaned up {dummy_dir}")
    else:
        print("No data to process for PCA.")