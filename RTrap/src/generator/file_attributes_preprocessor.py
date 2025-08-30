import os
import time
import datetime
import numpy as np
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
import pandas as pd # Pandas data handling ke liye helpful hoga

class FileAttributesPreprocessor:
    def __init__(self):
        # Standard Scaler numerical data ke liye (jaise file size)
        self.scaler = StandardScaler()
        # Ordinal Encoder categorical data ke liye (jaise file type)
        self.encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
        self.is_fitted = False # Track karne ke liye ki scaler aur encoder train hue hain ya nahi

    def extract_attributes(self, file_path):
        """
        Ek single file se attributes nikalta hai.
        """
        try:
            # File ka naam aur extension
            file_name, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower() # Extension ko lowercase mein kar dete hain

            # File size bytes mein
            file_size = os.path.getsize(file_path)

            # Creation time aur modification time (timestamp ke format mein)
            creation_timestamp = os.path.getctime(file_path)
            modification_timestamp = os.path.getmtime(file_path)

            # Yahaan aap aur attributes bhi add kar sakte hain agar paper mein mention hon ya zaroori laggein
            # Jaise, kya file hidden hai?, Read-only hai? (Windows specific ho sakte hain yeh)

            return {
                'file_path': file_path, # Original file path reference ke liye
                'extension': file_extension,
                'size': file_size,
                'creation_time': creation_timestamp,
                'modification_time': modification_timestamp
            }
        except Exception as e:
            print(f"Error extracting attributes for {file_path}: {e}")
            return None # Agar koi error aaye toh None return karein

    def load_and_preprocess_directory(self, directory_path):
        """
        Ek directory mein saari files ke attributes nikalta hai aur preprocess karta hai.
        """
        all_files_attributes = []
        # Walk through directory and subdirectories
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                attributes = self.extract_attributes(file_path)
                if attributes:
                    all_files_attributes.append(attributes)

        if not all_files_attributes:
            print(f"No files found or attributes extracted in {directory_path}")
            return pd.DataFrame() # Empty DataFrame return karein

        # List of dictionaries ko Pandas DataFrame mein convert karein
        df = pd.DataFrame(all_files_attributes)

        # Preprocessing steps
        # 1. Handle Categorical (Extension) - Ordinal Encoding
        # Pehle check karein agar encoder train nahi hua hai toh fit karein
        if not self.is_fitted:
             # Fit on all extensions found
            self.encoder.fit(df[['extension']])

        df['extension_encoded'] = self.encoder.transform(df[['extension']])

        # 2. Handle Numerical (Size) - Standard Scaling
        # Pehle check karein agar scaler train nahi hua hai toh fit karein
        if not self.is_fitted:
            # Fit on all sizes found
            # Reshape(-1, 1) because scaler expects input in this shape
            self.scaler.fit(df[['size']])

        df['size_scaled'] = self.scaler.transform(df[['size']])


        # 3. Handle Date/Time (Creation and Modification Time) - Sine/Cosine Transform
        # Timestamp ko datetime objects mein convert karein
        df['creation_dt'] = pd.to_datetime(df['creation_time'], unit='s')
        df['modification_dt'] = pd.to_datetime(df['modification_time'], unit='s')

        # Ab time ke cycles ko capture karne ke liye sine aur cosine use karein
        # Example: Time of day (hours)
        df['creation_hour'] = df['creation_dt'].dt.hour
        df['modification_hour'] = df['modification_dt'].dt.hour

        df['creation_hour_sin'] = np.sin(2 * np.pi * df['creation_hour'] / 24)
        df['creation_hour_cos'] = np.cos(2 * np.pi * df['creation_hour'] / 24)
        df['modification_hour_sin'] = np.sin(2 * np.pi * df['modification_hour'] / 24)
        df['modification_hour_cos'] = np.cos(2 * np.pi * df['modification_hour'] / 24)

        # Example: Day of the week (0=Monday, 6=Sunday)
        df['creation_dayofweek'] = df['creation_dt'].dt.dayofweek
        df['modification_dayofweek'] = df['modification_dt'].dt.dayofweek

        df['creation_dayofweek_sin'] = np.sin(2 * np.pi * df['creation_dayofweek'] / 7)
        df['creation_dayofweek_cos'] = np.cos(2 * np.pi * df['creation_dayofweek'] / 7)
        df['modification_dayofweek_sin'] = np.sin(2 * np.pi * df['modification_dayofweek'] / 7)
        df['modification_dayofweek_cos'] = np.cos(2 * np.pi * df['modification_dayofweek'] / 7)

        # Mark that scaler and encoder have been fitted
        self.is_fitted = True


        # Ab feature matrix select karein jo hum return karna chahte hain
        # Ismein sirf processed numerical features hongi
        feature_columns = [
            'extension_encoded',
            'size_scaled',
            'creation_hour_sin', 'creation_hour_cos',
            'modification_hour_sin', 'modification_hour_cos',
            'creation_dayofweek_sin', 'creation_dayofweek_cos',
            'modification_dayofweek_sin', 'modification_dayofweek_cos'
        ]
        # Yahaan hum sirf woh columns le rahe hain jinhe hum PCA aur AP ke liye use karenge
        processed_df = df[feature_columns]

        # Original file paths ko alag se return kar sakte hain ya DataFrame mein rehne dein
        # Filhaal ke liye hum poora processed DataFrame return kar dete hain jismein original paths bhi hain
        # Aap choose kar sakte hain ki aapko kya chahiye downstream components mein
        return df # Returning the entire dataframe with original and processed features

    def get_fitted_transformer_state(self):
        """
        Scaler aur encoder ka current state return karta hai,
        taki inhein save aur load kiya ja sake (production scenario ke liye zaroori).
        """
        if self.is_fitted:
            return {
                'scaler_mean': self.scaler.mean_,
                'scaler_scale': self.scaler.scale_,
                'encoder_categories': self.encoder.categories_
            }
        return None

    def load_transformer_state(self, state):
        """
        Saved state se scaler aur encoder ko load karta hai.
        """
        if state:
            self.scaler.mean_ = state['scaler_mean']
            self.scaler.scale_ = state['scaler_scale']
            self.encoder.categories_ = state['encoder_categories']
            self.is_fitted = True
            print("Transformer state loaded.")
        else:
            print("No transformer state provided.")


