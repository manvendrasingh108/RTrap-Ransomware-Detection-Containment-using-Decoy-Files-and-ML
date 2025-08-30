# src/generator/generator.py

import os # Directory checks ke liye
from .file_attributes_preprocessor import FileAttributesPreprocessor
from .feature_extractor import FeatureExtractor
from .decoy_picker import DecoyPicker
from .decoy_creator import DecoyCreator
# Agar zaroorat pade toh config ya utils se bhi import kar sakte hain
# from ..config import settings # Example agar config use karna ho

class DecoyGenerator:
    def __init__(self, config_settings=None): # Default None agar config nahi provide ki gayi hai
        """
        DecoyGenerator ko initialize karta hai saare components ke instances ke saath.
        config_settings: Configuration se mili hui settings (dictionary ya object).
        """
        if config_settings is None:
            config_settings = {} # Agar None hai toh empty dict use karein

        self.preprocessor = FileAttributesPreprocessor()

        # PCA settings config se aa sakti hain
        # .get() use kar rahe hain default value ke liye agar config mein key nahi hai
        self.feature_extractor = FeatureExtractor(n_components=config_settings.get('pca_n_components', 0.99))

        # Affinity Propagation settings config se aa sakti hain
        self.decoy_picker = DecoyPicker(
            damping=config_settings.get('ap_damping', 0.5),
            max_iter=config_settings.get('ap_max_iter', 200),
            convergence_iter=config_settings.get('ap_convergence_iter', 15),
            preference=config_settings.get('ap_preference', None) # Preference can be tricky, handle carefully
            )

        # Decoy marker config se aa sakta hai
        self.decoy_creator = DecoyCreator(decoy_marker=config_settings.get('decoy_marker', "decoy"))

        self.config = config_settings # Configuration settings store kar lete hain

        # Real application mein aapko model states (scaler, encoder, pca, ap) ko load karna padega agar train ho chuke hain
        # self.load_model_states() # hypothetical method

    def generate_decoys_for_directory(self, directory_path):
        """
        Ek specific directory ke liye decoy files generate karta hai.
        """
        if not os.path.isdir(directory_path):
            print(f"Error: Directory not found or is not a directory: {directory_path}")
            return []

        print(f"Starting decoy generation for directory: {directory_path}")

        # 1. Files ke attributes load aur preprocess karein
        # load_and_preprocess_directory poora dataframe return karega jismein original paths aur processed features honge
        original_and_processed_data_df = self.preprocessor.load_and_preprocess_directory(directory_path)

        if original_and_processed_data_df.empty:
            print("No valid data to proceed with decoy generation.")
            return [] # Empty list of created decoys

        print("File attributes preprocessed.")
        # print(original_and_processed_data_df.head()) # Debugging line


        # 2. Features ko dimension-reduce karein (PCA)
        # Fit aur transform karne ke liye humein pehle se fit kiye hue PCA ki zaroorat hogi
        # Testing ke liye hum yahaan har baar naya fit kar rahe hain, but real mein load karna hoga
        # Or fit_transform call kar sakte hain agar data par pehli baar fit ho raha hai
        # Assuming `fit_transform` handles selecting the correct feature columns internally based on preprocessor logic
        transformed_data_df = self.feature_extractor.fit_transform(original_and_processed_data_df)


        if transformed_data_df.empty:
             print("Feature extraction failed or resulted in empty data.")
             return []

        print("Features extracted and dimension reduced using PCA.")
        # print(transformed_data_df.head()) # Debugging line


        # 3. Decoy candidates select karein (Affinity Propagation)
        # DecoyPicker ko transformed data chahiye aur original data (file paths ke liye)
        # Fit aur get candidates call karte waqt bhi pehle se fit Affinity Propagation ki zaroorat hogi
        # Testing ke liye hum yahaan fir se fit kar rahe hain
        decoy_candidate_paths = self.decoy_picker.fit_and_get_candidates(transformed_data_df, original_and_processed_data_df)


        if not decoy_candidate_paths:
            print("No decoy candidates selected by Affinity Propagation.")
            return []

        print(f"Selected {len(decoy_candidate_paths)} decoy candidates.")
        # print("Candidate paths:", decoy_candidate_paths) # Debugging line


        # 4. Decoy files create karein
        created_decoys = self.decoy_creator.create_decoys(decoy_candidate_paths)

        print("Decoy files created.")
        return created_decoys # Return list of created decoy paths

    # def load_model_states(self):
    #     """
    #     Loads the states of the fitted preprocessor, feature extractor, and decoy picker models.
    #     (Not implemented yet - shows where this logic would go)
    #     In a real application, you would save the fitted state of scaler, encoder, PCA, and AP
    #     after initial training/generation and load them here instead of refitting every time.
    #     """
    #     # Example:
    #     # try:
    #     #     with open('model_states.pkl', 'rb') as f:
    #     #         states = pickle.load(f)
    #     #     self.preprocessor.load_transformer_state(states.get('preprocessor'))
    #     #     self.feature_extractor.load_pca_state(states.get('pca'))
    #     #     self.decoy_picker.load_ap_state(states.get('ap')) # Assuming DecoyPicker has load_ap_state
    #     #     print("Model states loaded.")
    #     # except FileNotFoundError:
    #     #     print("Model states file not found. Will fit models on first run.")
    #     # except Exception as e:
    #     #     print(f"Error loading model states: {e}")
    #     pass

    # def save_model_states(self):
    #      """
    #      Saves the states of the fitted preprocessor, feature extractor, and decoy picker models.
    #      (Not implemented yet - shows where this logic would go)
    #      """
    #     # Example:
    #     # if self.preprocessor.is_fitted and self.feature_extractor.is_fitted and self.decoy_picker.is_fitted:
    #     #      states = {
    #     #          'preprocessor': self.preprocessor.get_fitted_transformer_state(),
    #     #          'pca': self.feature_extractor.get_pca_state(),
    #     #          'ap': self.decoy_picker.get_ap_state() # Assuming DecoyPicker has get_ap_state
    #     #      }
    #     #      try:
    #     #          with open('model_states.pkl', 'wb') as f:
    #     #              pickle.dump(states, f)
    #     #          print("Model states saved.")
    #     #      except Exception as e:
    #     #          print(f"Error saving model states: {e}")
    #     # else:
    #     #     print("Models are not fitted, cannot save states.")
    #     pass


# Example Usage (in main.py or another orchestration script) - This part is not in this file, just for context
# from src.generator.generator import DecoyGenerator
# from src.config.settings import get_settings # Assuming settings module exists and has get_settings

# config = get_settings() # Load configuration
# decoy_generator = DecoyGenerator(config)
#
# directory_to_protect = "C:\\Users\\YourUser\\Documents" # Example directory
# created_decoys = decoy_generator.generate_decoys_for_directory(directory_to_protect)
#
# print(f"\nDecoy generation process finished.")
# if created_decoys:
#     print(f"Successfully created {len(created_decoys)} decoy files.")
# else:
#     print("No decoy files were created.")