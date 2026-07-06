# **Stainology Database**

This repository accompanies the paper:

**[Ovarian Stainology: Database of evidence-based immunohistochemical antigen expression in ovarian tumors](https://www.nature.com/articles/s41597-026-07776-1)**
Gruszczyński et al., *Scientific Data* (2026)

It provides all scripts and pipeline components used to extract, process, and structure immunohistochemistry (IHC) data from published scientific literature.

**Project website (database, documentation, more details): [stainology.cs.put.poznan.pl](https://stainology.cs.put.poznan.pl/)**

---

## **Version**

Current: **v1.1.0** — post-publication release with bug fixes to the deduplication step and extensive updates to stain and expression type nomenclature variation dictionaries.

To reproduce results exactly as published, use **[Release 1.0.1](https://github.com/jan-gruszczynski-publications/stainology-paper/releases/tag/v1.0.1)**.

---

## **Repository Structure**

### **`/data_extraction/`**

Contains all scripts used to identify relevant publications and extract IHC information from abstracts and tables.

---

### **`/post_processing/`**

Houses the implementation of pipeline modules used to clean, filter, normalize, and harmonize the raw extracted data.

Includes:

* Pipeline sub-modules that were used to implement post-processing steps.
* The full pipeline logic used to generate the final version of the dataset.

---