# Ek chota sa example code is class ko use karne ka (sirf testing ke liye)
if __name__ == "__main__":
    # Ek dummy directory banate hain testing ke liye
    dummy_dir = "test_directory"
    os.makedirs(dummy_dir, exist_ok=True)

    # Kuch dummy files banate hain
    with open(os.path.join(dummy_dir, "document1.txt"), "w") as f:
        f.write("This is a test document.")
    time.sleep(1) # Files ke creation time mein thoda farak ho
    with open(os.path.join(dummy_dir, "image.jpg"), "w") as f:
        f.write("Fake image content.")
    time.sleep(1)
    with open(os.path.join(dummy_dir, "report.pdf"), "w") as f:
        f.write("Fake pdf content.")
    time.sleep(1)
    # Ek file jise hum thodi der baad modify karenge
    file_to_modify = os.path.join(dummy_dir, "temp.txt")
    with open(file_to_modify, "w") as f:
        f.write("Initial content.")

    preprocessor = FileAttributesPreprocessor()

    print(f"Processing directory: {dummy_dir}")
    processed_data = preprocessor.load_and_preprocess_directory(dummy_dir)

    print("\nProcessed Data:")
    print(processed_data)

    # Dummy directory aur files ko clean up kar dete hain
    # import shutil
    # shutil.rmtree(dummy_dir)
    # print(f"\nCleaned up {dummy_dir}")

    # Note: Real application mein aapko files ko delete nahi karna hai!
    # Yeh example sirf preprocessing logic ko test karne ke liye hai.