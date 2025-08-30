import os
import shutil
import random # Decoy names ko thoda random banane ke liye use kar sakte hain
import time # Agar zaroorat pade delays ke liye

class DecoyCreator:
    def __init__(self, decoy_marker="decoy"):
        """
        DecoyCreator ko initialize karta hai.
        decoy_marker: Ek string jo decoy files ke naam mein use hogi.
        """
        self.decoy_marker = decoy_marker

    def generate_decoy_name(self, original_file_path):
        """
        Original file path se deceptive decoy name generate karta hai.
        Paper ke mutabik, decoy_marker ko original name mein add kiya jata hai.
        Hum yahaan marker ko extension se pehle add kar rahe hain.
        Example: "document.txt" -> "document_decoy.txt"
        """
        directory, filename = os.path.split(original_file_path)
        name, ext = os.path.splitext(filename)

        # Decoy marker ko naam mein add karein
        # Aap alag strategy bhi use kar sakte hain (jaise prefix)
        decoy_filename = f"{name}_{self.decoy_marker}{ext}"

        # Poora path wapas banayein
        decoy_file_path = os.path.join(directory, decoy_filename)

        # Optional: Agar zaroorat pade toh naam ko thoda aur random kar sakte hain
        # Example: Adding a random string
        # random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4))
        # decoy_filename = f"{name}_{self.decoy_marker}_{random_suffix}{ext}"
        # decoy_file_path = os.path.join(directory, decoy_filename)

        return decoy_file_path

    def create_decoys(self, original_file_paths):
        """
        Selected original file paths se decoy files create karta hai.
        original_file_paths: List of strings, jismein un original files ke paths hain jise decoy banana hai.
                             Yeh DecoyPicker se aayega.
        """
        created_decoy_paths = []
        if not original_file_paths:
            print("No original file paths provided to create decoys.")
            return created_decoy_paths

        print(f"Creating {len(original_file_paths)} decoy files...")

        for original_path in original_file_paths:
            if not os.path.exists(original_path):
                print(f"Original file not found, skipping: {original_path}")
                continue

            # Decoy file ka naya naam generate karein
            decoy_path = self.generate_decoy_name(original_path)

            # Check karein ki naya naam original file se alag hai ya nahi (should be)
            if os.path.abspath(original_path) == os.path.abspath(decoy_path):
                 print(f"Generated decoy path is the same as original, skipping: {original_path}")
                 continue

            try:
                # Original file ko decoy path par copy karein
                shutil.copy2(original_path, decoy_path) # copy2 copies metadata too (timestamps etc.)
                created_decoy_paths.append(decoy_path)
                # print(f"Created decoy: {decoy_path}") # Optional: print created decoys

            except Exception as e:
                print(f"Error creating decoy for {original_path} to {decoy_path}: {e}")

        print(f"Finished creating decoys. Successfully created {len(created_decoy_paths)} files.")
        return created_decoy_paths

    # --- Decoy Update Mechanism (Future Enhancement / Integration Point) ---
    # Paper mein decoy files ko fresh rakhne ke liye update karne ki baat hai.
    # Iska code yahaan add kiya ja sakta hai, ya yeh functionality ek alag scheduler ya watcher trigger kar sakta hai.
    # Example: update_decoy(self, decoy_path, original_source_path) method.
    # This would involve copying content/metadata from the original_source_path to the decoy_path periodically.
    # The logic to determine *when* to update a decoy would be needed (e.g., if original file changed).
    # This might involve monitoring the original files (separate from the decoy watcher).
    # For now, we focus on creation.
    # --------------------------------------------------------------------


# Example usage (Testing) - Is code ko run karne ke liye DecoyPicker se selected paths chahiye honge
if __name__ == "__main__":
    print("Testing DecoyCreator...")

    # Dummy directory aur files (same as previous examples)
    dummy_dir = "test_directory_creator"
    os.makedirs(dummy_dir, exist_ok=True)
    file_paths = []
    files_to_create = ["report_Q1.docx", "budget.xlsx", "presentation.pptx", "notes.txt", "photo.png"]
    for i, file_name in enumerate(files_to_create):
         file_path = os.path.join(dummy_dir, file_name)
         with open(file_path, "w") as f:
              f.write(f"Content for {file_name}.")
         time.sleep(0.1) # Small delay to vary timestamps
         file_paths.append(file_path)


    # Simulate getting selected original file paths from DecoyPicker
    # In a real scenario, this list would come from the DecoyPicker's output.
    # For testing, let's just select a few dummy paths from our created files.
    # Assume DecoyPicker selected these:
    selected_original_paths_for_decoy = [
        os.path.join(dummy_dir, "report_Q1.docx"),
        os.path.join(dummy_dir, "presentation.pptx"),
        os.path.join(dummy_dir, "notes.txt")
    ]

    print("\nSimulating selected original file paths for decoy creation:")
    for path in selected_original_paths_for_decoy:
        print(path)


    # DecoyCreator ka instance banayein
    decoy_creator = DecoyCreator(decoy_marker="IMPORTANT_CONFIDENTIAL_DO_NOT_TOUCH") # User-defined marker

    # Decoy files create karein
    created_decoys = decoy_creator.create_decoys(selected_original_paths_for_decoy)

    print("\nCreated Decoy Files:")
    for decoy_path in created_decoys:
        print(decoy_path)
        # Check if the decoy file actually exists
        print(f"Exists: {os.path.exists(decoy_path)}")


    # Clean up dummy directory and created decoys
    # import shutil
    # shutil.rmtree(dummy_dir)
    # print(f"\nCleaned up {dummy_dir} and decoys")