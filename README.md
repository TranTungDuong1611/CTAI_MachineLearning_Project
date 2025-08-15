# CTAI_MachineLearning_Project

## Objective

Developing a news aggregation and text summarization system based on users' personal experiences


## Project Structure

```
CTAI_MachineLearning_Project
├── LICENSE
├── Makefile                        <- Makefile with commands like `make data` or `make train`.
├── README.md                       <- The top-level README for developers using this project.
├── data
│   ├── external                    <- Data from third party sources.
│   ├── interim                     <- Intermediate data that has been transformed.
│   ├── processed                   <- The final, canonical data sets for modeling.
│   └── raw                         <- The original, immutable data dump.
├── docs                            <- Documentation file
├── notebooks                       <- Jupyter notebooks
├── references                      <- Data dictionaries, manuals, and all other explanatory materials.
├── reports
│   └── figures                     <- Generated graphics and figures to be used in reporting
├── requirements.txt                <- The requirements file for reproducing the analysis environment
├── setup.py                        <- Make this project
├── src
│   ├── __init__.py                 <- Makes src a Python module
│   ├── data                        <- Scripts to download or generate data
│   │   └── make_dataset.py
│   ├── features                    <- Scripts to turn raw data into features for modeling
│   │   └── build_features.py
│   ├── models                      <- Scripts to train models and then use trained models to make
│   │   ├── predict_model.py        <- predictions
│   │   └── train_model.py
│   └── visualization               <- Scripts to create exploratory and results oriented visualizations
│       └── visualize.py
├── scripts               
│   ├── infer.py                
│   └── test.py     
├── main.py                         <- main.py                
├── .gitignore                      <- .gitignore file
└── README.md                       <- README.md file
```
