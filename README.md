# Project ACE: Adversarial Chaos Engine

**Version:** 2.9  
**Status:** Research & Development (Act I Complete)  
**Project Lead:** Kaustubh Joshi

---

### 1. Project Summary

This repository contains the complete codebase and final results for Act I of **Project ACE (Adversarial Chaos Engine)**. This project is a research initiative into the generation of robust, visually complex adversarial examples designed to test the resilience of modern AI vision models.

The primary objective of this phase was to engineer and optimize a system capable of programmatically generating image masks that cause a high rate of misclassification in a diverse AI gauntlet (Google's Vision Transformer and Microsoft's ResNet-50), while aiming to preserve core structural information for human observers.

Through a rigorous, data-driven optimization process, the system achieved a **99.6% generalized misclassification rate** at a 95% intensity setting across a diverse, programmatically generated testbed of 100 images.

### 2. System Architecture & Methodology

The final V2.9 engine employs a strategy termed **"Saliency-Guided Perturbation,"** leveraging a **"Decoy Class Hallucination"** technique.

-   **Intelligence Layer:** The system first establishes a baseline classification from the target models. It then programmatically selects a plausible but incorrect "decoy" class from the model's own vocabulary. A saliency map is then generated based on the pixel gradients required to shift the model's prediction *towards this decoy class*.

-   **Perturbation Module (`generate_overlord_mask`):** This module uses the saliency "heat map" to apply a multi-layered and randomized set of visual artifacts to the image. The goal is to corrupt the features most critical to the AI's decision-making process. The layers include:
    1.  **Global Noise:** A low-density application of geometric shapes and lines across the entire image.
    2.  **Focused Noise:** A high-density application of shapes, lines, and T-Junction patterns concentrated on the salient regions identified by the intelligence layer.
    3.  **Structural Interference:** An adversarial grid pattern designed to disrupt the feature extraction process of both CNNs and Transformers.
    4.  **Data-Level Corruption:** Includes pixel scattering (shuffling local pixel regions) and a "glass storm" effect (high-frequency color noise) to finalize the corruption of salient features.

### 3. Key Findings from Automated Optimization

An autonomous agent (`optimizer.py`) was deployed to systematically evaluate the engine's performance across 15 different intensity levels (from 30% to 100%). This involved conducting over 7,500 individual tests against a 100-image testbed.

![ACE V2 Performance Curve](optimizer_results/performance_graph.png)

*   **Efficacy Threshold:** A significant performance increase was observed as intensity rose past the 50% mark, where the models' classification accuracy dropped below 5%.
*   **Peak Performance vs. Optimal Setting:** While 100% intensity yielded the highest misclassification rate (99.88%), an intensity of **0.95 (95%)** was identified as the optimal setting, achieving a **99.64%** success rate. This level provides near-total adversarial effectiveness while best preserving the original image's structural information for human interpretation.

### 4. How to Reproduce This Research

This project is structured for full reproducibility.

1.  **Setup the Environment:**
    - It is recommended to use a Python virtual environment.
    - Install all necessary dependencies:
      ```bash
      pip install torch torchvision transformers Pillow numpy tqdm matplotlib seaborn
      ```

2.  **Build the Image Testbed (Armory):**
    - Run the `armory_builder.py` script to automatically download 100 diverse test images into the `armory/` directory.
      ```bash
      python armory_builder.py
      ```

3.  **Run the Optimization Analysis:**
    - Execute the `optimizer.py` script. This is a long-running process that will replicate the full optimization campaign and generate the `optimization_log.json`.
      ```bash
      python optimizer.py
      ```

4.  **Visualize the Results:**
    - After the optimizer completes, run the `plot_results.py` script to generate the performance graph from the log file.
      ```bash
      python plot_results.py
      ```

### 5. Next Steps (Act II)

With the Gen-1 adversarial generation engine validated, the next phase of the project will focus on the "Arms Race" cycle:
1.  **Generate Dataset:** Use the V2.9 engine to create a large dataset of adversarial examples.
2.  **Adversarial Training:** Fine-tune a new AI model on this dataset to create a "hardened" defense.
3.  **Evolve the Attack:** Develop and test a new generation of adversarial techniques capable of defeating this hardened model. 
