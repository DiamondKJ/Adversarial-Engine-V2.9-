import requests
import os
from tqdm import tqdm # A library for creating smart progress bars

def build_armory(num_images=100, output_folder="armory", image_size="800/600"):
    """
    Populates the local armory with random images from a stable API source.
    """
    print(f"--- ARMORY BUILDER v1.1 ACTIVATED ---")
    
    # 1. SETUP THE FOLDER
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created armory folder at: '{output_folder}'")
    else:
        print(f"Armory folder found at: '{output_folder}'. Will add new images.")

    # 2. DOWNLOAD IMAGES FROM PICSUM.PHOTOS
    # This service is designed for providing placeholder images and is very stable.
    base_url = f"https://picsum.photos/{image_size}"
    
    print(f"Preparing to download {num_images} new random images.")
    
    headers = {'User-Agent': 'ACE_Project_Armory_Builder/1.1'}
    download_count = 0

    # Using tqdm for a progress bar
    for i in tqdm(range(num_images), desc="Stocking Armory"):
        # The ?random={i} parameter ensures we get a different image each time
        img_url = f"{base_url}?random={i}"
        
        # We need a predictable filename
        img_filename = f"random_image_{i+1:03d}.jpg"
        save_path = os.path.join(output_folder, img_filename)

        # Skip if we already have this file (less likely with this method, but good practice)
        if os.path.exists(save_path):
            continue

        try:
            # We need to handle potential redirects from the URL
            with requests.get(img_url, headers=headers, stream=True, allow_redirects=True, timeout=10) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            download_count += 1
        except Exception as e:
            print(f"\nWarning: Failed to download image {i+1}. Skipping. Reason: {e}")

    print("\n--- ARMORY BUILD COMPLETE ---")
    print(f"Successfully downloaded {download_count} new images.")
    print(f"Armory is now stocked and ready for testing.")

if __name__ == '__main__':
    # You can change the number of images to download here
    build_armory(num_images=100)