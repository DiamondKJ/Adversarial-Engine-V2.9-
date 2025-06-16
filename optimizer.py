import torch
from transformers import AutoImageProcessor, ResNetForImageClassification, AutoModelForImageClassification
from PIL import Image
import requests
import time
import os
import glob
import numpy as np
import random
import json # For logging results

# --- Import from our perfected V2.8 factory ---
from factory import generate_overlord_mask

# --- CONSOLIDATED UTILITY FUNCTIONS ---
def get_saliency_map(model, processor, image, target_class_id):
    device = model.device 
    inputs = processor(images=image, return_tensors="pt").to(device)
    inputs.pixel_values.requires_grad = True
    logits = model(**inputs).logits
    score = logits[:, target_class_id].sum()
    model.zero_grad()
    score.backward()
    saliency, _ = torch.max(inputs.pixel_values.grad.data.abs(), dim=1)
    saliency = saliency.squeeze(0)
    if saliency.max() > saliency.min():
        saliency = (saliency - saliency.min()) / (saliency.max() - saliency.min())
    return saliency.cpu().numpy()

def setup_environment(base_dir="optimizer_results"):
    """Creates a master directory for all optimization results."""
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return base_dir

def run_single_attack(original_image, combined_saliency, intensity):
    """Generates one mask and tests it, returning True if a dual kill."""
    masked_image = generate_overlord_mask(original_image, combined_saliency, intensity=intensity)
    
    with torch.no_grad():
        resnet_adv_id = resnet_model(**resnet_processor(images=masked_image, return_tensors="pt").to(device)).logits.argmax(-1).item()
        vit_adv_id = vit_model(**vit_processor(images=masked_image, return_tensors="pt").to(device)).logits.argmax(-1).item()
    
    return resnet_adv_id != resnet_baseline_id and vit_adv_id != vit_baseline_id, masked_image

if __name__ == "__main__":
    # --- GLOBAL SETUP ---
    print("PROJECT SISYPHUS: AUTONOMOUS OPTIMIZATION AGENT ACTIVATED.")
    device = torch.device("mps")
    print("Loading models...")
    resnet_processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
    resnet_model = ResNetForImageClassification.from_pretrained("microsoft/resnet-50").to(device)
    vit_processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")
    vit_model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224").to(device)
    print("Models loaded. Gauntlet is hardened.")

    # --- OPTIMIZATION PARAMETERS ---
    # --- OPTIMIZATION PARAMETERS: EXTENDED CAMPAIGN ---
    ARMORY_FOLDER = "armory"

    # We will now run 50 attacks for each data point to ensure high statistical confidence.
    NUM_RUNS_PER_IMAGE_PER_INTENSITY = 50 

    # We will search the intensity space with much higher resolution, in 2.5% increments.
    # This is a deep search from subtle to overwhelming.
    INTENSITY_LEVELS_TO_TEST = [
        0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 
        0.75, 0.80, 0.85, 0.90, 0.95, 1.0
    ]
    
    RESULTS_DIR = setup_environment()
    RESULTS_LOG_FILE = os.path.join(RESULTS_DIR, "optimization_log.json")

    target_paths = glob.glob(os.path.join(ARMORY_FOLDER, "*.jpg")) + glob.glob(os.path.join(ARMORY_FOLDER, "*.png"))
    if not target_paths: print(f"FATAL ERROR: The '{ARMORY_FOLDER}' is empty."); exit()
    
    # --- MASTER OPTIMIZATION LOOP ---
    campaign_results = {}

    for intensity in INTENSITY_LEVELS_TO_TEST:
        print("\n" + "*"*60)
        print(f"*** BEGINNING CAMPAIGN FOR INTENSITY LEVEL: {intensity*100:.1f}% ***")
        print("*"*60)
        
        # Create a subfolder for this intensity's successful images
        intensity_victory_folder = os.path.join(RESULTS_DIR, f"victories_at_{int(intensity*100)}pct")
        if not os.path.exists(intensity_victory_folder): os.makedirs(intensity_victory_folder)

        total_kills_this_intensity = 0
        total_attempts_this_intensity = 0

        for target_path in target_paths:
            filename = os.path.basename(target_path)
            print(f"\n--- Acquiring Target: {filename} ---")
            
            try: original_image = Image.open(target_path).convert("RGB")
            except Exception as e: print(f"  > ERROR: Could not load. Skipping. {e}"); continue

            with torch.no_grad():
                resnet_baseline_id = resnet_model(**resnet_processor(images=original_image, return_tensors="pt").to(device)).logits.argmax(-1).item()
                vit_baseline_id = vit_model(**vit_processor(images=original_image, return_tensors="pt").to(device)).logits.argmax(-1).item()

            label2id = {v: k for k, v in resnet_model.config.id2label.items()}
            decoy_class_id = random.randint(0, len(label2id) - 1)
            
            try:
                resnet_saliency = get_saliency_map(resnet_model, resnet_processor, original_image, decoy_class_id)
                vit_saliency = get_saliency_map(vit_model, vit_processor, original_image, decoy_class_id)
                vit_saliency_resized = np.array(Image.fromarray(vit_saliency).resize((resnet_saliency.shape[1], resnet_saliency.shape[0])))
                combined_saliency = resnet_saliency + vit_saliency_resized
            except Exception as e:
                print(f"  > Saliency failed. Defaulting to central focus. {e}");
                h,w = (224,224); combined_saliency=np.zeros((h,w)); combined_saliency[h//4:h*3//4,w//4:w*3//4]=1

            for run in range(NUM_RUNS_PER_IMAGE_PER_INTENSITY):
                is_kill, masked_image = run_single_attack(original_image, combined_saliency, intensity)
                if is_kill:
                    total_kills_this_intensity += 1
                    # Save a sample of the victorious images
                    if run < 3: # Save first 3 victories per image for review
                        save_path = os.path.join(intensity_victory_folder, f"{filename.split('.')[0]}_victory_{run+1}.png")
                        masked_image.save(save_path)
                
                total_attempts_this_intensity += 1

        # Log results for this intensity level
        success_rate = (total_kills_this_intensity / total_attempts_this_intensity) * 100
        campaign_results[intensity] = success_rate
        print(f"\n--- CAMPAIGN DEBRIEF FOR INTENSITY {intensity*100:.1f}% ---")
        print(f"  > Success Rate: {success_rate:.2f}% ({total_kills_this_intensity}/{total_attempts_this_intensity})")

        # Save results incrementally
        with open(RESULTS_LOG_FILE, 'w') as f:
            json.dump(campaign_results, f, indent=4)
    
    # --- FINAL REPORT ---
    print("\n\n" + "="*60); print("           PROJECT SISYPHUS COMPLETE"); print("="*60)
    
    best_intensity = 0
    best_rate = 0
    for intensity, rate in campaign_results.items():
        print(f"  - Intensity {intensity*100:.1f}% achieved a {rate:.2f}% success rate.")
        if rate > best_rate:
            best_rate = rate
            best_intensity = intensity
    
    print("\n--- FINAL RECOMMENDATION ---")
    print(f"The optimal balance of lethality was found at {best_intensity*100:.1f}% INTENSITY, achieving a {best_rate:.2f}% GENERALIZED SUCCESS RATE.")
    print(f"Review sample victory images in the 'optimizer_results/victories_at_{int(best_intensity*100)}pct' folder.")