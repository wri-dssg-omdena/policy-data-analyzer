## Tasks

To create a new task folder, run `./create_task_folder.sh --name={FOLDER_NAME}`. It will automatically create a folder named `{FOLDER_NAME}` and 3 directories inside of it (with `.gitkeep` files inside each to maintain the structure):
- input
- output
- src

In addition, if you want to have a `notebooks` folder, you can add the argument `--add_notebooks=True` or `-an=True`
