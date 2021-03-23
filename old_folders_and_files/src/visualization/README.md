# Visualization

## Web App

To run the web application:

1. From the Anaconda prompt create a new virtual environment
```
conda create --name [env_name] python=3.8 
Example: conda create --name wri_env python=3.8 
```

2. Activate the environment and install the requirements.txt file
```
conda activate [env_name]
example: conda activate wri_env

In the root directory `wrilatinamerica` execute the following command:
pip install -r requirements.txt
```

3. Download the contents of this [directory](https://drive.google.com/drive/folders/1eJe35OparLCM3CDKx_6dyJsixV1s9p9j) and place them inside `data/processed/2020-10-04`. The resulting directory structure should look like this:

```
data/
    external/
    interim/
    processed/
        2020-10-04/
            Chile/
                json/
                preprocessed_txt/
                txt/
                json_improved/
            El Salvador/
            Guatemala/
            Mexico/
            Peru/
            test/
docs/
env/
...
```

4. Deploy the web server locally. This command must be executed from the root of the project (the directory containing `src`..).
```
uvicorn src.visualization.app:app --reload
```

5. Visit the web interface at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).