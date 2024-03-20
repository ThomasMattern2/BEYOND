# #!/bin/bash

# # List of directories to run 'juni build' in
# directories=(
#     "functions/add-favourite"
#     "functions/create-object"
#     "functions/create-user"
#     "functions/delete-favourite"
#     "functions/delete-user"
#     "functions/edit-user"
#     "functions/get-all-objects"
#     "functions/get-favourites"
#     "functions/get-object"
#     "functions/get-user"
#     # Add more directories as needed
# )

# # Loop through each directory and run 'juni build'
# for dir in "${directories[@]}"; do
#     echo "Running 'juni build' in $dir..."
#     cd "$dir" && juni build
# done

# echo "Completed running 'juni build' in all directories."

#!/bin/bash

# Base directory containing the function directories
base_dir="./functions"

# Loop through each subdirectory in the base directory
for dir in "$base_dir"/*; do
    if [ -d "$dir" ]; then # Check if it's a directory
        echo "Running 'juni build' in $dir..."
        cd "$dir" && juni build
        cd - > /dev/null # Go back to the previous directory quietly
    fi
done

echo "Completed running 'juni build' in all directories."
